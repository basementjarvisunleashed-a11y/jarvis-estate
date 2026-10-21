# Phase 2 — Router Invariant Deferral Record

**Decision:** INV-R2, INV-R3, INV-R4 are UNCOVERED BY DESIGN in Phase 2.
**Written:** 2026-10-21 (HgX's order — close the Phase 2 gaps with real work).
**This document is what the milestone issue closes against.**

## The invariants

| ID | Statement (ROADMAP.md §5, verbatim) |
|---|---|
| INV-R2 | repeated identical error triggers escalation or path change |
| INV-R3 | repeated no-progress action denied |
| INV-R4 | fresh cache may suppress refetch when sufficient |

## Why they cannot be tested at contract level

Phase 2 verifies invariants against contracts, the TLA+ state machine, and
reference models. The router is estate *runtime*: its behaviour (error
repetition counting, no-progress detection, cache sufficiency judgement)
exists only in the running usage-router (`~/workspace/usage-router/`), not
in any contract artifact. There is no router contract in this repository —
`spec/router-policy.md` is a Phase 6 artifact (ROADMAP.md §9), and the
router's shadow/replay evaluation is Phase 6's entire programme.

A contract-level "test" of R2/R3/R4 would test a fiction: a reference model
invented for the occasion, asserting against itself. Phase 2's doctrine is
"no proof, no done" — an invented proof is worse than an honest gap.

## What Phase 6 will provide

- `spec/router-policy.md` — the normative router contract.
- Shadow/replay evaluation against live low-risk tasks (ROADMAP.md §9).
- Behavioural coverage of R2 (escalation on repeated identical error),
  R3 (denial of repeated no-progress actions), R4 (cache suppression
  only when sufficient) — against the real router, not a model.

## Companion invariants (for the record)

- INV-R1 (router recommends path only, never approves consequence) and
  INV-R5 (router fallback preserves safety if external backend fails) are
  exercised at reference level in this repository (Layer 2/3 harness);
  their full runtime proof likewise belongs to Phase 6.

## Sign-off

**Deferred by design — HgX's standing doctrine; Phase 6 owns the proof.**

An uncovered-by-design invariant, documented with its owner and its
proof plan, is not a failure. It is a scheduled proof.
