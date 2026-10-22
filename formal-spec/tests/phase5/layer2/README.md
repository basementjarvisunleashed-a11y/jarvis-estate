# Phase 5, Layer 2 — Security Test Suite: threat → control verification

**Status:** v0.1 · **Date:** 2026-10-22
**Authorized:** HgX's explicit word, 2026-10-22 ~08:01 ET (all three
Phase 5 work layers, sequentially).

Layer 2 tests every **testable** control from `control-matrix.md`
(C-1…C-31) against its threat (T-1…T-28) in the drafts that Layer 1
produced. It follows the Phase 3 Layer 2 pattern: `estate.py` is an
independent, test-side reimplementation of the v0.1 drafts; the tests
assert the model refuses what the drafts say it must refuse.

## Layout

| File | Family | Threats | Controls |
|---|---|---|---|
| `estate.py` | The estate model under test (sessions, approvals, capabilities, artifacts, evidence, tools, router, connectors, custody, planes, attention) | — | — |
| `test_spoofing.py` | Spoofing | T-1, T-2, T-4 | C-1…C-9, C-29 |
| `test_tampering.py` | Tampering | T-5, T-6, T-7, T-8, T-13, T-22 | C-10, C-11, C-12, C-13, C-16, C-22, C-23, C-24 |
| `test_repudiation.py` | Repudiation | T-9 | C-21, C-30 |
| `test_disclosure.py` | Disclosure | T-10, T-11, T-12 | C-14, C-15, C-27 (least-privilege part) |
| `test_dos_fatigue.py` | DoS / fatigue | T-14…T-17, T-23, T-24 | C-17, C-18, C-19, C-25, C-26 |
| `test_honest_limits.py` | Honest limitations (Q5) | T-26 (L), T-28 (L) | C-28; §5 L0 compensations |
| `test_elevation.py` | Elevation of privilege | T-18…T-21 | C-27, C-31 (mechanical part) |
| `review-procedure.md` | C-20's verification method (human review procedure) | T-27 (L) | C-20 |
| `run.sh` | Runner: runs everything, writes dated evidence logs | — | — |

Every test file documents what it checks, the threat ID (T-n) and
control ID (C-n) it verifies, and the draft section it cites.

## How to run

From this directory:

```bash
./run.sh
```

Writes to `tests/phase5/evidence/`:

- `<date>-phase5-layer2.log` — full verbose unittest output
- `<date>-phase5-layer2-rejections.log` — every refusal, with cause
- `<date>-phase5-layer2-summary.txt` — pass/fail per family

Python 3 stdlib only. Deterministic: fixed virtual clocks, hand-built
cases, no randomness, no network, no git, no publishing. The suite
touches nothing under `spec/` or `contracts/` — the ratified files
stay read-only.

## Honesty marks (what this suite does NOT claim)

- **C-20 (attention budget, human review).** Non-mechanically-
  testable by its own draft. `review-procedure.md` documents the
  verification method; `test_dos_fatigue.py::
  TestAttentionBudgetReviewProcedure` verifies the procedure exists,
  states thresholds as operational judgment (never a modeled fatigue
  curve), and that the budget log it reviews is exportable. The suite
  verifies the *verification method*, not the control.
- **C-31 (doctrinal part).** `test_elevation.py::
  TestCustodyBoundaries` unit-tests the mechanical crossing rules
  (exact-approval shape, single-use, sealed boundaries). The
  doctrinal part — enforcement by discipline plus HgX's word — is
  honestly non-mechanically-testable; its verification is change-
  control discipline and periodic review (control-matrix.md §3).
- **The L0 ceiling (T-28).** `TestPlaneViolation` exercises the one
  mechanical enforcement L0 has (cross-plane `PlaneViolation`). The
  suite does not claim a compromised shared runtime, a coerced
  operator, or a side-channel is stopped: those are the named ceiling
  in `threat-catalogue.md` T-28, and the upgrade path is
  `isolation-upgrade-roadmap.md`.
- **The model is a reimplementation, not the build.** These tests
  verify that the *specification as written* refuses the threats as
  named. They do not audit the deployment build's code (that is the
  build's own tests' job) and they do not re-litigate the v0.1
  drafts' open points (P5-OP-1…P5-OP-7), which await HgX's word.

## Refusal causes exercised

`unknown-session`, `enrolling-no-authority`, `revoked-session`,
`expired-session`, `suspended-session`, `suspend-not-operator`,
`terminal-session`, `fake-approval`, `digest-mismatch`,
`approval-replay`, `approval-expired`, `offline-tap-not-approval`,
`unallowlisted-source`, `artifact-digest-mismatch`,
`log-alter-refused`, `memory-write-not-orchestrator`,
`memory-write-no-provenance`, `injected-instruction-in-data`,
`credential-in-context`, `false-success-reported`,
`false-failure-reported` (flagged, not raised),
`unsupported-no-strong-approval`, `unsupported-approval-too-weak`,
`no-proof-no-done`, `packet-digest-mismatch`, `condition-false`,
`capability-expired`, `connector-overreach`,
`silent-by-default` (logged, not raised), `bulk-approval-refused`,
`high-risk-requires-local-auth`, `high-risk-not-exact`,
`attention-budget-exceeded`, `router-denies-loop`,
`no-retry-on-unknown`, `call-budget-exceeded`,
`stale-state-cannot-consequence`, `custody-crossing-refused`,
`money-approval-not-exact`, `money-approval-replay`,
`router-cannot-approve`, `router-cannot-spend`,
`client-cannot-orchestrate`, `health-sealed`, `research-sealed`,
`location-not-custodian`, `privacy-property-asserted`,
`plane-violation`, `component-not-asserted`.
