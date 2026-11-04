# J.A.R.V.I.S. — OPERATOR PRIME Course Material
**J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System)** — public identity, first and prominent.
Operator: HgX (small). Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

> **HGX Academy** — OPERATOR PRIME is taught by HGX Academy, HgX's own academy. No university affiliation. No external accreditation claimed.

> **STATUS: SUPERSEDED v0.9.0 — Superseded by COURSE-STRUCTURE-v2 v1.0.0. Retained for version history only; do not use as current structure.**

> **Audience and hard rules:** Consenting adults only. Controlled laboratory only. Own devices, own tags, own networks, own targets only. Spine: SEE → DOCUMENT → LOG → PREVENT. Face work only on consenting adult participants, in the lab only, for defensive education. Templates stay in the lab, deleted after the exercise. Never family, never his son, never strangers, never real-world surveillance or deployment. Radio transmit only on own authorised frequencies. Drone only in a safe, controlled flying area, Transport Canada rules first. Lasers Class 1 only.

> **Licence:** Course text CC-BY-4.0. Code MIT. © HGX Engineering. No secrets in public. No personal data: no real names, no Wi-Fi names, no home addresses, no serials, no passwords, no credentials, no live location, no family details, no financial details. No 2.0/3.0 material. No prompt text reproduced.

---

# Jarvis Operator Course — Structure v1 (STARTED 2026-10-29)

**Status:** Structure v1, slotted in on HgX's word 2026-10-29 15:40 ET. Not a finished syllabus. Modules, labs, and evidence packs grow on his word.
**Instructor:** HgX, alumni, PhD in mechanical and materials engineering, field: non-destructive testing (NDT).
**Cohort:** Toronto students, all from Toronto. Consenting adults, almost in their thirties, very mature, very high graded, doctoral-capable. NDT engineers going further than NDT. Summer course, summer 2027, optional. Participants eager volunteers, explicit legal consent on record.
**Cohort devices (2026-10-29):** ALL students have M1 iPad Pro with LiDAR (Apple LiDAR scanner, up to 5 m, ARKit + RoomPlan). iPad LiDAR is Apple closed hardware — open part is export + open processing (CloudCompare, Open3D, MeshLab, PCL, QGIS) + separate open LiDAR hardware on Acer (RPLIDAR family, see below). Scanning labs can run on student iPads at zero extra hardware cost.
**Purpose:** Show the capability of AI today with Kali + REA + the 10 stacks. Students see vulnerabilities in the lab, document them, log them, and only then build prevention for the real world — for work at defense companies, preventing in the real world what was first seen in the lab.
**Positioning:** Newer and more pinnacle than anything happening in nearby universities. The leading course in this.

## The spine (every module, no exceptions)
1. **See** — the vulnerability, signal, or flaw, in the lab.
2. **Document** — what it is, what was proven, with evidence.
3. **Log** — evidence saved, auditable, clean chain.
4. **Prevent** — only then, the defense, the fix, the rule.

## Hard rules
- **Controlled lab only.** Everything — attacks, face ID, radio, mesh, card tests — controlled lab only. Own devices, own tags, own networks, consenting participants, logging at every step. Nothing deployed or tested on real people, strangers, or real-world systems outside the lab.
- **Open source hardware is key.** Open can be seen, audited, documented, and logged. Closed hides flaws, so the See → Document → Log → Prevent chain cannot be honestly completed.
- **Face ID: consent-gated lab only.** Only on consenting adult course participants, in the controlled lab, for defensive education (enroll/match, lighting/angle, spoofing, liveness, multi-factor, consent, audit). Templates stay in the lab, deleted after the exercise. Never family, never his son, never strangers, never real-world surveillance or deployment.
- **Voice-first, professional.** Clear, precise delivery. Professional tone throughout; rigour is not replaced by informality.
- **Full Jarvis treatment for every piece.** Every hardware piece gets Kali everything + the 10 software stacks + the pillars talking to it. No orphan hardware.

