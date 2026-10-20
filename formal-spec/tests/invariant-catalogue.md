# Invariant Catalogue — Phase 2 (Invariant Verification)

*Opened 2026-10-20 on HgX's order. The 27 invariants of ROADMAP.md §5,
statements verbatim from the roadmap. Doctrine sources are Paper IV v1.1
§8.1/§8.3 (the paper's own catalogue and traceability table), cross-checked
against `contracts/glossary.md` and `contracts/events.md`. Layers are the
verification layers assigned in Paper IV §8.3 (L1 static contract tests,
L2 property-based tests, L3 chaos tests). Status reflects the Layer 1
suite in `tests/layer1/` as run on 2026-10-20 (39 tests, all passing).*

*"Layer 1 covered" means an executable test in `tests/layer1/` exercises
the invariant against the real artifacts or the guard reference model.
"Partial / structural" means Layer 1 checks the spec-level substrate
(structure or guard text) while the full behavioural check belongs to a
later layer or a runtime artifact. "Pending" means no Layer 1 test exists
yet, with the reason stated.*

## A. Completion

| ID | Statement (ROADMAP §5, verbatim) | Doctrine source | Layers | Status |
|---|---|---|---|---|
| INV-C1 | no completion without evidence packet | Paper IV §8.1; doctrine: "No proof, no done" (Paper I) | L1, L2, L3 | **Layer 1 covered** — CT-C1 |
| INV-C2 | no completion if required tests failed | Paper IV §8.1; doctrine: Acceptance discipline (Paper II); `contracts/glossary.md` "Acceptance test" (INV-C1, INV-C2) | L1, L2, L3 | **Layer 1 covered** — CT-C2 |
| INV-C3 | no delegated claim produces completion without verification | Paper IV §8.1; doctrine: Delegation boundary (Paper II); `contracts/glossary.md` "Subagent" / "Delegation boundary" (INV-C3) | L1, L2, L3 | **Layer 1 covered** (guard level) — CT-C3 |
| INV-C4 | no optimistic UI state overrides authoritative backend state | Paper IV §8.1; doctrine: Rendered contracts only (Paper III); RD-4 (`contracts/glossary.md` "Authoritative") | L1, L3 | **Pending** — no rendering/backend artifact exists in this repository to test; CT-C4 awaits the front-end contract implementation |
| INV-C5 | completion supported by observed output, not fluent text | Paper IV §8.1; doctrine: Observed output, not narration (Paper I); RD-3 (`contracts/glossary.md`) | L1, L2, L3 | **Layer 1 covered** (structural + guard) — CT-C5; full sequence-level check is PT-4 |

## B. Approval

| ID | Statement (ROADMAP §5, verbatim) | Doctrine source | Layers | Status |
|---|---|---|---|---|
| INV-A1 | consequential action cannot execute without approved intent | Paper IV §8.1; doctrine: Consequence boundary (Paper II) | L1, L2 | **Layer 1 covered** — CT-A1 |
| INV-A2 | approval binds to action, target, effect, scope, revision, expiry | Paper IV §8.1; doctrine: Exact intent (Paper I: approval); Paper IV §5.6 six bound fields | L1, L2 | **Layer 1 covered** — CT-A2 |
| INV-A3 | changed target/effect invalidates prior approval | Paper IV §8.1; doctrine: Digest binding (Phase 0 spec); `contracts/glossary.md` "Intent digest" (INV-A3) | L1, L2, L3 | **Layer 1 covered** — CT-A3 |
| INV-A4 | expired approval unusable | Paper IV §8.1; doctrine: Last safe moment (Paper I); RD-2 / OQ-3 (Paper IV §5.4–§5.5) | L1, L2, L3 | **Layer 1 covered** — CT-A4 |
| INV-A5 | offline approval cannot create authoritative consent | Paper IV §8.1; doctrine: Server-recorded authority (Phase 3); RD-4; `contracts/glossary.md` "Approval decision" (INV-A5) | L1, L3 | **Layer 1 covered** — CT-A5 |
| INV-A6 | duplicate taps must not duplicate execution | Paper IV §8.1; doctrine: Idempotency (Phase 4); Paper III duplicate-tap semantics (`contracts/events.md` §5) | L1, L2, L3 | **Layer 1 covered** (machine level) — CT-A6; full idempotency semantics are Phase 4 |
| INV-A7 | approval cannot authorize adjacent or future actions | Paper IV §8.1; doctrine: No blanket permission (Phase 0 spec) | L1, L2 | **Layer 1 covered** (binding mechanism) — CT-A7; fuzz coverage is PT-1 |

## C. Evidence

| ID | Statement (ROADMAP §5, verbatim) | Doctrine source | Layers | Status |
|---|---|---|---|---|
| INV-E1 | every completed consequential run has an evidence packet | Paper IV §8.1; doctrine: Proof bundle (Paper I: evidence) | L1, L2 | **Layer 1 covered** — CT-E1 |
| INV-E2 | evidence packet revision matches artifact revision | Paper IV §8.1; doctrine: Revision binding (Phase 0 spec); `contracts/glossary.md` "Revision" (INV-A2, INV-E2) | L1, L3 | **Pending** — the evidence-packet and artifact-manifest schemas are described in `contracts/README.md` as planned artifacts but do not yet exist as files under `contracts/`; CT-E2 awaits them |
| INV-E3 | missing evidence renders as missing | Paper IV §8.1; doctrine: Gaps visible (Paper I: honesty) | L1, L3 | **Pending** — rendering + packet-schema property; no artifact in this repository mechanises it yet |
| INV-E4 | gaps stay visible | Paper IV §8.1; doctrine: Required gaps field (Paper IV §6.6); `contracts/README.md` (omission of `gaps` is a schema violation — INV-E4) | L1, L3 | **Pending** — the `gaps` field is a property of the evidence-packet schema, which does not yet exist as a file under `contracts/`; CT-E4 awaits it |
| INV-E5 | sources current where live truth is required | Paper IV §8.1; doctrine: Live-source freshness (Paper I); `contracts/glossary.md` "Stale" (INV-S4) / "Freshness" | L1, L2, L3 | **Layer 1 covered** (structural, spec level) — CT-E5; behavioural injection is PT-5 / CH-7 |

## D. State rendering

| ID | Statement (ROADMAP §5, verbatim) | Doctrine source | Layers | Status |
|---|---|---|---|---|
| INV-S1 | unknown never renders as operational | Paper IV §8.1; doctrine: Forced unknown (Paper IV §7.3); `contracts/events.md` event 12 (INV-S1) | L1, L2, L3 | **Layer 1 covered** (machine level: single keyed exit from `unknown`) — CT-S1; rendering aspect is PT-5 / CH-7 |
| INV-S2 | paused never renders as failed | Paper IV §8.1; doctrine: Pause ≠ failure (Paper III); Paper IV §5.6 "Paused state" | L1, L3 | **Pending** — a rendering rule over the Watchtower contract enum (`operational \| paused \| degraded \| unknown`); the schema artifact is not present as a file under `contracts/`. Machine-level substrate (PO-5) was proven in Phase 1 |
| INV-S3 | degraded requires observed impairment | Paper IV §8.1; doctrine: Observed impairment (Watchtower); Paper IV §5.6 "Degraded state" | L1 | **Pending** — requires the Watchtower health-signal contract (runtime); no artifact in this repository mechanises it |
| INV-S4 | stale data shows reduced confidence or unknown | Paper IV §8.1; doctrine: Freshness rendering (Paper III); `contracts/glossary.md` "Stale" (INV-S4) | L1, L2, L3 | **Layer 1 partial** (structural: freshness guards and re-read discipline in the spec) — CT-S4; the rendering itself is PT-5 / CH-5 |
| INV-S5 | shared surfaces never render restricted content | Paper IV §8.1; doctrine: Shared-surface redaction (Paper III); trust boundary 10 (Paper IV §5.6) | L1 | **Pending** — Paper III shared-surface runtime; no artifact in this repository mechanises it |

## E. Router

| ID | Statement (ROADMAP §5, verbatim) | Doctrine source | Layers | Status |
|---|---|---|---|---|
| INV-R1 | router recommends path only, never approves consequence | Paper IV §8.1; doctrine: Router recommends only (Paper II) | L1, L3 | **Pending** — the usage router is estate runtime, outside this repository; its spec (`spec/router-policy.md`) is a planned artifact owned by Phase 6 |
| INV-R2 | repeated identical error triggers escalation or path change | Paper IV §8.1; doctrine: Loop guard (router policy) | L1 | **Pending** — router runtime; not yet mechanised in this repository |
| INV-R3 | repeated no-progress action denied | Paper IV §8.1; doctrine: Loop denial (router policy) | L1 | **Pending** — router runtime; not yet mechanised in this repository |
| INV-R4 | fresh cache may suppress refetch when sufficient | Paper IV §8.1; doctrine: Cache licence (router policy) | L1 | **Pending** — router runtime; not yet mechanised in this repository |
| INV-R5 | router fallback preserves safety if external backend fails | Paper IV §8.1; doctrine: Safe fallback (router policy) | L1, L3 | **Pending** — router runtime; not yet mechanised in this repository |

## Coverage summary (Layer 1, as of the 2026-10-20 opening run)

- **Covered:** 11 invariants with behavioural Layer 1 tests (INV-C1, C2, C3,
  A1, A2, A3, A4, A5, A6, A7, E1).
- **Covered at structural / machine level:** 4 (INV-C5, E5, S1, S4).
- **Pending:** 12 (INV-C4, E2, E3, E4, S2, S3, S5, R1–R5) — each blocked on
  a named artifact or runtime that does not yet exist in this repository,
  never on an unwritten test against an existing artifact.
- Layers 2 (PT-1…PT-5) and 3 (CH-1…CH-10) are specified in Paper IV §8.2
  and not yet built; every invariant's full layer assignment is in the
  table above.
