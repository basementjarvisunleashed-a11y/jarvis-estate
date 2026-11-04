# OPERATOR PRIME — Student Lab Reports L21–L50, Approved v1.0.0

J.A.R.V.I.S. first, HgX small. Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

**HGX Academy** — OPERATOR PRIME is taught by HGX Academy, HgX's own academy. No university affiliation. No external accreditation claimed.

**Status: APPROVED v1.0.0 — Approved by HgX, 2026-11-04.**
**APPROVED AS DRAFT PUBLICATION ONLY** — labs L21–L50 are NOT locked as canon; a separate express lock by name is still required.
Canon: syllabus v1.0.1, labs L1–L20 locked v1.0.0, year-expansion draft v0.1.0 for L21–L50 and H21–H30. Report templates follow the year-expansion draft; they do not lock any lab, and they do not change any locked lab, gate, or assessment. General draft gate, per the year-expansion draft, for every lab below unless a lab-specific gate is stated: present + safe self-test on own lab target only + evidence saved. No lab passes on assertion.

## How to file a lab report (every lab, same order)
1. Title, lab code, hardware, tools and versions, date-order, student role — roles only in any published copy, no personal data.
2. Goal, in the year-expansion draft's words, and scope: own target, own network, own venue, consent records where required.
3. Method, in order, with tool, version, command, output, and file path, for every step.
4. Results, with measurements, error against ground truth where applicable, and file paths for every capture. Blank until you file them.
5. Analysis: findings, one ledger row per finding, confidence scored BEFORE the write-up, hardening change, before-and-after test results.
6. Gate: stated per lab, with a pass / fail / not yet run status, on filed evidence only, never on assertion.
7. Declaration: "This report is my own laboratory work. Every claim traces to a filed capture or log listed above. No result has been fabricated, copied from another student, or presented from a non-owned target." Signed, role only in any published copy.
8. Attachments: evidence pack file paths, worksheet file path, deletion log where required, inspection note and correction where received.

## L21 Open Hardware Teardown — H21 Arduino — Lab — Report template
Goal: REA firmware + I/O on an open hardware board, own board only. Method: teardown own board; REA firmware; audit I/O; log findings.
Results (blank): [board, firmware version, hash] [REA report] [I/O log] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [hardening proposal, if any].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L22 Single-Board Linux Audit — H22 BeagleBone — Lab — Report template
Goal: services, device tree, logs, on a single-board Linux system, own board only. Method: audit services; audit device tree; audit logs; file findings per area.
Results (blank): [services list] [device tree notes] [log extracts, scrubbed] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [services to disable, harden, or monitor].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L23 Protocol Bridge Hunt — H23 Bus Pirate — Lab — Report template
Goal: UART / I2C / SPI, own boards only, protocol bridge hunt. Method: hunt UART, I2C, and SPI on own boards; decode protocol data; log findings.
Results (blank): [bus captures, per bus] [decoded data] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [trust question per bus].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L24 FPGA Glass-Box — H24 iCEBreaker — Lab — Report template
Goal: Verilog, bitstream, trust, glass-box design, own board only. Method: design / audit Verilog; build / audit bitstream; test on own board; log findings.
Results (blank): [Verilog source, versioned] [bitstream, hash] [test log] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [trust proved, trust not proved, stated plainly].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L25 ESP32 Firmware Extraction and Hardening — H25, own board only — Lab — Report template
Goal: firmware extraction (own board only), radio surface, update chain, then hardening. Method: extract firmware from own board; audit radio surface; audit update chain; harden; re-test.
Results (blank): [firmware version, hash] [radio log] [update-chain notes] [hardening change] [before-and-after test results].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [weakest surface before hardening, by measurement].
Gate: present + safe self-test on own lab target only + evidence saved; every layer hardened and re-verified, as in L5. Status: [passed / failed / not yet run].

