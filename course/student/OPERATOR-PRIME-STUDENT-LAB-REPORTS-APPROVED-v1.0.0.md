# OPERATOR PRIME — Student Lab Reports, Approved v1.0.0

J.A.R.V.I.S. first, HgX small. Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

**HGX Academy** — OPERATOR PRIME is taught by HGX Academy, HgX's own academy. No university affiliation. No external accreditation claimed.

**Status: APPROVED v1.0.0 — Approved by HgX, 2026-11-04.**
Canon: syllabus v1.0.1, labs L1–L20 locked v1.0.0. Report templates follow the locked labs file; they do not change any lab, gate, or assessment. Assessment for the report component: written report (GenOffice) 25% of the course, with narrated summary (VoiceStudio) 15% and defence brief / capstone defence 20% filed alongside, and evidence pack 40% filed as the pack itself.

## How to file a lab report (every lab, same order)
1. Title, lab code, modules, hardware, tools and versions, date-order, and student role (Operator / Recorder / Auditor) — roles only in any published copy, no personal data.
2. Goal, in the lab's own words, and scope: own target, own network, own venue, consent records where required.
3. Method, in order, with tool, version, command, output, and file path, for every step.
4. Results, with measurements, error against ground truth where applicable, and file paths for every capture. Blank until you file them.
5. Analysis: findings, one ledger row per finding, confidence scored BEFORE the write-up, hardening change, before-and-after test results.
6. Gate: the lab's gate, in the lab's own words, with a pass / fail / not yet run status, on filed evidence only, never on assertion.
7. Declaration: "This report is my own laboratory work. Every claim traces to a filed capture or log listed above. No result has been fabricated, copied from another student, or presented from a non-owned target." Signed, role only in any published copy.
8. Attachments: evidence pack file paths, worksheet file path, deletion log where required, inspection note and correction where received.

## L1 Digital Twin Lab — M7/M13 — Report template
Goal: build a measured 3D model of a laboratory room and quantify change over time. Hardware: M1 iPad Pro LiDAR, RPLIDAR A1, A2, C1, MLX90640 thermal, OpenMV Cam, Frigate. Method: scan the room four ways; fuse scans into one model with a thermal overlay; re-scan after one week; measure change, movement, and heat.
Results (blank): [scan 1 file path, measurement, error] [scan 2] [scan 3] [scan 4] [fused model] [re-scan] [change, movement, heat, with error against tape-measure ground truth].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [hardening / scan-plan change, if any] [before-and-after, if applicable].
Gate: error quantified; no unmeasured claim. Status: [passed / failed (method, error, resubmission) / not yet run].

## L2 Off-Grid Satellite Alert — M2/M6 — Report template
Goal: receive a satellite pass and deliver the result without internet or cellular service. Hardware: SatNOGS station, T-Watch, T-Beam, Acer gateway. Method: schedule a pass; receive and decode; push the result over the LoRa mesh to the watch; log latency and loss.
Results (blank): [pass schedule] [received data] [mesh delivery log] [latency] [loss].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [what broke, what worked, what would change].
Gate: end-to-end delivery demonstrated off-grid. Status: [passed / failed / not yet run].

## L3 Rogue Transmitter Hunt — M2/M6 — Report template
Goal: locate a transmitter by measurement. Hardware: KrakenSDR, HackRF One, T-Beam mesh nodes, one own rogue transmitter planted for the exercise. Method: record spectrum; triangulate with KrakenSDR; relay location over the mesh; walk to the transmitter; remove it; document the hunt.
Results (blank): [spectrum captures] [bearing estimates] [mesh log] [recovery photograph file path] [transmitter location, by measurement].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [largest bearing error, and why].
Gate: transmitter recovered by measurement, not by prior knowledge. Status: [passed / failed / not yet run].

## L4 Dark Lab — M7/M12 — Report template
Goal: sense a dark room without identity. Hardware: Near-IR camera with illuminator, MLX90640 thermal, OpenMV Cam, Frigate, RPLIDAR. Method: lights out; record near-IR, thermal, LiDAR, and motion in parallel; fuse into a presence map; identify blind spots.
Results (blank): [near-IR log] [thermal log] [LiDAR log] [motion log] [fused presence map] [blind-spot map].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [presence demonstrated, identity not attempted, stated plainly].
Gate: presence demonstrated without identity; no face or person identification attempted. Status: [passed / failed / not yet run].

## L5 Card-to-Chip Full Chain — M3/M5/M8 — Report template
Goal: attack and then harden one own access system end to end. Hardware: Flipper Zero, Proxmark3 RDV4, GreatFET One, ChipWhisperer-Lite. Method: field read; laboratory deep read; bus capture; power and glitch analysis; firmware analysis; harden card, bus, chip, and firmware; re-test.
Results (blank): [per-layer findings: card] [bus] [chip] [firmware] [hardening changes, per layer] [before-and-after test results, per layer].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [weakest layer before hardening, by measurement] [largest hardening effect, by measurement].
Gate: every layer hardened and re-verified. Status: [passed / failed / not yet run].

