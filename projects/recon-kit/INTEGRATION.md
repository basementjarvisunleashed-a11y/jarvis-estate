# INTEGRATION — The Jarvis Field Kit Trio (+ Brain, + Off-Grid Link)

How the pieces work as ONE coordinated system under Local Jarvis.
**Status: hardware-complete — all pieces owned/ordered.**

> Scope: strictly HgX's OWN devices and his OWN home network. Everything here is
> legal, defensive, and read-only recon of his own gear. No third parties.

## The roles (finalized)
| Piece | Role | What it does |
|-------|------|--------------|
| **Mentra Live glasses** | **EYES** | 12MP/1080p/119deg outward camera; streams over its OWN Wi-Fi via MentraOS startStream('direct') RTMP/SRT/WHIP to a LAN ingest URL -> Jarvis vision model. No HUD (camera+audio only). |
| **LilyGO T-Watch S3** | **COMMANDS + DISPLAY** | Wrist control surface, alerts, the display for glasses results, off-grid LoRa radio |
| **Flipper Zero** | **SENSE (RF hands)** | RFID/NFC, sub-GHz, IR, iButton, GPIO capture/replay (own cards/remotes) |
| **ESP32 Wi-Fi board** | **SENSE (Wi-Fi)** | Wi-Fi recon sensor on HgX's own network |
| **Local Jarvis (laptop)** | **BRAIN** | Decodes, reasons, routes — orchestrator :8080, Ollama :11434 (+ vision model), ComfyUI :8188 |
| **LoRa (SX1280 2.4 GHz)** | **NERVES (off-grid)** | Text link watch <-> laptop when there's no internet |

## The trio as a tag-team
Glasses, watch, and Flipper are not three gadgets — they're one loop:

```
         +----------------------------------------------------+
         |                  LOCAL JARVIS (brain)              |
         |  vision model / qwen3 / ComfyUI / orchestrator     |
         +------------------------^---------------------------+
                                  |
     (1) glasses SEE + STREAM     |   (4) result text back
         frames -> vision model   |       -> watch buzz + readout
                                  |
   EYES  --------->  BRAIN  --------->  SENSE  --------->  COMMAND/DISPLAY
  Mentra Live      decodes          Flipper/ESP32          T-Watch S3
  Wi-Fi stream   "that's an X,      (2) scan what Jarvis   (3) shows/buzzes
  to LAN ingest   try these RF"      told it to            the finding
```

### Walkthrough (one scenario)
1. **SEE:** HgX looks at one of his own devices; the Mentra Live streams the
   view over its own Wi-Fi to the laptop's LAN ingest URL; Jarvis's local vision
   model reads the frames.
2. **THINK:** Jarvis identifies it and decides what RF to look for.
3. **SENSE:** Jarvis tells the Flipper (sub-GHz/NFC/IR) and/or the ESP32
   (Wi-Fi) what to scan on HgX's own gear; captures feed back to Jarvis.
4. **DECODE + REPORT:** Jarvis interprets the capture and pushes a short result
   to the **watch**, which buzzes and shows it (the glasses have no screen) —
   optionally spoken back through the glasses' speakers.

The watch is both the **trigger** (tap to start a scan) and the **output**
(buzz + one-line readout) **and the display** for the screenless glasses. The
glasses keep HgX's hands free. The Flipper and ESP32 are the field antennas.
Jarvis is the only thing that "understands."

## Two operating modes
- **Home / Wi-Fi mode (fast):** full bandwidth. The Mentra Live streams 1080p
  over its own Wi-Fi to the laptop; voice and Flipper dumps flow over LAN; rich
  replies, even voice.
- **Off-grid / LoRa mode (resilient):** no internet, no cell. The watch talks
  to the laptop gateway over **SX1280 2.4 GHz LoRa**, carrying compact TEXT
  only (commands out, short results back). See PROTOCOL.md + MESHTASTIC-OPTION.md.

In off-grid mode the glasses stream only works in Wi-Fi range of the laptop;
when truly remote, the Flipper still captures locally and results are summarized
to fit the LoRa text budget and buzzed to the wrist.

## Data buses
- **Vision:** Mentra Live -> own Wi-Fi -> RTMP/SRT/WHIP LAN ingest -> Ollama vision model / Frigate -> orchestrator :8080
- **RF:** Flipper (USB-serial) + ESP32 (USB/Wi-Fi) -> flipper-kit helper -> orchestrator :8080
- **Command/alert:** orchestrator :8080 -> laptop-gateway LoRa bridge -> watch (LoRa or Wi-Fi)
- **Off-grid:** watch SX1280 <-> gateway SX1280 node (USB-serial) <-> jarvis_lora_bridge.py

## The third piece — RESOLVED
The third piece is **AI camera smart glasses**, and the chosen, ordered model is
the **Mentra Live** (open-source MentraOS, Apache-2.0). Full spec and the LAN
streaming architecture live in `glasses-kit/GLASSES-KIT.md`.

## Build order (see ROADMAP.md for detail)
1. Watch <-> laptop LoRa link (Meshtastic PoC first, then custom protocol).
2. Flipper + ESP32 recon helper wired to orchestrator.
3. Mentra Live LAN stream -> vision model -> orchestrator -> watch.
4. Full loop: glasses see -> Jarvis -> Flipper scan -> watch buzz.

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
