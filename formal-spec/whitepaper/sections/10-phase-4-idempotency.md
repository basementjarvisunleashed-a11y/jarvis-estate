# Phase 4 — Idempotency Guarantees: Consequence, Exactly Once or Not At All

*Paper IV, §10. Companion to the Phase 4 specification in the J.A.R.V.I.S. remediation roadmap. Builds on the single-writer rule and revision tokens of §9; its execution records become the evidence the security model of §11 reasons about.*

## 10.1 The Core Principle

> Consequential actions must be at-most-once unless the system has observed that they did not occur or are safely repeatable.

This principle is deliberately unfashionable. The dominant orthodoxy in distributed messaging is *at-least-once delivery with idempotent consumers*: send the message as many times as it takes, and let the receiver deduplicate. That orthodoxy is correct for its domain — moving bytes between systems that can absorb duplicates. It is wrong for the estate's domain, which is *causing effects in the world*: publishing, sending, purchasing, deleting, transferring. A duplicate message is a nuisance; a duplicate consequence is a harm the operator cannot un-experience. The estate therefore inverts the default: the consequence layer is at-most-once, guarded by idempotency keys, and retries are permitted only where the system has *observed* non-occurrence or *proven* safe repeatability.

The two defaults are not rivals; they govern different layers. At-least-once is appropriate for notification hints (§9.2), evidence fetches, log replication, and status polling — anywhere a duplicate is harmless and a loss is costly. At-most-once is appropriate for the execution of approved intents — anywhere a duplicate is harmful and the system can afford to stop, verify, and ask. The engineering error this phase prevents is letting the messaging layer's default leak into the consequence layer: a retry policy written for "deliver this packet" applied silently to "send this email."

## 10.2 Operation Classes and Their Retry Policies

| Class | Examples | Retry Policy |
|---|---|---|
| Read | Fetch calendar, price, document, status | Freely repeatable |
| Prepare | Draft, stage, calculate, reconcile | Repeatable if reversible |
| Approve | The operator grants an exact intent | Record once; duplicate returns same decision |
| Execute | Send, publish, purchase, delete, transfer | At-most-once unless verified safe |
| Verify | Observe result after execution | Freely repeatable |
| Compensate | Restore, revoke, undo if possible | Only if supported and approved |
| Memory write | Update durable memory | Reconcile; do not duplicate contradictions |

**Read — freely repeatable.** A read changes nothing, so repeating it changes nothing. *Estate example:* fetching the day's calendar to build the morning briefing. The only discipline reads require is the freshness one from §9: a read used *at decision time* must be read-current, but the act of reading itself needs no guard.

**Prepare — repeatable if reversible.** Preparation produces drafts, calculations, and staged artifacts — all of which can be discarded. *Estate example:* drafting the tax summary for the Tax Bot's return work. The draft can be regenerated any number of times; what it must never do is *leak* into execution. The boundary between Prepare and Execute is therefore the most audited boundary in the estate: preparation needs no approval precisely because it is defined as having no external effect, and anything with an external effect is, by definition, not preparation.

**Approve — record once; duplicate returns same decision.** Approval is the one operation class where a duplicate must return *the same answer*, not merely avoid a second effect. *Estate example:* the operator taps "Approve" on the white-paper publish intent; the tap retransmits (network stutter); the server finds the existing decision record and returns it. The operator sees one decision, one timestamp, one digest. (See §10.5 for the full duplicate-tap handling.)

**Execute — at-most-once unless verified safe.** The guarded class. *Estate example:* posting the campaign meme to X. The post either happened or it didn't; if the network dropped mid-post, the system does not assume — it verifies (§10.6) and retries only when verification shows non-occurrence or the operation is proven repeatable.

**Verify — freely repeatable.** Verification is observation, and observation is safe. *Estate example:* listing the Dropbox folder after an upload and comparing digests. A system that makes verification expensive or rate-limited will be tempted to skip it; the retry policy therefore states explicitly that verification is never the step to economize.

