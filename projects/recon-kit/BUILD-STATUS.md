# BUILD STATUS - Jarvis Recon Kit (watch-offgrid)

_Updated 2026-10-28. Source of truth: `C:\Jarvis\projects\watch-offgrid` on the Jarvis laptop.
Scope: HgX's OWN devices and home network only - legal, defensive, read-only._

## Hardware - COMPLETE
T-Watch S3 (SX1280) OWNED | 2nd SX1280 gateway OWNED | Flipper Zero OWNED |
ESP32 Wi-Fi board OWNED | Mentra Live ORDERED | Jarvis laptop (RTX 2060) OWNED

## DONE (code + docs only - nothing installed, started, flashed, or reconfigured)
- **shared/** `schema.json` + `jv_envelope.py`: envelope v1 `{v,id,ts,src,kind,payload,ack_of?}`, stdlib validator, fail closed.
- **phone-bridge/** MentraOS app (`@mentra/sdk`): "look"/"recon"/button -> `session.stream.startStream({direct: INGEST_URL})`
  -> envelope POST to 127.0.0.1:8767/look -> reply spoken on glasses. No IPs/keys in code; refuses to start without `.env`.
- **laptop-ingest/** `mediamtx.yml` (auth on publish AND read, creds via env, no recording, RTSP read 127.0.0.1)
  + `recon_ingest.py` on **127.0.0.1:8767** (moved off 8765): 1 frame/>=2 s, <=1024 px, <1 MB, RAM only;
  **Ollama pinned `moondream:1.8b`**, 30 s timeout, 2/5/10 s backoff, then queue (no hard fail);
  **no cloud/FreeLLMAPI fallback** (SAF); vision text sanitized + treated as untrusted; JSON-line metadata logs; `/health`.
- **laptop-gateway/jarvis_lora_bridge.py**: orchestrator contract **verified** in `C:\Jarvis\orchestrator.py`
  (`POST /jarvis {"text"}` -> `{"ok","reply","actions"}`); `recon[:prompt]` -> ingest; `RC:` replies;
  **127.0.0.1:8766/push implemented**; HMAC-SHA256/8 frames when `JV_LORA_KEY` set (fail closed).
- **watch-firmware/src/main.cpp**: recon buttons, EYES card, PENDING-until-ack, 3 retries 4/8/16 s, loud failure,
  per-chunk ACKs, HMAC, base36 ids, Wi-Fi envelope path; secrets only via gitignored `secrets.ini`.
- **flipper_jarvis.py**: `ALLOW_TX = False` guard - TX/replay/emulate/BadUSB refused by default.
- Docs: **ARCHITECTURE.md** (Cartographer map), PROTOCOL.md Recon extension, INTEGRATION/AWAY-FROM-HOME/GLASSES-KIT
  **data residency rule** (life-log -> laptop LOCAL ai-memory default/<USER> profile; laptop+USB only; never cloud/box;
  captures outside synced trees), root `.env.example` + `.gitignore`.

## Open TODOs (verify on hardware)
- Mentra SDK is beta: confirm `session.stream.startStream` vs older `session.camera.startStream`.
- Watch display/touch library still TODO (UI prints to serial). Laptop LAN IP + subnet (<LAN_SUBNET> assumed in mediamtx.yml).
- VRAM: qwen3:8b ~5.2/6 GB - moondream needs a model swap (keep_alive 2m); test before relying on it.
- Proposed orchestrator change: a NON-agentic `/recon` log route (no tools) - needs approval; not written.

## NEEDS HgX APPROVAL + Security Audit Force review (package format; prepared, NOT run)

**PKG-1 INSTALLED 2026-10-28 (HgX approved, SAF rev2):** v1.21.3 from official GitHub release; SHA256 b2f5246b07cb72961df03b8d5e8cad43dc657bcf3f49a87bb031bdf22721af74 verified before unzip (matches release checksums.sha256); `C:\Jarvis\tools\mediamtx\mediamtx.exe` (ACL: <USER>/SYSTEM/Admins, inheritance off); `C:\JarvisData\mediamtx` created (same ACL). No service/task/autostart, firewall untouched. Launcher refuse-test passed. NOT RUN: awaiting .env (PKG-9) + PKG-4 firewall + HgX before first run. Use project `laptop-ingest\mediamtx.yml`, not the stock yml shipped in the zip.

**PKG-1 MediaMTX (ingest server) - rev2, SAF GO-WITH-CHANGES applied 2026-10-28 (re-review pending; HgX approval required)**
- Version PINNED: **MediaMTX v1.21.3** (latest stable, published 2026-10-25 UTC).
  URL: `https://github.com/bluenviron/mediamtx/releases/download/v1.21.3/mediamtx_v1.21.3_windows_amd64.zip`
  Expected SHA256 (GitHub release asset digest, read 2026-10-28): `b2f5246b07cb72961df03b8d5e8cad43dc657bcf3f49a87bb031bdf22721af74`
  Cross-check at install against `checksums.sha256` from the same release + `gh attestation verify --repo bluenviron/mediamtx`.
  `(Get-FileHash .\mediamtx_v1.21.3_windows_amd64.zip -Algorithm SHA256).Hash` MUST match BEFORE unzip; mismatch = abort. SAF verifies before GO.
- Where: `C:\Jarvis\tools\mediamtx\` (user-level, no admin, no service). ACL locked to <USER> + SYSTEM + Administrators
  (`icacls C:\Jarvis\tools\mediamtx /inheritance:r /grant:r <USER>:(OI)(CI)F SYSTEM:(OI)(CI)F Administrators:(OI)(CI)F`).
  `.env` owner-only (`icacls .env /inheritance:r /grant:r <USER>:F`).
- Config: `laptop-ingest\mediamtx.yml` rev2: `webrtcICEServers2: []` (no Google STUN), `webrtcLocalUDPAddress :8189` pinned,
  TCP ICE off; api/metrics/pprof/playback/hls/moq = no; RTSP 127.0.0.1:8554 TCP-only; RTMP OFF (plaintext) - if Mentra
  needs it: Tailscale-IP bind or `rtmpEncryption: strict` + local cert, SAF re-review; SRT ON with required publish
  passphrase; WHIP ON; `pathDefaults.record: no`; only path `glasses` accepted; publisher IPs = 100.64.0.0/10 + specific /32s (no /24).
- Launcher: `laptop-ingest\start-mediamtx.ps1` - refuses (exit 2) unless the 4 `MTX_AUTHINTERNALUSERS_*` vars +
  `MTX_PATHS_GLASSES_SRTPUBLISHPASSPHRASE` are set, not `CHANGE_VIA_ENV`, >=24 random chars; blocks insecure env overrides;
  checks yml invariants, exe present, log dir present and not synced. Tested on laptop 2026-10-28: refuses correctly.
- Logs: `logLevel: info`, file `C:\JarvisData\mediamtx\mediamtx.log` (NOT OneDrive/Dropbox). No credentials in URLs/logs.
- Run: manual foreground `start-mediamtx.ps1`; no autostart. Rollback: delete folder.- Remote/device notes for SAF: clients = iPhone 16 Pro Max + M1 Pro iPad (Tailscale iOS/iPadOS 16.6+);
  Apple Watch Ultra 3 has no Tailscale client -> relays via the iPhone. Away = cellular via HgX's tailnet only;
  home = LAN or Tailscale. NO port-forwards, NO public ingest. Allow-list = `100.64.0.0/10` + named home device IPs
  (update `ips:` in mediamtx.yml). Encrypted transport: WireGuard (Tailscale); RTMPS/SRT passphrase/WHIP DTLS-SRTP
  where supported. Auth: MediaMTX users + per-device tokens (Keychain) + tailnet ACL. Phone/iPad buffer in-flight
  only, deleted on laptop ACK, local queue when offline, no cloud relay/storage, no iCloud backup.

**PKG-2 ffmpeg** - portable build to `C:\Jarvis\tools\ffmpeg\`, SHA256 verified, user PATH only. Rollback: delete.
**PKG-3 Vision model** - `ollama pull moondream:1.8b` (~1.7 GB). Rollback: `ollama rm moondream:1.8b`.
**PKG-4 Firewall** (admin) - FIRST `netsh advfirewall export C:\JarvisData\fw-backup-<date>.wfw`. Confirm the ACTUAL profile
(`Get-NetConnectionProfile`): Hub review saw Wi-Fi on **Public**; re-check (or the wired NIC once on Ethernet) - do not assume Private.
Rules: `New-NetFirewallRule -Program C:\Jarvis\tools\mediamtx\mediamtx.exe` (absolute path) -Profile <confirmed>, inbound allow:
UDP 8890 (SRT), TCP 8889 (WHIP signalling), UDP 8189 (WebRTC media). RTMP 1935 only if PKG-1 re-enables it.
RemoteAddress = `100.64.0.0/10` + named home device IPs (/32) ONLY - NOT the whole /24. (8767 only with `JV_INGEST_TOKENS` set.) No router port-forwards.**PKG-5 Python venv** - `laptop-gateway\.venv`, `pip install --require-hashes -r requirements.txt` (pyserial;
+ meshtastic pypubsub for Phase 0). requirements file with hashes to be generated at approval time.
**PKG-6 Bun/Node** - Bun (or Node 22) user install; `bun install` in phone-bridge, then pin `@mentra/sdk` exact version + lockfile.
**PKG-7 Tailscale** - Tailscale on laptop (Windows) + iPhone + iPad; tailnet ACL: HgX devices -> laptop tag on
8767/1935/8890/8889 only; no Funnel. (The Mentra app-server quick-start needs Mentra's session cloud for control -
offline-first path is the iOS Bluetooth-SDK app, PKG-14.)
**PKG-14 iOS app = DEFAULT phone path (offline, Bluetooth)** - Xcode universal iPhone+iPad app (Mentra Bluetooth SDK `startStream({streamUrl})` -> laptop ingest),
watchOS companion via WatchConnectivity, tokens in Keychain, ACK-then-delete queue. Installed from Xcode to HgX's own devices.
**PKG-8 Mentra app registration - OPT-IN ONLY (cloud control exception; HgX decided via SAF t115u/t116u)** - off by default, `JV_MENTRA_APPSERVER_ENABLED=false`; enabling writes a local log entry; video still direct to laptop; `com.hgx.jarvis.recon` on console.mentra.glass, camera+mic; HgX pastes API key into `.env` himself.
**PKG-9 Secrets** - HgX creates `.env` (LoRa HMAC key, MediaMTX users) and `watch-firmware\secrets.ini`; never in chat or sync.
**PKG-10 First run** - manual foreground: MediaMTX, `recon_ingest.py`, `jarvis_lora_bridge.py`, `bun run start`.
**PKG-11 Flash watch** - `pio run -t upload`, HgX present.
**PKG-12 Data dirs** - create `C:\JarvisData\captures` + `C:\JarvisData\lifelog` (outside OneDrive/Dropbox) + USB mirror plan.
**PKG-13 Autostart** (only after PKG-10 works) - scheduled tasks for the services; no auto sign-in, no voice auto-start.

## Guardrails
Files only. No installs, services, firewall, tasks, or config changed. No secrets stored. No cloud image fallback.
Life-log/captures never synced. Flipper TX off by default.

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

## MIRRORS (HgX via SAF t115u/t116u)
OneDrive `Jarvis-Projects/watch-offgrid/` + Dropbox mirrors KEPT for **code + docs only**. Never: `.env`, `secrets.ini`, tokens,
keys, certs, footage, captures, life-log, logs (see `sync-exclude.txt`, `.gitignore`). **Before every sync run
`tools\sync-preflight.ps1`** - exit 0 required (secret scan + eligible file list); exit 3 = do not sync.

## HYBRID MODES (HgX via Cartographer 2026-10-28 15:44 ET) - favour FAST and EFFICIENT
| Mode | When | Brain | RF limbs / storage | Cloud traffic |
|---|---|---|---|---|
| 1 Laptop hub (local) | default, incl. no internet | laptop orchestrator :8080 + Ollama | laptop: LoRa, Flipper/ESP32, ingest, vision; storage local+USB | none |
| 2 Connected | internet up + SAF-cleared flag on | Cloud Jarvis / Grok Bot for HEAVY reasoning; laptop for fast/local | laptop still owns RF + storage | snapshots/text only |
| 3 Laptop off + cellular | laptop unreachable | Cloud Jarvis fallback brain (phone/watch via tailnet) | phone queues; syncs to laptop later | snapshots/text only, no stored footage |
Rules: cloud = SNAPSHOTS only, never full streams; nothing mirrored is footage; Mentra Bluetooth (PKG-14) default, app-server (PKG-8)
opt-in; life-log/captures laptop+USB only; any cloud compute path behind a config flag (`JV_CLOUD_JARVIS_ENABLED=false`) and OFF until SAF clears it.
Not implemented in code this pass (docs + flags only).

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
