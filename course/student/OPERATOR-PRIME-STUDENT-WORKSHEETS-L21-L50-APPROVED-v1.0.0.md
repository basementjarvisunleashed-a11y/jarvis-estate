# OPERATOR PRIME — Student Worksheets L21–L50, Approved v1.0.0

J.A.R.V.I.S. first, HgX small. Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

**HGX Academy** — OPERATOR PRIME is taught by HGX Academy, HgX's own academy. No university affiliation. No external accreditation claimed.

**Status: APPROVED v1.0.0 — Approved by HgX, 2026-11-04.**
**APPROVED AS DRAFT PUBLICATION ONLY** — labs L21–L50 are NOT locked as canon; a separate express lock by name is still required.
Canon: syllabus v1.0.1, labs L1–L20 locked v1.0.0, year-expansion draft v0.1.0 for L21–L50 and H21–H30. Worksheet instructions follow the year-expansion draft; they do not lock any lab, and they do not change any locked lab, gate, or assessment. General draft gate, per the year-expansion draft, for every lab below unless a lab-specific gate is stated: present + safe self-test on own lab target only + evidence saved. No lab passes on assertion. Venue per lab: Lab = indoor lab, Airfield = private airfield, Farm = private farm.

## How to use a worksheet (every lab, same order)
Pre-lab: read the lab goal and hardware, pass the hardware gate, record tool versions, answer the pre-lab questions in writing, before any test. During-lab: follow the lab steps, in order, record tool, version, command, output, measurement, error, and file path, for every step. Post-lab: answer the post-lab questions, file the hardening change and re-test where applicable, file the deletion log where required, tick the evidence checklist on filed evidence only. Gate: stated per lab, passed only on filed evidence.

