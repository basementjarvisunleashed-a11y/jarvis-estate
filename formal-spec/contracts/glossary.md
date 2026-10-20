# Canonical Glossary — J.A.R.V.I.S. Doctoral Validation Programme, Phase 0

**Status:** RATIFIED by HgX 2026-10-19 — v1.0.0 normative · **Owner:** Phase 0 spec (`spec/state-machine.md`, `contracts/`) ·
**Sources:** Paper I v1.2 (vision/doctrine), Paper II v1.1 (backend), Paper III v1.1 (front-end), Paper IV v1.1 (roadmap; normative where it conflicts) ·
**Date:** 2026-10-19

> Ratification rule (decision-sheet D2, ratified): the chief of staff resolves vocabulary conflicts; the operator (HgX) ratifies the final glossary. Conflicts marked **[Paper IV RD-n, adopted]** were already decided in Paper IV §5.4 and are carried over unchanged. Conflicts marked **[new resolution]** are decided here for the first time and need HgX's explicit ratification.

> Precedence: where this glossary conflicts with usage in Papers I–III, the glossary governs (Paper IV §5.1).

---

## 1. Canonical terms

Each term carries one normative definition. Every definition is one sentence.

### Identity, authority, and control

- **Operator.** The human party of the machine — HgX — who briefs, grants or denies approval intents, pauses and resumes work; every guard, transition, and approval rule refers to the operator. (Papers II–III use *operator* throughout; Paper IV §14.2: "The operator as principal and final authority.")
- **Principal.** The person whose authority the estate serves and whose private life the publication boundary protects; in this estate the operator acts as the principal, but *principal* names the authority position while *operator* names the acting party. (Paper I: "the principal's private life never [goes public]"; Paper IV §14.2: "The operator (HgX) is the principal of this programme in the same sense that he is the principal of the estate.")
- **Orchestrator.** The single authoritative control plane of the estate: it receives briefs, routes, plans, delegates, verifies, requests approval, and owns the final handoff — exactly one orchestrator exists; clients render, subagents execute bounded work, the router recommends, and none of them orchestrate. (Paper IV §5.6; Papers I–II.)
- **Role.** A named, bounded remit with its own memory scope and approval posture; a role is a governance boundary, not a process. (Paper IV RD-6, §5.4.)
- **Role boundary.** The accountability boundary a role establishes — one named job, one owner, one memory scope — enforced procedurally through doctrine, discipline, and filesystem convention, never as a process, container, or cryptographic isolation. (Paper I p5: "role separation is an accountability mechanism, not proof of technical isolation"; Paper IV RD-6.)
- **Bot.** The Papers I–III estate name for a role's concrete occupant or instance (e.g. "Tax Bot" names the tax-documents-and-returns role); *bot* is a proper name of a role instance, never the governance term — governance speaks of roles. **[new resolution]**
- **Subagent.** The estate's implementation of delegated work: an independent bounded job briefed by the orchestrator, whose output is verification input, never a completion signal; the orchestrator remains accountable for acceptance of delegated work. (Paper IV §5.6; INV-C3.)
- **Worker.** The generic term for any delegated execution unit, including subagents and any future execution mechanism; in the current estate every worker is a subagent, and the term exists so the specification survives the mechanism. (Paper IV §5.6; RD-6.)

### Work and its objects

