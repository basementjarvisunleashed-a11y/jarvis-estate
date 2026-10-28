/**
 * Jarvis Recon Kit - phone-bridge (MentraOS app for Mentra Live)
 *
 * Eyes -> Brain. When HgX says "look" (or "recon"), the glasses publish their
 * camera straight to the Jarvis laptop's LAN ingest using startStream DIRECT
 * mode (no Mentra relay in the video path). The laptop-ingest service grabs a
 * frame, runs the local vision model, and replies to the watch.
 *
 * Scope: HgX's own glasses, phone, laptop, and home LAN only.
 * No secrets live in this file - everything comes from environment variables.
 */
import { AppServer, AppSession } from "@mentra/sdk";

const cfg = {
  packageName: process.env.PACKAGE_NAME ?? "com.hgx.jarvis.recon",
  apiKey: process.env.MENTRAOS_API_KEY ?? "",          // set in .env, never committed
  port: Number(process.env.PORT ?? 3000),
  // LAN ingest on the Jarvis laptop. rtmp://, srt://, or http(s)://.../whip
  ingestUrl: process.env.INGEST_URL ?? "",   // from .env only (includes MediaMTX publish creds)
  // laptop-ingest control API. This app server runs ON the laptop -> 127.0.0.1.
  ingestApi: process.env.INGEST_API ?? "http://127.0.0.1:8767",
  // Endpoint candidates, tried IN ORDER via GET /health only: LAN, then Tailscale, then cloud.
  // All from .env (no hardcoded IPs). Cloud leg is a STUB: disabled until HgX + SAF GO.
  ingestApiLan: process.env.INGEST_API_LAN ?? "",
  ingestApiTailscale: process.env.INGEST_API_TAILSCALE ?? "",
  cloudEnabled: (process.env.JV_CLOUD_JARVIS_ENABLED ?? "false") === "true",
  fps: Number(process.env.STREAM_FPS ?? 15),
  autoStopSec: Number(process.env.AUTO_STOP_SEC ?? 30),
};

if (!cfg.apiKey || !cfg.ingestUrl) {
  console.error("Missing MENTRAOS_API_KEY or INGEST_URL in .env - refusing to start.");
  process.exit(1);
}

const TRIGGERS = ["look", "recon", "what is this", "what am i looking at"];
// Nested timeouts (SAF): ingest 30 s < orchestrator 40 s < caller 45 s < voice 50 s.
const CALLER_TIMEOUT_MS = 45_000;
const VOICE_TIMEOUT_MS = 50_000;
const HEALTH_TIMEOUT_MS = 6_000;      // /health grabs one frame (<=4 s) on the laptop
const HEALTH_CACHE_MS = 60_000;

class AuthError extends Error {}       // auth fails CLOSED: never triggers failover

let picked: { url: string; at: number } | undefined;
/** LAN -> Tailscale -> (cloud stub). Only network errors move to the next leg; 401/403 stops. */
async function pickIngestApi(token: string): Promise<string> {
  if (picked && Date.now() - picked.at < HEALTH_CACHE_MS) return picked.url;
  const legs = [cfg.ingestApiLan, cfg.ingestApiTailscale, cfg.ingestApi].filter((u, i, a) => u && a.indexOf(u) === i);
  for (const url of legs) {
    try {
      const r = await fetch(`${url}/health`, { headers: { Authorization: `Bearer ${token}` },
                                               signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS) });
      if (r.status === 401 || r.status === 403) throw new AuthError("auth");
      if (r.ok) { picked = { url, at: Date.now() }; return url; }
    } catch (e) {
      if (e instanceof AuthError) throw e;   // fail closed
      /* network error -> next leg */
    }
  }
  if (cfg.cloudEnabled) {
    // TODO (BLOCKED - HgX answer + SAF GO): laptop-down leg = POST one `snapshot` envelope
    // straight to Cloud Jarvis over HTTPS. No tunnel, port-forward, or Funnel. Not implemented.
  }
  throw new Error("laptop unreachable");
}