## L21 Open Hardware Teardown — H21 Arduino — Lab
Goal, from the year-expansion draft: REA firmware + I/O on an open hardware board, own board only.
Pre-lab: [1] What is your own board, and what authorisation do you hold for it? [2] What firmware and I/O surfaces will you audit, and in what order? [3] What evidence will prove a finding, and what would prove nothing?
During-lab: teardown own board; REA firmware; audit I/O; log findings, one ledger row per finding. Record: [board, firmware version, hash] [REA report] [I/O log] [findings ledger].
Post-lab: [1] What did you find, with what evidence? [2] What would you harden first, and how would you re-test it? [3] What did openness of the hardware make possible that a closed board would not?
Evidence checklist: [ ] REA report [ ] I/O log [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved.

## L22 Single-Board Linux Audit — H22 BeagleBone — Lab
Goal: services, device tree, logs, on a single-board Linux system, own board only.
Pre-lab: [1] What services, device tree entries, and logs will you audit, and why those? [2] What is your own board, and what authorisation do you hold for it? [3] What would a clean audit look like, with what evidence?
During-lab: audit services; audit device tree; audit logs; file findings per area. Record: [services list] [device tree notes] [log extracts, scrubbed, no personal data] [findings ledger].
Post-lab: [1] What services worried you most, and why? [2] What would you disable, harden, or monitor, and how would you re-test? [3] What log entry taught you the most?
Evidence checklist: [ ] services list [ ] device tree notes [ ] logs [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved.

## L23 Protocol Bridge Hunt — H23 Bus Pirate — Lab
Goal: UART / I2C / SPI, own boards only, protocol bridge hunt.
Pre-lab: [1] What three buses will you hunt, and what does each one carry? [2] What is your own board, and what authorisation do you hold for it? [3] How will you prove a bridge finding by measurement, not by prior knowledge?
During-lab: hunt UART, I2C, and SPI on own boards; decode protocol data; log findings. Record: [bus captures, per bus] [decoded data] [findings ledger].
Post-lab: [1] Which bus was most revealing, and why? [2] What trust question does each bus raise? [3] What would you test next on the same boards?
Evidence checklist: [ ] bus captures [ ] decoded data [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved.

## L24 FPGA Glass-Box — H24 iCEBreaker — Lab
Goal: Verilog, bitstream, trust, glass-box design, own board only.
Pre-lab: [1] What is a glass-box design, in your own words, and why does it matter for trust? [2] What Verilog and bitstream work will you do, in what order? [3] What would a trustworthy bitstream prove, and what would it not prove?
During-lab: design / audit Verilog; build / audit bitstream; test on own board; log findings. Record: [Verilog source, versioned] [bitstream, hash] [test log] [findings ledger].
Post-lab: [1] What did the bitstream prove, by measurement? [2] What trust question remains, and why? [3] What would you change about the design?
Evidence checklist: [ ] Verilog [ ] bitstream [ ] test log [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved.

## L25 ESP32 Firmware Extraction and Hardening — H25, own board only — Lab
Goal: firmware extraction (own board only), radio surface, update chain, then hardening.
Pre-lab: [1] What is your own board, and what authorisation do you hold for it? [2] What extraction, radio, and update-chain surfaces will you audit? [3] What hardening change will you propose, and how will you re-test it?
During-lab: extract firmware from own board; audit radio surface; audit update chain; harden; re-test. Record: [firmware version, hash] [radio log] [update-chain notes] [hardening change] [before-and-after test results].
Post-lab: [1] What was weakest before hardening, by measurement? [2] What did re-testing prove? [3] What update-chain risk remains?
Evidence checklist: [ ] firmware [ ] radio log [ ] update-chain notes [ ] hardening + re-test. Gate: present + safe self-test on own lab target only + evidence saved; every layer hardened and re-verified, as in L5.

## L26 BLE Sensor Node Defense — H26 + H29 — Lab
Goal: Bluetooth surface, sensor trust, code audit, own nodes only.
Pre-lab: [1] What Bluetooth surface will you audit, and what sensor data trust question does it raise? [2] What are your own nodes, and what authorisation do you hold for them? [3] What code audit will you do, and what will it prove?
During-lab: audit Bluetooth surface; audit sensor data trust; audit code; harden; re-test. Record: [Bluetooth sweep] [sensor data log] [code audit notes] [hardening change] [re-test].
Post-lab: [1] What Bluetooth weakness did you find, by measurement? [2] What sensor trust question was hardest, and why? [3] What did re-testing prove?
Evidence checklist: [ ] Bluetooth sweep [ ] sensor log [ ] code audit [ ] hardening + re-test. Gate: present + safe self-test on own lab target only + evidence saved.

## L27 Touch Display Trust — H27 M5Stack — Lab
Goal: display / touch injection, own device only, display trust, touch input trust, firmware audit.
Pre-lab: [1] What is display trust, and what is touch input trust, in your own words? [2] What is your own device, and what authorisation do you hold for it? [3] What injection tests will you run, and what would each one prove?
During-lab: test display trust; test touch input trust; audit firmware; log findings; harden where applicable; re-test. Record: [display test log] [touch test log] [firmware audit notes] [findings ledger].
Post-lab: [1] Which injection test was most revealing, and why? [2] What defence would you file first? [3] What trust question remains?
Evidence checklist: [ ] display log [ ] touch log [ ] firmware audit [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved.

## L28 Toolchain Trust — H28 Pinecil — Lab
Goal: firmware update chain, thermal evidence, control, measurement, evidence.
Pre-lab: [1] What is a toolchain, and what trust question does it raise? [2] What firmware update chain will you audit, and what thermal evidence will you record? [3] What is your own device, and what authorisation do you hold for it?
During-lab: audit firmware update chain; record thermal evidence; log findings; propose a trust control. Record: [update-chain notes] [thermal evidence] [findings ledger] [trust control proposal].
Post-lab: [1] What update-chain risk did you find, by evidence? [2] What did thermal evidence add? [3] What trust control would you test first?
Evidence checklist: [ ] update-chain notes [ ] thermal evidence [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved.

## L29 Tiny Sensor Mesh — H29 XIAO nodes + mesh — Lab, then Farm for range
Goal: sensor node trust, Bluetooth surface, mesh node role, then range on the farm.
Pre-lab: [1] What mesh role will each node play, and how will you prove it? [2] What range will you measure, in the lab and on the farm, and how? [3] What failure modes will you test?
During-lab: build tiny sensor mesh in the lab; test node roles; measure range on the farm; log findings. Record: [mesh log] [node role log] [lab range measurements] [farm range measurements] [findings ledger].
Post-lab: [1] How did farm range differ from lab range, by measurement? [2] Which node role was weakest, and why? [3] What mesh change would you test next?
Evidence checklist: [ ] mesh log [ ] node roles [ ] range measurements, lab + farm. Gate: present + safe self-test on own lab target only + evidence saved.

## L30 Pocket Mesh Terminal — H30 T-Deck + H3 + H9 mesh — Airfield / Farm
Goal: pocket mesh terminal, with watch and T-Beam mesh, off-grid, airfield / farm.
Pre-lab: [1] What is the mesh path from terminal to watch to T-Beam, in order? [2] What off-grid test will you run, and what must not be used? [3] What range and loss will you measure, and where?
During-lab: build pocket mesh terminal; test mesh delivery off-grid; measure range and loss on airfield / farm; log findings. Record: [mesh log] [delivery log] [range and loss measurements] [findings ledger].
Post-lab: [1] Did delivery work off-grid, with what range and loss? [2] Where was loss highest, and why? [3] What would you change about the terminal plan?
Evidence checklist: [ ] mesh log [ ] delivery log [ ] range and loss measurements. Gate: present + safe self-test on own lab target only + evidence saved.

## L31 Kali Everything Audit Day 2 — Full 13 families, second pass, deeper — Lab
Goal: second-pass audit, deeper, across the full 13 families, on the student's own estate.
Pre-lab: [1] What did L16 teach you that this second pass must do deeper? [2] What 13 families will you audit, and what does each area need? [3] What does "explicitly marked out of scope with a reason" mean here?
During-lab: audit all families, second pass, deeper; file findings per area; write a defence brief. Record: [per-area findings] [evidence pack] [defence brief].
Post-lab: [1] What did the second pass find that the first pass missed, by area? [2] Which area worries you most now, and why? [3] What defence would you file first?
Evidence checklist: [ ] per-area findings [ ] evidence pack [ ] defence brief. Gate: every area audited or explicitly marked out of scope with a reason, as in L16, deeper.

## L32 Password Lab 2 — Lab-created hashes only, GPU, REA teardown of cracker — Lab
Goal: lab-created hashes only, GPU work, REA teardown of the cracker itself. Hard rule, from the year-expansion draft: lab-created hashes only, never real passwords, never another person's hashes.
Pre-lab: [1] What hashes will you create in the lab, and how will you prove they are lab-created? [2] What GPU work will you do, and what will you measure? [3] What REA teardown will you do on the cracker, and what will it prove?
During-lab: create lab hashes; run GPU work; teardown the cracker with REA; log findings. Record: [lab hash creation log] [GPU log] [REA teardown report] [findings ledger].
Post-lab: [1] What did the GPU work prove, by measurement? [2] What did the cracker teardown teach you about trust in your own tools? [3] What would you never do with a real hash, and why?
Evidence checklist: [ ] lab hash log [ ] GPU log [ ] REA teardown [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved; lab-created hashes only, proven by the creation log.

## L33 Wireless Lab 2 — Own access point only, monitor mode, external adapter if needed — Lab / Farm
Goal: own access point only, monitor mode, wireless audit, lab / farm.
Pre-lab: [1] What is your own access point, and what authorisation do you hold for it? [2] What monitor-mode work will you do, and what will it record? [3] What must you never sweep, and why?
During-lab: audit own access point in monitor mode; log wireless findings; harden where applicable; re-test. Record: [monitor-mode log] [findings ledger] [hardening change, if any] [re-test, if any].
Post-lab: [1] What did monitor mode reveal, by measurement? [2] What hardening change made the largest difference, if any? [3] What wireless risk remains?
Evidence checklist: [ ] monitor-mode log [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved; own access point only, proven by the audit log.

## L34 Web App Defense Lab — Own lab web app, headers, vuln scan, REA teardown — Lab
Goal: own lab web app, headers, vulnerability scan, REA teardown, then hardening.
Pre-lab: [1] What is your own lab web app, and what authorisation do you hold for it? [2] What headers will you audit, and what scan will you run, in what order? [3] What REA teardown will you do, and what will it prove?
During-lab: audit headers; run vulnerability scan on own app; teardown with REA; harden; re-test. Record: [headers audit] [scan report] [REA teardown report] [hardening change] [before-and-after test results].
Post-lab: [1] What was weakest before hardening, by measurement? [2] What did re-testing prove? [3] What web risk remains?
Evidence checklist: [ ] headers audit [ ] scan report [ ] REA teardown [ ] hardening + re-test. Gate: present + safe self-test on own lab target only + evidence saved.

## L35 Database Defense Lab — Own lab database, injection detection, hardening — Lab
Goal: own lab database, injection detection, hardening, then re-test.
Pre-lab: [1] What is your own lab database, and what authorisation do you hold for it? [2] What injection tests will you run, and what would each one prove? [3] What hardening change will you propose, and how will you re-test it?
During-lab: test injection detection on own database; log findings; harden; re-test. Record: [injection test log] [findings ledger] [hardening change] [before-and-after test results].
Post-lab: [1] What injection risk did you find, by measurement? [2] What did re-testing prove? [3] What database risk remains?
Evidence checklist: [ ] injection test log [ ] findings ledger [ ] hardening + re-test. Gate: present + safe self-test on own lab target only + evidence saved.

## L36 Network Forensics Lab — Own packet captures, timeline, evidence pack — Lab
Goal: own packet captures, timeline, evidence pack, forensic method, lab only.
Pre-lab: [1] What captures are your own, and what authorisation do you hold for them? [2] What timeline will you build, and what will each entry need? [3] What would a forensic conclusion need, and what would it not need?
During-lab: analyse own packet captures; build a timeline; file an evidence pack. Record: [capture file paths, own captures only] [timeline] [evidence pack] [findings ledger].
Post-lab: [1] What did the timeline prove, by capture? [2] What was hardest to timeline, and why? [3] What would you capture next time, and why?
Evidence checklist: [ ] captures [ ] timeline [ ] evidence pack. Gate: present + safe self-test on own lab target only + evidence saved.

## L37 Firmware Update Chain Lab — Signed vs unsigned, supply chain, provenance — Lab
Goal: signed vs unsigned firmware, supply chain, provenance, trust, lab only.
Pre-lab: [1] What is signed firmware, and what does a signature prove, and not prove? [2] What supply chain will you audit, and what provenance will you check? [3] What is your own firmware, and what authorisation do you hold for it?
During-lab: audit signed vs unsigned firmware; audit supply chain; check provenance; log findings; propose a trust control. Record: [signature audit notes] [supply chain notes] [provenance notes] [findings ledger] [trust control proposal].
Post-lab: [1] What supply chain risk did you find, by evidence? [2] What did provenance prove, and what did it not prove? [3] What trust control would you test first?
Evidence checklist: [ ] signature audit [ ] supply chain notes [ ] provenance notes [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved.

## L38 AI Model Audit Lab — Local Unsloth model (Stack 11), training code audit, REA — Lab
Goal: local model audit, training code audit, REA, lab only, local models only.
Pre-lab: [1] What local model will you audit, and what training code will you audit with it? [2] What REA work will you do, and what will it prove? [3] What model trust question will you answer, and what evidence will it need?
During-lab: audit local model; audit training code; teardown with REA; log findings. Record: [model version, hash, local only] [training code audit notes] [REA teardown report] [findings ledger].
Post-lab: [1] What model risk did you find, by evidence? [2] What did the training code audit teach you? [3] What model trust question remains?
Evidence checklist: [ ] model audit [ ] training code audit [ ] REA teardown [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved; local models only.

## L39 Prompt Injection Defense Lab 2 — M14 extension, synthetic benign cases only — Lab
Goal: M14 extension, synthetic benign cases only, LLM Firewall reference by name only, lab only, own local Acer models only, Muse excluded, no prompt text in course load.
Pre-lab: [1] What are synthetic benign cases, and why only synthetic and benign? [2] What defence will you test, and what would each case prove? [3] What must never appear in your course load, and why?
During-lab: run synthetic benign cases on own local models only; test defences; log findings. Record: [synthetic benign case log, no prompt text in course load] [defence test log] [findings ledger].
Post-lab: [1] Which defence worked best, by measurement on synthetic benign cases? [2] What defence failed, and why? [3] What would you test next, still synthetic and benign only?
Evidence checklist: [ ] synthetic benign case log [ ] defence test log [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved; synthetic benign cases only, Muse excluded, no prompt text in course load.

## L40 Hardware Side-Channel Lab 2 — ChipWhisperer + thermal, own chips only — Lab
Goal: hardware side-channel, second pass, deeper, ChipWhisperer + thermal, own chips only.
Pre-lab: [1] What did L12 teach you that this second pass must do deeper? [2] What are your own chips, and what authorisation do you hold for them? [3] What power and thermal work will you do in parallel, and what correlation will you test?
During-lab: record power traces; record thermal maps in parallel; correlate; identify the leak or document a negative result with method; propose a countermeasure. Record: [power traces] [thermal maps] [correlation analysis] [countermeasure proposal].
Post-lab: [1] Was a leak demonstrated in both senses, or was the result negative, with what method? [2] What correlation was strongest, by measurement? [3] What countermeasure would you test first?
Evidence checklist: [ ] power traces [ ] thermal maps [ ] correlation analysis. Gate: leak demonstrated in both senses, or a negative result documented with method, as in L12, deeper.

## L41 Drone Defense Lab 2 — Own drone, GPS / link detection in lab conditions, Transport Canada rules first, airfield only for flight — Airfield
Goal: own drone, GPS / link detection in lab conditions, Transport Canada rules first, airfield only for flight.
Pre-lab: [1] What is the Transport Canada checklist, and what must be filed before flight? [2] What GPS / link detection work will you do in lab conditions, and what will it prove? [3] What weather gates would stop a flight, and why?
During-lab: file Transport Canada checklist before flight; test GPS / link detection in lab conditions; fly only on the airfield, in a controlled area, where flight is required; log findings. Record: [safety checklist, filed before flight] [lab detection log] [flight log, airfield only, if flown] [findings ledger].
Post-lab: [1] What did lab detection prove, by measurement? [2] What did flight add, if flown, by measurement? [3] What drone defence would you file first?
Evidence checklist: [ ] safety checklist [ ] lab detection log [ ] flight log, if flown. Gate: safety checklist completed; Transport Canada rules first; airfield only for flight; present + safe self-test on own lab target only + evidence saved.

## L42 Night Sensing Fusion Lab — Frigate + near-IR + thermal, fused evidence — Farm (night)
Goal: Frigate + near-IR + thermal, fused evidence, farm at night, presence without identity.
Pre-lab: [1] What three senses will you fuse, and what does each one add? [2] What is presence, and how is it different from identity, in this lab? [3] What night safety, weather, and venue gates must be filed before the farm night?
During-lab: record Frigate, near-IR, and thermal in parallel on the farm at night; fuse into evidence; identify blind spots; log findings. Record: [Frigate log] [near-IR log] [thermal log] [fused evidence] [blind-spot map].
Post-lab: [1] Where was presence demonstrated, and where were the blind spots? [2] Which sense failed first, if any, and why? [3] How would you close the largest blind spot?
Evidence checklist: [ ] Frigate log [ ] near-IR log [ ] thermal log [ ] fused evidence. Gate: present + safe self-test on own lab target only + evidence saved; presence without identity, as in L4.

## L43 Satellite Ground Station Lab 2 — SatNOGS, own passes, signal decoding — Lab / Farm
Goal: SatNOGS, own passes, signal decoding, second pass, deeper, lab / farm.
Pre-lab: [1] What passes will you schedule, and what signals will you decode? [2] What did L2 teach you that this second pass must do deeper? [3] What latency and loss will you log, and why?
During-lab: schedule own passes; receive and decode; log latency, loss, and findings. Record: [pass schedule] [received data] [decoding log] [latency and loss] [findings ledger].
Post-lab: [1] What did the second pass decode that the first pass did not? [2] Where was loss highest, and why? [3] What would you schedule next?
Evidence checklist: [ ] pass schedule [ ] received data [ ] decoding log. Gate: present + safe self-test on own lab target only + evidence saved.

## L44 LiDAR Mapping Lab 2 — All three RPLIDAR scanners + iPad, new room / farm area, tape-measure ground truth — Farm / Lab
Goal: all three RPLIDAR scanners + iPad LiDAR, new room / farm area, tape-measure ground truth, second pass, deeper.
Pre-lab: [1] What new room / farm area will you map, and why that area? [2] What ground truth will you measure with a tape measure, and how? [3] What error would make a map claim unmeasured, and how will you avoid it?
During-lab: map the new area with all three RPLIDAR scanners + iPad; measure ground truth; quantify error; log findings. Record: [RPLIDAR A1 map] [RPLIDAR A2 map] [RPLIDAR C1 map] [iPad map] [ground truth table] [error table].
Post-lab: [1] What was the error, by scanner, and where was it largest? [2] Which scanner was most accurate here, and why? [3] What would you map next?
Evidence checklist: [ ] three RPLIDAR maps [ ] iPad map [ ] ground truth table [ ] error table. Gate: error quantified; no unmeasured claim, as in L1, deeper.

## L45 Rover Autonomy Lab 2 — DonkeyCar, obstacle, evidence log, larger course — Farm
Goal: DonkeyCar, obstacle, evidence log, larger course, farm, second pass, deeper.
Pre-lab: [1] What larger course will you run, and why that course? [2] What obstacles will you test, and what autonomy will you prove? [3] What evidence log will you file, and what will each entry need?
During-lab: run the larger farm course; test obstacles; log autonomy and evidence; report over the mesh where applicable. Record: [course map] [obstacle log] [autonomy log] [evidence log] [findings ledger].
Post-lab: [1] Did autonomy hold on the larger course, by measurement? [2] Where did it fail, and why? [3] What would you change about the course or the rover?
Evidence checklist: [ ] course map [ ] obstacle log [ ] autonomy log [ ] evidence log. Gate: present + safe self-test on own lab target only + evidence saved.

## L46 Mesh Resilience Lab — Watch + T-Beam + T-Deck + XIAO, off-grid, failure modes — Farm / Airfield
Goal: watch + T-Beam + T-Deck + XIAO mesh, off-grid, failure modes, farm / airfield, resilience.
Pre-lab: [1] What mesh nodes will you use, and what role will each one play? [2] What failure modes will you test, in what order? [3] What off-grid test will you run, and what must not be used?
During-lab: build the multi-node mesh; test failure modes, one at a time; measure range, loss, and recovery; log findings. Record: [mesh log] [failure mode log, per mode] [range, loss, and recovery measurements] [findings ledger].
Post-lab: [1] Which failure mode hurt most, by measurement, and how did the mesh recover? [2] Which node was most critical, and why? [3] What resilience change would you test next?
Evidence checklist: [ ] mesh log [ ] failure mode log [ ] range, loss, and recovery measurements. Gate: present + safe self-test on own lab target only + evidence saved; off-grid, failure modes demonstrated by measurement.

## L47 Supply Chain Lab — Bill of materials, open vs closed, provenance, honesty checks — Lab
Goal: bill of materials, open vs closed, provenance, honesty checks, lab only.
Pre-lab: [1] What bill of materials will you audit, and for what system? [2] What is open vs closed, in this audit, and how will you verify it? [3] What provenance checks will you run, and what would each one prove?
During-lab: audit the bill of materials; check open vs closed, per item; check provenance, per item; log honesty findings. Record: [bill of materials] [open vs closed table, per item, with verification] [provenance notes] [findings ledger].
Post-lab: [1] What was open, what was closed, and what was unverifiable, by item? [2] What honesty check surprised you most, and why? [3] What would you change about the supply chain?
Evidence checklist: [ ] bill of materials [ ] open vs closed table [ ] provenance notes [ ] findings ledger. Gate: present + safe self-test on own lab target only + evidence saved.

## L48 Incident Response Lab — Own lab incident, timeline, evidence pack, report — Lab
Goal: own lab incident, timeline, evidence pack, report, incident response method, lab only.
Pre-lab: [1] What own lab incident will you respond to, and what authorisation do you hold for it? [2] What timeline will you build, and what will each entry need? [3] What report will you write, and what must it trace to?
During-lab: respond to the own lab incident; build a timeline; file an evidence pack; write a report. Record: [incident log] [timeline] [evidence pack] [report] [findings ledger].
Post-lab: [1] What did the timeline prove, by capture and log? [2] What was the root cause, and what correction would you file? [3] What would you do differently in a real response, and why?
Evidence checklist: [ ] incident log [ ] timeline [ ] evidence pack [ ] report. Gate: present + safe self-test on own lab target only + evidence saved.

## L49 Capstone Prep Lab 2 — Evidence pack review, defence brief rehearsal — Lab
Goal: evidence pack review, defence brief rehearsal, preparation for the final defence, lab only.
Pre-lab: [1] Which evidence packs will you review, and what will you check in each one? [2] What defence brief will you rehearse, and what must it trace to? [3] What would a rehearsal failure teach you, and how would you correct it?
During-lab: review evidence packs; rehearse the defence brief; log corrections; re-test where a gate requires it. Record: [pack review notes, per pack] [defence brief rehearsal log] [corrections ledger] [re-test results, where applicable].
Post-lab: [1] Which pack was strongest, and which was weakest, by evidence? [2] What rehearsal correction mattered most? [3] What are you ready to defend, and what still needs work?
Evidence checklist: [ ] pack review notes [ ] rehearsal log [ ] corrections ledger. Gate: present + safe self-test on own lab target only + evidence saved; defence brief rehearsed on filed evidence only.

## L50 Year Capstone — Operator Prime Final Defence — Stretched, three weeks — Lab, with farm / airfield where required
Goal: final year capstone, stretched, not a single week, not a replacement for L20 Operator Olympics (mid-course capstone). Week 1: rehearsal and evidence review. Week 2: team challenges, scored on evidence quality, not speed alone. Week 3: defence briefs and capstone defence, verified by re-measurement. Buffer days sit inside each week, so a failed gate can be resubmitted without breaking the final.
Pre-lab: [1] What is your team, and what are your roles (Operator, Recorder, Auditor)? [2] What full-year evidence will you review in Week 1, and what will you correct? [3] What defence will you present in Week 3, and what re-measurement will verify it?
During-lab, Week 1: rehearsal and evidence review; file corrections; re-test where a gate requires it. Week 2: team challenges, scored on evidence quality first, then completeness, then clarity, speed alone does not win. Week 3: defence briefs and capstone defence, verified by re-measurement. Record: [full-year evidence pack] [report] [narration] [defence brief] [team score sheet] [re-measurement results].
Post-lab: [1] What did your team prove, by full-year evidence and by re-measurement? [2] What was your strongest evidence, and what was your weakest? [3] What would your team do differently, as a team, next time?
Evidence checklist: [ ] full-year evidence pack [ ] report [ ] narration [ ] defence brief [ ] team score sheet [ ] re-measurement results. Gate: capstone defence presented and verified by re-measurement, as in L20, stretched over three weeks with buffer days inside each week.

@basementjarvisu · basementjarvisunleashed@gmail.com