**Compensate — only if supported and approved.** Undoing is itself a consequential action. *Estate example:* retracting a scheduled routine that was published in error. Compensation requires its own approval when consequential (a retraction notice is a new public act), and it is only attempted where the external system supports it. There is no silent rollback of consequential effects — the saga rules in §10.7 make this explicit.

**Memory write — reconcile, do not duplicate contradictions.** Memory is the estate's long-term record; writing the same fact twice must not create two facts, and writing a contradictory fact must not silently overwrite. *Estate example:* recording the operator's corrected preference after a memory-correction request. The orchestrator reconciles against provenance (§9.7); the write is idempotent with respect to content, and contradictions surface for judgment rather than being resolved by recency.

## 10.3 The Idempotency Key Schema

The idempotency key names the *consequence*, not the gesture:

```
key = hash(work_id, intent_id, intent_digest,
           action, target, scope, revision, operation_class)
```

**Hash inputs, and why each is present.** `work_id` scopes the key to one unit of work. `intent_id` and `intent_digest` bind the key to the exact approved intent — a changed digest (new artifact bytes, new target) is a *different consequence* and must produce a *different key*, so that re-approval of a changed intent cannot accidentally dedupe against the old one. `action`, `target`, and `scope` name what will happen and where; `revision` pins the key to the work-item revision at approval time, so a replayed approval against a later revision cannot silently execute; `operation_class` separates Execute keys from Compensate keys, so a compensation can never dedupe against the execution it is undoing.

**What is excluded, and why.** Transient UI state and device-local nonces are *excluded* from the primary key — deliberately. The key must identify the consequence across devices and retries: the two-tap race in §10.5 (iPhone and Watch tapping the same intent within the same second) must resolve to the *same key*, or the dedupe fails exactly when it is most needed. A device-local nonce would make every tap unique and defeat the mechanism; a UI-state field (which card layout rendered, whether dark mode was on) would make the key fragile to irrelevant change. Device identity is still recorded — in the execution record's attempt log, for audit — but it is not part of the key. The principle: the key answers "what effect is being caused," never "who tapped what, where."

**Server-side record.** For each key, the server stores:

| Field | Purpose |
|---|---|
| `key` | The idempotency key itself |
| `status` | Current execution-record state (§10.4) |
| `created_at` / `updated_at` | Key lifecycle timestamps |
| `approval_ref` | The recorded approval decision authorizing this key |
| `execution_state` | Fine-grained execution state |
| `observed_result` | What verification actually saw (digests, IDs, timestamps) |
| `attempt_count` | How many execution attempts have been made |
| `last_error` | Most recent failure, if any |
| `safe_to_retry` | Boolean, set only by verification or policy — never assumed |

**Worked example.** The operator approves publishing the front-end white-paper PDF to Dropbox. Conceptually:

```
work_id:         wi-2026-10-08-112
intent_id:       ai-10442
intent_digest:   sha256(pdf bytes ‖ target=/J.A.R.V.I.S.-Front-End-White-Paper.pdf ‖ scope=dropbox-write)
action:          file_publish
target:          dropbox:/J.A.R.V.I.S.-Front-End-White-Paper.pdf
scope:           dropbox-write
revision:        6
operation_class: execute

key = sha256("wi-2026-10-08-112" ‖ "ai-10442" ‖ "9f2c…" ‖
             "file_publish" ‖ "dropbox:/J.A.R.V.I.S.-Front-End-White-Paper.pdf" ‖
             "dropbox-write" ‖ 6 ‖ "execute")
    = 7d31…
```

If the operator's finger double-taps, the second tap carries the same inputs and computes the same key: the server finds `7d31…` already `execution_observed` and returns the existing result. If the PDF is regenerated and re-approved, the digest changes, the key changes, and the new publish is correctly treated as a new consequence. If a *compensation* (retract the publish) is later approved, its key carries `operation_class: compensate` and cannot collide with the execution it reverses.

## 10.4 Execution Record Lifecycle

Nine states. Each lists its entry condition (what must be true to enter) and its exit condition (what must be true to leave):

