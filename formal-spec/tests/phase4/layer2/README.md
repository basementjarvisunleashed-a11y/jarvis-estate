# Phase 4 Layer 2 — protocol tests

Python 3 stdlib only. No network, no git, no publishing.

## Families

- **DT** (`test_duplicate_tap.py`, 7 tests) — duplicate taps: the second
  tap returns the existing decision and state, never a second execution;
  two devices share one key (Q3); key stability and change-isolation
  (K5/K6); execution needs approval (S4).
- **SR** (`test_safe_retry.py`, 6 tests) — safe retry: unsafe retries
  refused without advancing attempt_count (RF4/RF9); verified-absent
  retry still at-most-once (RF7/ER2); revision frozen at BIND keeps the
  key stable (Q2/K2); terminal records return existing (ER5).
- **AB** (`test_ambiguity.py`, 7 tests) — ambiguity: unknowns are never
  silently completed and never auto-retried (AP1/AP2); surfaced on next
  pull with safe options plus a stateless hint (Q4/AP5/AP6); external
  verification resolves (AP3); compensation needs a fresh ceremony
  (Q5/S6); worker intents signed by the orchestrator (Q1/S7); all nine
  record states exercised.

## Model

`idem.py` — the idempotency orchestrator reference model. Reuses the
Phase 3 harness's ratified `approval_digest` (tests/phase3/layer2) —
extended, not duplicated. Deterministic: virtual clock, hand-configured
tool-plane outcomes (`receipt` / `dropped` / `lost` / `failed`), no
randomness.

## Running

From this directory: `./run.sh`
