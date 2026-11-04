# OPERATOR PRIME — Student Worksheets, Approved v1.0.0

J.A.R.V.I.S. first, HgX small. Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

**HGX Academy** — OPERATOR PRIME is taught by HGX Academy, HgX's own academy. No university affiliation. No external accreditation claimed.

**Status: APPROVED v1.0.0 — Approved by HgX, 2026-11-04.**
Canon: syllabus v1.0.1, labs L1–L20 locked v1.0.0. Worksheet instructions follow the locked labs file; they do not change any lab, gate, or assessment.

## How to use a worksheet (every lab, same order)
- Pre-lab: read the lab goal, modules, and hardware, pass the hardware gate, record tool versions, and answer the pre-lab questions in writing, before any test.
- During-lab: follow the lab steps, in order, record tool, version, command, output, measurement, error, and file path, for every step, in the evidence pack standard.
- Post-lab: answer the post-lab questions, file the hardening change and re-test where applicable, file the deletion log where required, and tick the evidence checklist. A worksheet is not complete until its evidence checklist is ticked on filed evidence, never on assertion.
- Gate: each worksheet ends with the lab's gate, in the lab's own words. A gate is passed only on filed evidence.

## L1 Digital Twin Lab — M7/M13
Goal: build a measured 3D model of a laboratory room and quantify change over time. Hardware: M1 iPad Pro LiDAR, RPLIDAR A1, A2, C1, MLX90640 thermal, OpenMV Cam, Frigate.
Pre-lab: [1] What is ground truth in this lab, and how will you measure it? [2] What four scan methods will you use, and what does each one measure? [3] What error would make a change claim unmeasured, and how will you avoid it?
During-lab: scan the room four ways; fuse scans into one model with a thermal overlay; re-scan after one week; measure change, movement, and heat. Record: [scan 1 file path, tool, version] [scan 2] [scan 3] [scan 4] [fused model] [re-scan] [change measurements, with error against tape-measure ground truth].
Post-lab: [1] What changed, by how much, with what error? [2] What did thermal add that LiDAR alone did not? [3] What would you change about the scan plan next time, and why?
Evidence checklist: [ ] four scans [ ] fused model [ ] change report with error against ground truth. Gate: error quantified; no unmeasured claim.

## L2 Off-Grid Satellite Alert — M2/M6
Goal: receive a satellite pass and deliver the result without internet or cellular service. Hardware: SatNOGS station, T-Watch, T-Beam, Acer gateway.
Pre-lab: [1] What does off-grid mean in this lab, and what must not be used? [2] What is the mesh path from satellite to watch, in order? [3] What latency and loss will you log, and why?
During-lab: schedule a pass; receive and decode; push the result over the LoRa mesh to the watch; log latency and loss. Record: [pass schedule] [received data] [mesh delivery log] [latency] [loss].
Post-lab: [1] Did the full chain work off-grid, with what latency and loss? [2] Where did loss occur, if anywhere, and what would you change? [3] What would break first if the mesh gateway failed?
Evidence checklist: [ ] pass schedule [ ] received data [ ] mesh delivery log. Gate: end-to-end delivery demonstrated off-grid.

## L3 Rogue Transmitter Hunt — M2/M6
Goal: locate a transmitter by measurement. Hardware: KrakenSDR, HackRF One, T-Beam mesh nodes, one own rogue transmitter planted for the exercise.
Pre-lab: [1] What is triangulation, in your own words, and what measurement does it need? [2] How will you prove you found the transmitter by measurement, not by prior knowledge? [3] What is the mesh's role in this hunt?
During-lab: record spectrum; triangulate with KrakenSDR; relay location over the mesh; walk to the transmitter; remove it; document the hunt. Record: [spectrum captures] [bearing estimates] [mesh log] [recovery photograph file path].
Post-lab: [1] Where was the transmitter, and how did each bearing contribute? [2] What was the largest bearing error, and why? [3] What would you do differently on a second hunt?
Evidence checklist: [ ] spectrum captures [ ] bearing estimates [ ] mesh log [ ] recovery photograph. Gate: transmitter recovered by measurement, not by prior knowledge.

