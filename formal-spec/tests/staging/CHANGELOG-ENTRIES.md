# STAGING — proposed CHANGELOG entries (NOT APPLIED)
One-line entries per proposed version action. Applied only on HgX's word.

- PROOFS: phase1-tlc-report.md v1.0.0 → v1.1-draft — corrected intro count ("five" → "six"), matching the six enumerated counterexample fixes (D-A).
- CONTRACTS: README.md v1.0.0 → v1.1-draft — unresolved-term count corrected ("6" → "3 open: U-2, U-3, U-4"), matching glossary §3's 2026-10-19 ratification record (D-C).
- NOTE (no version action): standing summaries of the retest should read "12,524,558 distinct states, zero violations, killed 2026-10-19 23:43 ET by the pause order" — the 1.79M figure was a 23:05 reading (D-B).
- NOTE (no version action): the seven prescribed-but-unbuilt files (spec/state-machine.md, spec/approval-digest.md, five contract schemas) require HgX's word — build-out or amendment — before any version touches them (D-D).
- NOTE (no version action): vendor tla2tools.jar + Temurin JRE 21.0.12.1 under tools/ with sha256 hashes so the proof toolchain is pinned beside the proof (inventory note).
- TESTS (APPLIED 2026-10-21 ~12:50 ET on HgX's word — Q9): tests/audit_crosscheck.py's tests-md-phase1-citations check now accepts run-attributed citations (a figure attributed to its run/log in the same or previous line), accepts "0" alongside "zero" for invariant violations, and excludes version-number false positives ("v1.1 fixes"). 12/12 checks pass (log: tests/evidence/2026-10-21-crosscheck-v2.log). Working artifact, not ratified.
