# J.A.R.V.I.S. — OPERATOR PRIME Course Material
**J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System)** — public identity, first and prominent.
Operator: HgX (small). Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

> **HGX Academy** — OPERATOR PRIME is taught by HGX Academy, HgX's own academy. No university affiliation. No external accreditation claimed.

> **STATUS: LOCKED v1.0.1 — Syllabus ratified. Supersedes v1.0.0 on software stack count ONLY (10 → 17 items). All other content identical to v1.0.0. Modules M0–M14, Labs L1–L20, Hardware H1–H20 in hand, assessment 40/25/15/20, Project 25 prove entire suite, 21 checkpoints, no faked passes.**

> **Audience and hard rules:** Consenting adults only. Controlled laboratory only. Own devices, own tags, own networks, own targets only. Spine: SEE → DOCUMENT → LOG → PREVENT. Face work only on consenting adult participants, in the lab only, for defensive education. Templates stay in the lab, deleted after the exercise. Never family, never his son, never strangers, never real-world surveillance or deployment. Radio transmit only on own authorised frequencies. Drone only in a safe, controlled flying area, Transport Canada rules first. Lasers Class 1 only.

> **Licence:** Course text CC-BY-4.0. Code MIT. © HGX Engineering. No secrets in public. No personal data: no real names, no Wi-Fi names, no home addresses, no serials, no passwords, no credentials, no live location, no family details, no financial details. No 2.0/3.0 material. No prompt text reproduced.

---

# Full-Spectrum Operator Systems: Open-Source Hardware, Reverse Engineering, and Evidence-Based Defense
**Short name: OPERATOR PRIME**
**Level: Doctoral-level professional laboratory course**
**Audience: Consenting adult engineers, doctoral-capable, with a background in non-destructive testing within materials engineering. All students are Toronto-based.**
**Instructor: HgX, founder, HGX Academy. Field: non-destructive testing within materials engineering.**
**Delivery: Controlled laboratory only. Summer 2027 offering is optional in timing; the course build is complete now.**
**Status: HGX Academy syllabus. Taught by HGX Academy, HgX's own academy.**

## Course description
This course teaches the operation, measurement, reverse engineering, and defensive hardening of open-source hardware systems as a single integrated discipline. Students move from using computing systems to operating them: one Kali Linux system serves as the central platform, REA (Reverse Engineer Anything) serves as the local analysis engine, and twenty open-source hardware devices serve as the sensing, communication, and target systems. Instruction is laboratory-based throughout. Every claim must be supported by an auditable evidence chain: see, document, log, and only then prevent. The course prepares graduates for defensive work in industry and government-adjacent sectors, where the ability to demonstrate a vulnerability and a working defence, with measurement, is the required standard.

## Learning outcomes
On completion, students will be able to:
1. Operate the full Kali Linux tool suite across its families, and select the correct family for a stated measurement or test.
2. Reverse engineer software, firmware, and JavaScript applications locally with REA, and report findings with reproducible evidence.
3. Characterise radio, Bluetooth, RFID/NFC, mesh, and satellite systems using open hardware, and locate a transmitter or device by measurement.
4. Perform side-channel and bus-level analysis of embedded hardware, and propose a defence that is verified by a second measurement.
5. Fuse vision, LiDAR, thermal, and motion sensing into a measured model of a space, and quantify error against ground truth.
6. Design, execute, and defend an end-to-end laboratory exercise, and present it as an evidence pack, a written report, a narrated summary, and a defence brief.
7. Work within explicit consent, controlled-laboratory, and safety constraints, and refuse or stop any test that falls outside them.

## Prerequisites and required equipment
- Engineering background, with non-destructive testing experience preferred. Doctoral-capable level is expected; no prior Kali or REA experience is assumed, but independent laboratory work is required.
- Explicit, documented consent for all face, voice, and biometric exercises. No participant may be enrolled, recorded, or tested without it.
- Student device: M1 iPad Pro with LiDAR, for room scanning and measurement against ground truth.
- Course hardware (all twenty pieces, all delivered, opened, and tested as of 2026-10-29): Flipper Zero + Starter Kit, Mentra Live Camera Glasses, T-Watch S3 Plus Meshtastic, HackRF One, Proxmark3 RDV4, Ubertooth One, ChipWhisperer-Lite, KrakenSDR, T-Beam Meshtastic, OpenMV Cam, GreatFET One, PX4/ArduPilot Drone Kit, Frigate Motion System, Near-IR Night Vision, Thermal MLX90640, SatNOGS Satellite Station, RPLIDAR A1, RPLIDAR A2, RPLIDAR C1, DonkeyCar Rover.
- Platform: Acer laptop, Kali Linux installed once, NVIDIA drivers verified, Kali everything, REA everything, Grokbot, PipeWire voice layer, and the seventeen local-only software stacks (see below).

