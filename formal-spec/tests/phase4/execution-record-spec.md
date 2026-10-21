# Phase 4 — Execution Record Specification

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §7 (execution record states, stored fields);
`idempotency-key-spec.md` (the key is the record's identity);
`tests/phase3/revision-protocol.md` (orchestrator as single writer).

> **Governance.** Draft until HgX ratifies. Normative over the reference
> implementation where they disagree.

---

## 1. Purpose

The execution record is the single authoritative account of one
consequential execution: what was approved, what the orchestrator did,
what it observed, and what remains unknown. Every request after the
first — retry, duplicate tap, reconnect, escalation — reads this record
and acts on it. The record is the truth; everything else is a view.

## 2. Record schema

The server stores, per idempotency key:

| Field | Type | Meaning |
|---|---|---|
| `key` | string (hex) | The idempotency key — the record's identity (K1–K6). |
| `status` | string | The record's lifecycle state (§3). |
| `created_at` | integer | Epoch seconds at record creation (first execution request). |
| `updated_at` | integer | Epoch seconds at last transition. |
| `approval_ref` | string | The approval (intent digest + decision reference) that authorized this execution. |
| `execution_state` | string | The execution state machine state (§3). |
| `observed_result` | any / null | The receipt the tool plane returned, if any. |
| `attempt_count` | integer | Times the tool plane was fired for this key (ER2: at most once per record for consequential classes). |
| `last_error` | string / null | The most recent failure or ambiguity, machine-readable. |
| `safe_to_retry` | boolean | Whether a retry is permitted under the retry matrix (see `retry-policy-matrix.md`). |
| `operation_class` | string | One of the seven operation classes (ROADMAP.md §7). |

`created_at` / `updated_at` are integer epoch seconds (Phase 2 Q1:
machine truth).

## 3. The state machine

```
prepared → approved → execution_requested → execution_started
    → execution_observed → completed
    → execution_failed  → completed | cancelled
    → execution_unknown → (verify → observed/failed) | cancelled
```

### 3.1 Record rules

1. **ER1.** One record per key. The key is the record's identity; a
   second record under the same key cannot exist.
2. **ER2.** The tool plane fires **at most once per record** for
   consequential operation classes. `attempt_count` is the audit
   trail: for `execute`, it is 0 before the first fire and 1 after —
   and never 2.
3. **ER3.** Transitions follow only the machine's edges. There is no
   jump from `execution_requested` to `completed`, no resurrection
   from a terminal state.
4. **ER4.** `execution_unknown` is a **visible, non-terminal** state.
   It requires resolution — verify externally, cancel, or retry if
   safe — and it is surfaced on the next pull (see
   `ambiguity-protocol.md`). It is never silently completed.
5. **ER5.** `completed` and `cancelled` are terminal and final. Any
   request against a terminal record returns the existing record —
   never a new execution.
6. **ER6.** Every transition is a sealed, logged event with
   `updated_at` advanced. The sealed log is the audit trail of the
   record's life.

### 3.2 Per-class notes

- **Execute:** the at-most-once class. ER2 binds hardest here.
- **Approve:** records the decision once; duplicates return the
  existing decision (Phase 3 CR-2, revision-protocol.md §6).
- **Prepare:** repeatable if reversible — the record tracks
  preparation attempts without consequential force.
- **Verify:** freely repeatable — verification reads the world, it
  does not change it.
- **Compensate:** its own record, its own key, its own approval
  (see `saga-spec.md` S6).
- **Memory write:** reconciled, never duplicated (Phase 3 CR-5).

## 4. Cross-references

- `idempotency-key-spec.md` — the key that identifies the record.
- `saga-spec.md` — the saga transitions the record through.
- `retry-policy-matrix.md` — the `safe_to_retry` flag rules.
- `ambiguity-protocol.md` — the `execution_unknown` resolution path.
- `tests/phase3/revision-protocol.md` — the orchestrator as single
  writer; the sealed refusal ledger.

## 5. Open points

- None in this draft beyond P4-OP-2 (in `ambiguity-protocol.md`):
  what counts as "verified safe" per integration class touches the
  `safe_to_retry` flag's production semantics.

## 6. Version history

- **v0.1-draft — 2026-10-21.** First draft: record schema (ten
  fields), the state machine, ER1–ER6. Not ratified.