1. **`prepared`** — *Entry:* preparation artifacts exist and are staged; no external effect has occurred. *Exit:* an approval decision is recorded (→ `approved`), or the work is abandoned (→ `cancelled`).
2. **`approved`** — *Entry:* a valid, unexpired, digest-matched approval decision is recorded against the intent. *Exit:* execution is requested (→ `execution_requested`), the approval expires or is superseded (→ `cancelled`), or the operator denies (→ `cancelled`).
3. **`execution_requested`** — *Entry:* the orchestrator has dispatched the execution with the idempotency key. *Exit:* the attempt begins (→ `execution_started`), or dispatch is withdrawn before any external call (→ `cancelled`).
4. **`execution_started`** — *Entry:* the external call has been issued. *Exit:* a result is observed (→ `execution_observed` / `execution_failed`), or observation becomes impossible (→ `execution_unknown`). *This is the point of no return for retry policy:* from here, the system may not assume non-occurrence.
5. **`execution_observed`** — *Entry:* verification has confirmed the effect occurred (read-after-write, provider receipt, digest match). *Exit:* acceptance checks pass (→ `completed`).
6. **`execution_failed`** — *Entry:* verification has confirmed the effect did *not* occur, or the attempt returned a definitive failure. *Exit:* a safe retry is dispatched (→ `execution_requested`, only if `safe_to_retry`), or the work is abandoned (→ `cancelled`, surfaced to the operator).
7. **`execution_unknown`** — *Entry:* the attempt was issued but the outcome cannot be established — network loss, provider timeout with no read-back, ambiguous receipt. *Exit:* external verification later establishes the outcome (→ `execution_observed` / `execution_failed`), or the operator decides with full knowledge of the ambiguity (→ `completed` by explicit acceptance, or `cancelled`). *Never* exits silently to `completed`; *never* auto-retries while consequential.
8. **`completed`** — *Entry:* acceptance criteria passed with evidence attached (INV-C1). *Exit:* none — terminal. Corrections create new work items, not resurrections.
9. **`cancelled`** — *Entry:* operator denial, approval expiry, withdrawal before external effect, or explicit abandonment with reason recorded. *Exit:* none — terminal. A cancelled record remains queryable; cancellation is itself evidence.

The lifecycle's shape encodes the doctrine: `execution_unknown` exists because the honest answer to "did it happen?" is sometimes "we cannot know yet," and a system that cannot represent that answer will invent one.

## 10.5 Duplicate-Tap Handling

The duplicate tap is the most ordinary idempotency event in the estate and therefore the one the mechanism must handle most boringly. The two-tap sequence:

```
Tap 1 (iPhone, 20:14:03.112Z)
  → client transmits decision + revision token
  → server validates (intent exists, unexpired, digest matches, session authorized)
  → server records decision D-8814 exactly once
  → server creates execution record, key 7d31…, state execution_requested
  → server returns { decision: D-8814, execution: 7d31…, status: execution_started }
  → client renders authoritative result

Tap 2 (iPhone, 20:14:03.408Z — the double-tap; or Watch, 20:14:03.511Z — the race)
  → client transmits decision + revision token (same intent_id, same digest)
  → server computes key 7d31… (identical inputs → identical key, §10.3)
  → server finds existing record: decision D-8814 already recorded
  → server returns { decision: D-8814, execution: 7d31…, status: <current>, duplicate: true }
  → NO second decision record. NO second execution. NO second external call.
  → client renders the existing authoritative result
```

**The race case.** Two devices tap within the same second — the iPhone and the Watch, both presenting valid tokens for the same intent. Both requests reach the server; validation is atomic at the single writer (§9.3). The first valid decision to complete validation wins; the second finds the winner's record and returns it. There is no "tie" state and no operator-visible ambiguity: one decision exists, both devices render it. The loser's tap is not an error — it is a successful read of someone else's decision. This is the same rule as §9.7's approval-conflict row, now grounded in the key mechanism: *first valid decision recorded wins* is not a policy preference but a consequence of atomic validation plus idempotent recording.

## 10.6 Ambiguous Outcome Handling

When `execution_started` is followed by silence — network drop, provider timeout, no read-back — the system follows a decision procedure, stated here as a flowchart in prose:

