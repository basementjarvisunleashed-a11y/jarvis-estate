# Phase 0 + Phase 1 — Backtrace Manifest
## Evidence stress test ordered by HgX 2026-10-20 23:51 ET · filed 2026-10-21 (before the 02:12 ET deadline)

Read-only pass: no ratified file was modified. sha256 below is over full
file bytes at inventory time. mtime is America/Toronto.

## A. Inventory — 18 files, all present, none missing

| File | Bytes | mtime (ET) | sha256 (prefix) | Role |
|---|---|---|---|---|
| contracts/glossary.md | 45736 | 2026-10-19 20:32 | 4b86018784b06ba4 | 69 terms §1 (counted: 69 term bullets), 25 conflicts §2 (counted: 25), 6 open questions §3 |
| contracts/events.md | 21426 | 2026-10-19 20:04 | 39d38b45f77f5f25 | 19 canonical events (cross-validated vs .tla: crosscheck 12/12) |
| contracts/README.md | 10593 | 2026-10-19 21:31 | e69e9a9ce4e1b315 | Contract governance; Phase 0 normative core table; v1.0.0 gate |
| spec/state-machine.tla | 48682 | 2026-10-19 20:28 | 9814c28fae3e8245 | 12 states, 21 transitions (named TLA+ actions), PO/SafetyInvs properties |
| spec/state-machine.cfg | 1073 | 2026-10-19 20:13 | 706dc17c021ab950 | INVARIANTS + PROPERTIES + CHECK_DEADLOCK TRUE |
| spec/Debug.cfg | 174 | 2026-10-19 20:15 | 28cd4f0d94aa4822 | Debug config (Phase 1 working artifact) |
| spec/Debug2.cfg | 172 | 2026-10-19 20:18 | ba3fc2a5ca0d9aa8 | Debug config (Phase 1 working artifact) |
| spec/Debug3.cfg | 194 | 2026-10-19 20:29 | 37840336ea5f7612 | Debug config (Phase 1 working artifact) |
| proofs/phase1-tlc-report.md | 9123 | 2026-10-19 21:15 | 22c2e9bdee1007e7 | Phase 1 proof report (D-A: intro line says "five", enumerates six — see Findings) |
| proofs/tlc-exhaustive-run.log | 7636 | 2026-10-19 22:07 | bbe3b1cb34b03f8c | Exhaustive run: final 4,854,966 distinct states, 0 invariant violations, stopped by HgX's 18:08 ET order |
| proofs/tlc-retest-2026-10-19.log | 15452 | 2026-10-20 03:42 | 58d1e1f0def1bae3 | Retest: 0 violations; attempt 3 recovered checkpoint, reached 12,524,558 distinct states, killed 23:43 ET by pause order (see Findings D-B) |
| phase-0-decision-sheet.md | 3932 | 2026-10-09 16:17 | 001f7169a8b939e0 | Pre-ratification decision sheet (U-1/U-5/U-6 NOT recorded here — see Findings D-E) |
| phase-0-work/paper1.txt | 23275 | 2026-10-19 19:48 | 1cf82614cfbb0063 | Paper I extraction (reconciliation input) |
| phase-0-work/paper2.txt | 36463 | 2026-10-19 19:48 | 950450456296ac9d | Paper II extraction (reconciliation input) |
| phase-0-work/paper3.txt | 37672 | 2026-10-19 19:48 | b8312a472a6953a5 | Paper III extraction (reconciliation input) |
| phase-0-work/paper4.txt | 406811 | 2026-10-19 19:48 | 824cac66c77380f5 | Paper IV extraction (reconciliation input) |
| ROADMAP.md | 29224 | 2026-10-09 00:14 | 720906498b17757c | Programme roadmap (Phase 0/1 definitions §3–§4) |

spec/states/: 22 checkpoint directories. 26-10-19-21-56-17 INTACT
(vars.chkpt present, ~3.5 GB) — the preserved resumable checkpoint.
26-10-19-22-45-19 INCOMPLETE (no vars.chkpt — killed mid-write, as
recorded; not a valid resume point). No other checkpoint inspected.

Missing vs expected (prescribed by contracts/README.md, ROADMAP §0.4,
Paper IV §6.5 — none exist, no amendment on record):
spec/state-machine.md · spec/approval-digest.md ·
contracts/watchtower.schema.json · contracts/evidence-packet.schema.json ·
contracts/approval-intent.schema.json · contracts/decision-packet.schema.json ·
contracts/artifact-manifest.schema.json

## B. Backtrace — one row per claim

