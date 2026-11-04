# J.A.R.V.I.S. — OPERATOR PRIME Course Material
**J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System)** — public identity, first and prominent.
Operator: HgX (small). Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

> **DISCLAIMER — READ FIRST:** This is NOT an official University of Toronto calendar entry, course code, or accreditation. No university approval, blessing, government approval, or federal approval is claimed as verified. Any approval statement in this material is HgX's statement only, not independently verified. Do not invent a course code or claim accreditation.

> **STATUS: DRAFT v0.1.0 — REA app teardown draft. Lab only, own targets only.**

> **Audience and hard rules:** Consenting adults only. Controlled laboratory only. Own devices, own tags, own networks, own targets only. Spine: SEE → DOCUMENT → LOG → PREVENT. Face work only on consenting adult participants, in the lab only, for defensive education. Templates stay in the lab, deleted after the exercise. Never family, never his son, never strangers, never real-world surveillance or deployment. Radio transmit only on own authorised frequencies. Drone only in a safe, controlled flying area, Transport Canada rules first. Lasers Class 1 only.

> **Licence:** Course text CC-BY-4.0. Code MIT. © HGX Engineering. No secrets in public. No personal data: no real names, no Wi-Fi names, no home addresses, no serials, no passwords, no credentials, no live location, no family details, no financial details. No 2.0/3.0 material. No prompt text reproduced.

---

# REA App Teardown — Draft Workflow (from research note sent 2026-10-30)
**Source: screenshot sent by HgX, 2026-10-30 12:15 ET. Header: "RESEARCH NOTE · SEE WHAT AN APP SHIPS BEFORE IT LAUNCHES · ONE FREE MCP · FOR AI AGENTS". Footer attribution in the image: prompt by @gyome1_. Teardown workflow is the note author's, not written or endorsed by the REA authors. Status: DRAFT, not yet slotted into OPERATOR PRIME — awaiting HgX's word.**
**Professional standard: this draft contains no informal or entertainment references.**

## What the note does, in one line
Diff two builds of the same app, legally installed, and answer one question: what has shipped in the code that users cannot see yet?

## Workflow, summarised (not a verbatim copy of the note)
1. Setup: install with `npx rea-agents setup`, restart the agent, confirm the MCP server lists its tools. Engines named in the note: JADX, Apktool, ADB, Ghidra, plus Hopper, IDA, Rizin, Electron, .asar, .apk, .ipa, WASM, Frida as target tags.
2. Pick a target: two builds, same app, same platform. Record version and hash for both. No hash, no diff.
   - Test phone: list ADB devices, pull the package.
   - Android .apk: inspect the Android package.
   - Electron directory or .asar: analyse the JavaScript application.
   - Web app or bundle: analyse the web bundle.
   - Native .exe / ELF / Mach-O: open the binary.
3. Diff strings: run string listing on both builds, keep only what is new. New UI copy, new screens, layouts, icons, deep links, and new endpoints (/v2/, /beta/, /labs/, /experiments/) are the loudest leaks. Removed strings matter too: what is being killed.
4. Diff code: strings point, code confirms. Decompile only the new classes, not everything. Changed functions near a new string are live work. New manifest permissions (camera, microphone, NFC, location) indicate the hardware the feature needs.
5. Flags: find switches behind feature names (flag, feature_, enable_, experiment, rollout, kill_switch, gate, variant, holdout, is_internal). For each flag, find references to the name, then the screen it gates. A flag with no screen is a promise, not a feature. Record default value and who decides it: local or server.
6. Trace, for the three strongest leaks only: procedure callers from the new string up to the gate that hides it; procedure pseudo-code on that gate (who sees it first: country, plan, employee, percentage rollout); procedure callees down (what it calls, which new endpoint it hits).
7. Confidence, before writing up: shipped = wired UI + string + flag + endpoint; building = some pieces exist, not connected; rumour = one string, nothing calls it. Never present "building" as "launching next week".
8. Evidence: one row per leak in the ledger (feature, strings, flag, gate rule, endpoint, confidence, build hash, evidence id). Bookmark each call site. Ship with an evidence bundle export. No evidence, no claim.
9. Handoff: return the leak sheet ranked by confidence, the string diff, the flag map, the open unknowns, and the next build to watch. Another agent resumes from the ledger, not from memory.

## Boundaries in the note (already aligned with this course)
Read-only, never unlock. Do not flip flags, fake a plan, or call unreleased endpoints. No DRM, licence, or anti-cheat bypass. Do not repost proprietary art or code. Analyse only software you are authorised to inspect. Stop when every new string is explained or the rest needs a human.

## Two points to resolve before slotting this into OPERATOR PRIME
1. Version variance: the note footer states REA rea-agents 6.7.0, 130+ tools. The estate record pins rea-agents 6.8.0, and an earlier ~260-tool figure remains unverified. The authoritative count on any box is `rea doctor --json` on that box. Do not teach a tool count from this note alone.
2. Provider visibility: the note states results are seen by your AI provider. That conflicts with the course local-only doctrine if a cloud model is used. In OPERATOR PRIME, this workflow must run with a local model (local Ollama) unless HgX orders otherwise for a specific, authorised target, with that visibility stated in the lab record.

## Proposed fit, pending HgX's word
- Primary: L9 Firmware Glass-Box Cinema (REA analysis, evidence ledger, presentation from evidence) and L5 Card-to-Chip Full Chain (evidence chain, before-and-after verification).
- Alternative: a new standalone teardown unit inside M8 Bridge and Reverse Engineering, using this workflow as the unit prompt.
- Not a run: no target app, no builds, and no hash have been supplied, so no teardown has been executed from this note.


---

@basementjarvisu · basementjarvisunleashed@gmail.com