## L6 Voice-Controlled Lab — M9 — Report template
Goal: operate a laboratory by voice, with narration and reporting generated as the work runs. Hardware: Maono microphone, Acer, PipeWire voice layer. Stacks: VoiceStudio, GenOffice. Method: issue a spoken laboratory instruction; run the test; narrate results live; generate the report during the run.
Results (blank): [voice log] [test output] [generated report] [exact-match check: report vs logged test output, word for word, number for number].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [any narration claim not in the log, if any, and how it was corrected].
Gate: report matches the logged test output exactly. Status: [passed / failed / not yet run].

## L7 Drone Mapping and Ground Truth — M11/M13 — Report template
Goal: compare an aerial map against ground measurement. Hardware: PX4/ArduPilot drone kit, camera, thermal camera, ground RPLIDAR, iPad LiDAR. Method: fly a controlled area; build an aerial map; measure the same area from the ground; quantify aerial error.
Results (blank): [safety and Transport Canada checklist, filed before flight] [aerial map] [ground map] [error table, with largest error and where].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [cause of largest error] [flight-plan change].
Gate: safety and Transport Canada checklist completed before flight; error quantified. Status: [passed / failed / not yet run].

## L8 Autonomous Mesh Scout — M6/M13 — Report template
Goal: operate a rover that maps and reports over a mesh, without Wi-Fi. Hardware: DonkeyCar Rover, RPLIDAR, OpenMV Cam, T-Beam mesh. Method: map a laboratory area; avoid obstacles; report over the mesh; accept a mesh command; return.
Results (blank): [map] [obstacle log] [mesh command and response log] [full loop, link by link, off Wi-Fi].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [where the rover struggled, and why].
Gate: full loop completed off Wi-Fi. Status: [passed / failed / not yet run].

## L9 Firmware Glass-Box Cinema — M8/M9 — Report template
Goal: turn a verified firmware finding into a teachable, fully documented presentation. Hardware: GreatFET One, ChipWhisperer-Lite, own target firmware. Stacks: HyperFrames, ComfyUI, VoiceStudio, GenOffice. Method: analyse own firmware; prove a flaw; build video, visuals, narration, and a written report from the same evidence.
Results (blank): [REA report] [video] [visuals] [narration script] [written report] [trace table: every visual and narration claim → REA evidence file path].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [flaw proved, with evidence] [what the presentation taught that the raw report did not].
Gate: every visual and narration claim traces to the REA evidence. Status: [passed / failed / not yet run].

## L10 Bluetooth Ghost Hunt — M4 — Report template
Goal: find, harden, and prove the removal of a weak Bluetooth configuration. Hardware: Ubertooth One, Flipper Zero Bluetooth, HackRF One, Frigate. Method: sweep the laboratory; record devices and pairing behaviour; harden the weak configuration on your own device; re-sweep.
Results (blank): [first sweep] [hardening change] [second sweep] [weakness removed, by measurement].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [weakness remaining, if any, and next test].
Gate: second sweep demonstrates the weakness is removed. Status: [passed / failed / not yet run].

## L11 Spectrum Time Machine — M2 — Report template
Goal: record and analyse spectrum over time. Hardware: HackRF One, KrakenSDR, SatNOGS station. Method: record spectrum for twenty-four hours; replay; identify satellite passes, mesh traffic, and any rogue signals; log patterns.
Results (blank): [recording file path] [replay notes] [pattern log, with timestamp and measurement per signal].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [hardest signal to classify, and why].
Gate: every identified signal is classified with a timestamp and a measurement. Status: [passed / failed / not yet run].

## L12 Thermal Side-Channel Lab — M5 — Report template
Goal: correlate power and heat to detect a side-channel leak. Hardware: ChipWhisperer-Lite, MLX90640 thermal, own target chip. Method: record power traces; record thermal maps in parallel; correlate the two; identify the leak; propose a countermeasure.
Results (blank): [power traces] [thermal maps] [correlation analysis] [countermeasure proposal] [leak demonstrated in both senses, or negative result with method, stated plainly].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [strongest correlation, by measurement].
Gate: leak demonstrated in both senses, or a negative result documented with method. Status: [passed / failed / not yet run].

## L13 Drone Mesh Relay — M6/M11 — Report template
Goal: extend a mesh by using a drone as a relay node. Hardware: PX4/ArduPilot drone kit, T-Beam mesh node, ground mesh nodes. Method: establish a ground mesh that cannot reach across an obstacle; lift the relay node in a controlled area; relay messages; land; log range and loss.
Results (blank): [safety checklist, filed before flight] [before range measurements] [relay log] [after range measurements] [range change, by measurement].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [where loss was highest, and why].
Gate: safety checklist completed; relay demonstrated by measurement. Status: [passed / failed / not yet run].

