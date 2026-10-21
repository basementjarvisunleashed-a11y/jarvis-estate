# 6. Phase 0 — The Canonical Work-State Machine

*The twelve states, the legal transitions with their guards, the event vocabulary, and the specification repository. This section uses the glossary of §5 and defines the machine that §7 proves and §8 tests.*

## 6.1 The Twelve States

Each state carries one normative definition. A work item is in exactly one state at a time; the state is a property of the work item, not of any client's rendering of it. Where Papers I–III used nearby words ("done," "approved," "stuck"), those words are now retired in favour of the names below.

**`received`.** A brief exists and has been recorded, but the orchestrator has not yet accepted scope. The work item is a submission, not a commitment: it may be accepted, declined as out of scope, or held for one focused clarifying question. No tools have run; no plan exists. This is the only state in which the estate has taken on nothing.

**`accepted`.** The orchestrator has accepted the brief's scope and the work item is committed to planning. Acceptance is a scope decision, not a quality verdict: it means the request is well-formed, in remit, and from an authorised source — the operator (HgX) or an authorised routine. No execution has occurred.

**`in_progress`.** A bounded plan exists, tools are selected, and work is underway. All non-consequential execution — reading live sources, drafting, computing, delegating bounded sub-tasks — happens inside this state (RD-1, §5.4). The state also covers re-planning after a blockage clears or an intent expires. A work item may remain here indefinitely, but it may never complete from here.

**`awaiting_approval`.** The next operation is consequential and the estate is waiting for the operator's decision on an exact approval intent. Waiting is the state's defining property: the intent carries an expiry, and expiry is a transition, not a lingering condition (OQ-3, §5.5). No consequential effect may occur while a work item is in this state except via the single guarded exit to `executing`.

**`executing`.** A valid, unexpired, digest-matched approval exists and the approved consequential action is underway. This state is entered only through the approval gate; it is the only state from which consequential effects may be produced. Non-consequential work never enters here. The state ends when the result is observed — success or failure — never when the action is merely dispatched.

**`verifying`.** The work claims completeness: an artifact exists, an evidence packet exists, and the acceptance test is being applied against observed output. Verification is adversarial by design — the question is whether the output passes the stated test, not whether it reads convincingly. This is the only state from which `completed` is reachable.

**`completed`.** The acceptance test has passed against observed output with the evidence packet attached. A terminal state: nothing further happens to the work item itself, though its artifact may be handed off and its method promoted. Completion supported by fluent text alone is optimistic completion and is unreachable by construction.

**`blocked`.** Progress is stalled on a condition outside the work item's control — an unreachable live source, a missing permission, an unanswered clarifying question — but recovery is plausible and the plan remains valid. Blocked is distinguished from failed by recoverability: the estate expects to resume, not to abandon. The blockage cause is recorded in the execution record (OQ-2, §5.5).

**`failed`.** A required source, permission, validation, or retry budget is unavailable and the work item cannot proceed. Failed is terminal for the work item but informative for the estate: the failure is observed, recorded with its evidence, and escalated with the next safe option. Failure is visible by doctrine, and this state is its canonical form.

**`paused`.** The operator has stopped the work item or its service by intent. Paused is not an outage and not a failure; it is the machine's representation of "the operator said stop." A paused work item holds its state and revision; resumption re-validates the plan against live sources before work continues, because the world may have moved while it slept.

**`unknown`.** The work item's state cannot be established through observation. Unknown is not failure and not a guess — it is the explicit, rendered statement of insufficient observation, forced by the `observation_unavailable` event. It exists so that the alternative — rendering a guess as a state — is never the default. Unknown never renders as operational.

**`cancelled`.** The work item has ended without completion by decision: the brief was declined, the operator denied the approval intent, or the operator cancelled the work directly. Cancelled is terminal and deliberate. It is distinguished from failed by agency — somebody chose this — and the reason is recorded.

## 6.2 The Transition Table

Every legal transition, with its triggering event and its guard stated in prose. Guards are the informal expression of the formal guards of §7; where §7 gives `can_enter_completed` as a formula, this table says what must be true in words. Transitions marked with an asterisk are Phase 0 additions to the roadmap skeleton, adopted under the reconciliation decisions of §5.4.

