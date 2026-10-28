# ARCHITECTURE - Jarvis Recon Kit (Cartographer map, as built)

```
 LIMBS (sense / display only)                    BRAIN (Jarvis laptop, 127.0.0.1)
 ---------------------------                     ---------------------------------
 Mentra Live glasses --RTMP/SRT/WHIP (auth)-->  MediaMTX :1935/:8890/:8889 (LAN, publish auth)
   (camera, speakers)                               | rtsp 127.0.0.1:8554 (read auth)
        ^  speak reply                              v
        |                                       recon_ingest.py  127.0.0.1:8767
 phone-bridge (MentraOS app, on laptop :3000)      | 1 frame / >=2 s, <=1024 px, <1 MB, RAM only
   "look" -> POST /look envelope ----------->     | Ollama 127.0.0.1:11434 moondream:1.8b (pinned)
                                                   | retry 2/5/10 s -> queue (no cloud fallback)
                                                   v
                                         jarvis_lora_bridge.py push 127.0.0.1:8766
 T-Watch S3 <==LoRa SX1280, JV1 + HMAC==>  gateway node --USB serial--+
   "recon" / "recon:<prompt>"                                         |-> recon -> /look (8767)
   shows PENDING until ack, EYES card                                 |-> other -> orchestrator
   Wi-Fi path: POST /look (needs LAN bind)                                 POST 127.0.0.1:8080/jarvis
 Flipper Zero + ESP32 --USB serial--> flipper_jarvis.py (RX/scan only, ALLOW_TX=False)
```

## Rules
- **Brain-only:** only laptop-side services call models/tools; limbs never talk limb-to-limb.
- **Untrusted vision text:** never fed into the agentic `/jarvis` route (it can run tools);
  only displayed on the watch / spoken on the glasses. A non-agentic orchestrator
  `/recon` logging route is a *proposed* change (approval needed).
- **Envelope v1** `shared/schema.json` validated at ingest boundaries; fail closed.
- **LoRa:** <=200 B text only, never images; HMAC-SHA256/8 per frame when `JV_LORA_KEY` set;
  idempotent msgid; 3 retries 4/8/16 s; failures logged loudly.
- **Binding:** everything 127.0.0.1 except MediaMTX publish ports (LAN, auth, private firewall
  profile) and optionally ingest for the watch Wi-Fi path.
- **Health:** ingest `GET /health`; LoRa `P` presence frames; orchestrator `GET /`.
- **Data residency:** see INTEGRATION.md - life-log/captures laptop+USB only, outside synced trees.

## Ports
| Port | Service | Bind |
|------|---------|------|
| 1935 / 8890 / 8889 | MediaMTX RTMP / SRT / WHIP publish | LAN, auth |
| 8554 | MediaMTX RTSP read | 127.0.0.1, auth |
| 8767 | recon_ingest | 127.0.0.1 (LAN only with approval) |
| 8766 | LoRa bridge push | 127.0.0.1 |
| 3000 | phone-bridge app server | 127.0.0.1 + tunnel (approval) |
| 8080 / 11434 | orchestrator / Ollama (existing) | 127.0.0.1 |

## OFFLINE-FIRST + ONE CLOUD PATH (HgX rule via SAF, 2026-10-28)
**Everything is stored locally. Nothing touches the cloud except one opt-in compute path. The kit and the LoRa mesh keep running if the internet goes down.**

- **Offline-first:** ingest (MediaMTX), vision (Ollama, models pulled ahead of time), orchestrator :8080,
  storage (local ai-memory default/<USER> profile + USB), LoRa bridge, and watch all run with NO internet:
  no cloud DNS, no CDN assets, no telemetry. All endpoints are 127.0.0.1 or LAN IPs.
- **The ONE cloud path:** REA-initiated compute requests to **Cloud Jarvis** when heavy computation is needed.
  OFF by default. Minimum data only (text/metadata, never stored footage, never life-log). Every request is logged locally.
  Not implemented in code yet - it's a documented hook that needs HgX approval.
