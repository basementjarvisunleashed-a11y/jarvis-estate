# AWAY-FROM-HOME -- Mobile Modes for the Jarvis Field Kit

Scope: these modes operate strictly on HgX's OWN devices and network. All RF/recon activity is legal and defensive, limited to gear HgX owns or controls. No logins, credential attempts, or exploitation of third-party systems.

## The trio, away from home
- **Mentra Live glasses** = the eyes (outward camera + audio, open OS, live video stream).
- **LilyGO T-Watch-S3 Plus** = the wrist command surface, display, and alert/buzz node.
- **Flipper Zero + ESP32 Wi-Fi board** = the RF hands (sub-GHz, NFC, IR, Wi-Fi survey).
- **Jarvis laptop at home** = the brain (orchestrator :8080, qwen3:8b, vision model, local ai-memory, default/<USER> profile).

---

## 1. Remote vision (phone-bridged, over cellular)
When away, the phone acts as the bridge between the glasses and home.

- Glasses capture the point-of-view video stream.
- The stream relays over Bluetooth/Wi-Fi to the phone, then over cellular back to the Jarvis laptop at home.
- Jarvis's local vision model analyzes frames: identifies a device, reads a label, translates a sign, recognizes a tagged object.
- Answers come back to the glasses' speakers / HgX's ear and, when text is useful, to the watch display.

Result: HgX looks at a lock, router, board, or sign anywhere, and the home brain tells him what it is -- hands-free, regardless of distance from home.

---

## 2. Off-grid lifeline (watch <-> laptop over LoRa)
When there is no cell signal at all, the watch keeps a thread to Jarvis.

- Link: SX1280 2.4 GHz LoRa between the watch field node and the laptop gateway node.
- Payload: compact TEXT only (not live voice/video) -- status, short questions, alerts.
- Flow: wrist tap -> LoRa -> gateway node (USB-serial to laptop) -> Python bridge -> orchestrator :8080 -> qwen3 -> reply back over LoRa -> watch buzzes with the answer.

Result: HgX always has a lifeline to Jarvis, on or off the grid, out in dead zones.

---

## 3. Mobile RF recon (HgX's OWN gear only)
Every outing becomes a field survey of HgX's own equipment.

- Flipper Zero: survey the RF around him, scan HIS OWN tags, remotes, iButtons, IR.
- ESP32 board: map Wi-Fi presence on HIS OWN network / devices.
- The watch GPS-tags each capture with location and timestamp.
- Captures are logged and, when back in range, synced to the laptop so HgX comes home with a map of where he was and what he saw.

Strictly limited to HgX's own devices, cards, remotes, and network. No access attempts against anyone else's gear. Legal and defensive only.

---

## 4. Private life-log (into local ai-memory)
The day is recorded privately, nothing in any third-party cloud.

- Glasses capture scenes through the day.
- Frames/scenes are embedded into HgX's own LOCAL ai-memory on the laptop (default/<USER> profile) - never the box :49374 server, never cloud.
- Everything is timestamped and queryable later: "Jarvis, what did I look at at 2 PM?"
- All storage stays on HgX's own laptop -- no external cloud, fully owned end to end.

---

## Summary
Away from home, HgX has: remote vision through the phone bridge, an off-grid text lifeline through the watch + LoRa, mobile RF recon on his own gear through the Flipper and ESP32, and a private life-log into local ai-memory -- all tied back to one Jarvis brain at home.

## Data residency rule - life-log & captures (HgX, 2026-10-28)
1. **Life-log / Recon Kit memory target = the laptop's LOCAL ai-memory (default / <USER> profile).**
   Not the box server on :49374.
2. **Life-log data and its backups live on the laptop + USB only.** Never copy life-log
   entries, camera captures/frames, or memory dumps to Dropbox, OneDrive, the box, or any cloud.
3. **Project code and docs** (this folder) may sync to OneDrive `Jarvis-Projects/watch-offgrid/`
   and Dropbox `/Jarvis-Projects/watch-offgrid/` (Dropbox create-only, no deletes). That is
   separate from the life-log.
4. **Footage/captures folders sit outside every cloud-synced tree** (never under
   `C:\Users\<USER>\OneDrive`, any Dropbox folder, or this project folder). Proposed:
   `C:\JarvisData\captures\` and `C:\JarvisData\lifelog\` (+ USB mirror). `recon_ingest.py`
   keeps frames in memory only by default; any future capture save must target that path.
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
