# 5. Phase 0 — The Canonical Glossary

*Reconciling the vocabularies of Papers I–III into one normative specification.*

## 5.1 Three Vocabularies, One System

Papers I–III describe the same estate, but each paper coined its vocabulary for its own audience. Paper I (the operating white paper) describes the doctrine chain that every unit of work must traverse:

```text
Role → Live Source → Tool → Artifact → Evidence → Approval → Routine
```

Paper II (the backend technical paper) describes the request lifecycle through which accepted work moves:

```text
Brief → Route → Plan → Execute → Verify → Approve → Handoff
```

Paper III (the front-end paper) describes the operator loop as experienced on the five client surfaces:

```text
Brief → Work → Evidence → Approval → Decision
```

These three formulations are philosophically consistent — the introduction to this paper establishes that — but they are not the same sentence. A formal programme cannot begin from three sentences. Phase 0 exists to produce one: a single canonical glossary in which every term has one normative definition and one owner. The glossary below is that sentence, expanded into 34 terms. Every later section of this paper — the state machine (§6), the formal proof (§7), the invariant catalogue (§8), and the phase specifications that follow — uses these definitions and no others. Where this glossary conflicts with the usage of Papers I–III, the glossary governs; the reconciliation decisions in §5.4 record exactly where such conflicts were found and how they were resolved.

The operator (HgX) should note what this section is not. It does not change the doctrine. Role isolation remains procedural, approval remains the operator's explicit consent at the consequence boundary, and evidence remains observed proof rather than fluent narration. What changes is only that each of those claims now has one name, one definition, and one owning document — so that a model checker, a test suite, and a doctoral committee can all refer to the same thing.

## 5.2 The Compatibility Mapping

The following table maps each element of the three papers' formulations to its canonical term. The mapping is the evidence for the compatibility claim of §5.3; the genuinely divergent cases are taken up as reconciliation decisions in §5.4.