## L26 BLE Sensor Node Defense — H26 + H29 — Lab — Report template
Goal: Bluetooth surface, sensor trust, code audit, own nodes only. Method: audit Bluetooth surface; audit sensor data trust; audit code; harden; re-test.
Results (blank): [Bluetooth sweep] [sensor data log] [code audit notes] [hardening change] [re-test].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [largest defence effect, by re-test].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L27 Touch Display Trust — H27 M5Stack — Lab — Report template
Goal: display / touch injection, own device only, display trust, touch input trust, firmware audit. Method: test display trust; test touch input trust; audit firmware; log findings; harden where applicable; re-test.
Results (blank): [display test log] [touch test log] [firmware audit notes] [findings ledger] [hardening + re-test, if applicable].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [most revealing injection test, and why].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L28 Toolchain Trust — H28 Pinecil — Lab — Report template
Goal: firmware update chain, thermal evidence, control, measurement, evidence. Method: audit firmware update chain; record thermal evidence; log findings; propose a trust control.
Results (blank): [update-chain notes] [thermal evidence] [findings ledger] [trust control proposal].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [update-chain risk, by evidence].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L29 Tiny Sensor Mesh — H29 XIAO nodes + mesh — Lab, then Farm for range — Report template
Goal: sensor node trust, Bluetooth surface, mesh node role, then range on the farm. Method: build tiny sensor mesh in the lab; test node roles; measure range on the farm; log findings.
Results (blank): [mesh log] [node role log] [lab range measurements] [farm range measurements] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [lab vs farm range, by measurement].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L30 Pocket Mesh Terminal — H30 T-Deck + H3 + H9 mesh — Airfield / Farm — Report template
Goal: pocket mesh terminal, with watch and T-Beam mesh, off-grid, airfield / farm. Method: build pocket mesh terminal; test mesh delivery off-grid; measure range and loss on airfield / farm; log findings.
Results (blank): [mesh log] [delivery log] [range and loss measurements] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [where loss was highest, and why].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L31 Kali Everything Audit Day 2 — Full 13 families, second pass, deeper — Lab — Report template
Goal: second-pass audit, deeper, across the full 13 families, on the student's own estate. Method: audit all families, second pass, deeper; file findings per area; write a defence brief.
Results (blank): [per-area findings] [evidence pack] [defence brief].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [what the second pass found that the first pass missed, by area].
Gate: every area audited or explicitly marked out of scope with a reason, as in L16, deeper. Status: [passed / failed / not yet run].

## L32 Password Lab 2 — Lab-created hashes only, GPU, REA teardown of cracker — Lab — Report template
Goal: lab-created hashes only, GPU work, REA teardown of the cracker itself. Hard rule: lab-created hashes only, never real passwords, never another person's hashes. Method: create lab hashes; run GPU work; teardown the cracker with REA; log findings.
Results (blank): [lab hash creation log, proving lab-created] [GPU log] [REA teardown report] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [what the cracker teardown taught about trust in own tools].
Gate: present + safe self-test on own lab target only + evidence saved; lab-created hashes only, proven by the creation log. Status: [passed / failed / not yet run].

## L33 Wireless Lab 2 — Own access point only, monitor mode, external adapter if needed — Lab / Farm — Report template
Goal: own access point only, monitor mode, wireless audit, lab / farm. Method: audit own access point in monitor mode; log wireless findings; harden where applicable; re-test.
Results (blank): [monitor-mode log] [findings ledger] [hardening change, if any] [re-test, if any].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [largest hardening effect, if any].
Gate: present + safe self-test on own lab target only + evidence saved; own access point only, proven by the audit log. Status: [passed / failed / not yet run].