- **Work item.** One bounded unit of requested estate work, identified by a `work_id`, carrying a revision counter and a single current state from the canonical machine. (Paper IV §5.6.)
- **Brief.** The structured submission that creates a work item: objective, audience, success criteria, tools, constraints, and deadline, from the operator or an authorized routine; a brief is well-formed only if its success criteria are stated as acceptance tests. (Paper IV §5.6.)
- **Plan.** The bounded decomposition of an accepted brief into real jobs with identified parallelism and approval stops, created before execution begins. (Paper II p6: "Decompose into real jobs; identify parallelism and approval stops"; Paper IV §6.1.)
- **Routing decision.** The governed object recording which path — cheapest reliable among cache, direct work, research, browser, or subagent — was chosen for a brief, and why; the router recommends, the orchestrator decides. (Paper II pp11–12; Paper IV §5.2.)
- **Artifact.** Inspectable output produced by work — a file, a message draft, a figure, a decision record — content-addressed by digest and bound to a work-item revision; fluent text that has not been observed against its acceptance test is not an artifact. (Paper IV §5.6.)
- **Acceptance.** A bounded check with a stated test, applied against observed output — never against fluent text. (Paper IV §1: "'Acceptance' means a bounded check with a stated test, applied against observed output — never against fluent text.")
- **Acceptance test.** A bounded check with a stated test, applied against observed output — never against fluent text; every brief states its acceptance tests, and `verifying → completed` requires them passed and recorded in the evidence packet. (Paper IV §5.6; INV-C1, INV-C2.)
- **Accepted work.** Work items that reached `completed` with the acceptance test passed and the evidence packet attached — the programme's north-star metric, not work attempted or claimed. (Paper IV §12.1.)
- **Evidence.** Observed proof of what happened — as opposed to fluent narration. (Paper I p11: "Evidence converts fluent claims into inspectable results"; Paper II p15.)
- **Evidence packet.** The structured proof bundle attached to work: artifact digests, live-source observations with freshness stamps, test results, approval references, and explicitly listed gaps; the packet is the unit of verification, and "no proof, no done" is the rule that no work item completes without one. (Paper IV §5.6.)
- **Approval intent.** The exact consequential action awaiting the operator: action, target, effect, scope, revision, and expiry, bound together by the intent digest; an intent is not a request for general permission but a fully specified consequence the operator may grant or deny. (Paper IV §5.6.)
- **Intent.** Normative shorthand for *approval intent*; the bare word never means anything else in the spec. **[new resolution]**
- **Intent digest.** The cryptographic digest over the canonical serialisation of an approval intent — the binding mechanism by which any change to target, effect, scope, or revision changes the digest and invalidates prior approval. (Paper IV §5.6; INV-A3.)
- **Approval decision.** The operator's recorded verdict on an intent — granted or denied — captured with `intent_id`, `intent_digest`, device session, timestamp, and authentication method; a decision is authoritative only when recorded by the server. (Paper IV §5.6; INV-A5.)
- **Decision packet.** The single artifact of an approval moment, carrying `intent_id`, `intent_digest`, the decision, the device session, and the server-recorded timestamp. (Paper IV RD-4, §5.4; Paper III p15.)
- **Intent expiry.** The lapse of an approval intent's deadline without an operator decision: the intent dies (event `approval_expired`) while the work item survives and returns to `in_progress`, where it may issue a fresh intent. (Paper IV OQ-3, §5.5; decision-sheet D5.)
- **Approval boundary.** The declared line between free preparation and gated consequence: the exact final action that may not proceed without the operator's explicit approval for that action. (Paper I p6; Paper II p9; Paper III p17.)
- **Consequential action.** Any action that moves effects outside the estate's observation boundary: sending, publishing, purchasing, deleting, transferring, or changing shared state. (Paper IV §1.)
- **Last safe moment.** The point at which the system has completed every reversible preparation step and must pause, immediately before an action becomes external, binding, destructive, or difficult to undo. (Paper I p10; Papers II–III.)
- **Revision.** The monotonically increasing counter on a work item, artifact, evidence packet, or intent; every mutation creates a new revision, old revisions are immutable, and revision binding is what prevents an approval granted against yesterday's artifact from executing against today's. (Paper IV §5.6; INV-A2, INV-E2.)
- **Handoff.** The delivery to the operator of a completed work item's result, evidence packet, gaps, and links, together with the promotion of stable method or durable facts to their stores — the communication of completion, not completion itself. (Paper IV §5.6; RD-3.)
- **Escalation.** The controlled transfer of a work item from autonomous handling to operator attention, with the observed state, the blocked decision, and the next safe option attached — never silent, never a bare error string. (Paper IV §5.6.)

### The machine: state, transition, guard, event, invariant

- **State.** The machine state of a work item: exactly one of the twelve canonical states at any time, a property of the work item, not of any client's rendering of it. (Paper IV §6.1.)
- **Transition.** A legal move of a work item from one machine state to another, fired by one event and permitted only while its guard holds. (Paper IV §6.2.)
- **Guard.** The condition that must hold for a transition to fire — stated in prose in the transition table (Paper IV §6.2) and formalised as a checkable predicate in the Phase 1 TLA+ model (§7); a transition whose guard fails cannot fire.
- **Event.** A named, timestamped occurrence appended to a work item's append-only history that fires a transition; events are never rewritten — corrections are new events. (Paper IV §6.4.)
- **Invariant.** Doctrine made falsifiable: a property that must hold in every reachable machine state, catalogued in five families (completion, approval, evidence, state rendering, router — INV-C/A/E/S/R), each bound to doctrine, code, and tests by the traceability matrix. (Paper IV §8.1.)

#### The twelve machine states (Paper IV §6.1)

