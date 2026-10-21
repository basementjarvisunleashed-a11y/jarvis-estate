# Phase 3 — Consistency Model: One Estate, Five Observers

*Paper IV, §9. Companion to the Phase 3 specification in the J.A.R.V.I.S. remediation roadmap.*

## 9.1 The Problem: Five Surfaces, One Estate

Papers I through III describe an estate observed through five device surfaces: the iPhone as command surface, the Apple Watch as a five-second wrist gate, the iPad as review desk, the Apple TV as ambient wall, and — later — Vision Pro as spatial estate (Paper III). Each surface renders estate state. Each surface accepts input. Each surface caches.

The question this phase answers is therefore structural, not cosmetic: when five surfaces observe one estate, what prevents them from becoming five sources of truth?

Without a stated consistency contract, the failure modes are predictable and have all been observed in consumer software:

1. **Divergent approval.** Two devices render the same approval card; the operator (HgX) taps both; the consequence executes twice, or — worse — each device believes a different consequence was authorized.
2. **Stale authority.** A device renders state from a morning cache; the operator acts on it at noon; the action was valid at render time and invalid at action time.
3. **Optimistic fiction.** A client renders its own tap as success before the server confirms, and the operator walks away believing a consequence occurred that never did.
4. **Silent divergence.** Two devices show different statuses for the same work item, and there is no rule for which one the operator should believe.

The consistency model below exists to make each of these impossible by construction rather than by discipline. Discipline is what the estate has today (Paper I is honest about this); this phase converts it into mechanism.

## 9.2 The Hybrid Consistency Model

No single consistency level fits all estate operations. Status viewing can tolerate staleness; approval decisions cannot. The model is therefore hybrid — the guarantee follows the operation class, not the device:

| Operation Class | Guarantee |
|---|---|
| Status viewing | Eventual consistency with freshness stamps |
| Evidence viewing | Revision-stable reads |
| Approval decision | Strong authoritative consistency |
| Consequential execution | Linearized, single-writer execution |
| Memory correction | Orchestrator-mediated reconciliation |
| Live-source facts | Read-current at decision time |
| Artifact download | Digest-verified bytes |
| Notification delivery | At-least-once hints, never authoritative state |

Each row is defended below in terms of what the guarantee permits and, more importantly, what it forbids.

**Status viewing — eventual consistency with freshness stamps.** A Watchtower status rendered on the television may lag the orchestrator by minutes; nothing consequential follows from a status render, so the cost of staleness is confusion, not harm. The freshness stamp (`last_observed_at`, `fresh_until`) bounds the confusion: a stale render must say it is stale, or degrade to `unknown` (INV-S4). The stamp is the mechanism; "eventual" without the stamp would be a license to mislead.

**Evidence viewing — revision-stable reads.** An evidence packet is immutable once created (§9.7); a read of evidence must return the packet the operator asked for, byte-identical, regardless of what newer revisions exist. This is stronger than eventual consistency and weaker than linearizability: the guarantee is *stability of the addressed revision*, enforced by content digests. It forbids the quiet substitution of a revised packet under an old reference — the exact failure that would let a doctored artifact inherit a prior approval.

**Approval decision — strong authoritative consistency.** There is exactly one authority that can record an approval decision: the orchestrator (or its authorized execution layer). A client's tap is a *proposal* until the server validates and records it (§9.6). No local quorum, no offline accumulation, no "the button said approved." The guarantee forbids every path by which two devices could hold two different beliefs about whether consent was given.

**Consequential execution — linearized, single-writer execution.** Execution of an approved intent proceeds through one writer, in one order, with each step's precondition checked against current authoritative state. Two executions of the same intent cannot interleave; the second attempt finds the first's record and returns it (§10). This forbids the race in which a retry and a tap both reach the same external system.

**Memory correction — orchestrator-mediated reconciliation.** Durable memory is the operator's long-term record; two surfaces could hold contradictory corrections. Corrections are therefore not writes — they are *requests* the orchestrator reconciles against provenance (§9.7). This forbids silent contradiction in the record the estate reasons from.

**Live-source facts — read-current at decision time.** Wherever a decision depends on the world as it is now (a price, a schedule, a balance), the fact must be re-read from the live source at the moment of decision, not taken from cache. Memory may say X and the live source may say Y; for current facts, Y wins (§9.7). This forbids decisions made on cached reality — the precise failure behind the stale-state manipulation threat in §11.5.