## L34 Web App Defense Lab — Own lab web app, headers, vuln scan, REA teardown — Lab — Report template
Goal: own lab web app, headers, vulnerability scan, REA teardown, then hardening. Method: audit headers; run vulnerability scan on own app; teardown with REA; harden; re-test.
Results (blank): [headers audit] [scan report] [REA teardown report] [hardening change] [before-and-after test results].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [weakest surface before hardening, by measurement].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L35 Database Defense Lab — Own lab database, injection detection, hardening — Lab — Report template
Goal: own lab database, injection detection, hardening, then re-test. Method: test injection detection on own database; log findings; harden; re-test.
Results (blank): [injection test log] [findings ledger] [hardening change] [before-and-after test results].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [injection risk, by measurement].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L36 Network Forensics Lab — Own packet captures, timeline, evidence pack — Lab — Report template
Goal: own packet captures, timeline, evidence pack, forensic method, lab only. Method: analyse own packet captures; build a timeline; file an evidence pack.
Results (blank): [capture file paths, own captures only] [timeline] [evidence pack] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [what the timeline proved, by capture].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L37 Firmware Update Chain Lab — Signed vs unsigned, supply chain, provenance — Lab — Report template
Goal: signed vs unsigned firmware, supply chain, provenance, trust, lab only. Method: audit signed vs unsigned firmware; audit supply chain; check provenance; log findings; propose a trust control.
Results (blank): [signature audit notes] [supply chain notes] [provenance notes] [findings ledger] [trust control proposal].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [supply chain risk, by evidence].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L38 AI Model Audit Lab — Local Unsloth model (Stack 11), training code audit, REA — Lab — Report template
Goal: local model audit, training code audit, REA, lab only, local models only. Method: audit local model; audit training code; teardown with REA; log findings.
Results (blank): [model version, hash, local only] [training code audit notes] [REA teardown report] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [model risk, by evidence].
Gate: present + safe self-test on own lab target only + evidence saved; local models only. Status: [passed / failed / not yet run].

## L39 Prompt Injection Defense Lab 2 — M14 extension, synthetic benign cases only — Lab — Report template
Goal: M14 extension, synthetic benign cases only, LLM Firewall reference by name only, lab only, own local Acer models only, Muse excluded, no prompt text in course load. Method: run synthetic benign cases on own local models only; test defences; log findings.
Results (blank): [synthetic benign case log, no prompt text in course load] [defence test log] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [best defence, by measurement on synthetic benign cases].
Gate: present + safe self-test on own lab target only + evidence saved; synthetic benign cases only, Muse excluded, no prompt text in course load. Status: [passed / failed / not yet run].

## L40 Hardware Side-Channel Lab 2 — ChipWhisperer + thermal, own chips only — Lab — Report template
Goal: hardware side-channel, second pass, deeper, ChipWhisperer + thermal, own chips only. Method: record power traces; record thermal maps in parallel; correlate; identify the leak or document a negative result with method; propose a countermeasure.
Results (blank): [power traces] [thermal maps] [correlation analysis] [countermeasure proposal] [leak in both senses, or negative result with method, stated plainly].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [strongest correlation, by measurement].
Gate: leak demonstrated in both senses, or a negative result documented with method, as in L12, deeper. Status: [passed / failed / not yet run].

## L41 Drone Defense Lab 2 — Own drone, GPS / link detection in lab conditions, Transport Canada rules first, airfield only for flight — Airfield — Report template
Goal: own drone, GPS / link detection in lab conditions, Transport Canada rules first, airfield only for flight. Method: file Transport Canada checklist before flight; test GPS / link detection in lab conditions; fly only on the airfield, in a controlled area, where flight is required; log findings.
Results (blank): [safety checklist, filed before flight] [lab detection log] [flight log, airfield only, if flown] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [lab detection proved, flight added, stated separately].
Gate: safety checklist completed; Transport Canada rules first; airfield only for flight; present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L42 Night Sensing Fusion Lab — Frigate + near-IR + thermal, fused evidence — Farm (night) — Report template
Goal: Frigate + near-IR + thermal, fused evidence, farm at night, presence without identity. Method: record Frigate, near-IR, and thermal in parallel on the farm at night; fuse into evidence; identify blind spots; log findings.
Results (blank): [Frigate log] [near-IR log] [thermal log] [fused evidence] [blind-spot map].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [presence demonstrated, identity not attempted, stated plainly].
Gate: present + safe self-test on own lab target only + evidence saved; presence without identity, as in L4. Status: [passed / failed / not yet run].

## L43 Satellite Ground Station Lab 2 — SatNOGS, own passes, signal decoding — Lab / Farm — Report template
Goal: SatNOGS, own passes, signal decoding, second pass, deeper, lab / farm. Method: schedule own passes; receive and decode; log latency, loss, and findings.
Results (blank): [pass schedule] [received data] [decoding log] [latency and loss] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [what the second pass decoded that the first pass did not].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L44 LiDAR Mapping Lab 2 — All three RPLIDAR scanners + iPad, new room / farm area, tape-measure ground truth — Farm / Lab — Report template
Goal: all three RPLIDAR scanners + iPad LiDAR, new room / farm area, tape-measure ground truth, second pass, deeper. Method: map the new area with all three RPLIDAR scanners + iPad; measure ground truth; quantify error; log findings.
Results (blank): [RPLIDAR A1 map] [RPLIDAR A2 map] [RPLIDAR C1 map] [iPad map] [ground truth table] [error table].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [error, by scanner, largest error and where].
Gate: error quantified; no unmeasured claim, as in L1, deeper. Status: [passed / failed / not yet run].