## The build underneath
- **Pillars (3):** Kali everything (Acer, install-once) + REA everything + Grokbot (Cloud Jarvis takeover, inside the Acer, with guardrails).
- **The 10 software stacks (LOCAL-ONLY):** 1 REA, 2 security-audit-skill, 3 Graphify (local CLI), 4 HyperFrames, 5 ComfyUI, 6 FreeLLMAPI (router → local Ollama by default), 7 ai-memory, 8 claude-plugins-official (needs Claude Code), 9 VoiceStudio, 10 GenOffice. Local by design; cloud providers off by default; local Ollama as inference backend.
- **Jarvis-feel layer:** XFCE dark arc-blue HUD (original-inspired only, no Marvel assets), VoiceStudio primary voice, PipeWire voice layer (Maono → wake → speaker gate → Whisper → Ollama → orchestrator), voice-first, speak only when changed or needed.
- **Project 25:** Prove-out runs FIRST after the Acer build, before other projects. 21 family checkpoints (15 core + 6 specialty), evidence pack, GenOffice final report, VoiceStudio narrated summary, ai-memory log.

## Hardware — all 11, slotted in
**At home (first three):**
- H1 Flipper Zero + Complete Starter Kit (ESP32-S2 Wi-Fi board) — RFID, NFC, IR, Sub-GHz, Wi-Fi/Bluetooth via kit board.
- H2 Mentra Live Camera Glasses — vision + audio, screenless, camera, mics, speakers, Wi-Fi/Bluetooth.
- H3 LILYGO T-Watch-S3 Plus, SX1280 2.4G Meshtastic — wrist mesh node, touch, haptic, speaker, mic, GNSS.

**Secretary sent to buy 2026-10-29 (UPDATED 15:56 ET: ordered AND already here, via secretary — arrival confirmed, unpack/test pending):**
- H4 HackRF One — SDR, 1 MHz–6 GHz, TX/RX.
- H5 Proxmark3 RDV4 — deep RFID/NFC lab specialist.
- H6 Ubertooth One — Bluetooth / BLE sniffing.
- H7 ChipWhisperer-Lite — side-channel power analysis + glitching, fully open.
- H8 KrakenSDR — 5-channel coherent SDR, direction finding (software open).
- H9 LILYGO T-Beam Meshtastic node — mesh expansion, GPS/LoRa.
- H10 OpenMV Cam — edge vision, MicroPython, on-device inference.
- H11 GreatFET One — USB / hardware-hacking bridge.

**Mesh honesty:** The watch LoRa mesh is a real mesh. Flipper + glasses do not share that LoRa radio natively. Course/system mesh = laptop-orchestrated: watch LoRa mesh ↔ Acer gateway/orchestrator ↔ Flipper Wi-Fi/Bluetooth + glasses Wi-Fi/Bluetooth, verdicts and evidence bridged and logged. Never claim a single native radio mesh for all three.

## Modules (slotted)
- **M0 — Lab rules, consent, audit.** Controlled lab, consent, logging, See → Document → Log → Prevent. Safety, legal scope, evidence discipline. No hardware required.
- **M1 — Kali everything + Project 25 prove-out.** Full suite, 21 family checkpoints, safe self-tests, evidence pack. Hardware: Acer (brain) + all, as they arrive.
- **M2 — Spectrum: see the air.** HackRF One + KrakenSDR. Spectrum, GNU Radio, direction finding, signal documentation. Kali: SDR, Wireless, Sniffing. REA: signal/firmware context. Prevention: spectrum hygiene, detection, lawful use.
- **M3 — Cards and access: see the tag.** Flipper Zero + Proxmark3 RDV4. RFID/NFC/IR/Sub-GHz, field vs lab depth, key recovery on own tags, emulation on own tags. Prevention: card security, migration off weak schemes.
- **M4 — Bluetooth: see the pairing.** Ubertooth One + Flipper BLE. BLE/Classic capture, pairing analysis, Wireshark. Prevention: modern pairing, firmware updates, discoverability off.
- **M5 — Chips: NDT for silicon.** ChipWhisperer-Lite. Power traces, side-channel analysis, glitching on own target boards. This is NDT going further than NDT — non-destructive testing of a chip's secrets. Prevention: masking, shielding, secure implementation.
- **M6 — Mesh off-grid: see the network.** T-Watch + T-Beam + Acer gateway. Meshtastic mesh, off-grid text/telemetry, encryption, multi-node routing. Prevention: resilient comms, mesh security, gateway hardening.
- **M7 — Vision: see, don't identify strangers.** Mentra glasses + OpenMV Cam. Presence, tracking, AprilTag/QR, edge inference, lab-only. Face ID consent lab (separate, gated, see Hard rules). Prevention: vision abuse cases, liveness, multi-factor, audit.
- **M8 — Bridge: talk to the board.** GreatFET One + REA. USB, UART/SPI/I2C/JTAG, firmware analysis, protocol work. Prevention: interface hardening, firmware provenance.
- **M9 — Brain and voice: Jarvis-feel.** VoiceStudio + GenOffice + Ollama + orchestrator + PipeWire voice layer. Lecture studio, reports, voice control, local reasoning. Prevention: local-first reasoning, audit logs, no silent cloud leakage.
- **M10 — Capstone: all eleven talking.** Full mesh system through the Acer, Project 25 evidence pack, defense brief. Students present a vulnerability chain (See → Document → Log) and a prevention design, as they would to a defense company. GenOffice report + VoiceStudio narration + ai-memory / Graphify local research library.