## L4 Dark Lab — M7/M12
Goal: sense a dark room without identity. Hardware: Near-IR camera with illuminator, MLX90640 thermal, OpenMV Cam, Frigate, RPLIDAR.
Pre-lab: [1] What is presence, and how is it different from identity, in this lab? [2] What four senses will you record in parallel, and what does each one add? [3] What must you never attempt in this lab, and why?
During-lab: lights out; record near-IR, thermal, LiDAR, and motion in parallel; fuse into a presence map; identify blind spots. Record: [near-IR log] [thermal log] [LiDAR log] [motion log] [fused presence map] [blind-spot map].
Post-lab: [1] Where was presence demonstrated, and where were the blind spots? [2] Which sensor failed first, if any, and why? [3] How would you close the largest blind spot?
Evidence checklist: [ ] fused presence map [ ] blind-spot map [ ] per-sensor logs. Gate: presence demonstrated without identity; no face or person identification attempted.

## L5 Card-to-Chip Full Chain — M3/M5/M8
Goal: attack and then harden one own access system end to end. Hardware: Flipper Zero, Proxmark3 RDV4, GreatFET One, ChipWhisperer-Lite.
Pre-lab: [1] What are the four layers in this chain (card, bus, chip, firmware), and what does each one protect? [2] What is a before-and-after test, and why does every layer need one? [3] What is your own target, and what authorisation do you hold for it?
During-lab: field read; laboratory deep read; bus capture; power and glitch analysis; firmware analysis; harden card, bus, chip, and firmware; re-test. Record: [per-layer findings, one ledger row per finding] [hardening changes] [before-and-after test results].
Post-lab: [1] Which layer was weakest before hardening, and what proved it? [2] Which hardening change made the largest difference, by measurement? [3] Which layer still worries you, and what would you test next?
Evidence checklist: [ ] per-layer findings [ ] hardening changes [ ] before-and-after test results. Gate: every layer hardened and re-verified.

## L6 Voice-Controlled Lab — M9
Goal: operate a laboratory by voice, with narration and reporting generated as the work runs. Hardware: Maono microphone, Acer, PipeWire voice layer. Stacks: VoiceStudio, GenOffice.
Pre-lab: [1] What must a generated report match, exactly, and why? [2] What is the voice path from spoken instruction to test to narration, in order? [3] What error would make a narration untrustworthy?
During-lab: issue a spoken laboratory instruction; run the test; narrate results live; generate the report during the run. Record: [voice log] [test output] [generated report].
Post-lab: [1] Did the report match the logged test output exactly, word for word, number for number? [2] Where did narration add a claim not in the log, if anywhere? [3] What would you change about the voice workflow?
Evidence checklist: [ ] voice log [ ] test output [ ] generated report. Gate: report matches the logged test output exactly.

## L7 Drone Mapping and Ground Truth — M11/M13
Goal: compare an aerial map against ground measurement. Hardware: PX4/ArduPilot drone kit, camera, thermal camera, ground RPLIDAR, iPad LiDAR.
Pre-lab: [1] What is the Transport Canada checklist, and what must be filed before flight? [2] What is ground truth here, and how will you measure it? [3] What weather gates would stop a flight, and why?
During-lab: fly a controlled area; build an aerial map; measure the same area from the ground; quantify aerial error. Record: [safety checklist, filed before flight] [aerial map] [ground map] [error table].
Post-lab: [1] What was the aerial error, by how much, and where was it largest? [2] What caused the largest error? [3] What would you change about the flight plan?
Evidence checklist: [ ] safety checklist [ ] aerial map [ ] ground map [ ] error table. Gate: safety and Transport Canada checklist completed before flight; error quantified.

## L8 Autonomous Mesh Scout — M6/M13
Goal: operate a rover that maps and reports over a mesh, without Wi-Fi. Hardware: DonkeyCar Rover, RPLIDAR, OpenMV Cam, T-Beam mesh.
Pre-lab: [1] What does off-Wi-Fi mean in this lab, and what must not be used? [2] What is the full loop (map, avoid, report, command, return), in order? [3] What mesh command will you send, and what response proves it worked?
During-lab: map a laboratory area; avoid obstacles; report over the mesh; accept a mesh command; return. Record: [map] [obstacle log] [mesh command and response log].
Post-lab: [1] Did the full loop complete off Wi-Fi, with what evidence at each link? [2] Where did the rover struggle, and why? [3] What would you change about the mesh plan?
Evidence checklist: [ ] map [ ] obstacle log [ ] mesh command and response log. Gate: full loop completed off Wi-Fi.