**Artifact download — digest-verified bytes.** A download is not complete when the bytes arrive; it is complete when the digest matches the manifest. This forbids truncated or substituted artifacts from entering the estate under a trusted name.

**Notification delivery — at-least-once hints, never authoritative state.** Notifications may be duplicated or delayed; they are permitted to be, because they carry no authority. A notification says "something may have changed — look"; it never says "this is the state." This forbids the failure in which a delayed push and a current render disagree and the operator trusts the push.

### The Core Principle, Defended

> **Status may be eventually consistent; consequence must be strongly consistent.**

The first half exists because strong consistency is expensive — in latency, in complexity, and in the operator's attention. Forcing every status render through a synchronous authoritative read would make the ambient wall flicker, the Watch lag, and the estate feel broken. Eventual consistency with honest freshness stamps is the correct price: the operator sees slightly old state *labeled* as such, and the label is itself a guarantee (INV-S4).

The second half exists because the cost of inconsistency at the consequence boundary is not confusion but *unauthorized effect*: money moved, messages sent, artifacts published. These are the actions the doctrine chain exists to govern (Paper I: Role → Live Source → Tool → Artifact → Evidence → Approval → Routine), and the chain's Approval link is meaningless if two devices can disagree about whether approval happened. Strong consistency at the consequence boundary is therefore not an optimization — it is the load-bearing wall of the entire governance model.

**What breaks if the principle is inverted?** Invert it — make status strongly consistent and consequence eventually consistent — and the estate gets the worst of both: a sluggish ambient wall that still occasionally double-publishes, double-sends, or approves from a stale intent. The inversion is not merely suboptimal; it concentrates expense where harm is impossible and removes protection where harm is certain. Any implementation found to have drifted toward the inversion has failed Phase 3 regardless of its test results.

## 9.3 Single Authoritative Writer

The roadmap names the orchestrator (or the authorized execution layer) as the single authoritative writer. Concretely, the orchestrator owns:

- the canonical work-item record and its revision counter (§9.4);
- the approval decision log — which intents were granted, denied, or expired, and by whom;
- the execution record — which approved intents have executed, and with what observed result (§10);
- the reconciliation of memory corrections;
- the issuance and validation of revision tokens (§9.5).

Clients — all five surfaces — are deliberately and permanently weaker. What clients **may** do:

- submit briefs (requests for work) to the orchestrator;
- request evidence packets and artifacts by revision;
- render status from cached or fetched state, with freshness stamps;
- present approval cards rendered from server-issued hints;
- transmit approval decisions (proposals) with full revision tokens;
- open artifacts for inspection.

What clients **may not** do — the prohibitions are the actual content of this section:

- approve locally without server validation;
- infer completion from a tap, a notification, or a subagent's claim (INV-C3, INV-C4);
- mutate evidence packets or their references;
- reinterpret an approval intent (narrowing, widening, or retargeting it);
- bypass the approval boundary for any consequential action;
- become a second orchestrator — no client may accept briefs from another client, coordinate subagents, or maintain its own authoritative work-item records.

The last prohibition deserves emphasis because it is the one most likely to be violated by convenience. A future Vision Pro spatial client will be powerful enough to *feel* like an orchestrator; the contract must still hold. Capability is not authority.

## 9.4 Event-Sourced Work State

Every work item carries the following record:

| Field | Meaning |
|---|---|
| `work_id` | Stable identity of the work item across its lifetime |
| `revision` | Monotonic counter; increments on every meaningful transition |
| `state` | Current canonical state (from the Phase 1 state machine) |
| `history` | Append-only list of transition events, each with timestamp and actor |
| `evidence_refs` | References (with digests) to evidence packets attached to this work |
| `approval_refs` | References to approval intents and their recorded decisions |
| `last_observed_at` | When the authoritative record was last written |
| `fresh_until` | Bound after which readers must re-fetch before acting |

Transitions append events; they never rewrite history. The record is the log, and the current state is a fold over the log — which is what makes "stale data cannot masquerade as current" (§9.9) a structural property rather than a hope.

**Worked example.** A brief arrives: *"prepare the day-plan briefing."* The record evolves:

```
work_id:        wi-2026-10-08-041
revision:       1
state:          received
history:
  - { event: brief_received, at: 08:00:11Z, actor: tickler-bot,
      note: "brief accepted from scheduled routine" }
```

The orchestrator accepts scope; revision 2 appends `brief_accepted`:

```
revision:       2
state:          accepted
history:
  - { event: brief_received,  at: 08:00:11Z, actor: tickler-bot }
  - { event: brief_accepted,  at: 08:00:12Z, actor: orchestrator,
      note: "scope bounded: calendar + inbox + priorities" }
```

A bounded plan exists; revision 3 appends `plan_created` and the state moves to `in_progress`:

```
revision:       3
state:          in_progress
history:
  - { event: brief_received,  at: 08:00:11Z, actor: tickler-bot }
  - { event: brief_accepted,  at: 08:00:12Z, actor: orchestrator }
  - { event: plan_created,    at: 08:00:19Z, actor: orchestrator,
      note: "3 sources, 7 items, 1 approval expected" }
evidence_refs:  []
approval_refs:  []
last_observed_at: 08:00:19Z
fresh_until:      08:05:19Z
```

Three properties to note. First, nothing was overwritten: a reader at revision 1 sees exactly what revision 1 saw. Second, `fresh_until` bounds how long any client may treat this snapshot as actionable — after 08:05:19Z, a client holding revision 3 must re-fetch before submitting any mutation. Third, the history is the audit trail the evidence packet will later cite; Phase 7's doctoral evidence package is, in part, a corpus of such histories.

## 9.5 Revision Tokens: The Stale-Mutation Rejection Rule

Every client request that could change authoritative state carries a revision token:

| Field | Purpose |
|---|---|
| `work_id` | Which work item the request addresses |
| `revision` | The revision the client believes is current |
| `intent_id` | Which approval intent the request acts under (for approvals) |
| `intent_digest` | Digest binding the exact action, target, effect, scope, and expiry |
| `device_session_id` | Which device session issued the request (spoofing control, §11.4) |
| `timestamp` | Client-observed time of the request (clock-skew input, not authority) |

**The rejection rule.** The server compares the presented `revision` against the authoritative `revision`:

- `presented == current` → the request is *fresh*; validate the remaining fields and apply.
- `presented < current` → the request is *stale*; reject with `stale_revision`. The client must re-fetch authoritative state and, if the operator still wishes to act, present the new intent. The mutation is never applied, never queued, never "applied when convenient."
- `presented > current` → the request is *impossible*; reject and flag. A client cannot be ahead of the single writer; the condition indicates a corrupt cache, a replayed token, or a forged request, and it is logged as a security event (§11.4).

