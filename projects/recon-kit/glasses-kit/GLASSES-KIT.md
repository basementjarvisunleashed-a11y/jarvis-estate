# Glasses Kit — Jarvis Eyes (First-Person Camera)

**Role in the trio:** The AI camera smart glasses are the **EYES**. They give
HgX a hands-free, first-person camera that streams straight into **Local
Jarvis's vision model** so Jarvis can see what HgX is looking at and reason
about it in real time.

> Scope: strictly HgX's OWN devices and network. Legal, defensive, read-only
> recon of his own gear. No capture of other people or networks.

## Chosen model: MENTRA LIVE  (ordered)
The eyes piece is the **Mentra Live** — open-source AI camera glasses.

- **Price:** ~$449 USD.
- **Platform:** **MentraOS / AugmentOS**, open source under **Apache-2.0**.
  No app-store gatekeeping — we write our own app against the SDK and own the
  whole pipeline end to end.
- **Camera:** **12 MP**, **1080p video**, **119 deg field of view** outward camera.
- **Display:** **NO HUD / no lens display** — this is a **camera + audio** pair
  by design (lighter, longer battery). The wrist **T-Watch S3** is the display
  and alert surface for the kit.
- **Audio:** **stereo speakers** + **3 microphones** (voice capture / open-ear readback).
- **Radios:** has its **OWN Wi-Fi + Bluetooth** (not Bluetooth-only like the
  Halo) — this is what lets it push a real video stream onto the LAN.
- **Weight:** **43 g** glasses; **260 mAh** in the glasses + **2200 mAh** charge case.

### Why this one — the key unlock
The MentraOS SDK exposes **startStream()** with a **'direct' mode** that
publishes the camera feed as **RTMP / SRT / WHIP (WebRTC)** straight to an
**ingest URL on HgX's OWN LAN** — **no Mentra cloud in the middle**. That
LAN ingest stream is the feed into **local Jarvis's vision model**
(Ollama + moondream / llava) and/or a **Frigate** NVR/vision server on the
laptop. This is exactly the ownable, private, no-cloud pipeline the project needs.

## Architecture (glasses -> Jarvis brain -> watch)
```
  Mentra Live glasses (12MP / 1080p / 119deg)
        | own Wi-Fi
        | MentraOS SDK startStream('direct') -> RTMP / SRT / WHIP
        v
  LAN ingest URL on the LAPTOP   (e.g. rtmp://<laptop-lan-ip>:1935/glasses  or WHIP)
        |
        +--> Local Jarvis vision model (Ollama + moondream / llava)   describe / detect / OCR
        +--> (optional) Frigate server                                motion / object events
        |
        v  result text
  Orchestrator :8080
        |
        +--> pushed to the T-WATCH S3   (display + buzz — the glasses have no screen)
        +--> (optional) spoken back via the glasses' own stereo speakers
```

Because the glasses have no display, **all visual results land on the watch**
(and/or are spoken through the glasses' speakers). Glasses **see + stream**,
watch **shows + buzzes**, Jarvis **thinks**.

## Local vision endpoints already on the laptop
- **Ollama** — http://127.0.0.1:11434 (add a vision model: moondream / llava)
- **ComfyUI** — http://127.0.0.1:8188 (heavier image workflows / vision graph)
- **Orchestrator** — http://127.0.0.1:8080 (routes results to watch / LoRa)
- **Frigate** — (optional, to stand up) RTMP/SRT ingest + object detection

## Use cases (eyes role)
- **Look-and-know:** HgX looks at one of his own routers/locks/devices; Jarvis
  IDs it from the stream and buzzes the watch with the model + known RF angles
  to try with the Flipper.
- **Hands-free OCR:** read a label/serial/QR in view; Jarvis logs it.
- **Live security eye:** motion or a tagged object in the stream triggers a
  capture + log (Frigate or the vision model).
- **Private memory of the day:** scenes embedded into the laptop's LOCAL ai-memory (default/<USER> profile; laptop+USB only, never cloud)
  service — nothing leaves the house.
- **Trigger chain:** glasses see a target -> Jarvis tells the Flipper what to
  scan -> result buzzes to the watch. (See INTEGRATION.md.)

## Build steps
- [ ] Stand up a LAN ingest endpoint on the laptop (RTMP via MediaMTX/Frigate, or a WHIP/WebRTC sink).
- [ ] Write a minimal MentraOS app that calls startStream('direct', <laptop ingest URL>).
- [ ] Pull frames off the stream -> Ollama vision model (moondream/llava).
- [ ] Route result text to orchestrator :8080 -> watch buzz/readout.
- [ ] Optional: Frigate for motion/object events; glasses-speaker TTS readback.

## Links
- Product: https://mentraglass.com/live
- Streaming docs: https://docs.mentraglass.com/app-devs/core-concepts/stream
- Source: https://github.com/Mentra-Community/MentraOS

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