1. **Attempt external verification.** Query the external system for the effect: list the folder and compare digests (Dropbox), read back the timeline (X), check the provider's receipt log. Verification is freely repeatable (§10.2); spend it.
2. **If verification confirms the effect occurred** → transition to `execution_observed`, attach the observed result, proceed to acceptance. The ambiguity is resolved by evidence, not by assumption.
3. **If verification confirms the effect did not occur** → transition to `execution_failed`; consult `safe_to_retry`. Retry is permitted only where the failure is definitive and the policy allows.
4. **If verification is impossible** — the provider offers no read-back, the network is down, the receipt is ambiguous — **do not mark completed; do not auto-retry if consequential.** Transition to `execution_unknown`.
5. **From `execution_unknown`, escalate with the next safe option.** Present the operator with the full picture: what was attempted, what is known, what is unknowable, and the two honest choices — *accept the risk of a duplicate* (retry explicitly, with the operator's informed consent recorded as a new approval) or *accept the risk of non-effect* (verify later, or redo the work). The operator decides; the system never decides ambiguity on the operator's behalf.

**Worked scenario.** The operator approves publishing a PDF to Dropbox. The upload call is issued (`execution_started`); the network drops before the response arrives. What the operator sees:

- The approval card does not flip to "Published." It flips to **"Upload attempted — outcome unknown. Verifying…"** — the `execution_unknown` state rendered honestly (INV-S1: unknown never renders as operational).
- The system retries *verification*, not the upload: it re-lists the folder and compares digests. If the file is there with the right digest, the record moves to `execution_observed` and the card flips to "Published — verified 20:16:02Z."
- If the folder cannot be reached, the card stays at unknown and the operator is offered the next safe option: "Retry the upload (you accept the small risk of two copies) or wait and verify later." Either choice is recorded; neither is made silently.

Note what did not happen: the system did not mark the publish complete on the basis of the attempt, did not retry the upload blindly, and did not leave the operator staring at a spinner that meant nothing. Ambiguity is a first-class state with a first-class rendering.

## 10.7 The Governed Saga Pattern

The estate assumes no distributed transactions — Dropbox, X, the mail provider, and the operator's bank do not participate in two-phase commit, and pretending otherwise would be dishonest engineering. Coordination across systems therefore follows a *governed saga*: a sequence of steps, each guarded, each evidenced, each reversible only where reversal is real.

**The six steps:**

1. **Prepare** — stage artifacts, compute digests, bind the intent. No approval needed; no external effect permitted.
2. **Approval** — the operator grants the exact intent (action, target, effect, scope, expiry, digest).
3. **Execute** — the single writer issues the external call under the idempotency key.
4. **Verify** — observe the result through read-after-write or provider receipt.
5. **Record evidence** — attach the observed result to the evidence packet; only now can acceptance pass.
6. **Compensate** — if the outcome requires undoing and undoing is supported: issue the compensating action as its own governed mini-saga.

**The eight saga rules:**

1. Preparation needs no approval — but preparation is defined as having no external effect; anything with an effect is execution wearing a disguise.
2. Approval binds the exact target and effect (INV-A2); a changed target or effect invalidates the approval (INV-A3).
3. Execution requires a valid, unexpired, digest-matched approval for consequential actions (INV-A1, INV-A4).
4. Execution must be idempotent (keyed) or verified (observed); "fire and hope" is not a step.
5. Failed verification leads to `unknown` or `failed` — never to silent completion, never to silent retry.
6. Compensation needs its own approval if consequential — undoing a publication is itself a publication-shaped act.
7. No silent rollback of consequential effects — if the world was changed, the record says so, permanently; compensation is a new act, not an erasure.
8. No assumed distributed transactions — each step's guarantee is stated for what the external system actually provides (§10.8), and the saga is designed for the weakest participant, not the strongest.

**Why classical distributed transactions are not assumed.** Two-phase commit requires participants that can promise, prepare, and roll back on command. The estate's external systems offer none of these uniformly: some offer idempotency keys, some offer read-after-write, some offer nothing but a 200 OK of uncertain meaning. A saga designed for the weakest participant is not a compromise — it is the only design whose guarantees survive contact with the actual systems. The formalism's honesty about this is what makes the guarantees trustworthy: every step's precondition names what the external system *actually* provides, and the saga never assumes more.

## 10.8 External Integration Classification

| Integration Class | Handling | Estate Example |
|---|---|---|
| Supports idempotency key | Use native idempotency; map the estate key to the provider's token | **Notification dispatch** — the provider accepts a client dedupe token; the estate key (§10.3) is passed through, so a retried dispatch cannot double-notify |
| Supports read-after-write verification | Execute, then verify before acceptance | **Dropbox upload** — write the file, then list the folder and compare digests; acceptance passes only on digest match |
| No idempotency, no verification | High-risk; strongest approval or manual execution | **Email send** — the provider offers fire-and-forget with no reliable read-back; the estate requires its strongest approval class here, and the operator is told explicitly that verification is unavailable |
| Reversible action | Prefer reversible preparation; execute with normal guards | **Calendar write** — an event can be deleted or rescheduled; the saga may execute with lighter verification because compensation (delete) is real |
| Irreversible action | Exact approval and evidence; no compensation story | **Credential use** — a signing or authorization act, once performed, cannot be un-performed; the approval must be exact and the evidence packet complete, because there is no undo to fall back on |
| Financial transfer | Strongest verification, conservative retry | **Proline/betting record** — any money movement: verify through every available channel, retry only on definitive non-occurrence, and surface every ambiguity to the operator before proceeding |
| Publication | Digest-bound artifact and expiry | **X post** — the artifact digest is bound to the post intent and the intent carries an expiry (the hourly campaign window); a post approved for one window cannot execute in the next |
| Deletion | Recoverable change preferred; require a recovery path | **File delete** — move to trash, never `rm`; the recovery path (restore within N days) is named in the approval intent, and permanent deletion is a separate, separately approved act |

The classification is not a suggestion — it is assigned at integration time, stored with the connector's contract, and enforced by the saga: an integration classified "no idempotency, no verification" cannot be executed under a routine's standing approval, no matter how often the routine has run. The class follows the system, not the operator's familiarity with it.

## 10.9 Phase 4 Exit Criteria

- [ ] Duplicate taps cannot duplicate effects: double-tap and cross-device race tests produce exactly one decision record and one execution per key.
- [ ] Network loss cannot silently complete: partition during `execution_started` always lands in `execution_unknown`, never in `completed`.
- [ ] Ambiguous consequential actions become visible `unknown`/`failed`: every ambiguous path has a tested operator-facing rendering and an escalation with a next safe option.
- [ ] Retries only when safe: no test path retries a consequential execution without definitive non-occurrence or a proven-safe classification.
- [ ] At-most-once demonstrable under test: the idempotency key schema, execution record lifecycle, and saga rules hold under chaos injection (duplicate delivery, reordered events, dropped responses).
- [ ] Idempotency guarantees safe for open implementation: the key schema, execution record lifecycle, and saga rules are specified completely enough that a third-party client can implement at-most-once consequence without access to the estate's internals.

## Open Questions

1. **Dedupe window duration.** How long does the server retain execution records for duplicate detection — days, months, indefinitely? Storage is cheap; the question is whether indefinite retention creates a privacy or correctness liability (a year-old key colliding with a genuinely new but identical action).
2. **Safe-to-retry provenance.** The `safe_to_retry` flag is set "only by verification or policy — never assumed." Which policies may set it, and who approves a policy change? A permissive policy here silently reintroduces at-least-once semantics.
3. **Cross-intent dedupe.** Two *different* intents could name the same consequence (the operator approves the same publish twice, an hour apart). The keys differ (different `intent_id`), so both execute. Is that correct, or should the estate warn on semantic duplicates? The current model treats them as distinct acts of will; the alternative is a similarity check the operator did not ask for.
4. **`execution_unknown` aging.** An unknown that is never resolved is a permanent open loop. What is the escalation schedule — hours, days? — and at what point does a permanently unknown consequential action become a standing agenda item rather than a pending state?
5. **Provider key-mapping audit.** Where the estate maps its key to a provider's native idempotency token, a mapping bug silently disables dedupe. What test proves the mapping is live, not merely configured?