| # | From | To | Triggering event | Guard (prose) |
|---|---|---|---|---|
| T1 | `received` | `accepted` | `brief_accepted` | The brief is well-formed, in scope, and from an authorised source. |
| T2* | `received` | `cancelled` | `brief_declined` | The brief is out of scope or unauthorised; the reason is recorded. |
| T3 | `accepted` | `in_progress` | `plan_created` | A bounded plan exists with identified approval stops. |
| T4 | `in_progress` | `awaiting_approval` | `approval_requested` | The next operation is consequential; the intent specifies exact action, target, effect, scope, revision, and expiry. |
| T5 | `in_progress` | `blocked` | `failure_observed` (blocking) | A required condition is unavailable but recovery is plausible; the plan remains valid. |
| T6 | `in_progress` | `verifying` | `artifact_produced` + `evidence_packet_created` | The work claims completeness; the acceptance test is stated. |
| T7 | `in_progress` | `failed` | `evidence_of_failure` | A required source, permission, or the retry budget is exhausted. (Any-state rule.) |
| T8* | `blocked` | `in_progress` | `blockage_cleared` | The blocking condition is resolved and the plan is still valid against live sources. |
| T9 | `awaiting_approval` | `executing` | `approval_granted` | The intent is valid, unexpired, digest-matched, revision-current, and the session is authorised. Duplicate grants return the recorded decision without re-transitioning. |
| T10* | `awaiting_approval` | `in_progress` | `approval_expired` | The intent lapsed without a decision; the work item survives and may issue a fresh intent (OQ-3). |
| T11 | `awaiting_approval` | `cancelled` | `approval_denied` | The operator refused the consequence; no execution is permitted and the work item ends. |
| T12 | `awaiting_approval` | `failed` | `evidence_of_failure` | (Any-state rule.) |
| T13 | `executing` | `verifying` | `execution_observed` | The result is observed — success or failure. Dispatch without observation is not an exit. |
| T14 | `executing` | `failed` | `failure_observed` | Execution failed or the retry budget is exhausted. |
| T15 | `verifying` | `completed` | `acceptance_passed` | Evidence exists, the acceptance test passed against observed output, and no failure was observed. |
| T16 | `verifying` | `failed` | `failure_observed` | The acceptance test failed or required evidence is missing. |
| T17 | any state | `failed` | `evidence_of_failure` | Failure evidence interrupts normal flow from anywhere; it can never produce completion. |
| T18 | any state | `paused` | `operator_paused` | The operator intends a stop. In-flight consequential execution is brought to a safe point; no new consequential step begins. |
| T19* | `paused` | `in_progress` | `operator_resumed` | The operator intends resumption; the plan is re-validated against live sources before work continues. |
| T20 | any state | `unknown` | `observation_unavailable` | The state cannot be established; rendering is forced to unknown. |
| T21* | `unknown` | `in_progress` | `observation_restored` | The state is re-established by live re-read, never by assumption; the work item resumes from its recorded revision. |

Three notes on the table. First, T9's idempotency: a second `approval_granted` for the same intent is not a second transition. The server returns the recorded decision and the existing execution state — this is the machine-level expression of INV-A6 and the idempotency key of Phase 4. Second, T18's interaction with `executing` is deliberately narrow: pausing halts the initiation of further consequential steps, but an approved action already in flight is governed by the saga semantics of Phase 4, not by the pause. **Open question:** the exact safe-point semantics for pausing mid-`executing` — whether the in-flight step runs to observation or is held — is owned by the Phase 4 saga specification, which must define it before the guard can be formalised. Third, T20/T21 make unknown a one-way door with a single keyed exit: the machine can always admit ignorance, and it can only leave ignorance through verified observation.

## 6.3 Forbidden Transitions

The following transitions are explicitly forbidden. Each is the machine-level form of an invariant in §8; the parenthetical names the invariant it would violate.

- **F1.** Any state → `completed` except via `verifying` with `acceptance_passed`. (INV-C1, INV-C5.) There is exactly one road into `completed`, and it passes through verification.
- **F2.** `awaiting_approval` → `executing` without a valid, unexpired, digest-matched approval recorded by the server. (INV-A1.) The gate is the transition; there is no side entrance.
- **F3.** `executing` → `completed`. Execution is not verification; an observed dispatch is not an accepted result. (INV-C5, INV-E1.)
- **F4.** `in_progress` → `executing`. Consequential work cannot bypass the approval state, even when the operator is in a hurry and especially then. (INV-A1.)
- **F5.** `paused` → `executing`. Resumption re-validates before anything consequential happens; a paused item resumes into `in_progress`, never into execution. (INV-A1, INV-E5.)
- **F6.** `unknown` → any state except via `observation_restored`. Leaving ignorance requires evidence, not elapsed time or optimism. (INV-S1, INV-S4.)
- **F7.** `completed`, `failed`, `cancelled` → any state. Terminal states are absorbing. New work is a new revision or a new work item, never a resurrection. (INV-C1.)
- **F8.** `failed` → `completed`. Failure cannot silently become completion; the only forward path from failure is a new work item with its own evidence. (INV-C2.)
- **F9.** `verifying` → `executing`. A failed verification never retries execution directly; the path is `verifying` → `failed`, or back through `awaiting_approval` with a fresh intent binding the retry. (INV-A2, INV-A7.)

