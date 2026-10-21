# 7. Phase 1 — Formal State Machine Proof

*Proving that the canonical machine of §6 cannot enter illegal or unsafe states under the defined failure model. This section uses the glossary of §5 and proves the machine of §6; it specifies no new states and no new transitions.*

## 7.1 Objective and Method Choice

The objective is stated exactly by the roadmap: prove that the work-state machine cannot enter illegal or unsafe states under the defined assumptions. "Fixed" has ten concrete meanings (§7.6 turns them into proof obligations): no completion without acceptance evidence; no consequential execution without valid approval; mutated or expired approvals cannot lead to execution; unknown cannot render as operational; paused cannot be confused with failed; failure events cannot silently become completion; optimistic completion is unreachable; offline approval cannot become authoritative; duplicate taps cannot duplicate execution; stale state cannot masquerade as current.

The first decision is the modelling language. The roadmap recommends TLA+ or Alloy, notes Coq/Lean for stronger proof, and allows property-based state-machine testing if formal tools prove too heavy. The comparison below is the basis for the recommendation.

| Method | Expressiveness | Learning curve | Tooling | Fit for this system |
|---|---|---|---|---|
| **TLA+** | Temporal logic over state machines; native liveness ("every request eventually resolves") and safety ("no bad state reachable") | Moderate; PlusCal lowers the entry cost | TLC explicit-state model checker; mature, scriptable | Excellent: the artefact is a 12-state machine with interleaved events (duplicate taps, out-of-order delivery); TLA+ is designed for exactly this |
| **Alloy** | Relational first-order logic; strong for structural constraints and bounded scope checking | Moderate; relational idiom is unfamiliar to most engineers | Alloy Analyzer; automatic counterexample generation | Good for contract structure (digest relations, revision binding) but weaker on temporal behaviour and liveness |
| **Promela/SPIN** | Process algebra; strong for concurrent interleavings and protocol verification | Moderate; C-like syntax | SPIN model checker; excellent for message-passing protocols | Good, but the machine is a single state machine with event interleavings, not a network of communicating processes; the fit is adequate, not natural |
| **Coq/Lean** | Full dependent-type proof assistants; the strongest guarantees available | Steep; months to productive proof engineering | Superb but labour-intensive; every lemma is manual | Overkill for the safety properties at issue and disproportionate to a 12-state machine; the cost would consume the programme |
| **Property-based state-machine testing** | Executable: generates event sequences and asserts invariants | Low; standard engineering practice | Hypothesis (stateful), fast-check; integrates with CI | Excellent as engineering fallback and as Phase 2 Layer 2, but it tests rather than proves — it finds counterexamples without certifying absence |

**Recommendation: TLA+ as the primary modelling language, Alloy as a secondary structural check, property-based state-machine testing as the engineering fallback.**

The defence is as follows. The properties to be shown are temporal: safety ("no reachable illegal state") and liveness ("every `approval_requested` eventually resolves to granted, denied, or expired"; "no work item waits in `awaiting_approval` past expiry without a transition"). TLA+ expresses both natively, and TLC checks both over the finite state space — twelve work states, six approval states, boolean and small-enum auxiliaries — which is well within explicit-state enumeration once the model abstracts timestamps to an ordered `now` and digests to symbolic values. PlusCal makes the model readable to engineers who will never learn raw TLA+, which matters because the model must be reviewed, not merely run. Alloy earns its secondary place for the structural half of the problem: the digest-binding relation (intent → digest → decision), revision immutability, and the contract schemas' relational constraints are precisely the bounded relational properties Alloy checks best. The fallback is honest and already scheduled: if TLA+ proves too heavy for the team, the property-based state-machine tests of Phase 2, Layer 2 become the primary evidence, and the doctoral claim is downgraded from "model-checked proof" to "systematic falsification attempted and failed" — a weaker but still substantive claim, and one the limitations section (§15) must then state plainly.

**Open question OQ-4 — TLA+ or Alloy as the single primary language, if the programme can fund only one?** The roadmap leans toward either. **Recommendation:** TLA+, because the failure model (§7.5) is dominated by event interleavings (duplicate taps, out-of-order events, expiry racing a tap), and interleavings are TLA+'s home ground. Alloy remains the recommended second tool for contract structure, not a rival primary.

## 7.2 State Variables