## L14 Face-ID Defense Lab, Consent Only — M7 — Report template
Goal: test and then defend a face identification system, with full consent and no real-world deployment. Hardware: Mentra Live Camera Glasses, OpenMV Cam, Frigate. Participants: consenting adults only. Method: enrol with consent; test matching under lighting and angle variation; test spoofing and liveness; add multi-factor defence; re-test; delete all templates and recordings.
Results (blank): [consent records] [test matrix] [defence change] [re-test results] [deletion log, with no template retained, stated on filed evidence].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [largest defence effect, by re-test] [non-consenting person tested: none, stated on filed evidence].
Gate: deletion log filed; no template retained; no non-consenting person tested. Status: [passed / failed / not yet run].

## L15 Local Vulnerability Knowledge Graph — M9 — Report template
Goal: make laboratory findings searchable locally, without cloud services. Hardware: Acer only. Stacks: Graphify, ai-memory. Method: convert findings from prior laboratories into graph nodes; link flaw, device, method, and defence; query the graph for a stated question.
Results (blank): [graph export] [query and answer log] [trace table: every answer → filed laboratory finding].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [question asked, answer given, trace for each part of the answer].
Gate: every answer traces to a filed laboratory finding. Status: [passed / failed / not yet run].

## L16 Full Estate Audit Day — M0 to M13 — Report template
Goal: audit the student's own laboratory estate end to end in one day. Hardware: all twenty pieces, as required by each audit area. Method: audit network, web, wireless, RFID, Bluetooth, SDR, chips, vision, and mesh; file findings per area; write a defence brief.
Results (blank): [per-area findings: network] [web] [wireless] [RFID] [Bluetooth] [SDR] [chips] [vision] [mesh] [areas marked out of scope, with reasons, if any] [evidence pack] [defence brief].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [most concerning finding, and first defence to file].
Gate: every area audited or explicitly marked out of scope with a reason. Status: [passed / failed / not yet run].

## L17 Satellite to Rover Expedition — M2/M6/M13 — Report template
Goal: complete a space-to-ground chain with a rover. Hardware: SatNOGS station, T-Beam mesh, DonkeyCar Rover, RPLIDAR. Method: receive a satellite pass; send a mesh command to the rover; rover maps the target area; results return by mesh; report and narrate.
Results (blank): [pass log] [mesh logs] [rover map] [report] [narration] [full chain, link by link, with a log at every link].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [weakest link, by measurement].
Gate: full chain demonstrated with logs at every link. Status: [passed / failed / not yet run].

## L18 Wireless Implant Hunt — M2/M4 — Report template
Goal: find and remove planted rogue wireless devices in the laboratory. Hardware: HackRF One, Ubertooth One, Flipper Zero Wi-Fi kit, KrakenSDR. Method: sweep for Wi-Fi, Bluetooth, and sub-GHz devices; locate each planted device; document it; remove it; re-sweep.
Results (blank): [first sweep] [location measurements, per device] [removal log, per device] [second sweep] [second sweep clean for the planted devices, by measurement].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [hardest device to locate, and why].
Gate: second sweep is clean for the planted devices. Status: [passed / failed / not yet run].

## L19 Live Lecture Machine — M9 — Report template
Goal: generate a lecture from a live laboratory run, locally. Hardware: Acer only, with laboratory hardware as the subject. Stacks: VoiceStudio, GenOffice, ComfyUI, HyperFrames. Method: run a laboratory test; generate slides, video, visuals, and narration from the live evidence; present the result.
Results (blank): [test output] [slides] [video] [visuals] [narration script] [trace table: every lecture claim → live test output].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [hardest claim to trace, and how it was fixed].
Gate: every lecture claim traces to the live test output. Status: [passed / failed / not yet run].

## L20 Operator Olympics — M10 Capstone Extension — Report template
Goal: complete a competitive capstone across all twenty hardware pieces. Hardware: all twenty pieces. Scoring: evidence quality first, then completeness, then clarity. Speed alone does not win. Method: in teams, scan a laboratory estate; break an own target; defend it; report it; present the defence brief.
Results (blank): [full evidence pack] [report] [narration] [defence brief] [team score sheet] [team roles: Operator, Recorder, Auditor] [defence verified by re-measurement, with before-and-after results].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [strongest evidence, weakest evidence, team lesson].
Gate: capstone defence presented and verified by re-measurement. Status: [passed / failed / not yet run].

## Draft laboratories L21–L50 (not locked, not taught until locked)
No report template is issued for L21–L50 in this draft. When HgX locks a draft laboratory expressly, the Dean will issue its report template as a new version, with its goal, modules, hardware, steps, evidence, and gate, in the same format as L1–L20 above, and index it here. Until then, do not invent a report, a goal, or a result for any draft laboratory. L50, in the year draft, is the final year capstone, with a three-week structure (rehearsal and evidence review, team challenges, defence briefs and capstone defence verified by re-measurement) — its report template will be issued only when L50 itself is locked.

@basementjarvisu · basementjarvisunleashed@gmail.com