1. **received.** A brief exists and has been recorded, but the orchestrator has not yet accepted scope — the work item is a submission, not a commitment; no tools have run, no plan exists.
2. **accepted.** The orchestrator has accepted the brief's scope and the work item is committed to planning; acceptance is a scope decision, not a quality verdict — no execution has occurred.
3. **in_progress.** A bounded plan exists, tools are selected, and work is underway; all non-consequential execution happens inside this state, and it may never complete from here.
4. **awaiting_approval.** The next operation is consequential and the estate is waiting for the operator's decision on an exact approval intent; waiting is the state's defining property, and no consequential effect may occur here except via the single guarded exit to `executing`.
5. **executing.** A valid, unexpired, digest-matched approval exists and the approved consequential action is underway — the only state from which consequential effects may be produced; it ends when the result is observed, never when the action is merely dispatched.
6. **verifying.** The work claims completeness: an artifact exists, an evidence packet exists, and the acceptance test is being applied against observed output, adversarially — the only state from which `completed` is reachable.
7. **completed.** The acceptance test has passed against observed output with the evidence packet attached; terminal — nothing further happens to the work item itself, and completion supported by fluent text alone is unreachable by construction.
8. **blocked.** Progress is stalled on a condition outside the work item's control, but recovery is plausible and the plan remains valid; distinguished from `failed` by recoverability, with the blockage cause recorded.
9. **failed.** A required source, permission, validation, or retry budget is unavailable and the work item cannot proceed; terminal for the work item but informative for the estate — failure is observed, recorded, and escalated with the next safe option.
10. **paused.** The operator has stopped the work item or its service by intent; not an outage and not a failure — resumption re-validates the plan against live sources before work continues.
11. **unknown.** The work item's state cannot be established through observation — not failure and not a guess, but the explicit rendered statement of insufficient observation, forced by `observation_unavailable`, and never rendered as operational.
12. **cancelled.** The work item has ended without completion by decision — brief declined, approval denied, or operator cancellation; terminal and deliberate, distinguished from `failed` by agency, with the reason recorded.

#### The nineteen canonical events (Paper IV §6.4)

| Event | Normative meaning | Fires |
|---|---|---|
| `brief_received` | The operator or an authorised routine submits a brief; a work item is created in `received`. | creation |
| `brief_accepted` | The orchestrator accepts the brief's scope. | T1 |
| `brief_declined` * | The brief is out of scope or unauthorised; the reason is recorded. | T2 |
| `plan_created` | A bounded plan exists with identified approval stops. | T3 |
| `artifact_produced` | Inspectable output exists and is digest-bound to the work-item revision. | T6 |
| `evidence_packet_created` | The proof bundle exists and is complete against the brief's acceptance tests. | T6 |
| `approval_requested` | The consequence boundary is reached; an exact intent is presented to the operator. | T4 |
| `approval_granted` | The operator's decision is recorded by the server: granted, digest-matched, unexpired. | T9 |
| `approval_denied` | The operator's decision is recorded: denied; the consequence is refused. | T11 |
| `approval_expired` | The intent's expiry passed without a decision; the intent is dead, the work item survives. | T10 |
| `execution_started` | The approved consequential action began, recorded against the idempotency key. | within `executing` |
| `execution_observed` | The result of the action is observed — success, failure, or ambiguous. | T13 |
| `acceptance_passed` | The stated acceptance test passed against observed output. | T15 |
| `failure_observed` | A failure condition is observed: failed source, failed test, exhausted budget. | T5/T7/T12/T14/T16/T17 |
| `blockage_cleared` * | The blocking condition resolved; the plan re-validated. | T8 |
| `operator_paused` | The operator paused the service or work item by intent. | T18 |
| `operator_resumed` * | The operator lifted the pause; resumption re-validates against live sources. | T19 |
| `observation_unavailable` | The work item's state cannot be established through observation. | T20 |
| `observation_restored` * | Observation is re-established by live re-read. | T21 |

*Phase 0 additions to the roadmap skeleton.*

### Contracts, knowledge, and repetition

- **Contract.** A versioned, reviewable statement of what one part of the estate may expect from another — a role contract, a skill's SKILL.md, a filesystem path convention, or a JSON schema for the machine's data. (Paper I p13: "Give every role a versioned contract"; Paper II p8; Paper III p14; Paper IV §6.6.)
- **Skill.** A versionable operational contract capturing a proven method: on disk at `skills/<name>/SKILL.md` with Purpose, Workflow, Output Contract, and Operating Rules; a skill receives a schedule only after review. (Paper II pp8, 18; Paper IV RD-5.)
- **Method.** The captured know-how — decision, failure, validation, and approval rules written down — that a skill packages; in the promotion gate it names the stage between an observed task and a tested skill. (Paper II p18.)
- **Routine.** A scheduled skill that has earned repetition through reviewed, accepted work — a brief generator, not a work-item state: each scheduled firing emits `brief_received`, and the resulting work item traverses the machine independently; routines are silent by default and observable by the Watchtower. (Paper IV §5.6; RD-5.)
- **Capability.** A formal grant with seven fields — subject, action, object, scope, condition, expiry, approval requirement, evidence requirement — specifying exactly what a worker, routine, or connector may do; the unit of least privilege. (Paper IV §5.6; Phase 5 security spec.)
- **Live source.** An authoritative current-state system — a calendar, a mailbox, a price feed, a device sensor — that owns some changing fact about the world; current facts are read from live sources at decision time, never inferred from memory. (Paper IV §5.6.)
- **Durable memory.** Identity, preferences, principles, and commitments that persist across sessions — the curated MEMORY.md, relationship pages, dated notes; it carries what the operator is and has decided, never what the world currently is. (Paper IV §5.6.)
- **Working state.** Run logs, ledgers, watermarks, drafts, and source snapshots: read from the owning goal or service, neither durable memory nor live source. (Paper II p10.)
- **Freshness.** The property of an observation that it was taken recently enough to decide on: every live-source reading carries `observed_at` and `fresh_until`, and a reading past `fresh_until` is stale. (Paper IV §5.6.)
- **Current.** The property of a fact whose latest live-source observation is still fresh; current facts are read from live sources at decision time, never inferred from memory. (Paper I p9; Paper II p3; Paper IV §5.6.)
- **Stale.** An observation past its `fresh_until`, or a decision made on one; stale observations cannot satisfy a guard that requires current truth. (Paper IV §5.6; INV-S4.)
- **Traceability matrix.** The table binding each invariant to its doctrine source, the code or contract that implements it, and the tests that verify it — invariant → doctrine → code → test — the audit trail a doctoral committee follows from claim to evidence. (Paper IV §5.6.)

