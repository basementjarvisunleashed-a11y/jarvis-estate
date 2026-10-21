# Phase 2 — Third-Party Runbook

**Purpose:** a third party (doctoral committee, reviewer, auditor) can reproduce
every Phase 2 result from a clean checkout. No Muse, no estate access, no
credentials required. (Paper IV §8.4 phase-level gate: third-party runnability.)
**Written:** 2026-10-21 (HgX's order).

## 1. Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | stdlib only — no pip packages needed anywhere in `tests/` |
| Java | 21 (Temurin 21.0.12.1+1 recommended) | Only for the TLC model-check rerun (Phase 1 artifact, optional here) |
| `tla2tools.jar` | v1.7.4 (TLC 2.19) | Only for the TLC rerun; pinned under `tools/` in the workspace |

Verify: `python3 --version` → 3.11 or newer. That's the whole dependency list
for every Phase 2 suite.

## 2. Run every suite

From the repository root (`jarvis-estate/formal-spec/`):

```sh
# Layer 1 — static contract tests (39) + schema example tests (25)
#          + rendering invariant tests (19) = 83 tests
cd tests/layer1
python3 -m unittest test_layer1_contracts -v
python3 -m unittest test_schema_examples -v
python3 -m unittest test_rendering_invariants -v
# or: ./run.sh   (runs test_layer1_contracts)

# Layer 2 — property-based tests (10 properties)
cd ../layer2
python3 -m unittest test_layer2_properties -v
# or: ./run.sh

# Layer 3 — chaos tests (10 scenarios)
cd ../layer3
python3 -m unittest test_layer3_chaos -v
# or: ./run.sh

# Cross-artifact consistency audit (12 checks)
cd ..
python3 audit_crosscheck.py
```

## 3. Expected counts (as of 2026-10-21)

| Suite | Command | Expected |
|---|---|---|
| Layer 1 contract | `python3 -m unittest test_layer1_contracts` | **39/39 OK** |
| Layer 1 schema examples | `python3 -m unittest test_schema_examples` | **25/25 OK** |
| Layer 1 rendering invariants | `python3 -m unittest test_rendering_invariants` | **19/19 OK** |
| Layer 2 property-based | `python3 -m unittest test_layer2_properties` | **10/10 OK** |
| Layer 3 chaos | `python3 -m unittest test_layer3_chaos` | **10/10 OK** |
| Crosscheck | `python3 audit_crosscheck.py` | **12/12 checks passed** |

State the counts exactly as the runner prints them — no rounding, no
paraphrase into percentages. Any deviation is a finding, not noise.

## 4. How to read a failure

- A failing `test_*` name encodes its invariant: `test_r_e3_02` = rendering
  test, INV-E3, case 2; `SCH-EP-03` = schema test, evidence-packet, case 3;
  `CT-A4` = contract test, INV-A4; `PT-4` = property test 4; `CH-7` = chaos
  scenario 7.
- Every test asserts the REJECTION (fail closed): a failure means the
  reference model *accepted* something it must refuse, or rendered
  something it must not render.
- The crosscheck names its check (`tests-md-phase1-citations`, etc.) and
  prints the offending file and line.

## 5. Where the evidence lives

- Raw logs: `tests/evidence/2026-10-2*.log` — dated, one per suite per run.
- Run reports: `tests/PHASE-2-RUN-REPORT-2026-10-20.md`,
  `tests/PHASE-2-RUN-REPORT-2026-10-21.md` (the committee-facing one).
- History: `tests/PHASE-2-HISTORY.md` (every session, sourced).
- Open questions and answers: `tests/PHASE-2-OPEN-QUESTIONS.md`.
- Traceability: `tests/traceability-matrix.md` (invariant → doctrine → test).

## 6. Optional: re-run the Phase 1 TLC proof

```sh
cd spec
java -Xmx4G -XX:+UseParallelGC -cp ../tools/tla2tools.jar \
  tlc2.TLC -workers 4 -deadlock -checkpoint 30 StateMachine
```

Expected: 3,266,929 distinct states, zero invariant violations
(`proofs/phase1-tlc-report.md` v1.1). The exhaustive retest checkpoint
`states/26-10-19-21-56-17` resumes only on HgX's word.

## 7. Known limitations (honest list)

- INV-R2/R3/R4 are uncovered BY DESIGN in Phase 2 — see
  `tests/PHASE-2-ROUTER-DEFERRAL.md` (router is estate runtime; Phase 6
  owns the proof).
- CH-5/CH-6 run at contract level only (Paper III client/router artifacts
  are Phase 4/6 work).
- The crosscheck's `tests-md-phase1-citations` accepts run-attributed
  figures (a figure naming its run/log) — see the Q9 decision in
  `tests/PHASE-2-OPEN-QUESTIONS.md`.
