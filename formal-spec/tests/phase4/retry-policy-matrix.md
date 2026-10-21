# Phase 4 — Retry Policy Matrix

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §7 (operation classes); `execution-record-spec.md`
(the `safe_to_retry` flag); `ambiguity-protocol.md` (ambiguity bars retry).

> **Governance.** Draft until HgX ratifies. Normative over the reference
> implementation where they disagree.

---

## 1. Purpose

Not all retries are equal. A retry of a read is harmless; a retry of
an opaque consequential execution is a second effect wearing a retry's
clothes. This matrix assigns each operation class its retry posture
and states the rules for the `safe_to_retry` flag — the machine's
single gate on retries.

## 2. The matrix

| Class | Examples | Retry posture |
|---|---|---|
| Read | Fetch calendar, price, document, status | Freely repeatable |
| Prepare | Draft, stage, calculate, reconcile | Repeatable if reversible |
| Approve | HgX grants exact intent | Record once; duplicate returns same decision |
| Execute | Send, publish, purchase, delete, transfer | At-most-once unless verified safe |
| Verify | Observe result after execution | Freely repeatable |
| Compensate | Restore, revoke, undo if possible | Only if supported and approved |
| Memory write | Update durable memory | Reconcile, do not duplicate contradictions |

## 3. Retry rules

1. **RF1.** Reads and verifies are freely repeatable. They observe the
   world; they do not change it.
2. **RF2.** Prepares are repeatable iff reversible. A non-reversible
   preparation is a consequential act and is governed as one.
3. **RF3.** Approvals are recorded once. A duplicate approval request
   returns the existing decision and state — never a second decision
   (Phase 3 CR-2, revision-protocol.md §6).
4. **RF4.** Executes are at-most-once **unless verified safe.** A
   retry of an execution proceeds only when the record's
   `safe_to_retry` flag holds; otherwise it is refused and the
   existing record returned.
5. **RF5.** Compensations proceed only if supported and approved —
   and a consequential compensation requires its own fresh ceremony
   (saga-spec.md S6).
6. **RF6.** Memory writes are reconciled, never duplicated: a
   contradictory write is proposed as a correction citing both
   antecedents (Phase 3 CR-5), not written over.
7. **RF7.** The `safe_to_retry` flag is set **true** only when the
   effect is verified absent (the tool plane or external verification
   observed non-occurrence) or safely repeatable (the integration
   class guarantees idempotent replay — native idempotency keys). A
   definitive tool-reported failure sets the flag: the tool plane is
   the authority on whether it acted (trust boundary: P4-OP-5).
8. **RF8.** The flag is set **false** on ambiguity. An
   `execution_unknown` record never carries `safe_to_retry = true`
   until external verification resolves the unknown (see
   `ambiguity-protocol.md` AP3).
9. **RF9.** A refused retry changes nothing. Re-presenting a refused
   retry is the same refusal — it is not an attempt, and
   `attempt_count` does not advance.

## 4. Cross-references

- `execution-record-spec.md` — the flag lives on the record.
- `saga-spec.md` — where retries sit in the saga.
- `ambiguity-protocol.md` — ambiguity bars retry (RF8/AP2).
- `tests/phase3/revision-protocol.md` — R2/R4: stale tokens are
  re-pulled, not force-retried.

## 5. Open points

- None in this draft. The production semantics of "verified safe"
  per integration class are P4-OP-2 (in `ambiguity-protocol.md`).

## 6. Version history

- **v0.1-draft — 2026-10-21.** First draft: the seven-class matrix,
  RF1–RF9. Not ratified.
