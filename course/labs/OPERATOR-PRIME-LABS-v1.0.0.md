# J.A.R.V.I.S. — OPERATOR PRIME Course Material
**J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System)** — public identity, first and prominent.
Operator: HgX (small). Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

> **HGX Academy** — OPERATOR PRIME is taught by HGX Academy, HgX's own academy. No university affiliation. No external accreditation claimed.

> **STATUS: LOCKED v1.0.0 — Labs L1–L20 ratified. Full lab write-ups, gates per laboratory, evidence filing required.**

> **Audience and hard rules:** Consenting adults only. Controlled laboratory only. Own devices, own tags, own networks, own targets only. Spine: SEE → DOCUMENT → LOG → PREVENT. Face work only on consenting adult participants, in the lab only, for defensive education. Templates stay in the lab, deleted after the exercise. Never family, never his son, never strangers, never real-world surveillance or deployment. Radio transmit only on own authorised frequencies. Drone only in a safe, controlled flying area, Transport Canada rules first. Lasers Class 1 only.

> **Licence:** Course text CC-BY-4.0. Code MIT. © HGX Engineering. No secrets in public. No personal data: no real names, no Wi-Fi names, no home addresses, no serials, no passwords, no credentials, no live location, no family details, no financial details. No 2.0/3.0 material. No prompt text reproduced.

---

# OPERATOR PRIME — Laboratory Manual: All 20 Laboratories
**Course: Full-Spectrum Operator Systems: Open-Source Hardware, Reverse Engineering, and Evidence-Based Defense (OPERATOR PRIME)**
**Standard: professional, laboratory-only, own devices and targets only, consenting adults only. Every laboratory follows See → Document → Log → Prevent. A laboratory passes only when its evidence is filed.**
**How to use this manual: complete laboratories in order, one at a time. Do not start a laboratory until the hardware it requires has passed its own gate. Record tool, version, command, output, measurement, and error for every step.**

## L1 Digital Twin Lab — M7/M13
Goal: build a measured 3D model of a laboratory room and quantify change over time. Hardware: M1 iPad Pro LiDAR, RPLIDAR A1, A2, C1, MLX90640 thermal, OpenMV Cam, Frigate. Kali/REA: information gathering, measurement, CloudCompare/Open3D (local). Stacks: Graphify, ai-memory. Steps: scan the room four ways; fuse scans into one model with a thermal overlay; re-scan after one week; measure change, movement, and heat. Evidence: four scans, fused model, change report with error against tape-measure ground truth. Gate: error quantified; no unmeasured claim.

## L2 Off-Grid Satellite Alert — M2/M6
Goal: receive a satellite pass and deliver the result without internet or cellular service. Hardware: SatNOGS station, T-Watch, T-Beam, Acer gateway. Kali/REA: SDR, scheduling, logging. Steps: schedule a pass; receive and decode; push the result over the LoRa mesh to the watch; log latency and loss. Evidence: pass schedule, received data, mesh delivery log. Gate: end-to-end delivery demonstrated off-grid.

## L3 Rogue Transmitter Hunt — M2/M6
Goal: locate a transmitter by measurement. Hardware: KrakenSDR, HackRF One, T-Beam mesh nodes, one own rogue transmitter planted for the exercise. Kali/REA: spectrum analysis, direction finding. Steps: record spectrum; triangulate with KrakenSDR; relay location over the mesh; walk to the transmitter; remove it; document the hunt. Evidence: spectrum captures, bearing estimates, mesh log, recovery photograph. Gate: transmitter recovered by measurement, not by prior knowledge.

## L4 Dark Lab — M7/M12
Goal: sense a dark room without identity. Hardware: Near-IR camera with illuminator, MLX90640 thermal, OpenMV Cam, Frigate, RPLIDAR. Kali/REA: vision, detection, logging. Steps: lights out; record near-IR, thermal, LiDAR, and motion in parallel; fuse into a presence map; identify blind spots. Evidence: fused presence map, blind-spot map, per-sensor logs. Gate: presence demonstrated without identity; no face or person identification attempted.

