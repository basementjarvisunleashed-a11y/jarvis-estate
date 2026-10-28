# phone-bridge - Mentra Live -> Jarvis laptop (EYES -> BRAIN)

A MentraOS app (TypeScript, `@mentra/sdk`). On "look"/"recon" (voice) or a
short press of the glasses button it calls
`session.stream.startStream({ direct: INGEST_URL })` so the Mentra Live
publishes RTMP / SRT / WHIP **straight to the laptop's LAN ingest** (MediaMTX),
then POSTs `/look` to `laptop-ingest`, which grabs a frame, runs the local
vision model, and pushes the answer to the watch + orchestrator. The answer is
also spoken on the glasses' speakers. Long press or "stop recon" stops the
camera; it also auto-stops after `AUTO_STOP_SEC` idle.

Scope: HgX's own glasses / phone / laptop / LAN. No secrets in files (`.env` is gitignored).

## Caveats (verify on hardware)
- Mentra flags its app SDK as **beta**; method names may shift. Older SDKs used
  `session.camera.startStream({ rtmpUrl })`. Mentra recommends its **Bluetooth
  SDK** for Mentra Live - if the app-server route misbehaves, the same
  `startStream({ streamUrl })` call exists in the iOS Bluetooth SDK (Swift).
- The app server's *control* traffic goes through Mentra's session cloud; the
  **video** in direct mode goes glasses -> laptop only.
- Never use `localhost` in INGEST_URL - the glasses must reach the laptop's LAN IP.

## iPhone setup steps (HgX does these)
1. Install the **Mentra** app from the App Store, sign in, pair the Mentra Live.
2. In the Mentra app, join the glasses to the **home Wi-Fi** (same LAN as the laptop).
3. Settings -> Miniapp Developer Settings: enable developer mode.
4. On console.mentra.glass create an app with package `com.hgx.jarvis.recon`,
   grant **camera** + **microphone** permissions, copy the API key into `.env`
   on the machine running this server (never into chat or this repo).
5. Set the app's public server URL (the bridge must be reachable by Mentra's
   session cloud - e.g. a tunnel on the laptop; see BUILD-STATUS approval list).
6. In the Mentra app on the iPhone, open the app and start it.
7. Say "look" or short-press the glasses button. Watch buzzes with the result.

## Run (only after approval - see BUILD-STATUS.md)
```
cd C:\Jarvis\projects\watch-offgrid\phone-bridge
copy .env.example .env   # then fill in
bun install              # or npm install
bun run start
```

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

## LIVE VIDEO + SNAPSHOTS - both kept (HgX direct, 2026-10-28 ~15:55 ET)
- **Two modes, one obvious tap switch** in the iPhone/iPad UI: **Live** | **Snapshot**. Current mode always visible.
- **Live video** = MediaMTX (**PKG-1 stays**, SAF rev2 rules) - works on **Wi-Fi only (home LAN or Tailscale)**. Never over a cloud relay.
- **Snapshot** = lean path, **always available**: phone POSTs one `snapshot` envelope (JPEG <=640 px, q<=70, <=150 KB + local_summary).
  Used on **cellular, when the laptop is down, and for escalation**. Auto-falls back to Snapshot if Live can't reach the laptop.
- Cloud Jarvis receives snapshots only (opt-in, deleted right away); never live video.
- UI toggle is REQUIRED in PKG-14 (iOS app) and the phone-bridge; not implemented in code yet (app not built).