## L9 Firmware Glass-Box Cinema — M8/M9
Goal: turn a verified firmware finding into a teachable, fully documented presentation. Hardware: GreatFET One, ChipWhisperer-Lite, own target firmware. Stacks: HyperFrames, ComfyUI, VoiceStudio, GenOffice.
Pre-lab: [1] What is a verified finding, and what evidence makes it verified? [2] What must every visual and narration claim trace to, and why? [3] What is your own target firmware, and what authorisation do you hold for it?
During-lab: analyse own firmware; prove a flaw; build video, visuals, narration, and a written report from the same evidence. Record: [REA report] [video] [visuals] [narration script] [written report] [trace table: claim → evidence file path].
Post-lab: [1] Which visual was hardest to trace to evidence, and how did you fix it? [2] What did the presentation teach that the raw report did not? [3] What finding did you leave out, and why?
Evidence checklist: [ ] REA report [ ] video [ ] visuals [ ] narration script [ ] written report. Gate: every visual and narration claim traces to the REA evidence.

## L10 Bluetooth Ghost Hunt — M4
Goal: find, harden, and prove the removal of a weak Bluetooth configuration. Hardware: Ubertooth One, Flipper Zero Bluetooth, HackRF One, Frigate.
Pre-lab: [1] What is a weak Bluetooth configuration, in your own words? [2] What will your first sweep record, and what will your second sweep prove? [3] What is your own device, and what authorisation do you hold for it?
During-lab: sweep the laboratory; record devices and pairing behaviour; harden the weak configuration on your own device; re-sweep. Record: [first sweep] [hardening change] [second sweep].
Post-lab: [1] What weakness did the first sweep find, with what measurement? [2] What did the second sweep prove, by measurement? [3] What weakness remains, if any, and what would you test next?
Evidence checklist: [ ] first sweep [ ] hardening change [ ] second sweep. Gate: second sweep demonstrates the weakness is removed.

## L11 Spectrum Time Machine — M2
Goal: record and analyse spectrum over time. Hardware: HackRF One, KrakenSDR, SatNOGS station.
Pre-lab: [1] What will a twenty-four-hour recording show that a single sweep will not? [2] How will you classify a signal, and what timestamp and measurement does each classification need? [3] What patterns do you expect, and what would surprise you?
During-lab: record spectrum for twenty-four hours; replay; identify satellite passes, mesh traffic, and any rogue signals; log patterns. Record: [recording file path] [replay notes] [pattern log, with timestamp and measurement per signal].
Post-lab: [1] What patterns did you find, with what timestamps and measurements? [2] Which signal was hardest to classify, and why? [3] What would you record next time, and for how long?
Evidence checklist: [ ] recording [ ] replay notes [ ] pattern log. Gate: every identified signal is classified with a timestamp and a measurement.

## L12 Thermal Side-Channel Lab — M5
Goal: correlate power and heat to detect a side-channel leak. Hardware: ChipWhisperer-Lite, MLX90640 thermal, own target chip.
Pre-lab: [1] What is a side-channel leak, in your own words? [2] What do power traces and thermal maps each measure, and why record them in parallel? [3] What would a negative result look like, and how would you document it honestly?
During-lab: record power traces; record thermal maps in parallel; correlate the two; identify the leak; propose a countermeasure. Record: [power traces] [thermal maps] [correlation analysis] [countermeasure proposal].
Post-lab: [1] Was a leak demonstrated in both senses, or was the result negative, with what method? [2] What correlation was strongest, by measurement? [3] What countermeasure would you test first, and how?
Evidence checklist: [ ] power traces [ ] thermal maps [ ] correlation analysis. Gate: leak demonstrated in both senses, or a negative result documented with method.