F7 deserves emphasis because it is the most commonly violated in informal systems: the temptation to "reopen" a completed item when a defect is found. The canonical model forbids it. A defect in a completed artifact is a new brief — "fix the defect" — with its own plan, evidence, and acceptance test. The completed item's evidence packet remains immutable, which is exactly what makes it evidence.

## 6.4 The Canonical Event Vocabulary

Fifteen events, per the roadmap §0.3, each with its normative definition and the transition it triggers. Four Phase 0 additions follow, marked with an asterisk.

| Event | Normative meaning | Triggers |
|---|---|---|
| `brief_received` | The operator or an authorised routine submits a brief; a work item is created in `received`. | → `received` (creation) |
| `brief_accepted` | The orchestrator accepts the brief's scope. | T1 |
| `plan_created` | A bounded plan exists with identified approval stops. | T3 |
| `artifact_produced` | Inspectable output exists and is digest-bound to the work-item revision. | T6 (with evidence) |
| `evidence_packet_created` | The proof bundle exists and is complete against the brief's acceptance tests. | T6 (with artifact) |
| `approval_requested` | The consequence boundary is reached; an exact intent is presented to the operator. | T4 |
| `approval_granted` | The operator's decision is recorded by the server: granted, digest-matched, unexpired. | T9 |
| `approval_denied` | The operator's decision is recorded: denied. The consequence is refused. | T11 |
| `approval_expired` | The intent's expiry passed without a decision; the intent is dead, the work item survives. | T10 |
| `execution_started` | The approved consequential action began; recorded against the idempotency key. | (within `executing`) |
| `execution_observed` | The result of the action is observed — success, failure, or ambiguous. | T13 |
| `acceptance_passed` | The stated acceptance test passed against observed output. | T15 |
| `failure_observed` | A failure condition is observed: failed source, failed test, exhausted budget. | T5 / T7 / T12 / T14 / T16 / T17 |
| `operator_paused` | The operator paused the service or work item by intent. | T18 |
| `observation_unavailable` | The work item's state cannot be established through observation. | T20 |

Phase 0 additions, owned by this spec:

| Event | Normative meaning | Triggers |
|---|---|---|
| `brief_declined`* | The brief is out of scope or unauthorised; the reason is recorded. | T2 |
| `blockage_cleared`* | The blocking condition resolved; the plan re-validated. | T8 |
| `operator_resumed`* | The operator lifted the pause; resumption re-validates against live sources. | T19 |
| `observation_restored`* | Observation is re-established by live re-read. | T21 |

Every event is appended to the work item's history with a timestamp and, where applicable, a digest or reference. The history is append-only: it is the audit trail from which the traceability matrix of §8 is built, and it is never rewritten — corrections are new events.

## 6.5 The Specification Repository

The canonical spec lives in a versioned repository with the following layout, per the roadmap §0.4. Each entry notes what the file will contain; the contracts' full sketches are deferred to Appendix C (§16).

```text
jarvis-formal-spec/
├── spec/
│   ├── state-machine.md          # This section, normative: states, transitions, guards, events
│   ├── invariants.md             # The invariant catalogue of §8, one owner per invariant
│   ├── consistency.md            # Phase 3: the multi-device consistency contract
│   ├── idempotency.md            # Phase 4: keys, execution records, saga, retry policy
│   ├── security-threat-model.md  # Phase 5: assets, boundaries, threats, capabilities
│   └── router-policy.md          # Phase 6: policies, metrics, experiment protocol
├── contracts/
│   ├── watchtower.schema.json       # Service state rendering contract (§6.6)
│   ├── evidence-packet.schema.json  # Proof bundle schema (§6.6)
│   ├── approval-intent.schema.json   # Exact intent schema (§6.6)
│   ├── decision-packet.schema.json   # Recorded decision schema (§6.6)
│   └── artifact-manifest.schema.json # Artifact digest manifest (§6.6)
├── tests/
│   ├── contracts/    # Layer 1: schema validation, fail-closed rules (§8)
│   ├── properties/   # Layer 2: property-based invariant tests (§8)
│   └── chaos/        # Layer 3: fault-injection scenarios (§8)
├── proofs/
│   └── state-machine/  # Phase 1: the formal model, guard table, checker results (§7)
├── experiments/
│   └── router/        # Phase 6: decision logs, replay harness, comparison report
└── whitepaper/
    └── sections/      # This document
```

