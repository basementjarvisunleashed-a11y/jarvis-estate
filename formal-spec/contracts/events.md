# Canonical Event Vocabulary — J.A.R.V.I.S. Phase 0

*Version 1.0.0 — RATIFIED by HgX 2026-10-19 (decision D2). Normative.*
*Proof language: TLA+ (decision D1, 2026-10-19).*

## 1. Naming convention

**snake_case** — adopted for every event name, with the following justification:

1. **Fidelity.** Every source paper already names events, states, and contract fields in snake_case
   (`brief_received`, `approval_granted`, `intent_digest`, `fresh_until`). Adopting it requires zero
   renames of grounded terms. An UPPER_SNAKE or dotted convention would rename all nineteen events
   for no normative benefit.
2. **Proof-language mapping.** The ratified proof language is TLA+, whose action identifiers are
   plain identifiers. snake_case maps 1:1 into TLA+ actions with no translation layer.
3. **A dotted form invents hierarchy.** `work.brief.received` implies a namespace the papers never
   define, and dots collide with TLA+ record-field syntax and JSON path notation.
4. **UPPER_SNAKE breaks fidelity** with every cited source and with the schema enums the papers
   already publish in lowercase (`operational|paused|degraded|unknown`).

**Notification tiers** use the same convention as delivery-tier labels: `wrist_buzz`, `badge`, `silent`
(normalized from Paper III's prose "Wrist buzz / Badge / Silent"; they are delivery labels, not events).

## 2. Event envelope

Every canonical event is appended to the work item's append-only history and carries, at minimum:

| Field | Source |
|---|---|
| `work_id` | Roadmap §6 (Phase 3): event-sourced work state; each work item carries `work_id`, `revision`, `state`, `history`, …; every meaningful transition appends an event |
| `revision` | Roadmap §6; Paper IV §5.6 (Revision): every mutation creates a new revision; old revisions immutable |
| `timestamp` | Paper IV §6.4: "Every event is appended to the work item's history with a timestamp and, where applicable, a digest or reference" |
| `actor` | Paper IV §9 (Phase 3): "Append-only list of transition events, each with timestamp and actor" |
| `event_id` | Paper III (Contracts/Approval): "Push carries an opaque event identifier and minimal preview" |
| digest or reference | Paper IV §6.4: appended "where applicable" (intent digests, artifact digests, evidence refs) |

The history is append-only — "it is never rewritten — corrections are new events" (Paper IV §6.4).

## 3. Structural rules (from Paper IV §5.4 reconciliation decisions)

- **RD-2** — Approval is a *state–event pair*, not a stage: the `awaiting_approval` state plus the
  events `approval_requested`, `approval_granted`, `approval_denied`, `approval_expired`.
- **RD-3** — "Handoff" is an event and a packet, not a state. Completion is a property of the work
  item (`verifying → completed`); handoff is the communication of that property plus its evidence.
- **RD-5** — A routine is a *brief generator*, not a work-item state. Each scheduled firing emits
  `brief_received`; the resulting work item traverses the machine independently.
- **T6** is triggered by a joint event pair: `artifact_produced` **and** `evidence_packet_created`.
  Neither alone can move `in_progress → verifying`.

## 4. Work lifecycle events

| # | Event | Fires when | Payload (grounded) | Transitions | Papers |
|---|---|---|---|---|---|
| 1 | `brief_received` | The operator (HgX) or an authorised routine submits a brief; a work item is created in `received`. Per RD-5, each routine firing emits this event. | Brief fields: objective, audience, success criteria, tools, constraints, deadline (Paper II lifecycle; Paper IV §5.6 Brief). Submitter: operator or authorised routine (Paper IV §6.1, RD-5). | → `received` (creation) | I (brief establishes finish line), II (Brief), III (Brief), IV §6.4, Roadmap §0.3 |
| 2 | `brief_accepted` | The orchestrator accepts the brief's scope: well-formed, in remit, from an authorised source. | Accepted scope; authorised source (Paper IV §6.2 T1 guard). | T1: `received → accepted` | II (Routed / accepted scope), IV §6.4, Roadmap §0.3 |
| 3 | `brief_declined` ★ | The brief is out of scope or unauthorised. | Reason recorded (Paper IV §6.2 T2 guard). | T2: `received → cancelled` | IV §6.4 |
| 4 | `plan_created` | A bounded plan exists with identified approval stops. | Bounded plan with approval stops (Paper IV §6.2 T3 guard; Paper II: decompose into real jobs). | T3: `accepted → in_progress` | II (Plan), IV §6.4, Roadmap §0.3 |
| 5 | `artifact_produced` | Inspectable output exists, digest-bound to the work-item revision. Fluent text not observed against its acceptance test is not an artifact (Paper IV §5.6). | Artifact manifest: `artifact_id`, `work_id`, `revision`, `digest`, `media_type`, `location`, `provenance` (Paper IV §6.6). | T6 (joint with `evidence_packet_created`): `in_progress → verifying` | I (Artifact stage), II (Execute output), III (Work), IV §6.4, Roadmap §0.3 |
| 6 | `evidence_packet_created` | The proof bundle exists and is complete against the brief's acceptance tests. | Packet fields: `packet_id`, `work_id`, `revision`, `artifact_refs`, `source_observations` (each with `observed_at`, `fresh_until`), `test_results`, `approval_refs`, `gaps` (required field), `created_at`, packet checksum (Paper IV §6.6). | T6 (joint with `artifact_produced`) | I (Evidence stage), II (Verify), III (Evidence), IV §6.4, Roadmap §0.3 |
| 7 | `execution_started` | The approved consequential action began. Entered only through the approval gate; recorded against the idempotency key. | Idempotency key `hash(work_id, intent_id, intent_digest, action, target, scope, revision, operation_class)` (Paper IV §5.6); execution record fields: key, status, approval ref, attempt count, safe-to-retry flag (Roadmap §7). | Within `executing` (entry) | IV §6.4, Roadmap §0.3 |
| 8 | `execution_observed` | The result of the action is observed — success, failure, or ambiguous. "Dispatch without observation is not an exit" (Paper IV §6.2 T13). | Observed result (success / failure / ambiguous) (Paper IV §6.4; Roadmap §7 execution record: observed result). | T13: `executing → verifying` | IV §6.4, Roadmap §0.3 |
| 9 | `acceptance_passed` | The stated acceptance test passed against observed output. | Evidence exists; test result recorded in the evidence packet (Paper IV §6.2 T15 guard; INV-C1). | T15: `verifying → completed` | IV §6.4, Roadmap §0.3 |
| 10 | `failure_observed` | A failure condition is observed: failed source, failed test, exhausted retry budget (Paper IV §6.4). Any-state rule: interrupts normal flow from anywhere; can never produce completion (T17). | Observed error; for `blocked`, the blockage cause is recorded in the execution record (Paper IV §6.1, OQ-2); minimum incident record: time, owner, objective, last_safe_state, attempted_operation, observed_error, same_error_count, artifacts_preserved, approval_state, next_safe_option (Paper II, conceptual). | T5: `in_progress → blocked` (blocking) · T7: `in_progress → failed` · T12: `awaiting_approval → failed` · T14: `executing → failed` · T16: `verifying → failed` · T17: any state → `failed` | II (Failure semantics), IV §6.4, Roadmap §0.3 |
| 11 | `operator_paused` | The operator paused the work item or its service by intent. Pausing halts initiation of further consequential steps; an in-flight approved step is governed by the Phase 4 saga, not the pause (Paper IV §6.2 note). | Operator intent; holds state and revision (Paper IV §6.1). | T18: any state → `paused` | I (operator stops), IV §6.4, Roadmap §0.3 |
| 12 | `observation_unavailable` | The work item's state cannot be established through observation. Forces rendering to `unknown`; `unknown` never renders as operational (INV-S1). | — (absence is the payload; rendering forced to unknown, Paper IV §6.1) | T20: any state → `unknown` | IV §6.4, Roadmap §0.3 |
| 13 | `blockage_cleared` ★ | The blocking condition resolved and the plan re-validated against live sources. | Re-validation result against live sources (Paper IV §6.2 T8 guard). | T8: `blocked → in_progress` | IV §6.4 |
| 14 | `operator_resumed` ★ | The operator lifted the pause; resumption re-validates the plan against live sources before work continues (Paper IV §6.1; F5 forbids `paused → executing`). | Re-validation result (Paper IV §6.1). | T19: `paused → in_progress` | IV §6.4 |
| 15 | `observation_restored` ★ | Observation is re-established by live re-read, never by assumption (T21). The single keyed exit from `unknown` (Paper IV §6.2 note). | Live re-read observation; work item resumes from its recorded revision (Paper IV §6.2 T21). | T21: `unknown → in_progress` | IV §6.4 |

★ = Phase 0 addition (Paper IV §6.4). All nineteen events are appended to the work-item history.

## 5. Approval lifecycle events

The approval lifecycle is the state–event pair of RD-2: `awaiting_approval` plus four events.
`approval_requested` (event 5/16 below) is the lifecycle's entry; the other three are its exits.

| # | Event | Fires when | Payload (grounded) | Transitions | Papers |
|---|---|---|---|---|---|
| 16 | `approval_requested` | The consequence boundary is reached; an exact intent is presented to the operator. "The next operation is consequential; the intent specifies exact action, target, effect, scope, revision, and expiry" (Paper IV §6.2 T4). | Intent fields: `intent_id`, `work_id`, `action`, `target`, `effect`, `scope`, `revision`, `expiry`, `risk_class`, `intent_digest` over the canonical serialisation (Paper IV §6.6). | T4: `in_progress → awaiting_approval` | I (Approval stage), II (Approve / approval object), III (Approval / security semantics), IV §6.4, Roadmap §0.3 |
| 17 | `approval_granted` | The operator's decision is recorded **by the server**: granted, digest-matched, unexpired (Paper IV §6.4). Idempotent: a second grant for the same intent is not a second transition — the server returns the recorded decision and existing execution state (Paper IV §6.2 note on T9; INV-A6). | Decision packet: `intent_id`, `intent_digest` (as presented), `decision` = granted, `device_session_id`, `timestamp`, `auth_method`, `server_recorded_at` (Paper IV §6.6; RD-4: authoritative = recorded by the server, digest-matched, timestamped). | T9: `awaiting_approval → executing` | I, II, III (duplicate-tap idempotency), IV §6.4, Roadmap §0.3 |
| 18 | `approval_denied` | The operator refused the consequence; no execution is permitted and the work item ends. | Decision packet with `decision` = denied (Paper IV §6.6: "granted or denied"). | T11: `awaiting_approval → cancelled` (decision-sheet D5 recommendation, adopted in Paper IV §6.2) | III (decision packet outcome enum: `completed\|blocked\|failed\|cancelled`), IV §6.4, Roadmap §0.3 |
| 19 | `approval_expired` | The intent's expiry passed without a decision. "Expiry is a property of the intent, not a verdict on the work — INV-A4 kills the approval, not the task" (Paper IV §5.5 OQ-3). | Lapsed intent reference (intent_id, expiry); the work item survives and may issue a fresh intent with a new revision (Paper IV §6.2 T10). | T10: `awaiting_approval → in_progress` (decision-sheet D5 recommendation, adopted in Paper IV §6.2) | III (card expires → disable; refresh), IV §6.4, Roadmap §0.3 |

Supporting approval semantics (Paper III, Security semantics table — not separate events):
intent changes → invalidate the card, issue a new intent identifier and digest; card expires → disable
approval, refresh current source and effect; offline tap → record no local approval (INV-A5), re-fetch and
present current intent; duplicate tap → idempotency prevents duplicate execution, render the authoritative
result (INV-A6).

## 6. Verification outcomes

Verification is adversarial by design: "the question is whether the output passes the stated test, not whether
it reads convincingly" (Paper IV §6.1). Covered by events in §§4–5 above:

| Outcome | Event | Result |
|---|---|---|
| Artifact and proof bundle complete | `artifact_produced` + `evidence_packet_created` (joint) | T6: `in_progress → verifying` |
| Acceptance test passed against observed output | `acceptance_passed` | T15: `verifying → completed` (the only road into `completed` — F1) |
| Acceptance test failed or required evidence missing | `failure_observed` | T16: `verifying → failed` |
| Worker reports completion without inspectable evidence | `failure_observed` (delegation-without-proof → keep the task open; verify or rerun — Paper II failure semantics; INV-C3) | T16 / T7 |
| Decision packet invariant | A decision packet cannot claim `completed` if required tests failed or a critical gap remains (Paper III). | — |

## 7. Blockage

| Event | Role |
|---|---|
| `failure_observed` (blocking) | T5: `in_progress → blocked` — a required condition is unavailable but recovery is plausible and the plan remains valid (Paper IV §6.2). Blockage cause recorded in the execution record (OQ-2; recommendation adopted: single `blocked` state, cause as provenance — decision-sheet D6). |
| `blockage_cleared` ★ | T8: `blocked → in_progress` — blocking condition resolved, plan re-validated against live sources. |

Blocked is distinguished from failed by recoverability (Paper IV §6.1). Blockage cause (operator vs source)
is diagnostic metadata in the execution record, not a state split (OQ-2).

## 8. Routine scheduling

No dedicated routine events exist in the papers. Scheduling is covered as follows:

- **Routine firing** = `brief_received`, with the submitter identified as the authorised routine
  (RD-5: "each scheduled firing emits `brief_received`"; brief notes in Phase 3 event history may read
  "brief accepted from scheduled routine" — Paper IV §9).
- **Routine-run lifecycle states** (Paper II, §Scheduling): `SCHEDULED`, `RUNNING`, `SILENT SUCCESS`,
  `REPORTED RESULT`, `BLOCKED`, `PAUSED`. "A run is complete only when the execution result is observed.
  A queued or started job is not completion."
- **Service rendering states** (Paper III Watchtower contract; Paper IV §6.6
  `contracts/watchtower.schema.json`): `operational | paused | degraded | unknown` — a closed enum.
  Rendering mapping: `SILENT SUCCESS` / `REPORTED RESULT` render as `operational`; a deliberately
  stopped routine is `paused`, never down; `BLOCKED` renders as `degraded` or `paused` according to
  agency. "A 403 that prevents verification is `unknown`, not `degraded`" (Paper III).
- Routine runs retain their own execution history; goal logs and watermarks stay in `hidden_files/`
  (Paper II, decision telemetry). Silence on a quiet run is deliberate output, but internal run evidence
  must remain (Paper II observability principle).

## 9. Notification-tier events

The papers name **no notification events**. Notifications are a delivery discipline over the canonical
events, not events themselves:

- **Tiers** (Paper III, Notification discipline): `wrist_buzz` — a decision is needed now, delay risks the
  result or a stated deadline; `badge` — worth knowing today, no immediate consequence; `silent` —
  context for the next briefing or no actionable change. Routine mapping table (Paper III) assigns each
  routine class a default tier and promotion rule.
- **Delivery mechanics** (Paper III): "Push carries an opaque event identifier and minimal preview;
  clients fetch current authorized state." Deduplicate by work identifier and state revision; collapse
  superseded updates. Notifications are at-least-once hints, never authoritative state (Paper IV §9,
  Roadmap §6 consistency model).
- Because tier assignment is a property of event delivery, no `notification_sent` / `notification_acked`
  events are defined here. See §11 (UNRESOLVED).

## 10. Conflicts — naming collisions found and resolved

The coordinator's resolutions below are proposed under decision D2 (HgX ratifies).

**C1. `evidence_of_failure` vs `failure_observed`.** Paper III's state-transition rule
("any state + `evidence_of_failure` → failed", §Interaction/State machine) and Paper IV §6.2 T17
(triggering event: `evidence_of_failure`) use one name; Paper IV §6.4's canonical event vocabulary
(`failure_observed`, triggers T5/T7/T12/T14/T16/T17) and Roadmap §0.3 (`failure_observed`) use another.
**Resolution: `failure_observed` is canonical; `evidence_of_failure` is retired.** Rationale: three
sources (Roadmap, §6.4, and the failure semantics of Paper II) against two; §6.4 is the normative
vocabulary that Paper IV §5.1 says governs over Papers I–III usage; verb-form consistency with
`operator_paused` and `observation_unavailable`. The transition tables (Paper III rule, Paper IV T17)
must be amended to the canonical name.

**C2. "rejected as out of scope" vs `brief_declined`.** Paper II's lifecycle state table lists
`received`'s exits as "Routed, deferred for one focused question, or rejected as out of scope";
Paper IV §6.4 names the T2 event `brief_declined`.
**Resolution: `brief_declined` is canonical; "rejected" is retired in work-item context.**
Rationale: §6.4 is the normative vocabulary (Paper IV §5.1).

**C3. Paper II's "Verified" state vs Paper IV's `verifying` / `completed`.** Paper II's state table
defines a state `Verified` ("Acceptance evidence has been inspected. Handed off with evidence
packet.") Paper IV's canonical model has no such state: the state is `verifying` (the test is being
applied) and entry to `completed` requires the `acceptance_passed` event.
**Resolution: split.** The canonical state is `verifying`; `completed` is entered only via
`acceptance_passed` (T15); Paper II's "Verified" is retired per RD-2/RD-3 (approval is a state–event
pair; handoff is an event and a packet, not a state). This is exactly the optimistic-completion guard of
F1/INV-C1.