| Paper I (doctrine chain) | Paper II (lifecycle) | Paper III (operator loop) | Canonical term |
|---|---|---|---|
| Role | — (implicit in Brief: the orchestrator's remit) | — | orchestrator; role boundary |
| Live Source | Execute (reads live sources) | — | live source |
| Tool | Route (tool selection) | — | tool; capability |
| Artifact | Execute (output) | Work (output) | artifact |
| Evidence | Verify | Evidence | evidence packet |
| Approval | Approve | Approval | approval intent; approval decision |
| Routine | Handoff (promote stable method) | — | routine |
| — | Brief | Brief | brief |
| — | Route | — | routing decision |
| — | Plan | — | plan |
| — | Verify | — | verification |
| — | Handoff | — | handoff |
| — | — | Decision | decision packet |

Three observations follow from the table. First, `Brief`, `Evidence`, and `Approval` are already shared vocabulary across the papers that use them; no reconciliation is required, only canonisation. Second, several lifecycle stages name *activities* (Route, Plan, Verify) rather than *governed objects*; the canonical model governs objects (the routing decision, the plan, the evidence packet) because objects can carry digests, revisions, and acceptance tests while activities cannot. Third, Paper III's `Decision` and Paper II's `Approve` name the same operator moment from opposite sides of the glass: the operator experiences a decision; the estate records an approval stage. The decision packet (§5.6) is the artifact of that moment, and the two names are thereby reconciled without either paper being wrong.

## 5.3 Why the Vocabularies Are Compatible

Compatibility here is a precise claim, not a diplomatic one. Two vocabularies are compatible for the purposes of this programme if every element of each can be mapped to the canonical model without changing what the estate does — that is, the mapping is a renaming plus a small number of explicit structural decisions, and no paper's operational semantics are altered.

The doctrine chain (Paper I) is a governance ordering: it says which contracts a unit of work must satisfy and in what sequence authority is engaged. The request lifecycle (Paper II) is an execution ordering: it says what the orchestrator does, step by step, to move work through those contracts. The operator loop (Paper III) is an observation ordering: it says what the operator sees and where the operator's authority enters. Three orderings of one process, each complete for its audience, each naming the joints it cares about. The doctrine chain does not name "Plan" because planning is the orchestrator's internal business, not a governance joint. The lifecycle does not name "Role" because the orchestrator is the subject of the lifecycle, not one of its stages. The operator loop collapses "Route → Plan → Execute → Verify" into "Work" because the operator neither routes nor plans; the operator sees work being done and then sees evidence.

None of these are contradictions. They are projections — the same object viewed from the governance axis, the execution axis, and the observation axis. The canonical model in §6 is the object itself: the work-state machine, whose states and events give each projection a shared referent. Once the machine exists, "the operator loop's Evidence" and "the lifecycle's Verify" are no longer two phrases that happen to mean similar things; they are two names for the transition `in_progress → verifying` and the object it produces. That is what freezing the contracts means, and it is why Phase 0 precedes proof: you cannot model-check a system whose states have three names.

## 5.4 Reconciliation Decisions

Where the projections genuinely differed in structure — not merely in naming — this section records the decision taken, its rationale, and the section that owns its consequences. These decisions are part of the normative spec, not commentary on it.

**RD-1 — "Execute" is split across two machine states.** Paper II's Execute stage covers both non-consequential tool work (reading a calendar, drafting text, computing a figure) and consequential action (sending, publishing, purchasing). The canonical machine places non-consequential execution *inside* `in_progress` and reserves the `executing` state for approval-gated consequential execution. Rationale: the approval gate is the safety-critical boundary of the estate, and a boundary that is a stage label rather than a machine state cannot carry a transition guard. Consequences owned by §6 (transition table) and §7 (the `can_enter_executing` guard).

**RD-2 — Approval is a state–event pair, not a stage.** Paper II's "Approve" and Paper III's "Approval" both become the `awaiting_approval` state together with the events `approval_requested`, `approval_granted`, `approval_denied`, and `approval_expired`. Rationale: an approval is not something the estate does; it is something the estate waits for, and waiting is a state with an expiry. This decision is what makes INV-A4 (expired approval unusable) expressible as a guard rather than a hope. Owned by §6.

**RD-3 — "Handoff" is an event and a packet, not a state.** Paper II's final stage, "Handoff and capture," decomposes into the `verifying → completed` transition (acceptance passed, §6), the delivery of the handoff to the operator, and the promotion of stable method or durable facts to their stores. Rationale: completion is a property of the work item (a state); handoff is the communication of that property plus its evidence. Conflating them would let a delivered message masquerade as a verified result — precisely the optimistic-completion failure INV-C5 forbids. Owned by §6 and §8.

**RD-4 — "Decision" (Paper III) and "Approve" (Paper II) meet in the decision packet.** The operator's tap is a decision event; the estate's stage is approval. The decision packet — carrying `intent_id`, `intent_digest`, the decision, the device session, and the server-recorded timestamp — is the single artifact both names describe. Rationale: this makes INV-A5 (offline approval cannot create authoritative consent) testable, because "authoritative" now has a definition: recorded by the server, digest-matched, timestamped. Owned by §6 (contract schema overview) and Phase 3.

**RD-5 — A routine is a brief generator, not a work-item state.** Paper I's "Routine" and Paper II's "promote to routine" describe scheduling, not a phase of work. Canonically, a routine is a scheduled skill that has earned repetition; each firing emits a `brief_received` event, and the resulting work item traverses the machine independently. Rationale: routines must be pausable, degradable, and observable by the Watchtower as services — none of which is expressible if "routine" is a terminal stage of a work item. Owned by §6 (Watchtower contract) and the glossary definition below.

**RD-6 — Role is a governance boundary; subagent and worker are runtime constructs.** Paper I's "Role" is not a kind of process. A role is a named, bounded remit with its own memory scope and approval posture; a subagent is the estate's implementation of delegated work; a worker is the generic term for any delegated execution unit. A subagent executes *within* a role; the role is not the subagent. Rationale: this preserves Paper I's honest statement that role isolation is procedural — the boundary is doctrine, discipline, and filesystem convention, not a process boundary — while giving Phase 5 a clean subject (the role) and a clean mechanism (the worker) to formalise. Owned by §11 (Phase 5).

## 5.5 Open Questions

The following decisions are genuinely unresolved. Each is marked as required, with a recommendation and the reason the programme can proceed with the recommendation as a working assumption.

**Open question OQ-1 — Should `verifying` distinguish human verification from machine verification?** The machine's guard for `verifying → completed` is `acceptance_passed`; the guard does not care who ran the acceptance test. **Recommendation:** keep one `verifying` state and record the verification method (human, automated test, external observation) as provenance inside the evidence packet. Rationale: splitting the state doubles the transition table for no guard-level benefit, and the distinction that matters — whether the acceptance test was stated before the output was observed — is a property of the packet, not the state. If Phase 7's doctoral evidence requires human-verification rates as a metric, the packet provenance already supports it.

**Open question OQ-2 — Should `blocked` distinguish blockage-on-operator from blockage-on-source?** A work item can stall because the operator has not answered a clarifying question or because a live source is unreachable; the recovery paths differ. **Recommendation:** keep one `blocked` state and record the blockage cause in the execution record. Rationale: as with OQ-1, the guard structure is identical (blockage cleared → `in_progress`), and cause is diagnostic metadata. The Watchtower's rendering may surface the cause without the machine needing a new state.

**Open question OQ-3 — Where does an expired approval return?** The roadmap skeleton lists `awaiting_approval → cancelled` but does not say where `approval_expired` leads. Cancelling the work because the operator was slow to decide conflates intent expiry with work abandonment. **Recommendation:** `approval_denied → cancelled` (the operator refused the consequence; the work item ends), while `approval_expired → in_progress` (the intent lapsed; the work item survives and may issue a fresh `approval_requested` with a new intent and revision). Rationale: expiry is a property of the intent, not a verdict on the work — INV-A4 kills the approval, not the task. This recommendation is adopted in §6's transition table; if the operator prefers expiry to cancel work items, the change is one row.

## 5.6 The Canonical Glossary

Each term carries exactly one normative definition and one owner. The owner is the phase and specification document responsible for the term's formal treatment; questions of meaning are settled by the owner, and no other document may redefine the term.

**Work item.** One bounded unit of requested estate work, identified by a `work_id`, carrying a revision counter and a single current state from the canonical machine. *Owner: Phase 0 spec (`spec/state-machine.md`).*

**Brief.** The structured submission that creates a work item: objective, audience, success criteria, tools, constraints, and deadline, from the operator or an authorized routine. A brief is well-formed only if its success criteria are stated as acceptance tests. *Owner: Phase 0 spec.*

**Artifact.** Inspectable output produced by work — a file, a message draft, a figure, a decision record. An artifact is content-addressed by digest and bound to a work-item revision; fluent text that has not been observed against its acceptance test is not an artifact. *Owner: Phase 0 spec.*

**Evidence packet.** The structured proof bundle attached to work: artifact digests, live-source observations with freshness stamps, test results, approval references, and explicitly listed gaps. The packet is the unit of verification; "no proof, no done" is the rule that no work item completes without one. *Owner: Phase 0 spec (`contracts/evidence-packet.schema.json`).*

**Approval intent.** The exact consequential action awaiting the operator: action, target, effect, scope, revision, and expiry, bound together by the intent digest. An intent is not a request for general permission; it is a fully specified consequence the operator may grant or deny. *Owner: Phase 0 spec (`contracts/approval-intent.schema.json`).*

**Intent digest.** The cryptographic digest over the canonical serialisation of an approval intent. The digest is the binding mechanism: any change to target, effect, scope, or revision changes the digest and invalidates prior approval (INV-A3). The exact canonicalisation and hash function are defined by the Phase 0 spec. *Owner: Phase 0 spec.*

**Approval decision.** The operator's recorded verdict on an intent — granted or denied — captured with `intent_id`, `intent_digest`, device session, timestamp, and authentication method. A decision is authoritative only when recorded by the server; a tap on a client surface is a gesture until the server records it (INV-A5). *Owner: Phase 0 spec (`contracts/decision-packet.schema.json`).*

**Routine.** A scheduled skill that has earned repetition through reviewed, accepted work. A routine is a brief generator, not a work-item state: each scheduled firing emits `brief_received`, and the resulting work item has its own lifecycle. Routines are silent by default and observable by the Watchtower. *Owner: Phase 0 spec.*

**Live source.** An authoritative current-state system — a calendar, a mailbox, a price feed, a device sensor — that owns some changing fact about the world. Current facts are read from live sources at decision time; they are never inferred from memory. *Owner: Phase 0 spec.*

**Durable memory.** Identity, preferences, principles, and commitments that persist across sessions: the curated `MEMORY.md`, relationship pages, and dated notes. Durable memory carries what the operator *is* and *has decided*; it never carries what the world *currently* is — that is the live source's job, and the orchestrator reconciles the two without merging them by assumption. *Owner: Phase 0 spec.*

**Orchestrator.** The single authoritative control plane of the estate: it receives briefs, routes, plans, delegates, verifies, requests approval, and owns the final handoff. There is exactly one orchestrator; clients render, subagents execute bounded work, the router recommends — none of them orchestrate. *Owner: Phase 0 spec.*

**Subagent.** The estate's implementation of delegated work: an independent bounded job briefed by the orchestrator, whose output is verification input, never a completion signal. The orchestrator remains accountable for acceptance of delegated work (INV-C3). *Owner: Phase 0 spec.*

**Worker.** The generic term for any delegated execution unit, including subagents and any future execution mechanism. In the current estate every worker is a subagent; the term exists so the specification survives the mechanism. *Owner: Phase 0 spec.*

**Handoff.** The delivery to the operator of a completed work item's result, evidence packet, gaps, and links, together with the promotion of stable method or durable facts to their stores. Handoff is the communication of completion, not completion itself (RD-3). *Owner: Phase 0 spec.*

**Revision.** The monotonically increasing counter on a work item, artifact, evidence packet, or intent. Every mutation creates a new revision; old revisions are immutable. Revision binding is what prevents an approval granted against yesterday's artifact from executing against today's (INV-A2, INV-E2). *Owner: Phase 0 spec.*

**Idempotency key.** The deterministic key `hash(work_id, intent_id, intent_digest, action, target, scope, revision, operation_class)` that identifies one logical consequential operation across retries, duplicate taps, and network failures. The server records the key's execution state; a repeated key returns the recorded outcome instead of executing again. *Owner: Phase 4 idempotency spec (`spec/idempotency.md`).*

**Execution record.** The server-side record of one consequential operation's lifecycle: `prepared → approved → execution_requested → execution_started → execution_observed / execution_failed / execution_unknown → completed / cancelled`, with the idempotency key, approval reference, attempt count, observed result, and safe-to-retry flag. *Owner: Phase 4 idempotency spec.*

**Saga.** The governed transaction pattern for consequential work, used because the estate assumes no distributed transactions: prepare → approval → execute → verify → record evidence → compensate (only if approved and possible). Each step has its own approval and evidence requirements; there is no silent rollback of consequential effects. *Owner: Phase 4 idempotency spec.*

**Capability.** A formal grant with seven fields — subject, action, object, scope, condition, expiry, approval requirement, evidence requirement — specifying exactly what a worker, routine, or connector may do. Capabilities are the unit of least privilege in Phase 5. *Owner: Phase 5 security spec (`spec/security-threat-model.md`).*

**Trust boundary.** A named interface across which trust is not transitive: the ten boundaries of the roadmap (devices ↔ estate edge, edge ↔ orchestrator, orchestrator ↔ tools, ↔ subagents, ↔ connectors, ↔ external web, ↔ Secure Vault, ↔ external router, client ↔ notification system, personal ↔ shared surfaces). Data crossing a boundary is validated; authority crossing a boundary is re-established. *Owner: Phase 5 security spec.*

**Freshness.** The property of an observation that it was taken recently enough to decide on: every live-source reading carries `observed_at` and `fresh_until`. A reading past `fresh_until` is stale and cannot satisfy a guard that requires current truth (INV-S4, INV-E5). *Owner: Phase 3 consistency spec (`spec/consistency.md`).*

**Acceptance test.** A bounded check with a stated test, applied against observed output — never against fluent text. Every brief states its acceptance tests; `verifying → completed` requires them passed and recorded in the evidence packet (INV-C1, INV-C2). *Owner: Phase 0 spec.*

**Repair cost.** The human effort required to correct an accepted artifact that should not have been accepted: measured in minutes of operator or reviewer time plus the downstream cost of the error. One of the objective function's penalty terms in router evaluation. *Owner: Phase 6 router spec (`spec/router-policy.md`).*

**Attention cost.** The operator's scarce resource, measured as interruptions weighted by context-switch severity: a silent routine costs nothing; an approval request costs a decision; an ambiguous alert costs investigation. The estate's first duty is to spend it only where evidence and authority require. *Owner: Phase 6 router spec.*

**Shadow mode.** The router's current operating posture: it observes decisions and logs recommendations without overriding orchestrator judgment. Shadow mode is how the estate gathers labelled decision history for the Phase 6 evaluation without risking live routing authority. *Owner: Phase 6 router spec.*

**Escalation.** The controlled transfer of a work item from autonomous handling to operator attention, with the observed state, the blocked decision, and the next safe option attached. Escalation is never silent and never a bare error string; it is a handoff of a decision the estate cannot make alone. *Owner: Phase 0 spec.*

**Chaos test.** An experiment that injects a defined fault — device offline during approval, duplicate tap, stale live source, digest mismatch — into a running work item and asserts that the invariants hold and the failure is visible. Chaos tests are Layer 3 of the Phase 2 verification strategy. *Owner: Phase 2 invariant spec (`spec/invariants.md`, `tests/chaos/`).*

**Property test.** A test that asserts an invariant over generated inputs: random approval mutations, expiry times, duplicate events, network loss, subagent claims, stale sources. A property test fails if any generated case violates the invariant; it is Layer 2 of the Phase 2 strategy. *Owner: Phase 2 invariant spec (`tests/properties/`).*

**Traceability matrix.** The table binding each invariant to its doctrine source, the code or contract that implements it, and the tests that verify it (invariant → doctrine → code → test). The matrix is the audit trail a doctoral committee follows from claim to evidence. *Owner: Phase 2 invariant spec.*

**Scorecard.** The operator's instrument for measuring estate performance against attention and authority: accepted work, repair cost, attention cost, and related metrics, populated from router logs, evidence packets, and decision records. Paper I proposes the instrument; this programme's later phases schedule its population. *Owner: Phase 7 doctoral evidence.*

**Unknown state.** The rendering required when observation is insufficient: not failure, not a guess, but the explicit statement that the state cannot be established. Unknown is forced by `observation_unavailable` and can never be rendered as operational (INV-S1). *Owner: Phase 0 spec.*

**Paused state.** The operator-intent stop: the operator paused the service or work item. Paused is not an outage, not a failure, and never renders as failed (INV-S2). Resumption re-validates the plan against live sources before work continues. *Owner: Phase 0 spec.*

**Degraded state.** Observed impairment threatening the outcome: the service runs but a defined health signal — source freshness, error rate, latency — has crossed its threshold. Degraded requires observed impairment, never inference (INV-S3). *Owner: Phase 0 spec.*

**Completed state.** The terminal state entered only from `verifying` when the acceptance test has passed against observed output with the evidence packet attached. Completion supported by fluent text alone is optimistic completion and is unreachable by construction (INV-C1, INV-C5). *Owner: Phase 0 spec.*

## 5.7 Why One Vocabulary Is a Precondition for Proof

A model checker does not read intentions; it reads a transition relation over named states. If "completed" is also called "done," "handed off," and "accepted" in different documents, the property "no completion without evidence" is not one property but four — and the checker, the test author, and the committee will each prove a different one. The failure mode is not disagreement but the appearance of agreement: three teams certifying three different properties under one name, each correct about its own referent and none of them about the system. Doctoral evidence cannot be built on homonyms.

There is a second, subtler reason. The invariants of §8 are the testable expressions of the machine's guards (§7), and the guards are the formal expressions of the doctrine chain. That chain — doctrine to guard to invariant to test — is the traceability the thesis depends on, and it is a chain of *names*. If the name changes at any link, the trace breaks, and the committee is left with a test that cannot be shown to test the doctrine it claims. Freezing the vocabulary is therefore not administrative tidiness. It is the act that makes the rest of the programme refer to something — the precondition without which proof, testing, and measurement are performances rather than evidence.

There is a third reason, and it belongs to the trilogy's main vision. The frozen glossary is the vocabulary of the open specification: it is the document a community builds against, the file in which a stranger's pull request either conforms or does not. A programme that intends its control plane to be open-sourced cannot afford a private language; Phase 0's one normative spec is therefore also the publication contract — the first artifact the open-source release will carry, and the standard against which every later contribution is judged.
