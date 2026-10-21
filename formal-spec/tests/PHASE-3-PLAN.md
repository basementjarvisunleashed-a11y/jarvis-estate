# Phase 3 — Programme Plan
## Consistency Model · Opened 2026-10-21 on HgX's order

> Precedent (HgX's Phase 2 pacing directive, 2026-10-20): go hard, do not
> hurry — follow the roadmap, take the roadmap's full time, document
> everything, comment everything, show proof of work. Phase 2 closed
> 2026-10-21 ~16:52 ET on that standard. Phase 3 is held to it.
> Roadmap schedule options for Phase 3: Option A weeks 4–5; Option B
> inside the months 1–6 validation window; Option C months 7–9
> (consistency, idempotency, security formalization). Pacing follows
> HgX's word.

## The governing rule

Phase 3 closes when its exit criteria are met — not before, not on a date
invented for convenience. Each layer has a gate; a layer opens only when
the previous layer's gate has passed and been recorded.

## Objective (ROADMAP.md §6, quoted)

Define how iPhone, Watch, iPad, TV, and Vision Pro observe and interact
with estate state without becoming independent sources of truth.

## Recommended model (ROADMAP.md §6, quoted)

Hybrid consistency:

| Operation Class | Guarantee |
|---|---|
| Status viewing | Eventual consistency with freshness stamps |
| Evidence viewing | Revision-stable reads |
| Approval decision | Strong authoritative consistency |
| Consequential execution | Linearized, single-writer execution |
| Memory correction | Orchestrator-mediated reconciliation |
| Live-source facts | Read-current at decision time |
| Artifact download | Digest-verified bytes |
| Notification delivery | At-least-once hints, not authoritative state |

Core principle: **status may be eventually consistent; consequence must be
strongly consistent.**

## Architecture (ROADMAP.md §6, quoted faithfully)

**Single authoritative writer** — the orchestrator (or authorized
execution layer). Clients may submit briefs, request evidence, render
status, present approval, transmit approval decisions, open artifacts.
Clients may NOT approve locally without server validation, infer
completion, mutate evidence, reinterpret intent, bypass approval, or
become a second orchestrator.

**Event-sourced work state** — each work item carries `work_id`,
`revision`, `state`, `history`, `evidence_refs`, `approval_refs`,
`last_observed_at`, `fresh_until`; every meaningful transition appends
an event.

**Revision tokens** — every client request includes `work_id`,
`revision`, `intent_id`, `intent_digest`, `device_session_id`,
`timestamp`; the server rejects stale mutations.

**Approval flow** — client renders card from hint → operator taps →
client sends decision with intent_id + digest → server validates (intent
exists, unexpired, digest matches, action permissible, session
authorized) → server records once → returns authoritative result →
client renders. Changed intent → reject and present new intent. Expired
→ disable and refresh. Offline → no local approval; pending gesture
only, not consent.

## Conflict resolution (ROADMAP.md §6, quoted)

| Conflict | Resolution |
|---|---|
| Two devices show different status | Server state wins |
| Two devices attempt approval | First valid decision recorded wins |
| Client cache says operational, source expired | Render unknown / reduced confidence |
| Memory says X, live source says Y | Live source wins for current facts |
| Durable memory contradiction | Orchestrator reconciles |
| Notification arrives after state changed | Notification is a hint, not truth |
| Evidence packet updated | New revision; old immutable |
| Artifact changed after approval | Approval invalid; new approval required |

## Deliverables (ROADMAP.md §6, quoted)

Consistency model specification; revision protocol; conflict resolution
table; multi-device sequence diagrams; device cache policy; freshness
policy.

## Exit criteria (ROADMAP.md §6, quoted verbatim)

No device can become a source of truth; approval conflicts resolve
deterministically; stale data cannot masquerade as current; offline taps
cannot become approvals; behavior tested under clock skew and network
loss.

## Layers and gates

### Layer 1 — Consistency-model spec documents (opens on HgX's word)
- The six deliverables, drafted under Phase 0 governance (ratified
  contracts are normative; drafts stay drafts until he ratifies):
  consistency model specification; revision protocol (revision-token
  wire format, stale-mutation rejection rule); conflict resolution
  table (the eight rows, each with a testable assertion); multi-device
  sequence diagrams (approval from two devices; evidence update during
  review; offline tap then reconnect); device cache policy (what each
  surface may cache, for how long, under what invalidation); freshness
  policy (`fresh_until` semantics, stale rendering rules).
- Gate: all six documents written, reviewed against the ratified
  contracts (events.md v1.1, the seven v1.0.0 drafts), and every
  assertion in them traceable to a Layer 2 test.

### Layer 2 — Protocol tests (opens on Layer 1 gate)
- Executable tests of the revision protocol and the conflict table:
  revision-token rejection (stale `revision` refused); stale-mutation
  rejection (mutated work item re-proposed, not silently applied);
  digest-bound approval (changed target/effect invalidates the
  approval); offline-tap (pending gesture recorded, never consent);
  first-valid-decision-wins (two devices race; exactly one recorded).
- Gate: all protocol tests green with evidence logs; every conflict-
  table row exercised by at least one test.

### Layer 3 — Chaos (opens on Layer 2 gate)
- Clock skew (devices ±minutes apart; freshness windows hold);
  partition (device isolated mid-approval; no split-brain approval);
  conflicting approvals from two devices under adversarial timing —
  the genuinely open item (see head-start note).
- Gate: chaos scenarios green; no device becomes a source of truth
  under any scenario.

## Head-start note — honest accounting (2026-10-21)

The deployment build (`~/workspace/jarvis-deploy/`, 132/132 green,
mapping approved by HgX 2026-10-21 ~16:41 ET) already evidences parts
of the exit criteria — see `PHASE-EXIT-MAPPING.md`:
- No device a source of truth: SATISFIED (data plane owns sealed state;
  9 refusals + 9 allowances across surface contracts).
- Stale data cannot masquerade: SATISFIED (±301s skew → sealed
  `stale-request` denial; freshness windows enforced).
- Offline taps cannot become approvals: SATISFIED (asserted zero
  recording; pending gesture only).
- Clock skew and network loss: SATISFIED (partition/replay/skew chaos
  in the pull layer).

Genuinely open — not claimed, not implied:
- **Deterministic conflict resolution under adversarial test:**
  concurrent conflicting approvals from two devices are specified
  (first-valid-decision-wins; digest equality) but NOT adversarially
  tested. This is Layer 3's core work.
- **The hybrid consistency table formally proven:** the eight-row
  table is specified, not proven. Layer 1 writes it as a testable
  specification; Layer 2/3 test it. Formal proof of the table is
  beyond this phase's exit criteria and is recorded as such.
- Device scope and orchestrator identity: open questions Q1–Q2 below —
  the model cannot be written until HgX answers them.

## Session log

### 2026-10-21 ~17:28 ET — PHASE 3 OPENED (HgX's word)
- "Give me a status Jarvis and if everything is clean let's go ahead
  with phase three." Everything verified clean (closure commits on
  remote, deployment build published, Dropbox healthy) — Phase 3
  opened.
- Opening package: this plan + `tests/PHASE-3-OPEN-QUESTIONS.md`
  (Q1–Q4 awaiting his walkthrough).
- Standing rules carried forward: never advance a phase without his
  explicit consent; ratified files untouched; no email/post/purchase
  without approval; the research pipeline stays sealed (survey in
  flight in the research section, never returns here).
