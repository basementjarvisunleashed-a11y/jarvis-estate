# Invariant Catalogue — Phase 2 (Invariant Verification)

*Opened 2026-10-20 on HgX's order. The 27 invariants of ROADMAP.md §5,
statements verbatim from the roadmap. Doctrine sources are Paper IV v1.1
§8.1/§8.3 (the paper's own catalogue and traceability table), cross-checked
against `contracts/glossary.md` and `contracts/events.md`. Layers are the
verification layers assigned in Paper IV §8.3 (L1 static contract tests,
L2 property-based tests, L3 chaos tests). Status reflects the three
suites as run in the full sweep of 2026-10-20 (Layer 1 re-run 39/39;
Layer 2 PT-1…PT-5; Layer 3 CH-1…CH-10) — evidence in `tests/evidence/`,
summary in `tests/PHASE-2-RUN-REPORT-2026-10-20.md`.*

*"Layer 1 covered" means an executable test in `tests/layer1/` exercises
the invariant against the real artifacts or the guard reference model.
"Partial / structural" means Layer 1 checks the spec-level substrate
(structure or guard text) while the full behavioural check belongs to a
later layer or a runtime artifact. "Pending" means no Layer 1 test exists
yet, with the reason stated.*

## A. Completion

| ID | Statement (ROADMAP §5, verbatim) | Doctrine source | Layers | Status |
|---|---|---|---|---|
| INV-C1 | no completion without evidence packet | Paper IV §8.1; doctrine: "No proof, no done" (Paper I) | L1, L2, L3 | **Layers 1–3 covered** — CT-C1; PT-4; CH-8, CH-10 (completion writer) |
| INV-C2 | no completion if required tests failed | Paper IV §8.1; doctrine: Acceptance discipline (Paper II); `contracts/glossary.md` "Acceptance test" (INV-C1, INV-C2) | L1, L2, L3 | **Layers 1–3 covered** — CT-C2; PT-4; CH-10 |
| INV-C3 | no delegated claim produces completion without verification | Paper IV §8.1; doctrine: Delegation boundary (Paper II); `contracts/glossary.md` "Subagent" / "Delegation boundary" (INV-C3) | L1, L2, L3 | **Layers 1–3 covered** — CT-C3; PT-4; CH-8 |
| INV-C4 | no optimistic UI state overrides authoritative backend state | Paper IV §8.1; doctrine: Rendered contracts only (Paper III); RD-4 (`contracts/glossary.md` "Authoritative") | L1, L3 | **Pending** — no rendering/backend artifact exists in this repository to test; Layer 3 exercised the contract-level rule (authoritative state governs on read) — CH-5; CT-C4 still awaits the front-end contract implementation |
| INV-C5 | completion supported by observed output, not fluent text | Paper IV §8.1; doctrine: Observed output, not narration (Paper I); RD-3 (`contracts/glossary.md`) | L1, L2, L3 | **Layers 1–3 covered** — CT-C5 (structural + guard); PT-4; CH-8 |

## B. Approval

| ID | Statement (ROADMAP §5, verbatim) | Doctrine source | Layers | Status |
|---|---|---|---|---|
| INV-A1 | consequential action cannot execute without approved intent | Paper IV §8.1; doctrine: Consequence boundary (Paper II) | L1, L2 | **Layers 1–2 covered** — CT-A1; PT-4 |
| INV-A2 | approval binds to action, target, effect, scope, revision, expiry | Paper IV §8.1; doctrine: Exact intent (Paper I: approval); Paper IV §5.6 six bound fields | L1, L2 | **Layers 1–2 covered** — CT-A2; PT-1 |
| INV-A3 | changed target/effect invalidates prior approval | Paper IV §8.1; doctrine: Digest binding (Phase 0 spec); `contracts/glossary.md` "Intent digest" (INV-A3) | L1, L2, L3 | **Layers 1–3 covered** — CT-A3; PT-1; CH-3, CH-9 |
| INV-A4 | expired approval unusable | Paper IV §8.1; doctrine: Last safe moment (Paper I); RD-2 / OQ-3 (Paper IV §5.4–§5.5) | L1, L2, L3 | **Layers 1–3 covered** — CT-A4; PT-2; CH-2 |
| INV-A5 | offline approval cannot create authoritative consent | Paper IV §8.1; doctrine: Server-recorded authority (Phase 3); RD-4; `contracts/glossary.md` "Approval decision" (INV-A5) | L1, L3 | **Layers 1 and 3 covered** — CT-A5; CH-1 |
| INV-A6 | duplicate taps must not duplicate execution | Paper IV §8.1; doctrine: Idempotency (Phase 4); Paper III duplicate-tap semantics (`contracts/events.md` §5) | L1, L2, L3 | **Layers 1–3 covered** (machine level) — CT-A6; PT-3; CH-4; full idempotency semantics are Phase 4 |
| INV-A7 | approval cannot authorize adjacent or future actions | Paper IV §8.1; doctrine: No blanket permission (Phase 0 spec) | L1, L2 | **Layers 1–2 covered** — CT-A7; PT-1 |

## C. Evidence

| ID | Statement (ROADMAP §5, verbatim) | Doctrine source | Layers | Status |
|---|---|---|---|---|
| INV-E1 | every completed consequential run has an evidence packet | Paper IV §8.1; doctrine: Proof bundle (Paper I: evidence) | L1, L2 | **Layers 1–2 covered** — CT-E1; PT-4 |
| INV-E2 | evidence packet revision matches artifact revision | Paper IV §8.1; doctrine: Revision binding (Phase 0 spec); `contracts/glossary.md` "Revision" (INV-A2, INV-E2) | L1, L3 | **Pending (schema)** — the schema files still do not exist under `contracts/`; the binding rule itself is covered at Layer 3 by the completion-writer model — CH-5; CT-E2 awaits the schemas |
| INV-E3 | missing evidence renders as missing | Paper IV §8.1; doctrine: Gaps visible (Paper I: honesty) | L1, L3 | **Partial** — Layer 3 covers the packet side (a stale observation must be marked, not omitted) — CH-7; the rendering side still has no artifact in this repository |
| INV-E4 | gaps stay visible | Paper IV §8.1; doctrine: Required gaps field (Paper IV §6.6); `contracts/README.md` (omission of `gaps` is a schema violation — INV-E4) | L1, L3 | **Partial** — Layer 3 covers the rule at the completion writer (a packet missing `gaps` is rejected) — CH-10; the evidence-packet schema file itself is still a planned artifact |
| INV-E5 | sources current where live truth is required | Paper IV §8.1; doctrine: Live-source freshness (Paper I); `contracts/glossary.md` "Stale" (INV-S4) / "Freshness" | L1, L2, L3 | **Layers 1–3 covered** — CT-E5 (structural, spec level); PT-5; CH-7 |

## D. State rendering

| ID | Statement (ROADMAP §5, verbatim) | Doctrine source | Layers | Status |
|---|---|---|---|---|
| INV-S1 | unknown never renders as operational | Paper IV §8.1; doctrine: Forced unknown (Paper IV §7.3); `contracts/events.md` event 12 (INV-S1) | L1, L2, L3 | **Layers 1–3 covered** (machine + contract-renderer level) — CT-S1; PT-5; CH-7; surface rendering remains Paper III |
| INV-S2 | paused never renders as failed | Paper IV §8.1; doctrine: Pause ≠ failure (Paper III); Paper IV §5.6 "Paused state" | L1, L3 | **Partial** — Layer 3 covers the rendering rule at contract level (paused renders as paused, never failed) — CH-1; the Watchtower schema artifact is still absent. Machine-level substrate (PO-5) was proven in Phase 1 |
| INV-S3 | degraded requires observed impairment | Paper IV §8.1; doctrine: Observed impairment (Watchtower); Paper IV §5.6 "Degraded state" | L1 | **Pending** — requires the Watchtower health-signal contract (runtime); no artifact in this repository mechanises it |
| INV-S4 | stale data shows reduced confidence or unknown | Paper IV §8.1; doctrine: Freshness rendering (Paper III); `contracts/glossary.md` "Stale" (INV-S4) | L1, L2, L3 | **Layers 1–3 covered** (structural at L1; behavioural at contract-renderer level) — CT-S4; PT-5; CH-5, CH-7 |
| INV-S5 | shared surfaces never render restricted content | Paper IV §8.1; doctrine: Shared-surface redaction (Paper III); trust boundary 10 (Paper IV §5.6) | L1 | **Pending** — Paper III shared-surface runtime; no artifact in this repository mechanises it |

## E. Router

| ID | Statement (ROADMAP §5, verbatim) | Doctrine source | Layers | Status |
|---|---|---|---|---|
| INV-R1 | router recommends path only, never approves consequence | Paper IV §8.1; doctrine: Router recommends only (Paper II) | L1, L3 | **Partial** — Layer 3 covers the router contract at reference level (recommendation only, never approval) — CH-6; the estate router runtime and `spec/router-policy.md` (Phase 6) are still absent |
| INV-R2 | repeated identical error triggers escalation or path change | Paper IV §8.1; doctrine: Loop guard (router policy) | L1 | **Pending** — router runtime; not yet mechanised in this repository |
| INV-R3 | repeated no-progress action denied | Paper IV §8.1; doctrine: Loop denial (router policy) | L1 | **Pending** — router runtime; not yet mechanised in this repository |
| INV-R4 | fresh cache may suppress refetch when sufficient | Paper IV §8.1; doctrine: Cache licence (router policy) | L1 | **Pending** — router runtime; not yet mechanised in this repository |
| INV-R5 | router fallback preserves safety if external backend fails | Paper IV §8.1; doctrine: Safe fallback (router policy) | L1, L3 | **Partial** — Layer 3 covers the fallback contract at reference level (local policy on backend failure, fallback logged) — CH-6; the runtime is still absent |

## Coverage summary (as of the 2026-10-20 full sweep)

- **Layer 1:** 11 invariants behaviourally covered (INV-C1, C2, C3,
  A1–A7, E1); 4 at structural / machine level (INV-C5, E5, S1, S4).
  Suite re-run 2026-10-20: 39/39 passing.
- **Layer 2 (PT-1…PT-5, all passing):** behavioural coverage added —
  INV-A2, A3, A7 (PT-1 mutation fuzz, 900 mutated intents); INV-A4
  (PT-2 expiry sweep, 3,000 samples); INV-A6 (PT-3 duplicate storm,
  120 intents); INV-C1–C3, C5, A1, E1 (PT-4, 2,000 random sequences,
  56,261 attempted steps); INV-E5, S1, S4 (PT-5 stale injection).
  53,079 generator attempts were refused and logged by guard
  (`tests/evidence/2026-10-20-layer2-rejections.log`).
- **Layer 3 (CH-1…CH-10, all passing at contract level):** scenario
  coverage added — INV-A5, S2-rule (CH-1); A4 (CH-2); A3 (CH-3, CH-9);
  A6 (CH-4); C1, C2, C3, C5 (CH-8, CH-10); E3-packet, E5, S1, S4
  (CH-7); contract-level equivalents for INV-C4, E2, E4, R1, R5.
- **Still pending on named artifacts:** INV-C4 (front-end contract),
  INV-E2 / E4 (evidence-packet and artifact-manifest schema files —
  their rules are covered at the completion-writer level), INV-S3
  (Watchtower health-signal contract), INV-S5 (Paper III shared
  surfaces), INV-R1–R5 (usage-router runtime / `spec/router-policy.md`,
  owned by Phase 6; R1 and R5 contracts exercised at reference level).
- **Phase 2 remains OPEN.** The layer gates (PHASE-2-PLAN) also
  require the missing contract artifacts to exist and be covered, and
  Paper IV §8.4 requires the suites in CI / on schedule and runnable
  by third parties. See `tests/PHASE-2-RUN-REPORT-2026-10-20.md`.