## L45 Rover Autonomy Lab 2 — DonkeyCar, obstacle, evidence log, larger course — Farm — Report template
Goal: DonkeyCar, obstacle, evidence log, larger course, farm, second pass, deeper. Method: run the larger farm course; test obstacles; log autonomy and evidence; report over the mesh where applicable.
Results (blank): [course map] [obstacle log] [autonomy log] [evidence log] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [where autonomy failed, and why].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L46 Mesh Resilience Lab — Watch + T-Beam + T-Deck + XIAO, off-grid, failure modes — Farm / Airfield — Report template
Goal: watch + T-Beam + T-Deck + XIAO mesh, off-grid, failure modes, farm / airfield, resilience. Method: build the multi-node mesh; test failure modes, one at a time; measure range, loss, and recovery; log findings.
Results (blank): [mesh log] [failure mode log, per mode] [range, loss, and recovery measurements] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [failure mode that hurt most, and how the mesh recovered].
Gate: present + safe self-test on own lab target only + evidence saved; off-grid, failure modes demonstrated by measurement. Status: [passed / failed / not yet run].

## L47 Supply Chain Lab — Bill of materials, open vs closed, provenance, honesty checks — Lab — Report template
Goal: bill of materials, open vs closed, provenance, honesty checks, lab only. Method: audit the bill of materials; check open vs closed, per item; check provenance, per item; log honesty findings.
Results (blank): [bill of materials] [open vs closed table, per item, with verification] [provenance notes] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [open, closed, and unverifiable, by item].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L48 Incident Response Lab — Own lab incident, timeline, evidence pack, report — Lab — Report template
Goal: own lab incident, timeline, evidence pack, report, incident response method, lab only. Method: respond to the own lab incident; build a timeline; file an evidence pack; write a report.
Results (blank): [incident log] [timeline] [evidence pack] [report] [findings ledger].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [root cause, and correction to file].
Gate: present + safe self-test on own lab target only + evidence saved. Status: [passed / failed / not yet run].

## L49 Capstone Prep Lab 2 — Evidence pack review, defence brief rehearsal — Lab — Report template
Goal: evidence pack review, defence brief rehearsal, preparation for the final defence, lab only. Method: review evidence packs; rehearse the defence brief; log corrections; re-test where a gate requires it.
Results (blank): [pack review notes, per pack] [defence brief rehearsal log] [corrections ledger] [re-test results, where applicable].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [strongest pack, weakest pack, by evidence].
Gate: present + safe self-test on own lab target only + evidence saved; defence brief rehearsed on filed evidence only. Status: [passed / failed / not yet run].

## L50 Year Capstone — Operator Prime Final Defence — Stretched, three weeks — Lab, with farm / airfield where required — Report template
Goal: final year capstone, stretched, not a single week, not a replacement for L20 Operator Olympics (mid-course capstone). Week 1: rehearsal and evidence review. Week 2: team challenges, scored on evidence quality, not speed alone. Week 3: defence briefs and capstone defence, verified by re-measurement. Buffer days sit inside each week, so a failed gate can be resubmitted without breaking the final. Method: Week 1 rehearsal and evidence review, with corrections and re-tests where a gate requires it; Week 2 team challenges; Week 3 defence briefs and capstone defence, verified by re-measurement.
Results (blank): [full-year evidence pack] [report] [narration] [defence brief] [team score sheet] [team roles: Operator, Recorder, Auditor] [re-measurement results, Week 3].
Analysis (blank): [findings, one ledger row per finding, confidence scored before write-up] [strongest evidence, weakest evidence, team lesson].
Gate: capstone defence presented and verified by re-measurement, as in L20, stretched over three weeks with buffer days inside each week. Status: [passed / failed / not yet run].

@basementjarvisu · basementjarvisunleashed@gmail.com