### Boundaries, surfaces, and publication

- **Trust boundary.** A named interface across which trust is not transitive — the ten operational boundaries (devices ↔ estate edge, edge ↔ orchestrator, orchestrator ↔ tools, ↔ subagents, ↔ connectors, ↔ external web, ↔ Secure Vault, ↔ external router, client ↔ notification system, personal ↔ shared surfaces); data crossing a boundary is validated, authority crossing a boundary is re-established. (Paper IV §5.6; §11.)
- **Publication boundary.** The boundary beyond the ten operational boundaries: what may cross from the estate to the open-source release (doctrine, skills, contracts, schemas, the state machine, the invariant suite, the threat model, the evidence package — the system) and what never does (family, finances, credentials, personal data, live-source contents — the principal's private life). (Paper IV §11.)
- **Sanitization.** The reviewed removal of private values before anything enters the public staging tree; a private value found there is a security defect, not an editorial one. (Paper I p11: "The sanitising pass is real work"; Paper II p14; Paper IV §11.)
- **Side chat.** A procedural role-and-memory isolation scope aligned to a bot's duties; it improves relevance and discretion but is not a cryptographic isolation boundary on the shared host. (Paper II pp5, 10.)
- **Watchtower.** The estate's live status observation and rendering system: it emits versioned service records in the four canonical render states — operational, paused, degraded, unknown — and stays silent when there is nothing actionable. (Paper III p14; Paper IV §6.6.)
- **Service.** An estate capability under Watchtower observation — a routine, connector, or feed — rendered in exactly one of the four canonical states with a freshness pair and an evidence reference. (Paper III p14; Paper IV §6.6.)
- **Authoritative.** Of a record or decision: recorded by the server, digest-matched, timestamped — a client tap is a gesture until the server records it. (Paper IV RD-4, §5.4; INV-A5.)
- **Silent by default.** The output contract of a routine: no actionable change means no user-visible output — silence is deliberate, with internal run evidence retained. (Paper I p11; Paper II p9; Paper III p17.)

### Cost, attention, and governance

- **Attention.** The estate's scarcest resource: the operator's capacity to decide; the system protects it by speaking on signal, staying silent otherwise, and never substituting confidence for proof. (Paper I p2.)
- **Attention cost.** The operator's scarce resource measured as interruptions weighted by context-switch severity: a silent routine costs nothing, an approval request costs a decision, an ambiguous alert costs investigation. (Paper IV §5.6.)
- **Repair cost.** The human effort required to correct an accepted artifact that should not have been accepted, measured in minutes of operator or reviewer time plus the downstream cost of the error. (Paper IV §5.6.)
- **Scorecard.** The operator's instrument for measuring estate performance against attention and authority: accepted work, repair cost, attention cost, and related metrics, populated from router logs, evidence packets, and decision records. (Paper IV §5.6.)
- **Shadow mode.** The router's current operating posture: it observes decisions and logs recommendations without overriding orchestrator judgment, gathering labelled decision history for the Phase 6 evaluation without risking live routing authority. (Paper IV §5.6.)
- **Property test.** A test asserting an invariant over generated inputs — random approval mutations, expiry times, duplicate events, network loss, subagent claims, stale sources — failing if any generated case violates the invariant; Layer 2 of the Phase 2 verification strategy. (Paper IV §5.6.)
- **Chaos test.** An experiment injecting a defined fault — device offline during approval, duplicate tap, stale live source, digest mismatch — into a running work item and asserting the invariants hold and the failure stays visible; Layer 3 of the Phase 2 strategy. (Paper IV §5.6.)
- **Delegation boundary.** The rule that a subagent's response is input to verification, never a completion signal: the orchestrator remains accountable for acceptance of delegated work. (Paper II p5; Paper IV INV-C3.)
- **Consequence boundary.** The line at which preparation ends and consequence begins; every approval intent and approval card exists to represent exactly this boundary. (Paper III p6.)
- **Router.** The usage router: a gate consulted before live-browser work, deep research, retries, or delegation, which recommends the cheapest reliable path and never approves consequences; currently local policy in shadow mode. (Paper II pp11–12; Paper IV §5.6, §12.)
- **Idempotency key.** The deterministic key over `(work_id, intent_id, intent_digest, action, target, scope, revision, operation_class)` identifying one logical consequential operation across retries, duplicate taps, and network failures; the server records the key's execution state and returns the recorded outcome on repeat. (Paper IV §5.6.)
- **Execution record.** The server-side record of one consequential operation's lifecycle — prepared → approved → execution_requested → execution_started → execution_observed / execution_failed / execution_unknown → completed / cancelled — with the idempotency key, approval reference, attempt count, observed result, and safe-to-retry flag. (Paper IV §5.6.)
- **Saga.** The governed transaction pattern for consequential work, used because the estate assumes no distributed transactions: prepare → approval → execute → verify → record evidence → compensate (only if approved and possible); no silent rollback of consequential effects. (Paper IV §5.6.)
- **Single-writer rule.** Consequential execution proceeds through one writer, in one order, each step's precondition checked against current authoritative state; two executions of the same intent cannot interleave — the second finds the first's record and returns it. (Paper IV §9.3.)

---

## 2. Vocabulary conflicts

Every place where the papers use different words for the same concept, or the same word for different concepts. For each: the conflicting usages with paper references, the chosen canonical term, and why. **Conflicts marked [Paper IV RD-n, adopted]** were decided in Paper IV §5.4 and are carried over unchanged. **Conflicts marked [new resolution]** are decided here for the first time.

### C-1 — Role / agent / bot / subagent / worker **[new resolution; adopts Paper IV RD-6]**

- Paper I: "Role" (doctrine chain stage: "Who owns the finish line?"), a "federation of narrow roles", named bots as the role estate ("Tickler Bot", "Tax Bot"), and bare "agent" in team deployment ("Assign one agent to one clear job", "No agent publishes, sends, spends, or deletes").
- Paper II: "subagents" as the implementation of delegated work; "Bot" names in the skill registry; bare "agent" in the operating agent.
- Paper IV: RD-6 rules that a role is a named, bounded remit (governance), a subagent is the estate's implementation of delegated work, and a worker is the generic term for any delegated execution unit; examples name "the Tax Bot", "tickler-bot", "the meme bot".
- **Resolution:** canonical terms are **role** (governance boundary), **subagent** (current implementation of delegated work), **worker** (generic, mechanism-independent); Paper I's bare "agent" folds to **worker**; **bot** survives only as the proper name of a role instance (e.g. "Tax Bot" names the tax role), never as a governance term.
- **Why:** Paper IV RD-6 already split role from subagent from worker; keeping "agent" as a fourth loose synonym would re-introduce the homonym the freeze exists to remove, and "bot" needs preserving because it is the estate's live naming practice, just demoted from governance vocabulary to naming convention.

### C-2 — Operator / principal **[new resolution]**

- Paper I: "PRINCIPAL — HgX sets intent, constraints, priorities, and final authority"; "the principal's private life never [goes public]".
- Papers II–III: "operator" throughout ("Publication timing stays with the operator", "the operator's attention").
- Paper IV: uses both — "the operator (HgX)" as the acting party, and §14.2: "The operator as principal and final authority. The operator (HgX) is the principal of this programme in the same sense that he is the principal of the estate."
- **Resolution:** keep **both** as distinct canonical terms: **operator** = the acting human party the machine interacts with (briefs, grants/denies, pauses); **principal** = the person whose authority the estate serves and whose private life the publication boundary protects.
- **Why:** Paper IV §14.2 deliberately uses both words in one sentence for different jobs — operator names the counterparty, principal names the authority position — and collapsing them would erase the publication boundary's subject ("the principal's private life").

### C-3 — "Execute" split across two machine states **[Paper IV RD-1, adopted]**

- Paper II's lifecycle stage "Execute" covers both non-consequential tool work (reading a calendar, drafting, computing) and consequential action (sending, publishing, purchasing).
- Paper IV splits it: non-consequential execution lives inside `in_progress`; the `executing` state is reserved for approval-gated consequential execution.
- **Resolution:** canonical **in_progress** (all non-consequential execution) and **executing** (approved consequential execution only).
- **Why:** the approval gate is the safety-critical boundary of the estate, and a boundary that is a stage label rather than a machine state cannot carry a transition guard (Paper IV §5.4, RD-1).

### C-4 — Approval as stage → approval as state–event pair **[Paper IV RD-2, adopted]**

- Paper II "Approve" and Paper III "Approval" are lifecycle/loop stages — things the estate "does".
- **Resolution:** canonical **awaiting_approval** (a state) plus the events **approval_requested / approval_granted / approval_denied / approval_expired**.
- **Why:** an approval is not something the estate does; it is something the estate waits for, and waiting is a state with an expiry — this is what makes "expired approval unusable" expressible as a guard rather than a hope (Paper IV §5.4, RD-2; INV-A4).

### C-5 — "Handoff" as stage → event + packet **[Paper IV RD-3, adopted]**

- Paper II's final stage "Handoff and capture" is a lifecycle stage.
- **Resolution:** completion is the state `completed` (via `verifying → completed`); **handoff** is the communication of that property plus its evidence, not a state.
- **Why:** conflating them would let a delivered message masquerade as a verified result — precisely the optimistic-completion failure the invariants forbid (Paper IV §5.4, RD-3; INV-C5).

### C-6 — "Decision" (operator side) vs "Approve" (estate side) **[Paper IV RD-4, adopted]**

- Paper III's operator loop ends in "Decision" (the operator's tap); Paper II's lifecycle has "Approve" (the estate's stage).
- **Resolution:** the operator's tap is a **decision event**; the estate's stage is approval; both are described by the single artifact, the **decision packet**.
- **Why:** naming the artifact both sides describe makes "authoritative" testable — recorded by the server, digest-matched, timestamped — which is what INV-A5 (offline approval cannot create authoritative consent) needs (Paper IV §5.4, RD-4).