- **Removed from defaults:** FreeLLMAPI and any other cloud image path (no code path exists in recon_ingest.py).
- **Known exception, flagged honestly:** the MentraOS *app-server* route (phone-bridge/src/index.ts) needs
  Mentra's session cloud for **control** (video still goes glasses -> LAN directly). For a fully offline
  kit, use the **Mentra iOS Bluetooth SDK** route: the phone calls `startStream({streamUrl})` over Bluetooth
  to the laptop's LAN ingest with no cloud. Planned as phone-bridge v2 (Swift); the app-server version stays
  as the quick-start path.
- **Life-log:** laptop local ai-memory + USB only. Never cloud, never the box.

### Offline verification test (run after PKG-10)
1. Unplug the WAN cable from the router (or disable WAN in the router UI); keep home Wi-Fi/LAN up.
2. Confirm no internet: `Test-NetConnection 1.1.1.1 -Port 443` fails.
3. `GET http://127.0.0.1:8767/health` -> `ok:true`; `GET http://127.0.0.1:8080/` responds; `ollama list` shows moondream:1.8b.
4. Glasses (Bluetooth-SDK route) -> stream -> "look" -> reply spoken + watch EYES card.
5. Watch "recon" over LoRa -> `RC:` reply on the wrist; watch "status report" over LoRa -> qwen3 reply.
6. Check the logs: no DNS lookups or outbound connections (`Get-NetTCPConnection -State Established` shows only LAN/loopback).
7. Plug the WAN back in. Result PASS only if steps 3-6 all worked with WAN down.

## Target devices & remote access (HgX via SAF, 2026-10-28)
**Devices:** iPhone 16 Pro Max, M1 Pro iPad, Apple Watch Ultra 3 (cellular). The build targets iPhone + iPad
(universal iOS/iPadOS app), plus a watchOS companion.

**Tailscale support (checked 2026-10-28, Tailscale v1.104.x):**
| Device | Tailscale | Notes |
|--------|-----------|-------|
| iPhone 16 Pro Max | YES - App Store app, iOS 16.6+ (v1.104 dropped iOS 15) | primary relay |
| M1 Pro iPad | YES - same app, iPadOS 16.6+ | same build |
| Apple Watch Ultra 3 | **NO watchOS client** - Apple doesn't let third-party VPNs run on watchOS, and the phone's tunnel doesn't extend to the watch | relays **through the iPhone** (WatchConnectivity) |

So the watch companion talks to the iPhone app; the iPhone forwards over Tailscale/LAN. **No cloud relay,
no Tailscale Funnel, no public endpoint.** (watchOS also blocks third-party raw sockets/WebSockets; plain HTTP via the phone only.)