**Worked conflict example.** The iPad renders an approval card for work item `wi-2026-10-08-041` at revision 4 (intent: publish the white-paper PDF to Dropbox). The operator sets the iPad down and picks up the iPhone, where a newer brief advances the same work item to revision 5 (the artifact was regenerated; the old intent's digest no longer matches). The operator returns to the iPad and taps "Approve."

The iPad transmits `{work_id: wi-2026-10-08-041, revision: 4, intent_id: ai-9917, intent_digest: 9f2c…}`. The server holds revision 5. Presented (4) < current (5) → reject `stale_revision`. The iPad discards its card, fetches revision 5, and discovers the artifact changed after the card was rendered. Per §9.7, the old approval intent is invalid; a new intent is presented; the operator reviews the *new* artifact. The thirty seconds of re-reading are the entire price of preventing an approval from attaching to an artifact the operator never saw.

## 9.6 The Approval Flow

The approval flow is the consequence boundary made executable. Seven steps, in order, with no shortcuts:

1. **Client renders the card from a server-issued hint.** The card displays the exact action, target, effect, scope, expiry, and digest. The card is a *view* of a pending intent, not the intent itself.
2. **The operator taps.** The tap is a local gesture. It authorizes nothing. The client must not render any success state at this point — rendering "Approved ✓" before step 6 is optimistic fiction (INV-C4) and a Phase 3 failure.
3. **The client transmits the decision** with `intent_id`, `intent_digest`, and the full revision token (§9.5).
4. **The server validates**: the intent exists; it has not expired; the digest matches the current intent (unchanged target, effect, scope); the action is permissible for the requesting session; the session is authorized and device-bound.
5. **The server records the decision exactly once.** The decision record is idempotent: a retransmitted decision returns the existing record, never a second one (§10.5).
6. **The server returns the authoritative result.** Only now does a decision exist in the estate.
7. **The client renders the authoritative result.** What the operator sees after step 7 is truth; what the operator saw before it was a proposal.

Three failure branches, each with its scenario:

**Branch A — intent changed.** If the digest presented does not match the current intent (target, effect, or scope changed after the card rendered), the server rejects and the client presents the *new* intent. *Scenario:* the white-paper PDF is regenerated with a corrected figure between card render and tap. The tap's digest references the old bytes. The server rejects; the card re-renders against the new digest; the operator approves — or doesn't — the artifact as it actually is. No approval ever attaches to unseen bytes.

**Branch B — intent expired.** If the intent's expiry has passed, the client disables the control and refreshes. *Scenario:* an approval to post the hourly campaign meme sits open on the iPad while the operator takes a call; the intent expires. The button greys with "this request expired — a fresh intent has been prepared." The operator reviews the fresh intent, which re-binds the current artifact digest. Expiry is not an error; it is the mechanism by which "approval at the last safe moment" (Paper I) is enforced.

**Branch C — offline.** If the device has no path to the server, there is no local approval — only a *pending gesture*. *Scenario:* the operator taps "Approve" on the Watch in a tunnel. The Watch stores "the operator wishes to review intent ai-9917" — not consent, and labeled as such. On reconnect, the client fetches the *current* intent and presents it fresh; the operator confirms again. An offline tap can never become an approval, because the tap was never validated against the intent as it stands at decision time. This is the direct implementation of INV-A5.

## 9.7 Conflict Resolution

| Conflict | Resolution | Rationale |
|---|---|---|
| Two devices show different status | Server state wins | Only the single writer's record is authoritative; clients hold views, not votes. |
| Two devices attempt approval | First valid decision recorded wins | Validation is atomic at the server; the loser's tap returns the winner's record (§10.5). Determinism beats fairness here — the operator sees one outcome. |
| Client cache says operational, source expired | Render `unknown` / reduced confidence | A freshness stamp that has lapsed is a fact about ignorance, and ignorance must be visible (INV-S1, INV-S4). |
| Memory says X, live source says Y | Live source wins for current facts | Memory is the durable record of what was true; the live source is what is true. Conflating them is how stale-state manipulation succeeds (§11.5). |
| Durable memory contradiction | Orchestrator reconciles | Contradictions in the long-term record need provenance judgment, not last-write-wins; only the orchestrator has the full history. |
| Notification arrives after state changed | Notification is a hint, not truth | Hints carry no sequence authority; the client re-reads before acting. A late hint that contradicts current state is discarded, not reconciled. |
| Evidence packet updated | New revision; old immutable | Evidence is append-only. "Updating" a packet creates a successor revision; the original remains addressable forever, so no approval's basis can be retroactively altered. |
| Artifact changed after approval | Approval invalid; new approval required | The digest binds approval to exact bytes (INV-A2, INV-A3). New bytes, new intent, new decision. No exceptions, including "trivial" changes. |

## 9.8 Per-Device Guarantee Matrix

| Device | Read behaviour | Approval behaviour | Failure behaviour | Cache policy |
|---|---|---|---|---|
| iPhone (command) | Fresh fetch for consequential reads; stamped cache for status | Full approval flow (§9.6); device-bound session; local auth for high-risk | Explicit unknown states; retry with fresh token, never replay of stale token | Short-TTL status cache; no caching of intents past `fresh_until` |
| Watch (wrist gate) | Status only; minimal payload | Confirm-or-defer on pre-validated intents; offline → pending gesture only | Silent failure forbidden: every tap gets a visible outcome or a visible deferral | Minimal cache; hints only, re-fetch on wrist raise for consequential views |
| iPad (review desk) | Revision-stable evidence reads; long sessions | Extended review; expiry-aware (Branch B common here) | Stale-revision rejection surfaces as "refreshed — please re-read" | Longer-TTL evidence cache keyed by digest; status re-fetched per session |
| TV (ambient wall) | Status renders only | No approvals, ever | Degrades to ambient "unavailable" rather than alarming | Aggressive cache; freshness stamp always visible; never actionable |
| Vision Pro (spatial) | Full reads; immersive evidence review | Full approval flow when device ships; provisional until then | Same as iPhone once live | Same as iPad once live; provisional |

**iPhone.** The command surface carries the highest attention budget and the highest privilege: it is where briefs are issued, approvals granted, and consequences reviewed. Its privacy ceiling is the operator's own — full content, gated by device-local authentication for high-risk approvals (the approval-fatigue control in §11.5). Because it is the most-used surface, it is also the most likely to hold a stale token; hence the short TTL and the hard rule that intents are never cached past `fresh_until`.

**Watch.** The wrist gate operates on a five-second attention budget (Paper III): a buzz means "delay changes the outcome," and the response is confirm or defer — never compose, never review at length. Its privacy ceiling is deliberately low: minimal payloads, no sensitive content in notifications (notification redaction, §11.4), because a wrist is glanced at in public. Offline taps degrade to pending gestures (Branch C), and the design forbids the worst Watch failure — a tap that silently does nothing, leaving the operator believing a consequence was authorized.

**iPad.** The review desk is where long-form evidence is actually read: evidence packets, artifact diffs, approval histories. Its attention budget is measured in minutes, which makes it the natural home of Branch B — intents expiring mid-review. Its cache policy reflects its role: evidence cached by digest (safe, because digests are immutable addresses), status always re-fetched. The iPad is the surface where "stale data cannot masquerade as current" is most visibly tested, because it is where the operator spends the most time looking at almost-current things.

**TV.** The ambient wall is a shared surface in a shared room, and its contract is the strictest in the estate: *states, never contents* (Paper III). It renders "3 routines operational, 1 paused" — never the content of an email, a health metric, or an approval's target. It approves nothing, it acts on nothing, and its failure mode is graceful dimming to "unavailable" rather than any alarm that would leak information to a room. Its cache is aggressive because its reads are the least consequential; its freshness stamp is always visible because its reads are the stalest.

**Vision Pro.** The spatial estate does not yet exist in the operator's hands; its row in the matrix is therefore provisional, marked as such, and bound by the same contract the day it ships: full reads, full approval flow, iPad-class caching. The point of stating it now is that the contract precedes the device — no surface joins the estate without first accepting the single-writer rule (§9.3).

## 9.9 Phase 3 Exit Criteria

- [ ] No device can become a source of truth: every client mutation path requires server validation, verified by fault-injection tests.
- [ ] Approval conflicts resolve deterministically: two-device approval races always produce exactly one recorded decision, under test.
- [ ] Stale data cannot masquerade as current: every client render path carries a freshness stamp or degrades to `unknown`.
- [ ] Offline taps cannot become approvals: offline gestures are stored as intent-to-review and re-validated on reconnect; no test path converts a gesture into consent.
- [ ] Behaviour verified under clock skew (device timestamps ±5 minutes) and network loss (partition during each of the 7 approval steps).
- [ ] Consistency contract published as a specification: the guarantee matrix, the single-writer rule, and the conflict-resolution table are written for external implementers, not only for the estate's own clients.

## Open Questions

1. **Quantitative freshness bounds.** The model requires `fresh_until` on every record but does not set the bound per operation class. What is the right TTL for Watchtower status on the TV versus an approval intent on the iPhone? This needs measurement, not assertion.
2. **Hint sequencing.** Should notification hints carry monotonic sequence numbers so clients can detect *lost* hints, not merely late ones? The current model treats hints as unordered; loss detection would strengthen the "hint, not truth" guarantee at the cost of client complexity.
3. **Clock-skew tolerance.** The exit criteria propose ±5 minutes, but the revision token's timestamp is advisory. Should skew beyond tolerance invalidate a session, or merely annotate the record? The security implications are explored in §11.4; the consistency contract should state the rule.
4. **Memory-correction revision domain.** Should memory corrections share the work-item revision counter, or carry their own revision domain with its own tokens? The roadmap places reconciliation with the orchestrator; the token mechanics are unspecified.
5. **Vision Pro provisionality.** The matrix row for Vision Pro is a promise, not a test result. Phase 3 cannot be fully closed for that surface until the device exists in the estate; the exit criteria should record the surface as explicitly out of scope until then.