### C-7 — "Routine" as a work stage → routine as a brief generator **[Paper IV RD-5, adopted]**

- Paper I's doctrine chain ends in "Routine" ("Has the method earned repetition?"); Paper II's promotion gate ends "Routine — Only a reviewed method receives a schedule".
- **Resolution:** canonical **routine** = a scheduled skill that has earned repetition; each firing emits `brief_received`, and the resulting work item traverses the machine independently. "Routine" is never a work-item state.
- **Why:** routines must be pausable, degradable, and observable by the Watchtower as services — none of which is expressible if "routine" is a terminal stage of a work item (Paper IV §5.4, RD-5).

### C-8 — "Tool" vs "capability" **[new resolution]**

- Paper IV §5.2's compatibility table maps Paper I's "Tool" to the joint canonical cell "tool; capability".
- But Paper IV §5.6 defines **capability** separately as a formal seven-field grant (subject, action, object, scope, condition, expiry, approval requirement, evidence requirement) — the unit of least privilege in Phase 5 — while Paper I's "Tool" contract is "What path is reliable and permitted?" (a narrow, reliable access path).
- **Resolution:** keep **tool** and **capability** as distinct canonical terms; the §5.2 table cell over-folded two concepts.
- **Why:** a tool is what the orchestrator picks at the Route stage; a capability is what Phase 5 grants to a worker, routine, or connector — merging them would let "least privilege" be read as "reliable path selection", collapsing the entire Phase 5 security formalism into a routing preference.

