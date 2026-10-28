# Jarvis Recon Kit - Offline-First

> **Mentra control:** DEFAULT = iOS Bluetooth SDK app (PKG-14, fully offline). The MentraOS app-server (PKG-8) is the ONE
> control exception: OPT-IN, off by default (`JV_MENTRA_APPSERVER_ENABLED=false`), API key in `.env` only, a local log entry
> is written when enabled, and video still goes DIRECT to the laptop. **Hybrid modes:** see BUILD-STATUS.md / ARCHITECTURE.md.
> Cloud = snapshots only, never streams. Mirrors = code+docs only; run `tools\sync-preflight.ps1` before every sync.

> **Everything is stored locally. Nothing touches the cloud except one opt-in compute path (REA -> Cloud Jarvis, off by default, never footage). The kit and the LoRa mesh keep running if the internet goes down.** See ARCHITECTURE.md.

## Watch Off-Grid Jarvis Link

**Goal:** Let HgX talk to Local Jarvis (the laptop "brain") and the home Jarvis
with **no internet and no cell service**, using a LILYGO T-Watch-S3 as a wrist
node talking over **LoRa (SX1280, 2.4 GHz)** to a gateway node plugged into the
laptop.

This repo is a **scaffolding + design build**: code, config, and docs only.
Nothing here flashes the watch or changes the laptop's running services.

---

## The honest tradeoff up front

LoRa is a **low-bandwidth, long-range text radio**. On the SX1280 2.4 GHz build
you get, very roughly, a few hundred bytes to a couple kilobytes per second of
usable throughput depending on spreading factor and range, and per-message
latency of a fraction of a second to a few seconds. That is **nowhere near
enough for live voice**. So the off-grid path is **compact text only**:

- You speak a short command on the watch (optional on-device keyword/record),
  or tap a canned phrase, or type a short line.
- The watch sends a small (<200 byte) text frame over LoRa.
- The laptop runs qwen3 fully offline and sends a short text reply back.
- The watch shows the reply and buzzes.

When you are **home on Wi-Fi**, the watch switches to the fast HTTP path and you
get full/fast voice through the orchestrator. Off-grid, it degrades gracefully
to text.

---

## Architecture

```
  +-------------------+        LoRa SX1280 2.4GHz        +--------------------+
  |   T-Watch-S3      |  <---------------------------->  |  Gateway LoRa node |
  |  (field node)     |     compact framed text          |  (2nd SX1280 board)|
  |                   |     (<200 B payloads)            |                    |
  | - touch UI        |                                  | - USB serial to PC |
  | - canned cmds     |                                  +---------+----------+
  | - mic (optional)  |                                            | USB serial
  | - vibration motor |                                            v
  | - shows replies   |                               +------------------------+
  +-------------------+                               | jarvis_lora_bridge.py  |
                                                      | (Python on laptop)     |
          WIFI MODE (when home):                      | - reads framed msgs    |
   Watch --HTTP--> orchestrator:8080 directly         | - calls orchestrator   |
   (full/fast voice path)                             +-----------+------------+
                                                                  | HTTP 127.0.0.1:8080
                                                                  v
                                                      +------------------------+
                                                      | Jarvis orchestrator    |
                                                      |  -> Ollama qwen3:8b     |
                                                      |  -> reply text          |
                                                      |  (-> optional Piper TTS |
                                                      |     spoken at the house)|
                                                      +------------------------+
```

Reply text flows back the reverse way: orchestrator -> bridge -> gateway node
-> LoRa -> watch screen + vibration.

---

## Two firmware options for the watch

### Option A — STOCK Meshtastic (recommended first; fastest to a demo)
The watch already ships with Meshtastic (SX1280 2.4 G build). Meshtastic already
solves framing, addressing, retries, and encryption, and it exposes a **Python
serial API** on the laptop side. You reuse the stock firmware and just write the
laptop bridge. See `MESHTASTIC-OPTION.md`. This is the Phase 0 proof-of-concept.

- **Pros:** almost no firmware work; reuses encryption, ACKs, mesh routing; a
  second Meshtastic node as the gateway "just works"; proven range.