class JarvisReconBridge extends AppServer {
  protected async onSession(session: AppSession, sessionId: string, userId: string) {
    let streamId: string | undefined;
    let stopTimer: NodeJS.Timeout | undefined;
    session.logger.info(`recon bridge session ${sessionId}`);

    const stop = async () => {
      if (stopTimer) clearTimeout(stopTimer);
      stopTimer = undefined;
      if (!streamId) return;
      try { await session.stream.stop(streamId); } catch (e) { session.logger.warn(`stop: ${e}`); }
      streamId = undefined;
    };

    const say = async (msg: string) => {
      try { await session.audio.speak(msg); } catch { /* speaker optional */ }
    };

    const look = async (prompt: string) => {
      let stage = "stream";
      const voiceDeadline = Date.now() + VOICE_TIMEOUT_MS;
      try {
        if (!streamId) {
          const r = await session.stream.startStream({
            direct: cfg.ingestUrl,
            video: { fps: cfg.fps, width: 1280, height: 720 },
            sound: true,                       // audible cue: camera is live
          });
          streamId = r.streamId;
          await new Promise((res) => setTimeout(res, 2500)); // let ingest get keyframes
        }
        // Ask the laptop to analyze the live feed. msgid lets the watch match it.
        const msgid = Math.floor(Math.random() * 1296).toString(36);
        stage = "ingest";
        const token = process.env.INGEST_TOKEN ?? "";                 // per-device token, .env only
        const api = await pickIngestApi(token);
        const resp = await fetch(`${api}/look`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          // Envelope v1 (shared/schema.json)
          body: JSON.stringify({ v: 1, id: msgid, ts: Date.now() / 1000, src: "glasses",
                                 kind: "cmd", payload: { prompt: prompt.slice(0, 300) } }),
          signal: AbortSignal.timeout(Math.min(CALLER_TIMEOUT_MS, voiceDeadline - Date.now())),
        });
        if (resp.status === 401 || resp.status === 403) throw new AuthError("auth");
        if (!resp.ok) throw new Error(`ingest HTTP ${resp.status}`);
        const env = (await resp.json()) as { v?: number; ack_of?: string; payload?: { text?: string } };
        if (env.v !== 1 || env.ack_of !== msgid) throw new Error("bad reply envelope"); // fail closed
        const text = env.payload?.text ?? "No result";   // untrusted text: speak only
        // Mentra Live has no HUD: speak it on the glasses' speakers.
        try { await session.audio.speak(text.slice(0, 300)); } catch { /* optional */ }
      } catch (e) {
        session.logger.error(`look failed at ${stage}: ${e}`);
        picked = undefined;                                  // re-probe /health next time
        // Short spoken error so HgX is never left waiting in silence.
        if (e instanceof AuthError) await say("Recon auth failed.");
        else if (stage === "stream") await say("Camera stream failed.");
        else if ((e as Error)?.name === "TimeoutError") await say("Recon timed out.");
        else if (String(e).includes("unreachable")) await say("Laptop unreachable.");
        else await say("Recon failed.");
      } finally {
        if (stopTimer) clearTimeout(stopTimer);
        stopTimer = setTimeout(stop, cfg.autoStopSec * 1000); // camera off when idle
      }
    };

    session.events.onTranscription(async (t) => {
      if (!t.isFinal) return;
      const said = t.text.toLowerCase().trim();
      if (said.includes("stop recon")) return stop();
      const hit = TRIGGERS.find((k) => said.startsWith(k) || said.includes(`jarvis ${k}`));
      if (hit) await look(said);
    });

    // Physical button on the glasses = look.
    session.events.onButtonPress(async (b) => {
      if (b.pressType === "short") await look("describe what is in front of me");
      if (b.pressType === "long") await stop();
    });

    this.addCleanupHandler?.(() => { void stop(); });
  }
}

new JarvisReconBridge({ packageName: cfg.packageName, apiKey: cfg.apiKey, port: cfg.port })
  .start()
  .then(() => console.log(`Jarvis recon bridge on :${cfg.port} -> ${cfg.ingestUrl}`));