### C-9 — "Verify" (activity) vs "verifying" (state) **[new resolution]**

- Paper II's lifecycle stage "Verify" ("Inspect artifacts, source provenance, tests, and delegated evidence") is an activity; Paper IV's machine has the state `verifying`.
- **Resolution:** canonical **verification** = the adversarial activity of applying the acceptance test against observed output; **verifying** = the machine state in which that activity happens.
- **Why:** Paper IV §5.3 already treats them as "two names for the transition `in_progress → verifying` and the object it produces" — activity and state are different referents and the freeze must not let a test plan and a machine state share one name.

### C-10 — "Evidence" vs "evidence packet" **[new resolution]**

- Papers I–III use "evidence" loosely ("Evidence converts fluent claims into inspectable results", "returns evidence", "expose evidence").
- **Resolution:** **evidence** (uncounted) = observed proof as opposed to fluent narration; **evidence packet** = the structured, schema-governed bundle (artifact digests, source observations, test results, approval refs, explicit gaps) that is the unit of verification.
- **Why:** "no proof, no done" is only falsifiable against the packet — INV-C1 demands a packet, not a vibe — so the loose word survives as the general noun while the governed object gets the compound name.

### C-11 — "Work" vs "work item" **[new resolution]**

- Paper I's doctrine chain governs "every unit of work"; Paper III's operator loop has a "Work" stage ("inspectable on demand").
- **Resolution:** canonical **work item** = the governed object (one bounded unit, one `work_id`, one current state); bare "work" is informal collective shorthand; Paper III's "Work" loop-stage name is retired in favour of the machine states it observes (`in_progress`, `awaiting_approval`, `blocked`, `verifying`).
- **Why:** the machine's guards and invariants quantify over work items with IDs and revisions — "work" as a mass noun cannot carry a digest, a revision, or a guard.

### C-12 — Retired casual state words: "done", "approved", "stuck" **[new resolution]**

- Papers I–III use "done", "completion", "approved", "stuck" informally.
- **Resolution:** retired in favour of **completed**, **awaiting_approval** (a decision recorded, not a vibe), and **blocked**; Paper IV §6.1 states these words "are now retired".
- **Why:** a model checker reads a transition relation over named states — if "completed" is also called "done", "handed off", and "accepted", the property "no completion without evidence" becomes four properties and three teams certify three different ones (Paper IV §5.7).

### C-13 — "accepted" (state) vs "accepted work" (metric) **[new resolution]**