| Claim | Evidence file(s) | sha256 prefix | Verdict |
|---|---|---|---|
| Glossary: 69 terms | contracts/glossary.md §1 — 69 term bullets counted | 4b860187 | PRESENT |
| Glossary: 25 conflicts resolved | contracts/glossary.md §2 — 25 conflict entries counted | 4b860187 | PRESENT |
| Glossary: open questions | contracts/glossary.md §3 — 6 entries: U-1, U-5, U-6 RESOLVED 2026-10-19; U-2, U-3, U-4 open (see D-C) | 4b860187 | PRESENT (precision note) |
| Contracts v1.0.0 ratified 2026-10-19 | contracts/README.md ("HgX ratifies (v1.0.0 gate)"); glossary §3 RESOLVED annotations | e69e9a9c / 4b860187 | PRESENT |
| 12 states / 21 transitions / 19 events | spec/state-machine.tla (12 states in state set; 21 named actions) ↔ contracts/events.md (19 events); machine crosscheck tests/audit_crosscheck.py 12/12 | 9814c28f / 39d38b45 | PRESENT |
| U-1 digest = SHA-256 over canonical JSON | contracts/glossary.md:315 RESOLVED 2026-10-19 (HgX) | 4b860187 | PRESENT (implementing artifact spec/approval-digest.md MISSING — see D-D) |
| U-5/D7 clock-skew Δ = 60s | contracts/glossary.md (U-5 RESOLVED 2026-10-19) | 4b860187 | PRESENT |
| U-6 papers stand as historical | contracts/glossary.md (U-6 RESOLVED 2026-10-19) | 4b860187 | PRESENT |
| TLC 3,266,929 states, zero violations | proofs/phase1-tlc-report.md:67 ("zero invariant violations"); tlc-exhaustive-run.log: 0 "Invariant .* violated" | 22c2e9bd / bbe3b1cb | PRESENT |
| Six counterexample fixes | proofs/phase1-tlc-report.md:67/70/76 ("six fixes"; Fix 1–Fix 6 enumerated) | 22c2e9bd | PRESENT (intro wording slip — D-A) |
| Exhaustive partial run 4,854,966 states, 0 violations, stopped by order | proofs/tlc-exhaustive-run.log tail ("4,854,966 dist"); 0 violation matches | bbe3b1cb | PRESENT |
| Retest: checkpoint intact, resumable, paused | proofs/tlc-retest-2026-10-19.log:72 ("Starting recovery from checkpoint states/26-10-19-21-56-17/"); 0 violations; final 12,524,558 distinct at 23:42:56; spec/states/26-10-19-21-56-17 vars.chkpt YES | 58d1e1f0 | PRESENT (D-B: standing summary said "1.79M" — the log says 12.5M; the 1.79M was a 23:05 reading) |
| Retest commands/jar | tools/tla2tools.jar + JAVA_HOME — not in this inventory scope; recorded in estate build notes (Temurin JRE 21.0.12.1 at ~/workspace/tools/) | — | OUT OF SCOPE (see note) |

Note on "tools": tla2tools.jar and the JRE live outside jarvis-formal-spec
(~/workspace/tools/); they are cited in build notes, not versioned with the
phase artifacts. A future version action could vendor them under tools/ with
hashes — proposed in staging.

## C. Re-runs (observed 2026-10-21, before 02:12 ET)

- tests/layer1: `python3 -m unittest test_layer1_contracts` → **Ran 39, OK**
- tests/audit_crosscheck.py → **11/12** — the one failure is
  tests-md-phase1-citations, and it is a TRUE POSITIVE about the check,
  not the figures: the check requires every "N distinct states" citation
  in tests/*.md to equal the Phase 1 report's 3,266,929, but this
  manifest correctly cites three other runs' figures (4,854,966 —
  exhaustive log; 12,524,558 ×2 — retest log; "0 invariant violations"
  — the check only accepts the word "zero"). Each flagged citation is
  attributed to its log in the manifest's own text. Proposed: extend
  the check to accept run-attributed citations (staging note below).
- Full outputs in tests/evidence/2026-10-20-phase01-stress.log.

## D. Findings and proposed version actions

- **D-A — wording slip, proofs/phase1-tlc-report.md:45**: "TLC found **five**
  genuine spec bugs" vs Fix 1–Fix 6 and "six" on lines 67/70/76. Ground
  truth: six. Proposed: report v1.1-draft with line 45 reading "six".
  Draft at tests/staging/phase1-tlc-report-v1.1-draft-L45.md. Needs HgX's
  word (ratified file).
- **D-B — stale standing summary**: estate summaries say the retest was
  "killed at 1.79M states"; the log's last progress line (23:42:56 ET)
  reads 12,524,558 distinct states found, zero violations. The 1.79M was a
  23:05 reading. The log supports a stronger record than the summary.
  No file change needed — flag to parent to correct the standing summary.
- **D-C — precision, contracts/README.md:18**: "69 normative term
  definitions, 25 vocabulary conflicts with resolutions, 6 terms flagged
  unresolved" — glossary §3 records U-1/U-5/U-6 RESOLVED 2026-10-19,
  leaving U-2/U-3/U-4 open. Proposed: README v1.1-draft line reading
  "…25 vocabulary conflicts with resolutions, 3 open questions (U-2,
  U-3, U-4); 3 resolved at ratification (U-1, U-5, U-6)". Draft at
  tests/staging/contracts-README-v1.1-draft-L18.md. Needs HgX's word.
- **D-D — prescribed files never built**: the seven files in §A's
  missing list are promised by contracts/README.md and Paper IV but do
  not exist; no amendment decision on record. NOT a draft fix — the
  build-out (Phase 2 layer work) or an explicit amendment must decide.
  Needs HgX's word.
- **D-E — decision sheet predates ratification**: U-1/U-5/U-6 live in
  glossary.md §3 (RESOLVED 2026-10-19), not in phase-0-decision-sheet.md
  (2026-10-09). Not a defect — recorded so the sheet is not mistaken
  for the decision record.
- **D-F — checkpoint hygiene**: spec/states/26-10-19-22-45-19 is an
  incomplete checkpoint (killed mid-write). Harmless — the valid resume
  point is 26-10-19-21-56-17 (intact). Proposed: note in a future
  checkpoints README; not a version action.

Version law (VERSIONING.md): v0.x.x = draft, v1.0.0 = ratified; versions
only move forward. Staging drafts are labelled per the law and are NOT
applied to the originals — each needs HgX's explicit word.