The repository is versioned and reviewable: every change to a normative file is a commit with a rationale, and the Phase 0 exit criteria require that no two documents define the same concept differently — a condition the repository's own CI will check by validating that each glossary term has exactly one owning file.

## 6.6 Contract Schema Overview

Five JSON schemas carry the machine's data contracts. This section gives one paragraph on each — the key fields and their purpose. Full field-level sketches are deferred to Appendix C (§16), which owns the definitive field lists.

The specification repository this section describes is itself a publication artifact. The machine, the event vocabulary, and the five schemas are the estate's open contract surface: versioned, reviewable, and produced to be published — the system public, the principal's private life never. When the reference implementation is released, this repository is what it is released against; a stranger should be able to reimplement the machine from this section alone. That is the standard Phase 0's freeze must meet: not merely internally consistent, but externally legible.

**`watchtower.schema.json`.** The rendering contract for service state: `service_id`, `state` (enum restricted to `operational`, `paused`, `degraded`, `unknown` — the four Watchtower states, with paused explicitly distinct from failed), `last_observed_at`, `fresh_until`, `confidence`, and `evidence_ref`. Key fields are the freshness pair and the closed state enum: the schema makes INV-S1 through INV-S4 structurally expressible, because a renderer validating against this schema cannot emit a state the enum does not contain or a reading past its `fresh_until` without downgrading confidence.

**`evidence-packet.schema.json`.** The proof bundle: `packet_id`, `work_id`, `revision`, `artifact_refs` (each a digest bound to a revision), `source_observations` (each with `observed_at` and `fresh_until`), `test_results`, `approval_refs`, `gaps` (explicitly listed, never empty-by-default), `created_at`, and a packet checksum. The key design decision is that gaps are a required field: INV-E4 (gaps stay visible) is enforced by making omission a schema violation rather than a documentation lapse.

**`approval-intent.schema.json`.** The exact intent: `intent_id`, `work_id`, `action`, `target`, `effect`, `scope`, `revision`, `expiry`, `risk_class`, and `intent_digest` over the canonical serialisation of the rest. The digest field is what makes INV-A2 and INV-A3 mechanical: the server recomputes the digest at decision time, and any mutation — however small — fails the match.

**`decision-packet.schema.json`.** The recorded decision: `intent_id`, `intent_digest` (as presented), `decision` (`granted` or `denied`), `device_session_id`, `timestamp`, `auth_method`, and `server_recorded_at`. The key fields are the digest echo and the server timestamp: together they are the definition of "authoritative" (INV-A5), and the duplicate-tap path returns this packet instead of creating a second one (INV-A6).

**`artifact-manifest.schema.json`.** The digest manifest: `artifact_id`, `work_id`, `revision`, `digest`, `media_type`, `location`, and `provenance` (which worker produced it, from which sources, under which brief revision). The manifest is what binds INV-E2 (packet revision matches artifact revision) to bytes: the packet references the manifest, the manifest references the digest, and the digest references the content.

## 6.7 Phase 0 Exit Criteria

Phase 0 is complete when each of the following holds. The checklist is the roadmap's, expanded with the acceptance test for each item.

- [ ] **One normative spec.** All three papers reconciled: the glossary (§5), the state machine (§6.1–§6.4), the event vocabulary, and the contract overviews exist in exactly one version each, in the specification repository.
- [ ] **One owner per concept.** Every state, event, contract, and invariant names its owning phase and document; no concept is owned twice.
- [ ] **No duplicate definitions.** No two documents define the same term differently — checked, where mechanically possible, by CI over the glossary and schema files.
- [ ] **Versioned and reviewable.** The repository is under version control; changes to normative files carry rationales; the paper's version history records the freeze.
- [ ] **Reconciliation decisions recorded.** RD-1 through RD-6 are adopted in the machine (§6.2) and the glossary (§5.6); open questions OQ-1 through OQ-3 carry recommendations and named owners for resolution.
- [ ] **Contract sketches complete.** Appendix C (§16) holds the full field-level sketches of all five schemas, consistent with the overviews in §6.6.

When this checklist is green, the programme may proceed to Phase 1. Nothing is proven yet — that is the point. What exists is something provable: a machine with named states, guarded transitions, and contracts with owners. The proof is §7's work.