**C4. Routine-run states (Paper II) vs Watchtower service states (Paper III).** Paper II names six
routine-run states (`SCHEDULED`, `RUNNING`, `SILENT SUCCESS`, `REPORTED RESULT`, `BLOCKED`,
`PAUSED`); Paper III/Paper IV §6.6 restrict the service-rendering enum to
`operational | paused | degraded | unknown`.
**Resolution: different objects, no rename.** The six are the routine-run lifecycle (owned by the
scheduling/Phase 0 state-machine spec); the four are the closed rendering enum of
`contracts/watchtower.schema.json` (owned by Phase 0). The mapping in §8 documents how runs render.

## 11. UNRESOLVED — grounded concepts with no canonical event name

These are real, paper-grounded concepts. No event is invented for them; each names its owning document
and the question ratification must answer.

1. **Notification delivery events.** Paper III describes tiers, payload minimization, deduplication, and
   "opaque event identifier" transport, but names no `notification_delivered` / `notification_acked` /
   `notification_dismissed` events. If later phases need them, they are owned by the Phase 3
   consistency spec (`spec/consistency.md`).
2. **Escalation.** A glossary concept (Paper IV §5.6, owner: Phase 0 spec): "the controlled transfer of a
   work item from autonomous handling to operator attention, with the observed state, the blocked
   decision, and the next safe option attached. Escalation is never silent." No canonical event name
   exists; today it manifests as `failure_observed` → `failed` plus a `wrist_buzz`-tier delivery.
   Candidate resolution belongs to Phase 0 ratification, not to this draft.