## L13 Drone Mesh Relay — M6/M11
Goal: extend a mesh by using a drone as a relay node. Hardware: PX4/ArduPilot drone kit, T-Beam mesh node, ground mesh nodes.
Pre-lab: [1] What obstacle blocks the ground mesh, and how will you prove it blocks it? [2] What is the relay plan, in order, and what safety checklist must be filed before flight? [3] What range and loss will you measure, before and after?
During-lab: establish a ground mesh that cannot reach across an obstacle; lift the relay node in a controlled area; relay messages; land; log range and loss. Record: [before range measurements] [relay log] [after range measurements] [safety checklist, filed before flight].
Post-lab: [1] By how much did range change, by measurement? [2] Where was loss highest, and why? [3] What would you change about the relay plan?
Evidence checklist: [ ] before-and-after range measurements [ ] relay log. Gate: safety checklist completed; relay demonstrated by measurement.

## L14 Face-ID Defense Lab, Consent Only — M7
Goal: test and then defend a face identification system, with full consent and no real-world deployment. Hardware: Mentra Live Camera Glasses, OpenMV Cam, Frigate. Participants: consenting adults only.
Pre-lab: [1] Who are your consenting adult participants, and what consent records will you file before any test? [2] What matching, spoofing, and liveness tests will you run, and what will each one prove? [3] What deletion plan will you file, and when will templates and recordings be deleted?
During-lab: enrol with consent; test matching under lighting and angle variation; test spoofing and liveness; add multi-factor defence; re-test; delete all templates and recordings. Record: [consent records] [test matrix] [defence change] [re-test results] [deletion log].
Post-lab: [1] What did matching, spoofing, and liveness each prove, by measurement? [2] What defence made the largest difference, by re-test? [3] Is your deletion log filed, with no template retained, and no non-consenting person tested? Answer only on filed evidence.
Evidence checklist: [ ] consent records [ ] test matrix [ ] defence change [ ] re-test results [ ] deletion log. Gate: deletion log filed; no template retained; no non-consenting person tested.

## L15 Local Vulnerability Knowledge Graph — M9
Goal: make laboratory findings searchable locally, without cloud services. Hardware: Acer only. Stacks: Graphify, ai-memory.
Pre-lab: [1] What is a graph node, in this lab, and what four things does each node link? [2] What question will you ask the graph, and what answer would count as traced? [3] What findings will you convert, and from which prior laboratories?
During-lab: convert findings from prior laboratories into graph nodes; link flaw, device, method, and defence; query the graph for a stated question. Record: [graph export] [query and answer log] [trace table: answer → filed laboratory finding].
Post-lab: [1] What did the graph answer, and what filed finding traces to each part of the answer? [2] Which finding was hardest to convert, and why? [3] What question would you ask next, and what finding would it need?
Evidence checklist: [ ] graph export [ ] query and answer log. Gate: every answer traces to a filed laboratory finding.

## L16 Full Estate Audit Day — M0 to M13
Goal: audit the student's own laboratory estate end to end in one day. Hardware: all twenty pieces, as required by each audit area.
Pre-lab: [1] What nine areas will you audit (network, web, wireless, RFID, Bluetooth, SDR, chips, vision, mesh), and what does each area need? [2] What does "explicitly marked out of scope with a reason" mean, and when is it honest? [3] What defence brief will you write, and what must it trace to?
During-lab: audit network, web, wireless, RFID, Bluetooth, SDR, chips, vision, and mesh; file findings per area; write a defence brief. Record: [per-area findings, one ledger row per finding] [evidence pack] [defence brief].
Post-lab: [1] Which area had the most findings, and which had the fewest, by count? [2] Which finding worries you most, and what defence would you file first? [3] Which area did you mark out of scope, with what reason, if any?
Evidence checklist: [ ] per-area findings [ ] evidence pack [ ] defence brief. Gate: every area audited or explicitly marked out of scope with a reason.

