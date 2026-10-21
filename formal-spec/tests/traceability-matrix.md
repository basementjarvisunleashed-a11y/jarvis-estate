# Invariant Traceability Matrix — Phase 2

*Opened 2026-10-20. One row per invariant: invariant → doctrine source →
enforcement / spec artifact → Layer 1 test ID(s) in `tests/layer1/` where
covered. Extends the doctrine-level matrix of Paper IV §8.3 down to the
mechanised artifacts of this repository. "Runtime — not yet mechanised"
is stated plainly wherever no artifact in this repository enforces the
invariant today.*

| Invariant | Doctrine source | Enforcement / spec artifact | Test(s) — L1 · L2 · L3 |
|---|---|---|---|
| INV-C1 | "No proof, no done" (Paper I); Paper IV §8.1 | `spec/state-machine.tla`: `can_enter_completed` (evidence conjunct), PO1_NoCompletionWithoutEvidence; `contracts/events.md` T15 | CT-C1 · PT-4 · CH-8, CH-10 |
| INV-C2 | Acceptance discipline (Paper II); Paper IV §8.1 | `spec/state-machine.tla`: `can_enter_completed` (`acceptance_passed ∧ ¬failure_observed`); `contracts/glossary.md` "Acceptance test" | CT-C2 · PT-4 · CH-10 |
| INV-C3 | Delegation boundary (Paper II); Paper IV §8.1 | `spec/state-machine.tla`: `can_enter_completed` (no claim input), PO7_NoOptimisticCompletion; `contracts/glossary.md` "Delegation boundary" | CT-C3 · PT-4 · CH-8 |
| INV-C4 | Rendered contracts only (Paper III); RD-4 | Runtime — not yet mechanised (front-end rendering contract; no artifact in this repository) | CH-5 (contract-level equivalent); front-end artifact pending |
| INV-C5 | Observed output, not narration (Paper I); RD-3 | `spec/state-machine.tla`: machine structure — F1/F3 (single road into `completed`, no `executing → completed`), T13/T15 | CT-C5 · PT-4 · CH-8 |
| INV-A1 | Consequence boundary (Paper II); Paper IV §8.1 | `spec/state-machine.tla`: `can_enter_executing`, PO2_NoExecutionWithoutApproval; forbidden F2/F4 | CT-A1 · PT-4 |
| INV-A2 | Exact intent (Paper I: approval); Paper IV §5.6 | `spec/state-machine.tla`: `IntentType` (six bound fields), `DigestOf`; digest rule U-1 (SHA-256 over canonical JSON) | CT-A2 · PT-1 |
| INV-A3 | Digest binding (Phase 0 spec); Paper IV §8.1 | `spec/state-machine.tla`: digest recomputed in `can_enter_executing`; `ServerRecordsApproval` digest equality; `MutateIntent` failure action; PO-3/PO-8 | CT-A3 · PT-1 · CH-3, CH-9 |
| INV-A4 | Last safe moment (Paper I); RD-2 / OQ-3 | `spec/state-machine.tla`: expiry guards in `can_enter_executing` and `ServerRecordsApproval`; `ApprovalExpired` (T10) | CT-A4 · PT-2 · CH-2 |
| INV-A5 | Server-recorded authority (Phase 3); RD-4 | `spec/state-machine.tla`: `tapped` vs `recorded` distinction; `ServerRecordsApproval` is the only writer of `recorded`; PO8_RecordedImpliesServerValidated | CT-A5 · CH-1 |
| INV-A6 | Idempotency (Phase 4); Paper III duplicate-tap semantics | `spec/state-machine.tla`: `DuplicateTap` stutter; T9 note (second grant returns the recorded decision). Full idempotency semantics owned by Phase 4 (`spec/idempotency.md`, planned) | CT-A6 · PT-3 · CH-4 |
| INV-A7 | No blanket permission (Phase 0 spec); Paper IV §8.1 | `spec/state-machine.tla`: approval binds a single intent record via `DigestOf`; a grant for intent X cannot satisfy the guard for intent Y | CT-A7 · PT-1 |
| INV-E1 | Proof bundle (Paper I: evidence); Paper IV §8.1 | `spec/state-machine.tla`: `can_enter_completed` evidence conjunct; `contracts/events.md` §4–§6 (packet fields, Paper IV §6.6) | CT-E1 · PT-4 |
| INV-E2 | Revision binding (Phase 0 spec); Paper IV §5.6 | `contracts/evidence-packet.schema.json` + `contracts/artifact-manifest.schema.json` — v0.1 drafts (2026-10-21, promoted on HgX's word; ratification pending). Revision binding enforced at schema level | SCH-EP-01/03 · CH-5 (completion-writer level) |
| INV-E3 | Gaps visible (Paper I: honesty); Paper IV §8.1 | Partial — packet side schema-backed: `contracts/evidence-packet.schema.json` v0.1 draft requires `gaps` and marks stale observations (CH-7 rule). "Missing evidence renders as missing" on a surface still awaits a rendering artifact | SCH-EP-02 · CH-7 (packet-marking rule); rendering pending |
| INV-E4 | Required gaps field (Paper IV §6.6) | `contracts/evidence-packet.schema.json` v0.1 draft (2026-10-21) — `gaps` required; omission is a schema violation | SCH-EP-02 · CH-10 (completion-writer level) |
| INV-E5 | Live-source freshness (Paper I); Paper IV §8.1 | `spec/state-machine.tla`: `BlockageCleared` freshness guard; `OperatorResumed` / `ObservationRestored` set `source_freshness' = "fresh"`; PO-10 guard construction | CT-E5 (structural) · PT-5 · CH-7 |
| INV-S1 | Forced unknown (Paper IV §7.3); Paper IV §8.1 | `spec/state-machine.tla`: `ObservationLost` (T20) / `ObservationRestored` (T21) — single keyed exit from `unknown`; PO4_UnknownNotOperational | CT-S1 · PT-5 · CH-7 |
| INV-S2 | Pause ≠ failure (Paper III); Paper IV §5.6 | `contracts/watchtower.schema.json` v0.1 draft (2026-10-21): closed state enum, paused never renders as down; renderer rule still at contract level (CH-1). Machine-level substrate PO5_PausedNotFailed proven in Phase 1 | SCH-WT-01/02 · CH-1 (renderer rule, contract level) |
| INV-S3 | Observed impairment (Watchtower); Paper IV §5.6 | Partial — schema-level only: `contracts/watchtower.schema.json` v0.1 draft requires an impairment note for any non-operational state and rejects stale readings rendered at full confidence. The Watchtower health-signal contract itself is still absent | SCH-WT-04/06 |
| INV-S4 | Freshness rendering (Paper III); Paper IV §8.1 | `spec/state-machine.tla`: freshness discipline (T8 guard, T19/T21 re-validation/re-read); rendering owned by Paper III surfaces / Phase 3 freshness policy | CT-S4 (structural) · PT-5 · CH-5, CH-7 |
| INV-S5 | Shared-surface redaction (Paper III); trust boundary 10 | Runtime — not yet mechanised (Paper III shared surfaces) | — |
| INV-R1 | Router recommends only (Paper II); Paper IV §8.1 | Runtime — not yet mechanised in this repository (usage router is estate runtime; `spec/router-policy.md` planned, owned by Phase 6) | CH-6 (contract level); router spec pending (Phase 6) |
| INV-R2 | Loop guard (router policy); Paper IV §8.1 | Runtime — not yet mechanised in this repository | — |
| INV-R3 | Loop denial (router policy); Paper IV §8.1 | Runtime — not yet mechanised in this repository | — |
| INV-R4 | Cache licence (router policy); Paper IV §8.1 | Runtime — not yet mechanised in this repository | — |
| INV-R5 | Safe fallback (router policy); Paper IV §8.1 | Runtime — not yet mechanised in this repository | CH-6 (contract level); router spec pending (Phase 6) |

## Notes on construction

- The Layer 1 suite derives its legal-transition table from the two
  ratified artifacts at run time (`contracts/events.md` ×
  `spec/state-machine.tla`) and asserts their agreement (test ST-05), so
  this matrix cannot silently drift from the spec: if either artifact
  changed, the suite would fail before the matrix could lie.
- Two spec subtleties the matrix depends on, both verified by the suite:
  (1) T6 is a joint firing — `artifact_produced` and
  `evidence_packet_created` together move `in_progress → verifying`
  (events.md §3 structural rules); (2) the any-state rows (T17/T18) cannot
  fire from `unknown`, because `FailureObserved` and `OperatorPaused`
  require `observation_status = "observed"` (Phase 1 Fixes 4–5) — which
  is what makes F6 (single keyed exit from `unknown`) true of the table.

## Update — 2026-10-21 (day work)

Layer 1 gate remainder closed: the five v0.1 schema drafts are covered by
`tests/layer1/test_schema_examples.py` (23/23 passing). INV-E2, INV-E4,
INV-S2 moved to schema-backed; INV-E3, INV-S3 partially; INV-S5 and
INV-R2/R3/R4 remain uncovered. The Layer 1 contract suite grew from 39 to
62 passing tests (39 + 23). All five schemas remain v0.1 drafts —
normative only on HgX's ratification. Crosscheck run 2026-10-21: 11/12
(the one failure is the documented honest limitation, unchanged from
2026-10-20).
