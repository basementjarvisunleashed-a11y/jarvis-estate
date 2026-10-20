# Phase 2 — Invariant Verification: Opening Note

*Phase opened 2026-10-20 on HgX's direct order ("start the next phase of
our roadmap"). Phase definition: ROADMAP.md §5; programme treatment:
Paper IV v1.1 §8. This note records the objective, the entry criteria as
verified at opening, the scope, the verification layers, the exit
criteria, and the status of every deliverable at opening.*

## Objective

Convert architectural promises into executable invariants (ROADMAP.md
§5): every core doctrine statement of the estate becomes a property a
test can fail — first as static contract tests over the ratified
specification artifacts, then as generated property tests, then as chaos
tests against running work items.

## Entry criteria — verified at opening

| Criterion | Evidence |
|---|---|
| Phase 0 contracts ratified | `contracts/events.md` v1.0.0 — RATIFIED by HgX 2026-10-19 (decision D2); `contracts/glossary.md` v1.0.0 normative; governance in `contracts/README.md` |
| Phase 1 proven | Closed 2026-10-19. TLC model-checked `spec/state-machine.tla`: **3,266,929 distinct states explored, zero invariant violations**, after six genuine spec bugs were found via counterexamples and fixed (`proofs/phase1-tlc-report.md`). The report's own caveat stands: the finite instance (Actions = 2, MaxNow = 6, Δ = 60s) was explored as a deep BFS prefix, not exhausted; PO-12 (liveness) was out of scope, and PO-3/PO-9/PO-10 were spot-checked rather than exhaustively checked — which is part of what this phase's suites are for |
| Proof language and digest rule settled | TLA+ ratified (D1); intent digest = SHA-256 over canonical JSON (U-1); clock-skew bound Δ = 60s (U-5/D7) |

## Scope — the 27 invariants (ROADMAP.md §5)

- **Completion** — INV-C1…C5
- **Approval** — INV-A1…A7
- **Evidence** — INV-E1…E5
- **State rendering** — INV-S1…S5
- **Router** — INV-R1…R5

Full statements, doctrine sources, layer assignments, and per-invariant
status: `tests/invariant-catalogue.md`.

## Verification layers (ROADMAP.md §5; Paper IV §8.2)

- **Layer 1 — Static contract tests.** Schema/contract validation and
  guard semantics over the ratified artifacts: unknown enums fail closed;
  missing fields fail; expired approvals fail; mutated digests fail;
  incomplete evidence cannot produce completion.
- **Layer 2 — Property-based tests.** Generated event sequences and
  adversarial inputs asserting the invariants (PT-1…PT-5 in Paper IV
  §8.2: approval mutation fuzz, expiry sweep, duplicate decision storm,
  random event sequences, stale source injection).
- **Layer 3 — Chaos tests.** Fault injection against running work items
  (CH-1…CH-10 in Paper IV §8.2: offline approval, expiry mid-review,
  intent change after render, duplicate tap, stale source, subagent
  completion without evidence, digest mismatch, missing tests, …).

## Exit criteria (ROADMAP.md §5)

Phase 2 is complete when:

1. Every major doctrine statement has a testable invariant.
2. All tests are automated.
3. Mutated/expired approval cannot pass.
4. Optimistic completion fails tests.
5. The suite is citable as empirical validation.

(Paper IV §8.4 adds: rejection logs archived as evidence; the
traceability matrix complete and current; the suite runnable by third
parties.)

## Deliverable status at opening

| Deliverable (ROADMAP.md §5) | Status at opening |
|---|---|
| Invariant catalogue | **Done** — `tests/invariant-catalogue.md` (27 invariants, verbatim statements, doctrine sources, layers, status) |
| Contract test suite (Layer 1) | **Done and running** — `tests/layer1/` (Python 3 stdlib `unittest`; parses the real `contracts/events.md` and `spec/state-machine.tla`). Opening run, 2026-10-20: **39 tests, 39 passing, 0 failures** (`python3 -m unittest test_layer1_contracts -v`) |
| Property-based test suite (Layer 2) | **Not started** — PT-1…PT-5 specified in Paper IV §8.2 |
| Chaos test suite (Layer 3) | **Not started** — CH-1…CH-10 specified in Paper IV §8.2 |
| Invariant traceability matrix | **Done** — `tests/traceability-matrix.md` (invariant → doctrine → enforcement/spec artifact → Layer 1 test ID) |

## Layer 1 coverage at opening (honest position)

- **Behaviourally covered (11):** INV-C1, C2, C3, A1, A2, A3, A4, A5, A6,
  A7, E1 — the approval gate and completion gate, exercised against the
  guard reference model and the cross-parsed legal-transition table.
- **Covered at structural / machine level (4):** INV-C5, E5, S1, S4.
- **Pending (12):** INV-C4, E2, E3, E4, S2, S3, S5, R1–R5 — each blocked
  on a named artifact or runtime that does not yet exist in this
  repository (packet/manifest schemas, the Watchtower contract, Paper III
  rendering surfaces, the usage router), as recorded per-invariant in the
  catalogue. None is pending merely for want of a test against an
  existing artifact.

## Constraints observed

No ratified file was modified: nothing under `contracts/`, `spec/`,
`proofs/`, or `ROADMAP.md` was touched by this opening package. All new
material lives under `tests/`. Nothing was published or committed; the
package is local until HgX directs otherwise.
