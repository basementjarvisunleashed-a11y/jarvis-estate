# Phase 4 — Idempotency Key Specification

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §7 (idempotency model); `tests/PHASE-4-OPEN-QUESTIONS.md`
(Q2, Q3 — answered by HgX 2026-10-21 ~18:27–18:29 ET); `tests/phase3/revision-protocol.md`
(R1–R5, the five-step rejection order); Phase 2 rulings (integer revisions,
eight-field approval digest, canonical-JSON procedure).

> **Governance.** Draft until HgX ratifies. Normative over the reference
> implementation where they disagree.

---

## 1. Purpose

The idempotency key is the estate's answer to the duplicate-effect
problem: one key identifies one approved effect, and the orchestrator
executes at most once per key. Retries, duplicate taps, replays, and
reconnects all converge on the same key — and the key returns the
existing record instead of a second execution.

## 2. The key formula

```
key = sha256(canonical({
  work_id, intent_id, intent_digest, action, target, scope,
  revision, operation_class
}))
```

The eight fields are exactly the roadmap's formula (ROADMAP.md §7),
with the two walkthrough rulings baked in.

### 2.1 Key rules

1. **K1.** The key binds exactly these eight fields — no more, no fewer.
   A key that hashes a different field set is not a key.
2. **K2 (Q2 ruling).** `revision` is the revision **at approval time,
   frozen at BIND.** Retries of the same approved intent share the key,
   because the key identifies the approved effect, not the attempt. A
   retry issued after a revision bump still hashes the frozen
   revision — the key's purpose is preserved.
3. **K3 (Q3 ruling).** `device_session_id` is **excluded.** The key
   identifies the EFFECT; the revision token identifies the REQUEST.
   Two devices, one intent, one key, one execution. Per-device keys
   would let the same intent execute once per device — exactly the
   duplicate effect this phase exists to prevent.
4. **K4.** The canonical form follows the Phase 2 Q4 procedure:
   Unicode code-point key order, exact `(',', ':')` separators, UTF-8,
   `ensure_ascii=False`. SHA-256 over the canonical bytes, hex-encoded.
5. **K5.** The key is computable deterministically at BIND from the
   approved intent record: `intent_digest` is the eight-field approval
   digest (Phase 2 Q3), `revision` is the frozen approval-time revision,
   and the remaining fields are the intent's own fields. The same
   approved intent always yields the same key.
6. **K6.** A changed intent cannot ride an old key: any change to the
   intent changes `intent_digest`, and digest binding lapses the
   ceremony before revision currency is even evaluated (digest-first,
   per the Phase 3 chaos fix). The new intent is a new key.

### 2.2 The effect/request asymmetry

The key and the revision token are deliberately asymmetric:

| | Identifies | Includes session? | One per |
|---|---|---|---|
| **Idempotency key** | the EFFECT (what was done) | no (K3) | approved intent |
| **Revision token** | the REQUEST (who asked) | yes | client request |

The token says who asked; the key says what was done. The server
deduplicates on the key and authorizes on the token. This asymmetry is
principled, not accidental — it is what makes duplicate taps from two
devices converge on one execution.

## 3. Key lifecycle

1. **Computed at BIND.** The orchestrator computes the key from the
   approved intent record at BIND time. The key is part of the sealed
   record of the decision.
2. **Record created on first execution request.** The first execution
   request under the key creates the execution record (see
   `execution-record-spec.md`). The record's identity is the key.
3. **Never reused for a different effect.** A new intent (new digest,
   new approval-time revision) is a new key. Keys are never recycled.
4. **Lookup key for everything after.** Retries, duplicate taps,
   reconnects, and ambiguity resolutions all look up the record by key
   and receive the existing record — never a second execution.

## 4. Cross-references

- `execution-record-spec.md` — the record the key identifies.
- `retry-policy-matrix.md` — when a retry under the same key is permitted.
- `tests/phase3/revision-protocol.md` — the token (request identity),
  R1–R5 monotonicity, the five-step rejection order.
- `tests/phase3/layer2/digest.py` — the canonical procedure this
  spec reuses for `intent_digest`.

## 5. Open points

- **P4-OP-1 — The `device_session_id` lifecycle** (carried from Phase 3
  OP-3): enrollment, revocation, re-enrollment, and session expiry
  belong to Phase 5 (security). K3 is written so the key never depends
  on session semantics Phase 5 will define — but the token still does.
  **Needs HgX's word** in Phase 5, not here.

## 6. Version history

- **v0.1-draft — 2026-10-21.** First draft: eight-field formula with
  Q2 (revision frozen at BIND) and Q3 (device_session_id excluded)
  rulings baked in; K1–K6; the effect/request asymmetry. Not ratified.