## L5 Card-to-Chip Full Chain — M3/M5/M8
Goal: attack and then harden one own access system end to end. Hardware: Flipper Zero, Proxmark3 RDV4, GreatFET One, ChipWhisperer-Lite. Kali/REA: RFID/NFC, bus analysis, side-channel analysis, firmware analysis with REA. Steps: field read; laboratory deep read; bus capture; power and glitch analysis; firmware analysis; harden card, bus, chip, and firmware; re-test. Evidence: per-layer findings, hardening changes, before-and-after test results. Gate: every layer hardened and re-verified.

## L6 Voice-Controlled Lab — M9
Goal: operate a laboratory by voice, with narration and reporting generated as the work runs. Hardware: Maono microphone, Acer, PipeWire voice layer. Kali/REA: orchestrator tools, local Ollama. Stacks: VoiceStudio, GenOffice. Steps: issue a spoken laboratory instruction; run the test; narrate results live; generate the report during the run. Evidence: voice log, test output, generated report. Gate: report matches the logged test output exactly.

## L7 Drone Mapping and Ground Truth — M11/M13
Goal: compare an aerial map against ground measurement. Hardware: PX4/ArduPilot drone kit, camera, thermal camera, ground RPLIDAR, iPad LiDAR. Kali/REA: mapping, measurement, error analysis. Steps: fly a controlled area; build an aerial map; measure the same area from the ground; quantify aerial error. Evidence: aerial map, ground map, error table. Gate: safety and Transport Canada checklist completed before flight; error quantified.

## L8 Autonomous Mesh Scout — M6/M13
Goal: operate a rover that maps and reports over a mesh, without Wi-Fi. Hardware: DonkeyCar Rover, RPLIDAR, OpenMV Cam, T-Beam mesh. Kali/REA: navigation, mapping, mesh logging. Steps: map a laboratory area; avoid obstacles; report over the mesh; accept a mesh command; return. Evidence: map, obstacle log, mesh command and response log. Gate: full loop completed off Wi-Fi.

## L9 Firmware Glass-Box Cinema — M8/M9
Goal: turn a verified firmware finding into a teachable, fully documented presentation. Hardware: GreatFET One, ChipWhisperer-Lite, own target firmware. Kali/REA: REA firmware analysis. Stacks: HyperFrames, ComfyUI, VoiceStudio, GenOffice. Steps: analyse own firmware; prove a flaw; build video, visuals, narration, and a written report from the same evidence. Evidence: REA report, video, visuals, narration script, written report. Gate: every visual and narration claim traces to the REA evidence.

## L10 Bluetooth Ghost Hunt — M4
Goal: find, harden, and prove the removal of a weak Bluetooth configuration. Hardware: Ubertooth One, Flipper Zero Bluetooth, HackRF One, Frigate. Kali/REA: Bluetooth sniffing, pairing analysis. Steps: sweep the laboratory; record devices and pairing behaviour; harden the weak configuration on your own device; re-sweep. Evidence: first sweep, hardening change, second sweep. Gate: second sweep demonstrates the weakness is removed.

## L11 Spectrum Time Machine — M2
Goal: record and analyse spectrum over time. Hardware: HackRF One, KrakenSDR, SatNOGS station. Kali/REA: spectrum recording, replay, analysis. Steps: record spectrum for twenty-four hours; replay; identify satellite passes, mesh traffic, and any rogue signals; log patterns. Evidence: recording, replay notes, pattern log. Gate: every identified signal is classified with a timestamp and a measurement.

## L12 Thermal Side-Channel Lab — M5
Goal: correlate power and heat to detect a side-channel leak. Hardware: ChipWhisperer-Lite, MLX90640 thermal, own target chip. Kali/REA: power analysis, thermal analysis. Steps: record power traces; record thermal maps in parallel; correlate the two; identify the leak; propose a countermeasure. Evidence: power traces, thermal maps, correlation analysis. Gate: leak demonstrated in both senses, or a negative result documented with method.

