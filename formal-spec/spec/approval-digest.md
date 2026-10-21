# Approval Intent Digest — spec/approval-digest.md

**DRAFT 0.1 — built 2026-10-21 on HgX's order; awaiting ratification.**
*Normative anchor: glossary U-1 (RESOLVED 2026-10-19, HgX): "SHA-256 over the canonical JSON serialisation of the approval intent." Owner: Phase 0 spec. Version: 0.1-draft.*

## 1. What the digest is

The **intent digest** is the cryptographic binding between the operator and the exact consequence being authorised. It makes INV-A2 (revision binding) and INV-A3 (mutation invalidates) mechanical: the server recomputes the digest at decision time, and any mutation of any bound field — however small — fails the match.

The digest binds the **intent record**: `intent_id`, `work_id`, `action`, `target`, `effect`, `scope`, `revision`, `expiry` (Paper IV §6.6). The digest field itself is never an input to its own computation.

> **Interpretation note (not ratified):** the TLA+ finite-instance concretization binds the six fields `(action, target, effect, scope, revision, expiry)` as a 6-tuple. This document additionally includes `intent_id` and `work_id` in the bound record, because the six-field tuple is a model-checking concretization, not the production rule, and the identifiers are part of the intent record per Paper IV §6.6. Recorded as an open question in BUILD-NOTES.md.

## 2. Canonical JSON

The canonical serialisation is defined by three rules:

1. **Sorted keys** — keys in ascending Unicode code-point order.
2. **No whitespace** — separators are `,` and `:` exactly (i.e. `json.dumps(..., separators=(',', ':'))`).
3. **UTF-8** — the string is encoded to UTF-8 bytes before hashing (`ensure_ascii=False`).

Reference procedure (Python 3 stdlib):

```python
import json, hashlib

def canonical_json(intent_record: dict) -> bytes:
    return json.dumps(intent_record, sort_keys=True,
                      separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def intent_digest(intent_record: dict) -> str:
    record = {k: v for k, v in intent_record.items() if k != "intent_digest"}
    return hashlib.sha256(canonical_json(record)).hexdigest()
```

Digest output is 64 lowercase hex characters (`^[0-9a-f]{64}$` — enforced by the schemas).

> **Interpretation note (not ratified):** "sorted" is read as Unicode code-point order and "no whitespace" as the exact `(',', ':')` separators. Number encoding (integers vs floats) and duplicate-key handling are not specified by the papers; the reference procedure serialises Python ints as plain integers and objects with unique keys. Recorded as an open question in BUILD-NOTES.md.

## 3. Worked example

Sample intent record (intent, not a real authorization):

```json
{"action":"publish","effect":"paper-v1.2.pdf posted to public Dropbox folder","expiry":1792593737,"intent_id":"intent-7f3a","revision":42,"scope":"release publishing house","target":"dropbox:/J.A.R.V.I.S./papers/paper-i/v1.2/","work_id":"work-9b21"}
```

- Canonical bytes: the 249 bytes above, UTF-8 encoded.
- `intent_digest = SHA-256(canonical bytes) =`
  **`a5ba4f85e85058c009047fd497df0bfa97122822f5286551adba15fa18f63179`**

(Computed 2026-10-21 with `hashlib.sha256`; any independent implementation of §2 must reproduce it byte-for-byte.)

## 4. tap_digest semantics (matching the TLA+)

- When the operator taps approve on the client surface, the client records `tap_digest` = the digest of the intent **as presented to the operator** (`DigestOf(intent)` at tap time — TLA+ `OperatorTapsApprove`). The tap is a gesture, not authority (INV-A5).
- The server records the decision only if the intent it holds digest-matches what the operator tapped: `DigestOf(intent) = tap_digest` (TLA+ `ServerRecordsApproval`). Any mutation of any intent field between tap and record changes the digest and **forces rejection** (PO-3).
- `MutateIntent` (failure model, Paper IV §7.5#3): a mutation arriving while `approval_state ∈ {requested, tapped}` is observable; after recording, the intent is server-held and immutable.
- Digest equality is recomputed at transition time (T9's `can_enter_executing`), never cached.

## 5. Where digests appear

- `contracts/approval-intent.schema.json`: `intent_digest` — the binding.
- `contracts/decision-packet.schema.json`: `intent_digest` — the digest echo (as presented); together with `server_recorded_at` this is the definition of "authoritative" (INV-A5).
- Idempotency key (glossary): `hash(work_id, intent_id, intent_digest, action, target, scope, revision, operation_class)`.

## 6. Collision resistance

Assumed as lemma (a), Paper IV §7.6. The TLA+ concretization is injective over intent records (a 6-tuple), strictly stronger than assumed collision resistance, so PO-3 is exercised faithfully in the finite instance.

---
*Sources: contracts/glossary.md §1 (Intent, Intent digest, Approval decision, Tap), §3 U-1; spec/state-machine.tla (`OperatorTapsApprove`, `DuplicateTap`, `ServerRecordsApproval`, `can_enter_executing`, `MutateIntent`); Paper IV §5.6, §6.6, §7.6.*

> Promotion note (2026-10-21, on HgX's order "push all of it"): promoted to canonical placement as v0.1 draft. Formal ratification to v1.0.0 remains HgX's call. Open questions OQ-1..OQ-6 recorded in tests/staging/prescribed-files/BUILD-NOTES.md.
