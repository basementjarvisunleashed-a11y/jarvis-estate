# Roadmap — Watch Off-Grid Jarvis Link

Phased so each step is small, reversible, and gives a working result before the
next. Nothing here flashes the watch or changes laptop services without HgX
present and approving.

## Phase 0 — Proof of concept over Meshtastic  (fastest; do first)
**Outcome:** type a short command on the watch with no internet, get a qwen3
reply back on the watch.
- Hardware: the T-Watch-S3 (have) + **a 2nd SX1280 2.4 GHz Meshtastic node**
  (need) as the laptop gateway + USB data cable.
- Steps: put both radios on the same Meshtastic channel/region; plug the gateway
  into the laptop; run `jarvis_lora_bridge.py` with `MODE="MESHTASTIC"`; verify
  the orchestrator endpoint/field names in `ask_jarvis` (TODO) against real
  Jarvis; send a canned message from the watch; confirm the reply returns.
- No watch flashing. No laptop service changes.

## Phase 1 — Custom compact protocol  (bespoke wrist UI)
**Outcome:** our own Jarvis UI on the watch and our tiny `PROTOCOL.md` frames.
- Hardware: same two nodes.
- Steps: flash Option B firmware (`watch-firmware/`) to the watch **and** a
  matching sketch to the gateway (or keep the gateway on Meshtastic and move the
  watch only — but easiest is both on the custom protocol); wire the display/
  touch/DRV2605 libs (TODOs in `main.cpp`); switch the bridge to `MODE="CUSTOM"`;
  implement ACK/retry per `PROTOCOL.md`.
- Flashing done with HgX present (bad flash recovery: hold BOOT, tap RST).

## Phase 2 — On-watch voice capture
**Outcome:** speak a short command instead of tapping canned text.
- Uses the watch PDM mic. Off-grid stays **text**: either a tiny on-device
  keyword/wake match that maps to a canned command, or (only when in Wi-Fi range)
  send a short audio blob to Whisper on the laptop. Live audio never crosses
  LoRa.
- Steps: capture + VAD on the watch; keyword model or Wi-Fi fallback to Whisper;
  map result to a command frame.

## Phase 3 — Full two-way + Piper at the house + hardening
**Outcome:** robust daily-driver link.
- Piper TTS speaks replies aloud at the house; watch still shows + buzzes.
- Harden ACK/retry, dedup, presence/link-alive, power management on the watch,
  and tune SX1280 BW/SF/CR for the real range you need.
- Optional: compact binary protocol variant; GPS/geofence telemetry frames.

## Cross-cutting TODOs
- Verify the orchestrator's real HTTP contract (path + request/response fields)
  and update `ask_jarvis` in `jarvis_lora_bridge.py`.
- Choose Meshtastic addressing (dedicated channel or node id) so only Jarvis
  messages trigger qwen3.
- Tune `MAX_FRAME`, retry timers, and reply truncation against real airtime.
- Keep all channel keys / PSKs out of this repo.

## Phase 4 — Flipper Zero on HgX's own devices  (RF/IR/NFC)
**Outcome:** Jarvis catalogs and drives HgX's own RF/IR/NFC gear.
- Hardware: Flipper Zero (owned), USB-C data cable, optional microSD + blank
  NFC/T5577 spares.
- Steps: run `flipper-kit/flipper-jarvis/flipper_jarvis.py --list` to enumerate
  his own saved captures; `--pull` to catalog them via the orchestrator; wire IR
  scenes ("movie mode") and own-remote sub-GHz replay behind Jarvis commands.
- Strict scope: only HgX's own cards, tags, remotes, appliances, machines. Flag
  rolling-code remotes as non-replayable. No third-party targets.

## Phase 5 — ESP32 Wi-Fi recon tied to the network watchdog
**Outcome:** continuous own-airspace wireless inventory feeding Jarvis alerts.
- Hardware: ESP32 Wi-Fi dev board / Marauder companion (owned), optional 2.4 GHz
  antenna.
- Steps: build the sibling `esp32_marauder.py` helper (recon/monitor commands
  ONLY — no deauth/attack); parse AP/station lists on HIS OWN network; feed the
  inventory to the Jarvis network-watchdog; alert (watch buzz / status hub /
  voice) when a new or rogue device/AP appears. This is the "Jarvis RF &
  Wireless Security Scout" flagship — defensive, on his own property only.