The model carries ten state variables — the roadmap's minimum set — each with a type and a meaning. Abstraction discipline: timestamps are modelled as integers on a totally ordered `now`; digests are modelled as symbolic values where equality is the only operation (the model checks binding, not cryptography — collision resistance of the hash function is an assumed lemma, stated in §7.6).

| Variable | Type | Meaning |
|---|---|---|
| `work_state` | Enum of the 12 canonical states | The work item's current state (§6.1); exactly one value at a time |
| `approval_state` | Enum: `none`, `requested`, `granted`, `denied`, `expired`, `recorded` | The lifecycle position of the current approval intent; `recorded` means the server has persisted the decision |
| `intent_digest` | Symbolic digest value | The digest of the canonical intent as presented to the operator; the binding anchor |
| `intent_expiry` | Integer timestamp | The instant after which the intent is dead; compared against `now` |
| `evidence_exists` | Boolean | Whether a complete evidence packet is attached to the current revision |
| `acceptance_passed` | Boolean | Whether the stated acceptance test passed against observed output |
| `execution_observed` | Enum: `none`, `success`, `failure`, `unknown` | What observation says about the consequential action's outcome |
| `source_freshness` | Enum: `fresh`, `stale`, `unknown` | Whether live-source readings are within their `fresh_until` |
| `operator_pause` | Boolean | Whether the operator has paused the work item or service |
| `observation_status` | Enum: `observed`, `unavailable` | Whether the work item's state can currently be established |

Two variables deserve a note on why they are separate. `evidence_exists` and `acceptance_passed` are not the same fact: a packet can exist and be incomplete (missing tests), and a test can pass while its packet is malformed. The guard for completion requires both, and the separation is what lets the model distinguish "no evidence" from "bad evidence" — different failures, different tests (§8). Similarly, `approval_state` separates `granted` (the operator tapped) from `recorded` (the server persisted): the gap between those two values is exactly where INV-A5 (offline approval) lives, and a model that merged them could not express the illegal state at all.

## 7.3 Transition Guards

Each safety-critical transition carries a guard — the formal version of the prose guards in §6.2. The guards are written here in predicate style for readability; the TLA+ model renders them as enabling conditions on actions. `now` is the model's current time; `digest(i)` is the recomputed digest of intent `i`.