## L17 Satellite to Rover Expedition — M2/M6/M13
Goal: complete a space-to-ground chain with a rover. Hardware: SatNOGS station, T-Beam mesh, DonkeyCar Rover, RPLIDAR.
Pre-lab: [1] What is the full chain, link by link, from satellite to rover to report? [2] What log will you file at every link, and what would a missing link prove? [3] What mesh command will you send to the rover, and what response proves it worked?
During-lab: receive a satellite pass; send a mesh command to the rover; rover maps the target area; results return by mesh; report and narrate. Record: [pass log] [mesh logs] [rover map] [report] [narration].
Post-lab: [1] Did the full chain work, with what log at every link? [2] Where was the weakest link, by measurement? [3] What would you change about the chain?
Evidence checklist: [ ] pass log [ ] mesh logs [ ] rover map [ ] report [ ] narration. Gate: full chain demonstrated with logs at every link.

## L18 Wireless Implant Hunt — M2/M4
Goal: find and remove planted rogue wireless devices in the laboratory. Hardware: HackRF One, Ubertooth One, Flipper Zero Wi-Fi kit, KrakenSDR.
Pre-lab: [1] What three wireless families will you sweep (Wi-Fi, Bluetooth, sub-GHz), and what does each sweep record? [2] How will you prove a second sweep is clean, and clean for what, exactly? [3] What is a planted device, and what authorisation do you hold for removing it?
During-lab: sweep for Wi-Fi, Bluetooth, and sub-GHz devices; locate each planted device; document it; remove it; re-sweep. Record: [first sweep] [location measurements] [removal log] [second sweep].
Post-lab: [1] How many planted devices did you find, where, and by what measurement? [2] What did the second sweep prove, by measurement? [3] What device was hardest to locate, and why?
Evidence checklist: [ ] first sweep [ ] location measurements [ ] removal log [ ] second sweep. Gate: second sweep is clean for the planted devices.

## L19 Live Lecture Machine — M9
Goal: generate a lecture from a live laboratory run, locally. Hardware: Acer only, with laboratory hardware as the subject. Stacks: VoiceStudio, GenOffice, ComfyUI, HyperFrames.
Pre-lab: [1] What is a live laboratory run, and what test output will you generate the lecture from? [2] What must every lecture claim trace to, and why? [3] What slides, video, visuals, and narration will you generate, and in what order?
During-lab: run a laboratory test; generate slides, video, visuals, and narration from the live evidence; present the result. Record: [test output] [slides] [video] [visuals] [narration script] [trace table: claim → live test output].
Post-lab: [1] Which lecture claim was hardest to trace, and how did you fix it? [2] What did the lecture teach that the raw test output did not? [3] What would you generate differently next time?
Evidence checklist: [ ] test output [ ] slides [ ] video [ ] visuals [ ] narration script. Gate: every lecture claim traces to the live test output.

## L20 Operator Olympics — M10 Capstone Extension
Goal: complete a competitive capstone across all twenty hardware pieces. Hardware: all twenty pieces. Scoring: evidence quality first, then completeness, then clarity. Speed alone does not win.
Pre-lab: [1] What is your team, and what are your roles (Operator, Recorder, Auditor)? [2] What estate will you scan, what own target will you break, and what defence will you present? [3] What does "verified by re-measurement" mean for your defence?
During-lab: in teams, scan a laboratory estate; break an own target; defend it; report it; present the defence brief. Record: [full evidence pack] [report] [narration] [defence brief] [team score sheet].
Post-lab: [1] What did your team break, defend, and prove, by measurement? [2] What was your strongest evidence, and what was your weakest? [3] What would your team do differently, as a team, next time?
Evidence checklist: [ ] full evidence pack [ ] report [ ] narration [ ] defence brief [ ] team score sheet. Gate: capstone defence presented and verified by re-measurement.

## Draft laboratories L21–L50 (not locked, not taught until locked)
No worksheet is issued for L21–L50 in this draft. When HgX locks a draft laboratory expressly, the Dean will issue its worksheet as a new version, with its goal, modules, hardware, steps, evidence, and gate, in the same format as L1–L20 above, and index it here. Until then, do not invent a worksheet, a goal, or a result for any draft laboratory. L50, in the year draft, is the final year capstone, with a three-week structure (rehearsal and evidence review, team challenges, defence briefs and capstone defence verified by re-measurement) — its worksheet will be issued only when L50 itself is locked.

@basementjarvisu · basementjarvisunleashed@gmail.com