## Course structure
**Three pillars:** (1) Kali everything. (2) REA everything, local model and local providers. (3) Grokbot, cloud reasoning with local execution.
**Seventeen software stacks, all local-only, in efficient order:** REA first; then quick tools (security-audit-skill sandboxed, Graphify, HyperFrames); then Ollama tools (FreeLLMAPI routed to local Ollama, ai-memory); then heavy GPU separate venvs (ComfyUI); then DeepTutor; then Prism; then Macro Kali only; then Hacking-Tools gaps one by one; then Claude Plugins (requires Claude Code); then VoiceStudio; then GenOffice; then reference libraries last. Total 17 items. Present planned stacks as planned, built stacks as built. (v1.0.0 stated ten stacks; corrected to seventeen in v1.0.1 per HgX's addendum.)
**Project 25:** prove the entire suite. Twenty-one family checkpoints (fifteen core plus GPU, Bluetooth, RFID, SDR, VoIP, and Labs). Each checkpoint requires tool presence, a safe self-test, and saved evidence.

## Syllabus — units M0 to M14, with laboratories L1 to L20
- M0 Laboratory Rules, Consent, and Audit. Foundations: consent, logging, safety, academic integrity.
- M1 Kali Linux and Project 25. Laboratory: L16 (in part, audit preparation).
- M2 Spectrum. Laboratories: L2, L3, L11, L18 (in part).
- M3 Cards and Access Systems. Laboratory: L5 (in part).
- M4 Bluetooth. Laboratories: L10, L18 (in part).
- M5 Chips and Side Channels. Laboratories: L5 (in part), L12.
- M6 Mesh Systems. Laboratories: L2, L3, L8, L13, L17 (in part).
- M7 Vision and Sensing. Laboratories: L1, L4, L14.
- M8 Hardware Bridging and Reverse Engineering. Laboratories: L5 (in part), L9.
- M9 Brain, Voice, and Local Intelligence. Laboratories: L6, L15, L19.
- M10 Capstone Preparation. Evidence pack, report, narration, defence brief.
- M11 Aerial Systems. Laboratories: L7, L13.
- M12 Motion and Night Sensing. Laboratory: L4 (in part).
- M13 Space and Mapping. Laboratories: L1 (in part), L7 (in part), L17.
- M14 Prompt-Injection Defense. Documented catalog: STACK-12-DOCUMENTED-CATALOG.md. Laboratories: synthetic, benign prompt-injection exercises E-P1 to E-P6 (see Prevent Module). Lab only, own local Acer models only, Muse excluded, no prompt text in course load.
- Year expansion (DRAFT, NOT FINAL, 2026-10-30): Labs L21-L50, Hardware H21-H30, buffer / audits / inspections, Toronto holidays, weather / airfield / farm venues, homework / lecture notes / Graphify / Image / Cartographer sections — see OPERATOR-PRIME-YEAR-EXPANSION-DRAFT.md. Course still building, many more labs / modules / stacks to come.
- Capstone: L20 Operator Olympics. All twenty hardware pieces, team challenges, scored on evidence quality, not speed alone.
Full laboratory specifications are in OPERATOR-PRIME-LABS.md. Laboratories are completed in order, one at a time, with a gate per laboratory. A laboratory is not complete until its evidence is filed.

## Assessment
Assessment is evidence-based. No laboratory passes on assertion alone.
- Evidence pack: 40 percent. One folder per laboratory, with checklist, raw outputs, measurements, and logs.
- Written report (GenOffice): 25 percent. Findings, method, error analysis, and defence, with tracked revisions.
- Narrated summary (VoiceStudio): 15 percent. Clear, professional narration of method and result.
- Defence brief and capstone defence: 20 percent. Presentation of the capstone, including a defence that is verified by re-measurement.
A failed gate is resubmitted until it passes. No mark is awarded for a fabricated, incomplete, or unverifiable result.

## Policies
- Controlled laboratory only. All tests use devices, tags, networks, and targets owned by the course or the student, or explicitly authorised in writing.
- Face, voice, and biometric work is restricted to consenting adult participants, in the laboratory only, for defensive education. Templates and recordings remain in the laboratory and are deleted after the exercise.
- Radio transmission is restricted to the student's own authorised frequencies and devices. Drone operation is restricted to a safe, controlled flying area, subject to Transport Canada rules. Lasers are Class 1 only.
- Open-source hardware is the required standard for course targets, because a target that cannot be inspected cannot be honestly audited.
- Academic integrity: all evidence must be the student's own laboratory work, with sources, tools, versions, and commands recorded. Fabricated evidence is a failure of the laboratory, not a technical error.

## Resources
Platform documentation: Kali Linux, REA (morluto/rea, rea.tools, npm rea-agents), and the seventeen stacks, each used locally as specified in the course build. Published 2026-11-04 on HgX's explicit publication order for 1.0 course material.


---

@basementjarvisu · basementjarvisunleashed@gmail.com
