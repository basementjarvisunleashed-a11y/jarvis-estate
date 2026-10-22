# Phase 4 — Programme Plan
## Idempotency Guarantees · Opened 2026-10-21 on HgX's order

> Precedent (HgX's Phase 2 pacing directive, 2026-10-20): go hard, do not
> hurry — follow the roadmap, take the roadmap's full time, document
> everything, comment everything, show proof of work. Phase 3 closed
> 2026-10-21 ~18:07 ET on that standard (PROVEN ~18:05 ET: six drafts,
> 42 protocol tests, 80 adversarial cases, all five exit criteria met
> with covering tests). Phase 4 is held to it.
> Roadmap placement: Phase 4 sits in the months 7–9 formalization window
> (consistency, idempotency, security formalization). Pacing follows
> HgX's word.

## The governing rule

Phase 4 closes when its exit criteria are met — not before, not on a date
invented for convenience. Each layer has a gate; a layer opens only when
the previous layer's gate has passed and been recorded. The work layers
open on HgX's word after the question walkthrough — this package is the
opening, not the work.

## Objective (ROADMAP.md §7, quoted)

Prevent duplicate consequential effects from retries, duplicate taps,
network failures, or ambiguous execution.

## Core principle (ROADMAP.md §7, quoted)

> Consequential actions must be at-most-once unless the system has
> observed that they did not occur or are safely repeatable.

## Operation classes (ROADMAP.md §7, quoted)

| Class | Examples | Retry Policy |
|---|---|---|
| Read | Fetch calendar, price, document, status | Freely repeatable |
| Prepare | Draft, stage, calculate, reconcile | Repeatable if reversible |
| Approve | HgX grants exact intent | Record once; duplicate returns same decision |
| Execute | Send, publish, purchase, delete, transfer | At-most-once unless verified safe |
| Verify | Observe result after execution | Freely repeatable |
| Compensate | Restore, revoke, undo if possible | Only if supported and approved |
| Memory write | Update durable memory | Reconcile, do not duplicate contradictions |

## Idempotency model (ROADMAP.md §7, quoted faithfully)

Idempotency key =
`hash(work_id, intent_id, intent_digest, action, target, scope, revision,
operation_class)`.

Server stores: key, status, created/updated timestamps, approval ref,
execution state, observed result, attempt count, last error,
safe-to-retry flag.

Execution record states: `prepared → approved → execution_requested →
execution_started → execution_observed / execution_failed /
execution_unknown → completed / cancelled`.

**Duplicate taps**: first tap validates and records; second tap returns
existing decision and state — never a second execution.

**Ambiguous outcome**: do not mark completed; do not auto-retry if
consequential; verify externally if possible; else mark
`execution_unknown` and escalate with the next safe option.

## Transaction pattern — the governed saga (ROADMAP.md §7, quoted)

Governed saga (no assumed distributed transactions): prepare → approval
→ execute → verify → record evidence → compensate if approved and
possible. Preparation needs no approval; approval binds exact
target/effect; execution needs valid approval; execution must be
idempotent or verified; failed verification → unknown/failed;
compensation needs its own approval if consequential; no silent rollback
of consequential effects.

Phase 3's six-step ceremony (PROPOSE→RENDER→APPROVE→BIND→EXECUTE→ATTEST)
is the path the saga governs: EXECUTE is the at-most-once point, and
everything Phase 4 builds extends outward from it — the key, the record,
the retry rules, and the unknown-state protocol.

## External system classification (ROADMAP.md §7, quoted)

| Integration Class | Handling |
|---|---|
| Supports idempotency key | Use native idempotency |
| Supports read-after-write verification | Execute then verify |
| No idempotency, no verification | High-risk; strongest approval or manual execution |
| Reversible action | Prefer reversible preparation |
| Irreversible action | Exact approval and evidence |
| Financial transfer | Strongest verification, conservative retry |
| Publication | Digest-bound artifact and expiry |
| Deletion | Recoverable change preferred; require recovery path |

Note: financial transfers sit under the Money Bot's sole custody
(HgX's direct order, 2026-10-20) — the saga spec must name the
custodian, not route around it.

## Deliverables (ROADMAP.md §7, quoted)

Idempotency key specification; execution record schema; saga
specification; retry policy matrix; ambiguity handling protocol;
duplicate-tap and offline-approval test suites.

## Exit criteria (ROADMAP.md §7, quoted verbatim)

Duplicate taps cannot duplicate effects; network loss cannot silently
complete; ambiguous consequential actions become visible
unknown/failed; retries only when safe; at-most-once demonstrable
under test.

## Layers and gates

### Layer 1 — Idempotency spec documents (opens on HgX's word, after the walkthrough)
- The six deliverables, drafted under Phase 0 governance (ratified
  contracts are normative; drafts stay drafts until he ratifies):
  idempotency key specification (the key formula with the walkthrough's
  rulings on `revision` and `device_session_id` semantics baked in);
  execution record schema (the state machine, per-class transitions,
  the stored fields); saga specification (the governed saga over the
  six-step ceremony; per-operation-class behavior); retry policy matrix
  (the seven operation classes × retry posture, with the safe-to-retry
  flag rules); ambiguity handling protocol (verify-externally rules per
  integration class; `execution_unknown` marking; escalation with the
  next safe option); the Q6 resolution (who signs the digest for
  worker-prepared intents) recorded where it belongs.
- Gate: all six documents written, reviewed against the ratified
  contracts and the Phase 3 drafts (the ceremony, the revision
  protocol, CR-8), and every assertion in them traceable to a Layer 2
  test.

### Layer 2 — Protocol tests (opens on Layer 1 gate)
- Executable tests of the key, the record, and the saga:
  duplicate-tap (two devices, same intent — one execution; the second
  tap returns the existing record); safe-retry (retries permitted
  exactly where the matrix allows; unsafe retries refused);
  ambiguity visibility (ambiguous execution → `execution_unknown`,
  surfaced, escalated — never silently completed).
- Gate: all protocol tests green with evidence logs; every
  execution-record state transition exercised by at least one test.

### Layer 3 — Chaos (opens on Layer 2 gate)
- Network loss mid-execution (link severed between
  `execution_started` and observation — no silent completion);
  ambiguous outcomes (external system yields no receipt — visible
  unknown, never assumed); adversarial duplicate submissions
  (replays, duplicate taps under partition, racing devices — the
  at-most-once point under fire).
- Gate: chaos scenarios green; at-most-once holds under every
  scenario; no ambiguous consequential action stays invisible.

## Head-start note — honest accounting (2026-10-21)

The deployment build (`~/workspace/jarvis-deploy/`, 132/132 green,
mapping approved by HgX 2026-10-21 ~16:41 ET) and the Phase 3 harnesses
(42/42 protocol, 80/80 adversarial, PROVEN 2026-10-21 ~18:05 ET) already
evidence parts of the exit criteria:

- At-most-once at the decision layer: SATISFIED — the deployment
  handshake's actuation check verifies seal, digest, expiry, and nonce
  freshness; the nonce burns on first use; replay → refused + incident
  logged. Phase 3's Layer 3 replayed 6 times under partition: nothing
  changed.
- Digest-bound execution: SATISFIED — EXECUTE only after BIND, and
  digest binding is evaluated before revision currency (the Phase 3
  chaos fix); mutated intents lapse, never execute.
- Duplicate taps at the decision layer: SATISFIED —
  first-valid-decision-wins tested adversarially (CR-2, 18 race
  interleavings + 24-order fuzz); second tap returns the existing
  decision.
- Offline taps cannot become approvals: SATISFIED (Phase 3 exit
  criterion, tested).

Genuinely open — not claimed, not implied:

- **The governed saga as a formal spec:** the execution record state
  machine (`prepared → approved → execution_requested →
  execution_started → execution_observed / execution_failed /
  execution_unknown → completed / cancelled`) is specified by the
  roadmap, not written as a testable spec. Layer 1's core work.
- **The ambiguity protocol:** "verify externally if possible" is a
  policy, not a procedure — what counts as verification per
  integration class, and the concrete `execution_unknown` escalation
  path, are unwritten. Open question Q4.
- **The external-system classification:** the eight rows are quoted
  above, but the estate's actual integrations are not yet inventoried
  against them (which support native idempotency keys, which support
  read-after-write). Layer 1 writes the classification; the inventory
  is estate work beyond the spec.
- **Q6 — who signs the digest for worker-prepared intents:** carried
  over from Phase 2 (deferred on HgX's word, 2026-10-21 ~12:47 ET).
  Open question Q1.
- **The key's `revision` and `device_session_id` semantics:** the
  roadmap formula is quoted as-written; its two tensions (below) are
  open questions Q2–Q3 — the spec cannot be written until HgX rules.

## Session log

### 2026-10-21 ~18:07 ET — PHASE 4 OPENED (HgX's word)
- "Okay, close the phase, make sure you push the close, make sure
  everywhere the publishing house knows to close everything and open
  up the next phase and start the next phase up." Phase 3 CLOSED
  (PROVEN ~18:05 ET); Phase 4 — Idempotency Guarantees — OPENED.
- Opening package: this plan + `tests/PHASE-4-OPEN-QUESTIONS.md`
  (Q1–Q5 awaiting his walkthrough; Q1 is the Phase 2 Q6 carryover).
- The work layers open on his word after the walkthrough — this
  package is the opening, not the work.
- Standing rules carried forward: never advance a phase without his
  explicit consent; ratified files untouched; no email/post/purchase
  without approval; the research pipeline stays sealed.

## Phase 4 CLOSED
- **2026-10-21 ~22:31 ET, on HgX's word.** Idempotency is proven and closed: five drafts, 20 protocol tests, 15 chaos tests, all five exit criteria met with covering tests. Closure committed and pushed per his order. Phase 5 (Security Boundary Formalism) awaits his word.