- Paper I's scorecard: "Accepted work — Did the artifact pass its stated acceptance test?" (work that passed the test).
- Paper IV's machine state `accepted`: "Acceptance is a scope decision, not a quality verdict."
- **Resolution:** both survive with distinct referents: **accepted** = the machine state (brief scope accepted, no execution yet); **accepted work** = the metric (work items that reached `completed` with acceptance passed and evidence attached, Paper IV §12.1).
- **Why:** Paper IV itself uses both senses, so neither can be retired; the resolution is to keep the state name bare and the metric always as the two-word noun phrase, and to prefer "completed work" in normative prose where the metric is meant.

### C-14 — "Approval card" vs "approval intent" **[new resolution]**

- Paper III's "approval card" ("an approval card is not a prettier confirm dialog") is the UI representation of the consequence boundary.
- **Resolution:** canonical **approval intent** = the governed object (action, target, effect, scope, revision, expiry, digest); **approval card** = the front-end rendering of an approval intent on a client surface (Paper III p6: "the user interface representation of the consequence boundary defined by both companion papers").
- **Why:** the intent is what the server records and the digest binds; the card is what a surface shows — INV-A3 and INV-A5 constrain the object, never the pixels, and conflating them would let a screenshot count as consent.

### C-15 — Bare "intent" **[new resolution]**

- Paper III uses "intent" loosely ("Intent expires after 10 minutes", "immutable intent digest", "Any content or destination change requires a new approval").
- **Resolution:** in normative text, always **approval intent**; bare "intent" is accepted only as shorthand for approval intent and never means anything else.
- **Why:** the digest binds the exact consequence — any other reading of "intent" (a wish, a plan, a general permission) would smuggle unbound consequences past the gate.

### C-16 — "Current" vs "fresh"/"stale" **[new resolution]**

- Paper II's invariant "Current facts stay live" and Paper I's "Keep facts current" use *current* for facts held by live sources; Paper IV's **freshness** is the measured property of an observation (`observed_at`, `fresh_until`).
- **Resolution:** **current** = a fact whose latest live-source observation is still fresh; **freshness** = the measured property of an observation; **stale** = an observation past `fresh_until`.
- **Why:** "current" was doing two jobs — the fact's truth-status and the observation's age — and INV-S4 ("no source-dependent guard is satisfied by stale data") needs the observation's age as the checkable property.

### C-17 — Bare "memory" **[new resolution]**

- Papers I–III use "memory" for the durable store, while Paper II also distinguishes working state and live sources as separate persistence classes.
- **Resolution:** canonical **durable memory**; bare "memory" is shorthand for durable memory and never means a live source or working state.
- **Why:** the control "memory answers 'how do we work?', live systems answer 'what is true now?'" (Paper I p9) fails the moment "memory" is read as a synonym for remembered current facts.

### C-18 — "Method" vs "skill" **[new resolution]**

- Paper I: "Skills encode methods that have already worked"; Paper II's promotion gate runs Observed task → **Captured method** ("Decision, failure, validation, and approval rules are written") → Safe test → Routine, while the skill itself is the versionable on-disk contract.
- **Resolution:** canonical **skill** = the versionable operational contract; **method** = the captured know-how (decision, failure, validation, approval rules) that a skill packages — "method" survives only as a stage of the promotion gate and as the content of a skill.
- **Why:** without the split, "promote the method" and "version the skill" read as two different processes when the papers describe one pipeline.

### C-19 — "Routine": Paper II's rich definition vs Paper IV's abstract one **[new resolution]**

- Paper II: "A routine is not merely a timer; it is a schedule bound to a tested skill, a live source, a failure policy, and an approval boundary."
- Paper IV RD-5: "a routine is a scheduled skill that has earned repetition", a brief generator.
- **Resolution:** compatible, not conflicting — Paper IV's sentence is the canonical *definition*; Paper II's list is the canonical *required contract fields* (owner, schedule+timezone, live input, expected result, failure rule, approval boundary) every routine must carry.
- **Why:** the two papers describe the same object at different altitudes; recording both as definition-vs-fields preserves Paper II's operational detail without demoting Paper IV's machine-level ruling.

### C-20 — "Approval boundary" wording **[new resolution]**

- Paper I's role contract lists "approval boundary" as a field; Paper II: "The exact final action that may not proceed unattended"; Paper III's approval semantics: cards bound to "an immutable intent digest".
- **Resolution:** canonical **approval boundary** = the declared line between free preparation and gated consequence: the exact final action that may not proceed without the operator's explicit approval for that action.
- **Why:** the three usages agree in substance; canonising one sentence stops "boundary" drifting between "the field in the contract", "the thing that stops", and "the digest" in later phase specs.

### C-21 — "Failure" / "failed" / "failure_observed" **[new resolution]**

- Paper I: "Failure is visible" (doctrine); Paper II: "Failure semantics" (failure classes and responses); Paper IV: the machine state `failed` and the event `failure_observed`.
- **Resolution:** compatible — **failure** (uncounted) = the doctrine/posture that errors surface rather than hide; **failed** = the terminal machine state; **failure_observed** = the event that fires the transition into it.
- **Why:** the doctrine word and the machine words were never in conflict, but Phase 2's chaos tests will write "inject a failure" constantly — the freeze records which referent that phrase takes in each context.