## L13 Drone Mesh Relay — M6/M11
Goal: extend a mesh by using a drone as a relay node. Hardware: PX4/ArduPilot drone kit, T-Beam mesh node, ground mesh nodes. Kali/REA: mesh logging, range measurement. Steps: establish a ground mesh that cannot reach across an obstacle; lift the relay node in a controlled area; relay messages; land; log range and loss. Evidence: before-and-after range measurements, relay log. Gate: safety checklist completed; relay demonstrated by measurement.

## L14 Face-ID Defense Lab, Consent Only — M7
Goal: test and then defend a face identification system, with full consent and no real-world deployment. Hardware: Mentra Live Camera Glasses, OpenMV Cam, Frigate. Participants: consenting adults only. Kali/REA: enrolment, matching, spoofing, liveness analysis. Steps: enrol with consent; test matching under lighting and angle variation; test spoofing and liveness; add multi-factor defence; re-test; delete all templates and recordings. Evidence: consent records, test matrix, defence change, re-test results, deletion log. Gate: deletion log filed; no template retained; no non-consenting person tested.

## L15 Local Vulnerability Knowledge Graph — M9
Goal: make laboratory findings searchable locally, without cloud services. Hardware: Acer only. Kali/REA: REA findings, security-audit-skill (sandboxed). Stacks: Graphify, ai-memory. Steps: convert findings from prior laboratories into graph nodes; link flaw, device, method, and defence; query the graph for a stated question. Evidence: graph export, query and answer log. Gate: every answer traces to a filed laboratory finding.

## L16 Full Estate Audit Day — M0 to M13
Goal: audit the student's own laboratory estate end to end in one day. Hardware: all twenty pieces, as required by each audit area. Kali/REA: all families, security-audit-skill (sandboxed). Steps: audit network, web, wireless, RFID, Bluetooth, SDR, chips, vision, and mesh; file findings per area; write a defence brief. Evidence: per-area findings, evidence pack, defence brief. Gate: every area audited or explicitly marked out of scope with a reason.

## L17 Satellite to Rover Expedition — M2/M6/M13
Goal: complete a space-to-ground chain with a rover. Hardware: SatNOGS station, T-Beam mesh, DonkeyCar Rover, RPLIDAR. Kali/REA: satellite reception, mesh command, mapping. Steps: receive a satellite pass; send a mesh command to the rover; rover maps the target area; results return by mesh; report and narrate. Evidence: pass log, mesh logs, rover map, report, narration. Gate: full chain demonstrated with logs at every link.

## L18 Wireless Implant Hunt — M2/M4
Goal: find and remove planted rogue wireless devices in the laboratory. Hardware: HackRF One, Ubertooth One, Flipper Zero Wi-Fi kit, KrakenSDR. Kali/REA: wireless sweeping, direction finding. Steps: sweep for Wi-Fi, Bluetooth, and sub-GHz devices; locate each planted device; document it; remove it; re-sweep. Evidence: first sweep, location measurements, removal log, second sweep. Gate: second sweep is clean for the planted devices.

## L19 Live Lecture Machine — M9
Goal: generate a lecture from a live laboratory run, locally. Hardware: Acer only, with laboratory hardware as the subject. Kali/REA: REA findings, local Ollama. Stacks: VoiceStudio, GenOffice, ComfyUI, HyperFrames. Steps: run a laboratory test; generate slides, video, visuals, and narration from the live evidence; present the result. Evidence: test output, slides, video, visuals, narration script. Gate: every lecture claim traces to the live test output.

## L20 Operator Olympics — M10 Capstone Extension
Goal: complete a competitive capstone across all twenty hardware pieces. Hardware: all twenty pieces. Kali/REA: all families as required. Steps: in teams, scan a laboratory estate; break an own target; defend it; report it; present the defence brief. Scoring: evidence quality first, then completeness, then clarity. Speed alone does not win. Evidence: full evidence pack, report, narration, defence brief, team score sheet. Gate: capstone defence presented and verified by re-measurement.


---

@basementjarvisu · basementjarvisunleashed@gmail.com