## Assessment
- Evidence pack per module (logs, captures, photos, outputs — own lab only).
- GenOffice final report + VoiceStudio narrated summary per capstone.
- Defense brief: what was seen, what was logged, what prevention follows. No prevention claim without the evidence chain.

## Status log
- 2026-10-29: Structure v1 started, all 11 slotted. First three at home. Eight via secretary (sent to buy, arrival pending). Published 2026-11-04 on HgX's explicit publication order for 1.0 course material.
- 2026-10-29 15:56 ET: All eight ordered AND already here (via secretary). All 11 in hand. Arrival only — unpack/test/inventory pending. Home start is ONE BY ONE, see HOME-START-ONE-BY-ONE.md. Published 2026-11-04 on HgX's explicit publication order for 1.0 course material.
- 2026-10-29 16:09 ET: ALL 7 NEW LOCKED — course load now 18 ITEMS TOTAL (11 in hand + 7 new locked, pending order/arrival). New items H12–H18 below, modules M11–M13 added. RPLIDAR tier (A1/A2/C1) still open — A1 is teaching default.

## Hardware — 7 new, locked 2026-10-29 16:09 ET (pending order/arrival)
- H12 PX4/ArduPilot drone kit — Pixhawk autopilot, QGroundControl/Mission Planner, airframe + motors + GPS + battery. Safety/legal gate: safe flying area + Transport Canada rules, controlled area only, never over people/strangers.
- H13 Frigate motion system — Open source NVR, Docker on Acer, local AI object detection, RTSP camera node (camera to be named at build), no cloud, Frigate+ paid optional not required.
- H14 Near-IR night vision — Pi NoIR-style camera (no IR filter) + IR illuminator, lab night sight.
- H15 Thermal night vision — MLX90640 32x24, -40 to 300°C, I2C, Pi/Arduino, presence in complete darkness. True military NVG is NOT in this list — lab night vision = near-IR + thermal.
- H16 SatNOGS satellite ground station system — Pi + RTL-SDR (starter) + VHF/UHF antenna, non-rotator starter build, schedule observations. Alternative SDR (HackRF) possible at build — radio choice to confirm, not locked.
- H17 RPLIDAR A1 — 360° laser scanning, open SDK, ROS/ROS 2, USB, Linux, Class 1 laser. Teaching scanner (0.15–12 m, 8000 samples/s, 5.5 Hz typical).
- H18 RPLIDAR A2 — Faster scanner (12 m, 16k samples/s, 10–15 Hz, 0.225° resolution), for moving rover / cleaner maps faster.
- H19 RPLIDAR C1 — DTOF compact scanner (0.05–12 m white / 0.05–6 m black, 5kHz, 8–12 Hz, ±30 mm, IP54), for small/nearby objects, anti-interference.
- H20 DonkeyCar rover — Open source self-driving RC car, Pi + camera + TensorFlow/PyTorch autopilot, telemetry, GPS, LiDAR-capable.