**Paths:**
- **Home:** LAN IP or Tailscale IP of the laptop. **Away:** cellular -> Tailscale only (HgX's tailnet).
- **No router port-forwards. No public ingest/API.** Firewall allows only Tailscale `100.64.0.0/10` + specific home device IPs.
- **Auth on every endpoint:** per-device bearer token (stored in iOS Keychain; laptop side `JV_INGEST_TOKENS` in `.env`)
  plus tailnet ACL (only HgX's devices -> laptop tag, ports 8767/1935/8890/8889). recon_ingest refuses a non-loopback
  bind with no tokens and returns 401 without a valid token. MediaMTX publish/read auth.
- **Encryption:** WireGuard via Tailscale on every off-LAN hop; RTMPS/SRT-encryption/WHIP-DTLS-SRTP where the protocol supports it.
- **Phone/iPad buffering:** in-flight only; each item is deleted after the laptop ACKs it (envelope `ack_of`). If the
  laptop is unreachable, queue locally (app sandbox, protected file storage) and sync later. Nothing goes to iCloud
  (exclude from backup); no cloud relay or storage.

## Hybrid modes (HgX, 2026-10-28) - fast and efficient first
| Mode | Brain | Laptop role | Cloud |
|---|---|---|---|
| 1 Laptop hub | laptop :8080 + Ollama (qwen3, moondream) | everything: LoRa, Flipper/ESP32, ingest, vision, storage | none - works with WAN unplugged |
| 2 Connected | Cloud Jarvis / Grok Bot for heavy reasoning | still owns RF limbs + local storage | snapshots/text, flag-gated |
| 3 Laptop off + cellular | Cloud Jarvis fallback | phone/watch queue, sync on return | snapshots/text, flag-gated |
Invariants: snapshots only (never full streams); life-log/captures laptop+USB only; no footage in OneDrive/Dropbox;
Mentra Bluetooth default, app-server opt-in; cloud compute behind `JV_CLOUD_JARVIS_ENABLED` (off until SAF clears). Docs/flags only, no cloud code yet.

## PASS 2026-10-28 ~15:50 ET - Cartographer code fixes + SAF/Armoury verdicts + HgX decisions
_Supersedes earlier hybrid/cloud lines above where they conflict. Code + docs only: nothing installed, run, flashed, or reconfigured._

### Code changed this pass (GO from SAF/Cartographer)
- **laptop-gateway/jarvis_lora_bridge.py**: `JV_LORA_KEY` REQUIRED (refuses start if missing/<16); HMAC + **monotonic counter replay window**
  (frame `JV1|id|t|seq|tot|payload|ctr|mac|crc`, counters persisted in `C:\JarvisData\lora\counters.json`); Bearer `JV_INGEST_TOKEN` on ingest call;
  radio text goes to **`JV_RECON_ROUTE` (default `/recon`, documented, NOT YET in orchestrator.py)** and is **refused if pointed at `/jarvis`**;
  reply chunks resent on missing ACK (4/8/16 s, NACK = immediate) and re-signed; chunk budget in **bytes**; COM port/mode from env;
  `/push` requires `X-JV-Push-Token` = `JV_PUSH_TOKEN` (refuses start without it); orchestrator timeout 40 s, ingest 45 s;
  401/403 -> `AUTH` (fail closed, no failover). **Meshtastic mode** disabled unless `JV_MESH_ALLOW_NODES` set; accepts only signed JV1 frames from allowlisted nodes, replies direct.
- **watch-firmware/src/main.cpp**: build **fails** without `JV_LORA_KEY` (`#error` + `static_assert` >=16); signing always on; NVS-persisted tx/rx counters, stale/replayed frames dropped. (Reflash = PKG-11, HgX.)
- **laptop-ingest/recon_ingest.py**: **30 s hard reply cap** (ok/queued/error); per-attempt timeout clipped to budget; queue max 5 items,
  **3 background tries** (10/30/60 s) or 10 min TTL, then **dead-letter JSONL** `C:\JarvisData\recon\deadletter.jsonl` (metadata only) + log + watch notice; push sends shared token; refuses start without `JV_PUSH_TOKEN`.
- **flipper_jarvis.py**: COM port from `JV_FLIPPER_COM`; catalog route from `JV_FLIPPER_CATALOG_ROUTE` (read-only route not yet built).
- **shared/schema.json + jv_envelope.py**: kinds `snapshot` (JPEG <=640 px, q<=70, <=150 KB, + `local_summary`) and `escalate` (question + local_summary); unknown kinds rejected.
- **phone-bridge/src/index.ts**: endpoint pick via `GET /health` only: `INGEST_API_LAN` -> `INGEST_API_TAILSCALE` -> local; cloud leg = disabled stub;
  only network errors fail over, 401/403 fail closed; short spoken errors (stream failed / auth failed / timed out / laptop unreachable); timeouts 45 s caller / 50 s voice.
- `.env.example` files: new keys (no values). PKG-1 rev2 (`mediamtx.yml`, `start-mediamtx.ps1`) already done - unchanged.
- Nested timeouts: **ingest 30 s < orchestrator 40 s < caller 45 s < voice 50 s**.

### HgX decisions (2026-10-28)
1. **Cloud Jarvis = compute only. NO cloud memory, NO cloud cataloguing. The laptop is the ONLY store** (+ USB backup).
2. **Laptop off:** opt-in snapshots to Cloud Jarvis, **deleted right away** after the answer. **FreeLLMAPI** also kept as an available **secondary** path (both documented, both OFF by default). SAF still gates the cellular path.
3. **MediaMTX stays as an OPTIONAL package (PKG-1, SAF rev2 rules).** Lean default (Armoury) = phone POSTs sampled snapshots.
4. Unchanged by HgX ruling: orchestrator `0.0.0.0:8080` no-auth and Ollama all-interfaces; existing python/ollama firewall rules. **No new Recon Kit listeners on the Public profile.**

### Armoury hybrid design (docs)
- Laptop owns fast + radio work (LoRa, Flipper, short watch replies, vision glance **<=2 s**) and always answers first.
- Cloud Jarvis does deep reasoning only on **escalation**, receiving a `snapshot` (1 JPEG <=640 px q70 + JSON local summary, text first) - never streams; nothing stored cloud-side.
- **One brain at a time:** 8080 when the laptop is up; Cloud Jarvis only when the laptop is down; same schema + ids.
- Orchestrator states: (1) laptop+net up: local first, async escalation pushed to watch; (2) net down: local only + outbox (SQLite/JSONL) flushed later;
  (3) laptop down: phone sees 3 missed `/health` beats @5 s -> cloud over cellular (**BLOCKED**), LoRa/Flipper show offline; msg ids dedupe; laptop reconciles on return.
- Targets: local glance <=2 s, LoRa round trip <=3 s, cloud escalation <=15 s async.
- **Simplifications PENDING HgX:** fold ingest into 8080 `/ingest/frame`; skip MediaMTX in v1 (optional PKG-1); one serial gateway with LoRa + Flipper adapters; one schema + one outbox; thin watch client.

### BLOCKED / TODO (gated)
- **Cellular laptop-down path: NOT IMPLEMENTED - BLOCKED** until HgX answers + SAF GO. Design: phone POSTs `snapshot` envelopes straight to Cloud Jarvis over HTTPS (or FreeLLMAPI secondary); no tunnel, no port-forward, no Funnel; snapshot deleted right away.

### WAITING ON HgX APPROVAL (not done)
- Orchestrator changes: **`/recon` no-tools route** (radio text currently gets "route missing"), **read-only Flipper `/catalog` route** (flipper_jarvis.py stores raw only until then).
- VRAM choice on the 2060: vision only on escalation vs small model with short keep_alive.
- Installs: mediamtx (PKG-1, optional), moondream (PKG-3), pyserial/meshtastic/pypubsub (PKG-5), PlatformIO; firewall (PKG-4); watch reflash with key (PKG-11);
  any network exposure/tunnel; Tailscale (PKG-7); Armoury simplifications above.

## LIVE VIDEO + SNAPSHOTS - both kept (HgX direct, 2026-10-28 ~15:55 ET)
- **Two modes, one obvious tap switch** in the iPhone/iPad UI: **Live** | **Snapshot**. Current mode always visible.
- **Live video** = MediaMTX (**PKG-1 stays**, SAF rev2 rules) - works on **Wi-Fi only (home LAN or Tailscale)**. Never over a cloud relay.
- **Snapshot** = lean path, **always available**: phone POSTs one `snapshot` envelope (JPEG <=640 px, q<=70, <=150 KB + local_summary).
  Used on **cellular, when the laptop is down, and for escalation**. Auto-falls back to Snapshot if Live can't reach the laptop.
- Cloud Jarvis receives snapshots only (opt-in, deleted right away); never live video.
- UI toggle is REQUIRED in PKG-14 (iOS app) and the phone-bridge; not implemented in code yet (app not built).
