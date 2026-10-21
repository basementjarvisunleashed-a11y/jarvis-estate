# Phase 4 Layer 3 — adversarial chaos

Python 3 stdlib only. No network, no git, no publishing.

## Families

- **NL** (`test_netloss.py`, 5 tests) — network loss mid-execution via a
  severable `ChaosLink`: severed links yield `execution_unknown`, never
  silent completion; reconnect + verify-absent → one safe retry;
  reconnect + verify-present → no refire; flapping links still converge
  on one record.
- **AD** (`test_adversarial_duplicates.py`, 5 tests, 12 interleavings) —
  racing duplicate execution requests, duplicate approvals, replayed
  requests, execute-vs-cancel races: every permutation on a fresh
  fixture — at-most-once and one-record hold in all of them.
- **AX** (`test_ambiguous_chaos.py`, 5 tests) — ambiguous outcomes under
  chaos: opaque tools become visible unknowns (one hint each);
  mixed-outcome scripts resolve per kind; definitive failures retry
  safely (RF7) without duplicating; a 12-key sweep holds every
  invariant.

## Driver

`chaos.py` — `ChaosLink` (severable request/receipt path),
`run_interleavings` (systematic permutation enumeration, fresh fixture
per order), the chaos invariants `assert_at_most_once` and
`assert_visible_unknown_or_settled`.

## Running

From this directory: `./run.sh`