**`can_enter_completed`** ≜ `work_state = verifying ∧ evidence_exists ∧ acceptance_passed ∧ ¬failure_observed`. Completion requires the conjunction: the machine must be in `verifying` (F1), a complete packet must exist (INV-C1), the test must have passed (INV-C2), and no failure may have been observed (INV-C2's second half). Weakening any conjunct must produce a counterexample (§7.7).

**`can_enter_executing`** ≜ `work_state = awaiting_approval ∧ approval_state = recorded ∧ now < intent_expiry ∧ digest(current_intent) = intent_digest ∧ ¬mutated ∧ ¬operator_pause`. Execution requires the recorded — not merely tapped — grant (INV-A5), a live intent (INV-A4), a digest match against the current intent (INV-A3), and no pause. Note that `digest(current_intent) = intent_digest` is evaluated at transition time, not cached from request time: this is the guard-level expression of "changed target/effect invalidates prior approval."

**`can_render_operational`** ≜ `observation_status = observed ∧ source_freshness = fresh ∧ ¬operator_pause ∧ work_state ∉ {failed, paused, unknown, cancelled, blocked}`. Rendering is a guarded act, not a default: operational is shown only when observation is available, sources are fresh, no pause is in effect, and the machine is in a state consistent with operation. This guard is the formal content of INV-S1 and INV-S4.

**Rendering guards for the non-operational states** complete the picture, because the illegal states of §7.4 include rendering failures:

- `render_paused` ≜ `operator_pause ∧ observation_status = observed` — paused is rendered only when the pause itself is observed, never inferred from silence (INV-S2).
- `render_failed` ≜ `failure_observed ∧ observation_status = observed ∧ ¬operator_pause` — failure rendering requires observed failure and yields to pause when both are true, because the operator's intent outranks the machine's diagnosis.
- `render_unknown` ≜ `observation_status = unavailable ∨ source_freshness = unknown` — unknown is forced, not chosen; whenever observation fails or freshness is unknown, the other rendering guards' preconditions fail and this one holds (INV-S1).
- `render_degraded` ≜ `observed_impairment ∧ observation_status = observed` — degraded requires a defined, observed impairment signal crossing its threshold (INV-S3); suspicion is not impairment.

The guards compose: exactly one rendering guard holds in every reachable state, which the model checks as a coverage property — there is no reachable configuration in which the renderer has no legal rendering and no reachable configuration in which two renderings are simultaneously legal.

## 7.4 The Illegal-State Catalogue

Each illegal state from the roadmap §1.4, with a plain-language account of the harm if it were reachable. These are the states the proof must show unreachable; §8 turns each into at least one executable test.

1. **Completed without evidence packet.** The machine reaches `completed` with `evidence_exists = false`. Harm: the operator — and any downstream routine — acts on output whose provenance, tests, and gaps were never recorded. Optimistic completion becomes indistinguishable from verified completion, and the doctrine "no proof, no done" becomes unenforceable because there is no artefact to audit.
2. **Executing without valid approval.** The machine reaches `executing` with `approval_state ≠ recorded`, an expired intent, or a digest mismatch. Harm: consequential effects — sends, purchases, publications, deletions — occur without the operator's authority. This is the single most severe illegal state: every other property is about truthfulness, but this one is about agency.
3. **Approved intent with changed target/effect.** `digest(current_intent) ≠ intent_digest` while `approval_state = recorded`. Harm: the bait-and-switch — the operator approves sending a draft to one recipient and the machine sends a different text to another, or approves a $15 stake and the machine places $150. The approval ceremony is performed and the authority it confers is spent on something else.
4. **Unknown rendered as operational.** `observation_status = unavailable` while the renderer shows operational. Harm: the operator trusts a guess. A service whose state cannot be established is shown as healthy; the operator takes no corrective action precisely when corrective action is most needed. This is how outages hide inside green dashboards.
5. **Paused rendered as failed.** `operator_pause = true` while the renderer shows failed. Harm: the operator "fixes" an outage that is actually their own stop — restarting a service they meant stopped, re-running work they meant halted, and generating the exact consequential effects the pause was meant to prevent.
6. **Optimistic completion from delegated claim.** `completed` reached on a subagent's fluent claim with `acceptance_passed = false`. Harm: delegation becomes abdication. The orchestrator's accountability for acceptance (INV-C3) collapses, and the estate learns to report done when work merely sounds done — the failure mode the entire evidence discipline exists to prevent.
7. **Offline approval becoming authoritative.** `approval_state` transitions to `recorded` from a client gesture without server validation. Harm: a tap made in a tunnel, on a stale card, or by a replayed message becomes consent. The consequence boundary — the one place where the operator's authority is absolute — becomes forgeable.

## 7.5 The Failure Model

Thirteen failure conditions, per the roadmap §1.5. For each: how the model represents it, and which illegal states it threatens. The model does not assume these failures away; it assumes them *in* and shows the guards hold regardless.

1. **Network interruption.** Modelled as event loss and delay: `execution_observed` remains `none` while the action may or may not have occurred, and `observation_status` may flip to `unavailable`. Threatens illegal states 1 and 7 — the temptation is to complete on dispatch ("it probably went through") or to treat a retried tap as a fresh grant.
2. **Expired approval.** Modelled as `now` advancing past `intent_expiry` while `approval_state = requested`. Threatens illegal state 2: a grant arriving after expiry must not open the gate. The model checks that the expiry transition (T10) is taken and that a late `approval_granted` is rejected, not queued.
3. **Mutated intent.** Modelled as a change to any intent field between request and decision, making `digest(current_intent) ≠ intent_digest`. Threatens illegal state 3 directly. The model checks the digest comparison at transition time (T9), including the adversarial case where the mutation arrives *with* the grant in the same event batch.
4. **Duplicate tap.** Modelled as two `approval_granted` events for the same intent, possibly with network duplication multiplying them further. Threatens a double-execution variant of illegal state 2. The model checks that the second grant is idempotent — it returns the recorded decision and produces no new transition — per the idempotency key of Phase 4.
5. **Stale live source.** Modelled as `source_freshness = stale`: readings exist but are past `fresh_until`. Threatens illegal state 4 — the renderer showing operational on expired readings — and illegal state 1, where verification passes against yesterday's source. The model checks that stale freshness forces unknown rendering and blocks the completion guard's source-dependent conjuncts.
6. **Missing evidence.** Modelled as `evidence_exists = false` at the `verifying → completed` boundary, including the partial case (packet exists, tests missing). Threatens illegal state 1. The model checks that the completion guard's conjunction fails closed — missing evidence is not "evidence pending," it is a guard failure.
7. **Subagent completion without proof.** Modelled as a worker emitting a completion claim while `acceptance_passed = false` and `evidence_exists = false`. Threatens illegal state 6. The model checks that the claim is treated as verification input — it can move `in_progress → verifying` — but can never satisfy `can_enter_completed`.
8. **Router failure.** Modelled as the usage router (currently shadow mode, local policy) producing no recommendation or a corrupt one. Threatens no illegal state directly — the router recommends paths, never approves consequences (INV-R1) — but the model checks the fallback: routing failure degrades to direct orchestration, never to an unguarded transition. This is the formal shadow of INV-R5.
9. **Device clock skew.** Modelled as `now` differing between the client surface and the server by a bounded skew Δ. Threatens illegal states 2 and 4: a skewed client may present an "unexpired" intent the server considers dead, or a "fresh" reading the server considers stale. The model checks that all time comparisons use server `now` and that the skew bound is explicit — **open question OQ-5:** the acceptable skew bound Δ (recommendation: 60 seconds, with any decision inside the skew window re-validated rather than trusted).
10. **Out-of-order events.** Modelled as event permutation: `approval_expired` arriving before `approval_granted`, `execution_observed` arriving before `execution_started`. Threatens illegal states 2 and 7 — a grant processed after its expiry, or an observation credited to the wrong execution. The model checks event histories against the revision counter: stale events (revision behind current) are rejected, not applied.
11. **Missing permissions.** Modelled as a required capability absent at execution time. Threatens the `executing → failed` path being skipped in favour of silent partial execution. The model checks that missing permission produces `failure_observed` and the any-state transition to `failed` — visible failure, never silent degradation into a false success.
12. **Credential challenge.** Modelled as an authentication demand (re-authentication, Secure Vault unlock) arriving mid-flow, e.g. between `approval_granted` and `execution_started`. Threatens illegal state 7's cousin: execution proceeding on a grant whose authentication has lapsed. The model checks that the challenge suspends the transition — the grant is held, not honoured, until authentication is re-established — and that a denied challenge moves the work item to `blocked`, not `failed`.
13. **Operator pause.** Modelled as `operator_paused` arriving in any state, including mid-`executing`. Threatens illegal state 5 (pause rendered as failure) and a pause-during-execution race: the pause must prevent new consequential steps without corrupting the in-flight step's observation. The model checks T18's guard and the rendering precedence (`render_paused` outranks `render_failed`).

## 7.6 Proof Obligations

Numbered, traceable, and each falsifiable — §7.7 explains what falsifiability demands of them.

- **PO-1.** No reachable state satisfies `work_state = completed ∧ ¬(evidence_exists ∧ acceptance_passed)`. (Fixed-meaning 1; illegal state 1.)
- **PO-2.** No reachable state satisfies `work_state = executing ∧ ¬(approval_state = recorded ∧ now < intent_expiry ∧ digest(current_intent) = intent_digest)`. (Fixed-meaning 2; illegal state 2.)
- **PO-3.** For every reachable transition into `executing`, the intent digest at decision time equals the digest at request time; any mutation forces rejection. (Fixed-meaning 3; illegal state 3.)
- **PO-4.** In every reachable state with `observation_status = unavailable`, the only legal rendering is unknown. (Fixed-meaning 4; illegal state 4.)
- **PO-5.** In every reachable state with `operator_pause = true`, the legal rendering is paused and never failed. (Fixed-meaning 5; illegal state 5.)
- **PO-6.** `evidence_of_failure` from any state leads to `failed` or `blocked`; no event sequence containing `failure_observed` after `verifying` can reach `completed`. (Fixed-meaning 6.)
- **PO-7.** A worker's completion claim with `acceptance_passed = false` can never satisfy `can_enter_completed`. (Fixed-meaning 7; illegal state 6.)
- **PO-8.** No transition to `approval_state = recorded` is enabled by a client gesture alone; recording requires server validation of intent existence, expiry, digest, permissibility, and session. (Fixed-meaning 8; illegal state 7.)
- **PO-9.** Two `approval_granted` events for one intent produce at most one `executing` entry and one consequential effect. (Fixed-meaning 9.)
- **PO-10.** No guard that depends on source truth is satisfiable when `source_freshness ≠ fresh`. (Fixed-meaning 10.)
- **PO-11.** `completed`, `failed`, and `cancelled` are absorbing: no transition leaves them. (F7, §6.3.)
- **PO-12 (liveness).** Every `approval_requested` is eventually followed by exactly one of `approval_granted`, `approval_denied`, or `approval_expired`; no work item remains in `awaiting_approval` past `intent_expiry` without a transition. (The machine must not only be safe but responsive — a gate that never opens or closes is a denial of service against the operator's attention.)

Assumed lemmas, stated explicitly because a proof is only as honest as its assumptions: (a) the digest function is collision-resistant — the model checks binding given distinct digests, not the cryptography; (b) the server's `now` is monotonic within the skew bound of OQ-5; (c) the event history is append-only — the model does not defend against history rewriting, which is a Phase 5 tamper-evidence concern, not a Phase 1 transition concern.

## 7.7 Counterexample Discipline

A model checker that finds nothing has either verified the system or failed to look. The programme distinguishes the two by requiring that every accepted guard earn its place: for each guard in §7.3, the modelling team produces a *weakened twin* — the guard with one conjunct removed — and runs the checker against it. If the weakened guard yields no counterexample, the guard is suspect: either the conjunct is genuinely redundant (and should be removed, simplifying the model) or the failure model is too weak to exercise it (and the failure model must be strengthened). If the weakened guard yields a reachable illegal state, the counterexample is filed as evidence — the trace, the violated obligation, the illegal state reached — and the full guard is accepted as load-bearing.

This is falsifiability as engineering practice, and it is what makes the Phase 1 results doctoral evidence rather than a certificate printed by a friendly tool. A guard that has never been shown to fail when weakened is an assertion; a guard whose weakened twin produces a concrete trace to `executing` without approval is a demonstrated necessity. The counterexample report (§4 deliverables) therefore contains two halves: the illegal states the full model excludes, and the illegal states the weakened models reach. The second half is the more valuable one — it is the proof that the proof was trying.

## 7.8 What Model-Checked Results Would Look Like

The table below is **illustrative** — a specimen of the results artefact Phase 1 must produce, not results already obtained. It shows the shape of the evidence: property, outcome, and the interpretation a committee should draw.

| Property | Illustrative result | Interpretation |
|---|---|---|
| PO-1: no completion without evidence | Holds (0 violations in 4.2M states) | The completion guard's conjunction is sufficient under the failure model |
| PO-2: no execution without valid approval | Holds | The approval gate has no side entrance in the modelled interleavings |
| PO-3: digest binding under mutation | Counterexample found in weakened model (digest check removed); holds in full model | The digest comparison is load-bearing — filed as evidence per §7.7 |
| PO-9: duplicate tap idempotency | Holds | Second grant returns recorded decision; no double execution reachable |
| PO-12: approval requests always resolve | Holds under fairness assumption | Liveness depends on the scheduler eventually processing expiry; the fairness assumption is stated, not hidden |
| OQ-5 skew bound (Δ = 60s) | Counterexample at Δ = 300s (stale grant honoured) | The skew bound is not arbitrary — it is the largest Δ for which PO-2 holds |

The honest row is the last one: it shows a parameter whose value was *discovered* by the checker rather than chosen by intuition. That is the standard to which every quantitative choice in the programme — retry budgets, freshness windows, escalation thresholds — should aspire.

## 7.9 Phase 1 Exit Criteria

- [ ] **Formal model exists.** A TLA+ (or Alloy, per OQ-4) model of the §6 machine, with the ten state variables of §7.2 and the guards of §7.3, is committed under `proofs/state-machine/` and reviewed.
- [ ] **No reachable illegal state.** The checker finds no reachable instance of any §7.4 illegal state under the §7.5 failure model; PO-1 through PO-11 hold.
- [ ] **Liveness shown.** PO-12 holds under stated fairness assumptions; the assumptions are documented, not buried.
- [ ] **Weakened guards produce counterexamples.** For each guard, the weakened twin reaches an illegal state and the counterexample is filed; any guard that cannot be made to fail is either removed or its failure model strengthened, with the reasoning recorded.
- [ ] **Proof obligations documented.** PO-1 through PO-12, the assumed lemmas, and the OQ-5 skew recommendation are written down as the proof's contract with its readers.
- [ ] **Results artefact produced.** A results table in the form of §7.8 — property, outcome, interpretation — with the checker's raw output archived alongside it.
- [ ] **Model and results published.** The formal model, the checker's raw output, and the results table are committed as publishable artifacts — the verification reproducible by anyone with the model checker, not merely asserted by the estate.

When this checklist is green, the machine is proven under its failure model — and the programme turns to the harder question of whether the running estate honours the machine. That is Phase 2.