## Modules — new (M11–M13, appended, M0–M10 unchanged)
- **M11 — Aerial: see from above.** H12 drone. GPS missions, return-to-home, failsafe, logging, aerial sensing + drone detection defense. Safety/legal gate first, before any flight.
- **M12 — Motion + Night: see movement, see in the dark.** H13 Frigate + H14 near-IR + H15 thermal. Motion vs object, presence vs identity, night sight (near-IR vs thermal), lab cameras only, consenting participants only.
- **M13 — Space + Mapping: see far, map the room.** H16 SatNOGS + H17/H18/H19 RPLIDAR (all three, comparison lab: same room, three scanners, three maps, tape-measure ground truth) + H20 DonkeyCar + student M1 iPad Pro LiDAR. Satellite reception, 360° mapping, SLAM, rover navigation, iPad 3D (5 m) vs RPLIDAR 2D (12 m) comparison, accuracy vs ground truth, NDT metrology.
- 2026-10-29 16:13 ET: ALL 3 RPLIDAR SCANNERS LOCKED — total now 20 items (H17 A1, H18 A2, H19 C1, H20 DonkeyCar renumbered). Comparison lab locked. New items still pending order/arrival.

## Crazy labs — all 20 locked 2026-10-29 16:32 ET (HgX: "I want all of them")
**Status: LOCKED into course, NOT built yet.** Build order: after the hardware one-by-one gates pass for the hardware each lab needs. Each lab = own lab only, evidence logged, See → Document → Log → Prevent, no faked passes. Full detail in CRAZY-IDEAS-REA-KALI-HARDWARE.md.
- L1 Digital Twin Lab — M7/M13: iPad LiDAR + 3 RPLIDARs + thermal + OpenMV + Frigate, 3D twin + thermal overlay + change detection.
- L2 Off-Grid Satellite Alert — M2/M6: SatNOGS pass → LoRa mesh alert, no internet.
- L3 Rogue Transmitter Hunt — M2/M6: Kraken + HackRF + mesh, find your own rogue, kill it, log it.
- L4 Dark Lab — M7/M12: NoIR + thermal + OpenMV + Frigate + LiDAR, presence without identity, blind-spot map.
- L5 Card-to-Chip Full Chain — M3/M5/M8: Flipper → Proxmark → GreatFET → ChipWhisperer → REA → harden every layer.
- L6 Voice-Controlled Lab — M9: speak a lab, lab runs, Jarvis narrates, GenOffice reports as it runs.
- L7 Drone Mapping + Ground Truth — M11/M13: drone aerial map vs ground LiDAR truth, measure the error.
- L8 Autonomous Mesh Scout — M6/M13: DonkeyCar + RPLIDAR + OpenMV + T-Beam mesh, off-grid rover.
- L9 Firmware Glass-Box Cinema — M8/M9: REA + GreatFET + ChipWhisperer → HyperFrames video + ComfyUI visuals + VoiceStudio narration.
- L10 Bluetooth Ghost Hunt — M4: Ubertooth + Flipper BLE + HackRF + Frigate, sweep, harden, re-sweep to prove it.
- L11 Spectrum Time Machine — M2: HackRF + Kraken + SatNOGS, 24-hour spectrum replay, patterns logged.
- L12 Thermal Side-Channel Lab — M5: ChipWhisperer power + MLX thermal, see a leak in power AND heat.
- L13 Drone Mesh Relay — M6/M11: drone as flying mesh node, controlled area only, relay logged.
- L14 Face-ID Defense Lab (consent only) — M7: Mentra + OpenMV + Frigate, consenting adults only, spoofing/liveness/multi-factor, templates deleted after.
- L15 Local Vulnerability Knowledge Graph — M9: Graphify + ai-memory + REA + security-audit-skill, local only, no cloud.
- L16 Full Estate Audit Day — M0–M13: Kali all families + all 20 hardware + security-audit-skill (sandboxed), evidence pack + defense brief.
- L17 Satellite → Rover Expedition — M2/M6/M13: SatNOGS → mesh → DonkeyCar → LiDAR map → mesh back → report + narration.
- L18 Wireless Implant Hunt — M2/M4: HackRF + Ubertooth + Flipper Wi-Fi + Kraken, find your own planted rogues, remove them.
- L19 Live Lecture Machine — M9: VoiceStudio + GenOffice + ComfyUI + HyperFrames + Ollama + REA, lab becomes lecture live.
- L20 Jarvis Operator Olympics — M10 capstone extension: all 20 items, Toronto teams, scan → break own target → defend → report, scored on evidence, not speed alone.


---

@basementjarvisu · basementjarvisunleashed@gmail.com