3. **Clarifying-question hold.** Paper II (`received`: "deferred for one focused question") and
   Paper IV §6.1 ("held for one focused clarifying question") describe a hold with no named event and
   no transition in §6.2. Presumed semantics: the item remains in `received` until `brief_accepted`
   or `brief_declined`. UNRESOLVED — needs a named event or an explicit "no event" ruling.
4. **Execution-record sub-state entries.** Phase 4's execution record
   (`prepared → approved → execution_requested → execution_started → execution_observed /
   execution_failed / execution_unknown → completed / cancelled`, Paper IV §5.6, §10) names state
   entries that have no canonical events: the dispatch (`execution_requested`), the observed failure
   entry (`execution_failed`), and the ambiguous-outcome entry (`execution_unknown`) are state names,
   not events. `execution_started` and `execution_observed` are the only execution-record entries with
   canonical event names. Owned by `spec/idempotency.md` (Phase 4); UNRESOLVED until Phase 4
   formalizes the record's event set.
5. **Router decisions.** Paper II names five router outcomes (`proceed`, `use-cache`, `defer`,
   `escalate`, `deny`) recorded in the JSONL decision log. These are decision records, not work-item
   events, and are owned by the Phase 6 router spec (`spec/router-policy.md`). No rename proposed.

## 12. Event count

**19 canonical events**: 15 from Roadmap §0.3, adopted in Paper IV §6.4, plus 4 Phase 0 additions
(`brief_declined`, `blockage_cleared`, `operator_resumed`, `observation_restored`). Plus 4 resolved
naming collisions (§10) and 5 UNRESOLVED gaps (§11).

---
*Sources: Paper I v1.2, Paper II v1.1, Paper III v1.1, Paper IV v1.1 (esp. §5.4–§6.4, §9–§10, §14),
ROADMAP.md (§0.3, §0.4, §6–§7), phase-0-decision-sheet.md (D1, D2, D5, D6).*