- **Cons:** you ride Meshtastic's UI/text model on the watch (canned text, phone
  app, or keyboard) rather than a custom Jarvis UI; message format is theirs.

### Option B — CUSTOM Arduino/ESP-IDF firmware (full control; more work)
Flash our own sketch using RadioLib for the SX1280 and the TTGO T-Watch library
for display/touch/haptics. Full control of the UI and our own compact protocol
(see `PROTOCOL.md`). See `watch-firmware/`.

- **Pros:** bespoke Jarvis UI, our own tiny protocol, tighter payloads, direct
  control of mic/motor/accelerometer.
- **Cons:** we own framing, retries, power management, and debugging; much more
  effort; flashing risk (do only with HgX present).

**Recommendation:** Do Option A to prove the end-to-end loop, then migrate to
Option B for the polished wrist experience.

---

## Bill of materials — HARDWARE COMPLETE (all owned)

| Item | Why | Notes |
|------|-----|-------|
| **2nd SX1280 2.4 GHz LoRa node** (laptop-side gateway) | **OWNED (just purchased)**. Plugs into the laptop over USB and bridges LoRa <-> Python. | A **LILYGO T3-S3 (SX1280 2.4 G revision)** is the clean match. A second T-Watch-S3 (SX1280) also works. **Both radios must be the same band — SX1280 2.4 GHz — to talk to each other.** |
| USB-C data cable for the gateway node | USB serial to the laptop | Must be a data cable, not charge-only |
| (Optional) external 2.4 GHz antenna / U.FL pigtail | Better range | Match the board's connector |
| (Optional) small LiPo for the gateway node | Portability | T3-S3 has a JST battery port |
| (Have already) T-Watch-S3 (SX1280), USB-C cable | Field node | — |

No paid/cracked software. All toolchains below are free and open source.

---

## Build phases (summary; full detail in ROADMAP.md)

- **Phase 0 — Proof of concept over Meshtastic.** Stock firmware on both nodes,
  `jarvis_lora_bridge.py` in Meshtastic mode, prove: watch text -> qwen3 ->
  reply on watch. No flashing of the watch.
- **Phase 1 — Custom compact protocol.** Flash Option B firmware, implement
  `PROTOCOL.md` on both ends, bespoke wrist UI with canned commands.
- **Phase 2 — On-watch voice capture.** Record short speech on the watch; either
  tiny on-device keyword spotting or send a short Whisper-transcribable blob when
  in Wi-Fi range; off-grid stays canned/typed text.
- **Phase 3 — Full two-way + Piper at the house + ACK/retry hardening.**

---

## Laptop bridge setup (do NOT run during this scaffolding build)

```
cd C:\Jarvis\projects\watch-offgrid\laptop-gateway
python -m venv .venv
.venv\Scripts\activate
pip install pyserial            # for Option B custom-protocol serial
pip install meshtastic pypubsub # for Option A Meshtastic mode
# then: python jarvis_lora_bridge.py
```

We intentionally do **not** install anything system-wide or run the bridge in
this build. These steps are for HgX to run later, with his approval.

---

## Range & limitations (be realistic)

- SX1280 is **2.4 GHz** — more bandwidth than sub-GHz LoRa but **shorter range**
  and worse wall penetration than 433/915 MHz LoRa. Expect solid whole-house and
  near-property coverage; long open-air links need line of sight and antennas.
- Text only off-grid. No live audio over LoRa. Keep payloads < ~200 bytes.
- Replies from qwen3 must be **short** — the bridge truncates/chunks them.
- Duty cycle / airtime: large or frequent messages hog the channel; keep it terse.

---

## Safety notes

- This build writes files only. It does **not** flash the watch, does **not**
  change the laptop's running services, and uses **no secrets**.
- Flashing firmware (Option B) should be done with HgX present, since a bad flash
  can brick or require recovery (hold BOOT, tap RST to force download mode).
- The laptop bridge, when HgX chooses to run it, binds only to 127.0.0.1 for the
  orchestrator call. Review before running.