### C-22 — "Consequential action" **[new resolution]**

- Papers I–III use "consequential action/boundary" pervasively ("stops before a consequential action", "Consequential actions stop at exact approval boundaries") without fixing the extension.
- **Resolution:** canonical definition from Paper IV §1: any action that moves effects outside the estate's observation boundary — sending, publishing, purchasing, deleting, transferring, or changing shared state.
- **Why:** the entire approval apparatus (gate, intent, digest, single-writer rule) is scoped by this term; leaving its extension to reader intuition would let each phase spec draw the consequence boundary in a different place.

### C-23 — "Last safe moment" **[new resolution]**

- Paper I §6: "Approval belongs at the last safe moment"; Paper II: "Pause at the last safe moment"; Paper III: "pauses at the last safe moment".
- **Resolution:** canonised as defined above — the point where every reversible preparation step is complete and the system must pause before an action becomes external, binding, destructive, or difficult to undo.
- **Why:** shared vocabulary, no conflict in substance — canonisation records that it is a normative term of art, not a rhetorical flourish, and pins it to the reversibility principle.

### C-24 — Bare "source" **[new resolution]**

- Papers I–III use "source" loosely ("reads current facts from authoritative systems", "Refresh current source and effect", "Sources display as human labels").
- **Resolution:** canonical **live source** for the authoritative current-state system; "sources" inside an evidence packet = provenance references (labels, URIs, retrieval times), not the systems themselves.
- **Why:** "the source failed" must be unambiguous in incident records — it means the live system was unreachable, not that a citation was missing from a packet.

### C-25 — Paper III's operator-loop states vs the machine **[new resolution]**

- Paper III's operator loop renders work as "accepted, in progress, blocked, or awaiting approval" — a four-word summary set that is close to, but not identical with, the machine's twelve states.
- **Resolution:** Paper III's words are *rendering labels*, not machine states; the canonical states are the twelve of §6.1, and any client label must map 1:1 onto them (Paper III's own state-transition rule already points this way: "received → accepted → in_progress → {awaiting_approval | blocked | verifying}").
- **Why:** Paper III §2's reading contract says the operating paper answers what the estate is and the backend paper answers how work is proven — the front end renders contracts; it does not mint states. (Consistent with Paper III p14: "Unknown values render as unknown", i.e. the renderer follows the machine's enum.)

---

## 3. Terms not reconciled

Things the sources do not settle. Stated plainly; nothing invented.

- **U-1 — Intent digest canonicalisation and hash function.** ~~Cannot be frozen from the papers.~~ **RESOLVED 2026-10-19 (HgX): SHA-256 over the canonical JSON serialisation of the approval intent.** Owner: Phase 0 spec (`contracts/approval-intent.schema.json`).
- **U-2 — Revision token.** The term appears in Paper III ("Clients resynchronize against server state using idempotency keys and revision tokens") and Paper IV §9 ("the issuance and validation of revision tokens (§9.5)"), but neither source gives it a frozen definition — it is adjacent to, but distinct from, **revision** (the counter) and the **idempotency key**. Owner: Phase 3 consistency spec (`spec/consistency.md`). Flagged here so the freeze does not silently absorb it into *revision*.
- **U-3 — Freshness expectation values per source class.** Paper I's roadmap (item 3) calls for mapping "each fact class to its authoritative system" and setting "freshness expectations"; Paper IV defines the freshness mechanism (`observed_at`/`fresh_until`) but no source assigns actual thresholds (how fresh is fresh enough for a calendar read vs a price read). Owner: Phase 3 consistency spec. The glossary freezes the mechanism, not the values.
- **U-4 — Safe-point semantics for pausing mid-executing.** Paper IV §6.2, note on T18: pausing halts the initiation of further consequential steps, but "whether the in-flight step runs to observation or is held" is explicitly left open — "owned by the Phase 4 saga specification, which must define it before the guard can be formalised." Owner: Phase 4 idempotency spec (`spec/idempotency.md`).
- **U-5 — Clock-skew bound Δ.** **RESOLVED 2026-10-19 (HgX): Δ = 60 seconds** (Paper IV §7.5 recommendation accepted; proof obligation PO-2 fails at 300s). The glossary's time-dependent terms (intent expiry, freshness) now use Δ = 60s.
- **U-6 — Back-editing Papers I–III to the canonical terms.** **RESOLVED 2026-10-19 (HgX): the published papers stand as historical; the glossary is the normative overlay** (per Paper IV §5.1, the glossary governs where it conflicts).

---

*Prepared 2026-10-19 for ratification under D2. Nothing in this file has been published, shared, or pushed. Ratification checklist for HgX: adopt/reject each [new resolution] (C-1, C-2, C-8 – C-25); confirm the six carried-over Paper IV RD decisions stand; note decisions on U-5 and U-6.*
