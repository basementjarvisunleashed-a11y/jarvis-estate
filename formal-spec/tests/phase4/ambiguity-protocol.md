# Phase 4 — Ambiguity Handling Protocol

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §7 (ambiguous outcome); `tests/PHASE-4-OPEN-QUESTIONS.md`
(Q4 — answered by HgX 2026-10-21 ~18:30 ET); `execution-record-spec.md`
(ER4); `retry-policy-matrix.md` (RF8).

> **Governance.** Draft until HgX ratifies. Normative over the reference
> implementation where they disagree.

---

## 1. Purpose

Some executions end ambiguously: the tool plane gave no receipt, the
network died mid-flight, the external system is opaque. The protocol
for those endings is the difference between a system that is honest
about what it does not know and one that silently completes. This
document is the honest one.

## 2. Ambiguity rules

1. **AP1.** Do not mark `completed` on ambiguity. A record whose
   outcome was not observed is not complete.
2. **AP2.** Do not auto-retry a consequential execution on ambiguity.
   The unknown effect may have happened; a retry may be a second
   effect. (RF8: the `safe_to_retry` flag is false on unknown.)
3. **AP3.** Verify externally if possible. The integration class
   determines what counts as verification (§3). A verified outcome
   resolves the record — to `execution_observed` or
   `execution_failed` — and only then may the record complete.
4. **AP4.** If verification is impossible, mark `execution_unknown`
   and escalate with the next safe option: what HgX can do now that
   does not risk a duplicate effect (cancel, verify manually,
   re-approve afresh).
5. **AP5 (Q4 ruling).** `execution_unknown` is surfaced on the next
   pull: the record, its state, the last error, and the safe options
   enumerated. An escalated notification goes to HgX — a hint
   pointing at the sealed record, never the record itself.
6. **AP6.** The notification carries no state. It is a hint, not the
   record — the pull discipline holds (Phase 3 CR-6, deployment
   build phase 1).

## 3. Verification by integration class

| Integration class | What counts as verification |
|---|---|
| Supports idempotency key | The native key's receipt, or a re-query returning the same effect |
| Supports read-after-write verification | A read that observes the effect (or its verified absence) |
| No idempotency, no verification | No external verification is possible — AP4 applies immediately |
| Reversible action | Reversal observation (the undo is itself observed) |
| Irreversible action | Exact receipt only; absent a receipt, the record stays unknown |
| Financial transfer | Strongest verification; where impossible, conservative — unknown, manual, no retry (custodian: Money Bot) |
| Publication | The published artifact, digest-verified, within expiry |
| Deletion | The recovery path verified (the deletion is confirmed by the recoverable change) |

## 4. Visibility path (Q4, concrete)

1. The record transitions to `execution_unknown` with `last_error`
   set and `updated_at` advanced — sealed and logged.
2. The next pull for the work returns the record: state
   `execution_unknown`, the last error, and the safe options
   enumerated (cancel; verify manually; re-approve afresh).
3. An escalated notification hint is emitted to HgX: the key, the
   state, and a pointer to the record. It carries no payload state.
4. The unknown persists, visible, until AP3 resolves it or HgX
   cancels it. It is never silently completed and never auto-retried.

## 5. Cross-references

- `execution-record-spec.md` — ER4 (unknown is visible, non-terminal).
- `retry-policy-matrix.md` — RF8 (ambiguity bars retry).
- `saga-spec.md` — S5 (verification in the saga).
- `tests/phase3/conflict-resolution.md` CR-6 — notification as hint.

## 6. Open points

- **P4-OP-2 — "Verified safe" production semantics.** The table in §3
  states what counts as verification per class at the spec level; the
  concrete production mechanics (which receipts, which read paths,
  timeouts) belong to implementation depth. The spec's rules stand
  regardless of the mechanics.
- **P4-OP-4 — The escalated notification channel.** Q4 rules the shape
  (hint, not the record; next pull is the truth). The channel and its
  mechanics are estate implementation, out of spec scope.
- **P4-OP-5 — Tool-plane truthfulness.** The retry rules trust the tool
  plane to report its own outcomes truthfully: a definitive "failed"
  is taken as observed non-occurrence (RF7). A Byzantine tool that
  reports failure after executing is outside this spec's threat model
  — it belongs to Phase 5 (security boundary formalism).

## 7. Version history

- **v0.1-draft — 2026-10-21.** First draft: AP1–AP6 with Q4 baked in;
  per-class verification table; the concrete visibility path;
  P4-OP-2, P4-OP-4. Not ratified.