- Keep any Meshtastic channel keys out of this repo.


---

# Jarvis Field Kit — broader project

This folder is now the **Jarvis Field Kit**, HgX's legacy R&D project for his son
to inherit. The off-grid watch link above is the first module. A second module
lives in `flipper-kit/`.

## Module: Flipper Kit (`flipper-kit/`)
HgX's **Flipper Zero** + **ESP32 Wi-Fi dev board** (Marauder companion) wired into
Jarvis — RFID/NFC catalog & emulate of his OWN cards, sub-GHz capture/replay of
his OWN garage/gate/remotes, IR universal remote Jarvis drives, BadUSB macros on
his OWN machines, GPIO chip RE, and ESP32 Wi-Fi recon feeding the Jarvis
**network-watchdog**. Flagship build: a **Jarvis RF & Wireless Security Scout**
that inventories his own RF/wireless environment and flags anything new or rogue.
See `flipper-kit/FLIPPER-KIT.md`. **Strictly scoped to HgX's own devices and
network — defensive, legal, no third-party targets.**

- Helper: `flipper-kit/flipper-jarvis/flipper_jarvis.py` (USB serial CLI to the
  Flipper; pulls SD captures; hands them to the orchestrator to catalog).
- Setup (later, with approval — not run in this build):
  `python -m venv .venv && .venv\Scripts\activate && pip install pyserial`

## Combined bill of materials

**Watch off-grid link (ALL OWNED):** T-Watch-S3 (SX1280), 2nd SX1280 2.4 GHz LoRa gateway node (just purchased), USB-C data cables; optional antenna/LiPo.

**Flipper Kit:** Flipper Zero (OWNED), ESP32 Wi-Fi dev board (OWNED), USB-C data
cables; optional: Flipper microSD, 2.4 GHz Wi-Fi antenna for the ESP32 board,
blank NFC cards / T5577 fobs to clone HIS OWN tags, GPIO jumper leads.

## Glasses (EYES) — OWNED / ORDERED
**Mentra Live** open-source AI camera glasses (~$449, MentraOS/AugmentOS,
Apache-2.0) — ordered. 12MP/1080p/119deg camera, own Wi-Fi+Bluetooth, no HUD
(camera+audio only). Streams to a LAN ingest URL for the local vision model.
See `glasses-kit/GLASSES-KIT.md`.

## HARDWARE-COMPLETE BOM (summary)
| Item | Role | Status |
|------|------|--------|
| LilyGO T-Watch S3 (SX1280) | Wrist command + display | OWNED |
| 2nd SX1280 2.4 GHz LoRa gateway node | Laptop off-grid gateway | OWNED (just purchased) |
| Flipper Zero | RF/NFC/IR/sub-GHz hands | OWNED |
| ESP32 Wi-Fi dev board | Wi-Fi recon sensor | OWNED |
| Mentra Live glasses | Eyes (camera + stream) | ORDERED |
| Jarvis laptop (RTX 2060) | Brain | OWNED |

**All hardware for the kit is now owned or ordered — the kit is hardware-complete.**
Remaining work is software/firmware (see BUILD-STATUS.md).


## LIVE VIDEO + SNAPSHOTS - both kept (HgX direct, 2026-10-28 ~15:55 ET)
- **Two modes, one obvious tap switch** in the iPhone/iPad UI: **Live** | **Snapshot**. Current mode always visible.
- **Live video** = MediaMTX (**PKG-1 stays**, SAF rev2 rules) - works on **Wi-Fi only (home LAN or Tailscale)**. Never over a cloud relay.
- **Snapshot** = lean path, **always available**: phone POSTs one `snapshot` envelope (JPEG <=640 px, q<=70, <=150 KB + local_summary).
  Used on **cellular, when the laptop is down, and for escalation**. Auto-falls back to Snapshot if Live can't reach the laptop.
- Cloud Jarvis receives snapshots only (opt-in, deleted right away); never live video.
- UI toggle is REQUIRED in PKG-14 (iOS app) and the phone-bridge; not implemented in code yet (app not built).
