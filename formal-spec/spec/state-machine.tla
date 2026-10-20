---------------------------- MODULE StateMachine ----------------------------
(***************************************************************************)
(* J.A.R.V.I.S. canonical work-state machine — Phase 0 ("Freeze the          *)
(* contracts"), doctoral validation programme.                              *)
(*                                                                           *)
(* TLA+ primary modelling language, ratified by HgX 2026-10-19 (decision     *)
(* D1; Paper IV v1.1 §7, OQ-4). Alloy is the secondary tool for quick        *)
(* checks only.                                                              *)
(*                                                                           *)
(* PRIMARY SOURCE: Paper IV v1.1 ("From Doctrine to Proof"), §6.1 (twelve    *)
(* states), §6.2 (transition table T1–T21), §6.3 (forbidden transitions      *)
(* F1–F9), §5 (glossary: approval intent, intent digest, approval decision),  *)
(* §5.4 (reconciliation decisions RD-1–RD-6), §7.2 (state variables),        *)
(* §7.3 (transition guards), §7.5 (failure model), §7.6 (proof obligations    *)
(* PO-1–PO-12), §8 (invariant catalogue). Papers I–III supply the doctrine   *)
(* chain (Role → Live Source → Tool → Artifact → Evidence → Approval →       *)
(* Routine) and approval-at-the-last-safe-moment semantics.                  *)
(*                                                                           *)
(* FIVE PRINCIPLES (Paper I v1.2 foundation; Paper IV §1): truth over        *)
(* comfort, discretion, reversibility, stewardship, open source from day     *)
(* one. The machine is where doctrine becomes checkable: approval is the     *)
(* operator's authority at the consequence boundary, evidence is observed    *)
(* proof rather than fluent narration ("no proof, no done"), and a pause     *)
(* is never rendered as failure.                                             *)
(*                                                                           *)
(* PROVISIONAL (adopted working baseline, awaiting HgX ratification):        *)
(*   - D5: approval_expired → in_progress; approval_denied → cancelled.      *)
(*     Expiry lapses the intent, not the work (Paper IV §5.5, OQ-3, §6.2).   *)
(*   - D6: single `verifying` and single `blocked` states; verification      *)
(*     method and blockage cause recorded as provenance only (Paper IV       *)
(*     §5.5, OQ-1/OQ-2).                                                    *)
(*   - D7: clock-skew bound Δ = 60 seconds (Paper IV §7.5#9, OQ-5; largest   *)
(*     Δ for which PO-2 holds — counterexample at Δ = 300s).                 *)
(*     Instantiate Delta <- 60 when model checking.                          *)
(*                                                                           *)
(* VOCABULARY NOTE: the seven chain-of-custody link names are used exactly   *)
(* as handed to this task (Role, Live Source, Tool, Artifact, Evidence,     *)
(* Approval, Routine); the sibling glossary coordinator owns the normative   *)
(* definitions. Task-brief "queued/assigned" is reconciled to Paper IV's    *)
(* `received` / `accepted` (§6.1) — the task's words are retired in favour    *)
(* of the canonical names per §6.1.                                          *)
(*                                                                           *)
(* UNRESOLVED / OPEN — not invented here; recorded for the Phase 0 exit     *)
(* criteria and later phases:                                                *)
(*   U1. T18 mid-execution pause safe-point semantics: whether the in-flight *)
(*       step runs to observation or is held is owned by the Phase 4 saga    *)
(*       specification; the guard cannot be fully formalised until then       *)
(*       (Paper IV §6.2, transition-table notes). Modelled here as           *)
(*       executing → paused ("brought to a safe point") with no further      *)
(*       consequential step permitted — deliberately narrow.                  *)
(*   U2. Chain-anchor depth mapping (Depth/ChainGate below) is interpretive: *)
(*       grounded in Paper IV §3.1 ("every link corresponds to transitions   *)
(*       in the machine") and §6.1/§6.2, but the paper gives no anchor       *)
(*       table. The anchors are monotonic so the chain order is a custody    *)
(*       order, not an event order — see note at ChainGate.                  *)
(*   U3. Non-consequential work items never record an approval; whether the  *)
(*       Approval chain link is vacuous or unreachable for them is not       *)
(*       stated in the papers.                                               *)
(*   U4. Routine "earned only through repeated, evidenced completed          *)
(*       transitions" (Paper IV §3.1): repetition counting lives in the      *)
(*       routine scheduler, not in Phase 0; modelled here as single         *)
(*       attainment on completed.                                            *)
(*   U5. Exact intent-digest canonicalisation and hash function are owned by *)
(*       contracts/approval-intent.schema.json (Paper IV §5.6); DigestOf     *)
(*       here is opaque (collision resistance is assumed lemma (a), §7.6).   *)
(*                                                                           *)
(* FORBIDDEN TRANSITIONS (Paper IV §6.3) — enforced by construction: no      *)
(* action in Next has these as source→target; TLC checks the temporal        *)
(* properties in §7.6 PO-1–PO-12. F1: →completed except via verifying.       *)
(* F2: awaiting_approval→executing without valid recorded approval. F3:      *)
(* executing→completed. F4: in_progress→executing. F5: paused→executing.     *)
(* F6: unknown→any except via observation_restored. F7: completed/failed/    *)
(* cancelled are absorbing. F8: failed→completed. F9: verifying→executing.   *)
(***************************************************************************)

EXTENDS Integers, Naturals, Sequences

CONSTANTS
    Actions,          \* Opaque set of consequential action identifiers
    Targets,          \* Opaque set of action target identifiers
    Effects,          \* Opaque set of action effect descriptors
    Scopes,           \* Opaque set of action scope descriptors
    MaxNow,           \* Upper bound on server `now` for finite model checking
    Delta             \* Clock-skew bound, seconds. PROVISIONAL: D7/OQ-5.

ASSUME Delta \in Nat
(* Instantiate Delta <- 60 for Phase 1 model checking (Paper IV §7.5#9). *)

VARIABLES
    work_state,         \* One of the twelve canonical states (Paper IV §6.1)
    chain,              \* 0..7: chain-of-custody links completed, in order
    approval_state,     \* none | requested | tapped | recorded | denied | expired
    intent,             \* The approval intent record (Paper IV §5.6)
    intent_digest,      \* Server-recorded digest of the approved intent
    tap_digest,         \* Digest the operator saw when tapping (PO-3)
    session_authorised, \* Authorised device session for the current intent
    revision,           \* Work-item revision; intents bind to a revision (INV-A2)
    evidence_exists,    \* Evidence packet exists (Paper IV §7.2)
    acceptance_passed,  \* Acceptance test passed against observed output
    execution_observed, \* none | success | failure
    failure_observed,   \* Failure evidence seen (blocks completion, §7.3)
    source_freshness,   \* fresh | stale | unknown
    operator_pause,     \* Operator has paused the item/service (Paper IV §7.2)
    observation_status, \* observed | unavailable
    blocked_cause,      \* Provenance only, per D6 (OQ-2)
    verification_method,\* Provenance only, per D6 (OQ-1)
    now                 \* Server time. All time comparisons use server now (D7).

vars == << work_state, chain, approval_state, intent, intent_digest,
           tap_digest, session_authorised, revision, evidence_exists,
           acceptance_passed, execution_observed, failure_observed,
           source_freshness, operator_pause, observation_status,
           blocked_cause, verification_method, now >>

(***************************************************************************)
(* The twelve states (Paper IV §6.1). A work item is in exactly one state   *)
(* at a time; the state is a property of the work item, not of any client's *)
(* rendering of it.                                                        *)
(***************************************************************************)
States == { "received", "accepted", "in_progress", "awaiting_approval",
            "executing", "verifying", "completed",
            "blocked", "failed", "paused", "unknown", "cancelled" }
(* received:        brief recorded, orchestrator has not accepted scope.
                    Only state in which the estate has taken on nothing.
   accepted:        orchestrator accepted the brief's scope (well-formed, in
                    remit, authorised source — operator or authorised routine).
   in_progress:     bounded plan exists, tools selected, work underway. ALL
                    non-consequential execution lives here (RD-1, §5.4; §6.1).
                    Never completes from here.
   awaiting_approval: next operation is consequential; waiting on the exact
                    approval intent (RD-2, §5.4: approval is a state–event
                    pair, not a stage; waiting is the state's defining
                    property; expiry is a transition, OQ-3 §5.5).
   executing:       valid, unexpired, digest-matched approval exists; the
                    approved consequential action is underway. Entered ONLY
                    through the approval gate; the ONLY state from which
                    consequential effects may be produced (RD-1).
   verifying:       work claims completeness; artifact + evidence packet
                    exist; acceptance test applied against OBSERVED output.
                    Only state from which completed is reachable (F1).
   completed:       acceptance passed against observed output, evidence
                    attached. TERMINAL. Optimistic completion unreachable.
   blocked:         stalled on a condition outside the item's control, but
                    recovery plausible and plan valid. Cause = provenance
                    (D6, OQ-2). Single state — no human/machine split.
   failed:          required source/permission/retry budget unavailable.
                    TERMINAL for the item; failure is visible by doctrine.
   paused:          operator said stop. Holds state and revision; resumption
                    re-validates the plan against live sources.
   unknown:         state cannot be established through observation —
                    explicit rendered ignorance, never a guess, never
                    rendered as operational.
   cancelled:       ended without completion by decision (brief declined,
                    approval denied, operator cancelled). TERMINAL and
                    deliberate; distinguished from failed by agency.        *)

TerminalStates == { "completed", "failed", "cancelled" }  \* Absorbing (F7, PO-11)
NonTerminal    == States \ TerminalStates

ApprovalStates == { "none", "requested", "tapped", "recorded",
                     "denied", "expired" }
(* tapped vs recorded: the operator tapped; the SERVER persisted.
   The gap between them is where INV-A5 (offline approval) lives —
   the model must not merge them (Paper IV §7.2). *)

NoIntent == [ action |-> "none", target |-> "none", effect |-> "none",
              scope |-> "none", revision |-> 0, expiry |-> 0 ]

(* The six bound fields of an approval intent (Paper IV §5.6, INV-A2):
   action, target, effect, scope, revision, expiry — bound by the digest.
   Approval is granted to a specific future, never a category of futures. *)
IntentType == [ action   : Actions \cup {"none"},
                target   : Targets \cup {"none"},
                effect   : Effects \cup {"none"},
                scope    : Scopes  \cup {"none"},
                revision : Nat,
                expiry   : Nat ]

(* intent_expiry, one of the roadmap's ten state variables (Paper IV §3.1,
   "What Fixed Means"), is the expiry field of the intent record. *)
intent_expiry == intent.expiry

(***************************************************************************)
(* Phase 1 finite-instance bound. TLC cannot enumerate the unbounded      *)
(* IntentType (revision/expiry range over Nat), so ApprovalRequested and   *)
(* MutateIntent quantify over FiniteIntentType in Next below. This loses   *)
(* no behavior relevant to the checked properties:                         *)
(*   - revision is invariant (always 0: no action modifies it);            *)
(*   - expiry values beyond MaxNow+1 are behaviorally indistinguishable    *)
(*     (server now never exceeds MaxNow, so they never expire and satisfy  *)
(*     every expiry guard identically); 0..MaxNow+1 covers every expiry    *)
(*     timing the guards can distinguish.                                  *)
(* The normative IntentType above is unchanged; TypeOK still uses it.      *)
(***************************************************************************)
FiniteIntentType == [ action   : Actions \cup {"none"},
                      target   : Targets \cup {"none"},
                      effect   : Effects \cup {"none"},
                      scope    : Scopes \cup {"none"},
                      revision : {0},
                      expiry   : 0..(MaxNow + 1) ]

(***************************************************************************)
(* Phase 1 concretization of the intent digest. The normative spec treats   *)
(* DigestOf as opaque (U5; collision resistance is assumed lemma (a),      *)
(* Paper IV §7.6), but the TLC configuration parser cannot instantiate     *)
(* operator constants or tuple/set-comprehension values, so the digest is  *)
(* concretized here for the finite instance. The field-tuple encoding is   *)
(* injective over intent records — strictly stronger than the assumed     *)
(* collision resistance: any mutation of any intent field changes the      *)
(* digest, so PO-3 (mutation forces rejection) is exercised faithfully.    *)
(* No canonical term is renamed; TypeOK still constrains digests to        *)
(* Digests \cup {NoDigest}.                                                *)
(***************************************************************************)
DigestOf(r) == <<r.action, r.target, r.effect, r.scope, r.revision, r.expiry>>
Digests == {DigestOf(i) : i \in FiniteIntentType}

(* The empty digest: no decision recorded yet. A 0-tuple, distinct from
   every real digest (all 6-tuples). TLC throws (rather than returning
   FALSE) when an action guard compares a string with a tuple, so the
   empty digest must be a tuple for all digest equalities to be
   type-homogeneous. Semantically identical to a "none" marker. *)
NoDigest == <<>>

(***************************************************************************)
(* The seven-stage chain of custody (Paper I doctrine chain; Paper IV §1,   *)
(* §3.1): Role → Live Source → Tool → Artifact → Evidence → Approval →      *)
(* Routine. Each link is a contract; §3.1: "every link corresponds to       *)
(* transitions in the machine: evidence attaches at verifying, approval is  *)
(* granted at awaiting_approval, execution begins at executing, routine     *)
(* status is earned only through repeated, evidenced completed transitions."*)
(* `chain` counts completed links IN ORDER: link i+1 can complete only      *)
(* after link i, so skipping a stage is unreachable by construction.        *)
(***************************************************************************)
ChainLinks == <<"Role", "Live Source", "Tool", "Artifact",
                "Evidence", "Approval", "Routine">>
NumLinks == Len(ChainLinks)   \* 7

(* Interpretive anchor mapping (U2): how far the machine has travelled, for
   gating chain-link completion. Anchors are MONOTONIC predicates: the chain
   order is a custody-demonstration order, not the event order — e.g. the
   machine grants approval (T9) before verifying (T13), yet the Approval
   link (6) completes after the Evidence link (5), because the anchor for
   link 6 only needs to HOLD when link 6's turn comes, not at the moment
   of the physical grant. This preserves Paper IV §3.1's link order. *)
Depth(s) == CASE s = "received"          -> 0
              [] s = "accepted"          -> 1
              [] s = "in_progress"       -> 2
              [] s = "blocked"           -> 2
              [] s = "awaiting_approval" -> 3
              [] s = "executing"         -> 4
              [] s = "verifying"         -> 5
              [] s \in TerminalStates    -> 6
              [] OTHER                   -> -1
(* paused/unknown get -1: while control is suspended or observation is
   unavailable, no custody link may be claimed. *)

(* ChainGate(l): the machine condition under which chain link l (1-based)
   may be marked complete. Grounded: §3.1 anchors + §6.1 state definitions.
   U3: the Approval link requires a recorded approval; non-consequential
   items (which never enter awaiting_approval) cannot complete it. *)
ChainGate(l) ==
    CASE l = 1 -> Depth(work_state) >= 1
      (* Role: brief accepted; orchestrator committed to scope (§6.1
         accepted; §5 glossary maps Role → orchestrator; role boundary). *)
      [] l = 2 -> Depth(work_state) >= 2
      (* Live Source: plan built on live reads; all non-consequential
         execution, incl. reading live sources, is inside in_progress
         (RD-1 §5.4; §6.1 in_progress). *)
      [] l = 3 -> Depth(work_state) >= 2
      (* Tool: tools selected in the bounded plan (§6.1 in_progress). *)
      [] l = 4 -> Depth(work_state) >= 5
      (* Artifact: inspectable output produced (T6 artifact_produced). *)
      [] l = 5 -> Depth(work_state) >= 5 /\ evidence_exists
      (* Evidence: packet attached; verification applies the acceptance
         test against observed output (§3.1; §6.1 verifying). *)
      [] l = 6 -> Depth(work_state) >= 4 /\ approval_state = "recorded"
      (* Approval: a valid, unexpired, digest-matched approval was
         recorded (§3.1; §7.3 can_enter_executing). *)
      [] l = 7 -> work_state = "completed"
      (* Routine: earned only through evidenced completed transitions
         (§3.1); repetition counting deferred to the scheduler (U4). *)
      [] OTHER -> FALSE

(***************************************************************************)
(* Clock skew (Paper IV §7.5#9, OQ-5; D7). now is server time; all time     *)
(* comparisons use it. Client-observed time may differ by at most Δ; any    *)
(* decision inside the skew window must be re-validated, never trusted.    *)
(***************************************************************************)
WithinSkew(t1, t2) == t1 <= t2 + Delta /\ t2 <= t1 + Delta

(***************************************************************************)
(* Guards — the formal versions of the §6.2 prose guards (Paper IV §7.3).   *)
(* now is server time; digest recomputed at transition time, never cached.  *)
(***************************************************************************)
can_enter_completed ==
    /\ work_state = "verifying"       \* F1: exactly one road in (INV-C1, INV-C5)
    /\ evidence_exists                 \* packet exists (INV-C1)
    /\ acceptance_passed               \* test passed against observed output (INV-C2)
    /\ ~failure_observed               \* no failure observed (INV-C2 second half)

can_enter_executing ==
    /\ work_state = "awaiting_approval"
    /\ approval_state = "recorded"     \* recorded, not merely tapped (INV-A5)
    /\ now < intent.expiry             \* live intent (INV-A4); expiry is a guard
    /\ intent_digest = DigestOf(intent) \* evaluated at transition time (INV-A3)
    /\ intent.revision = revision       \* revision-current (T9 guard)
    /\ session_authorised              \* authorised session (T9 guard; PO-8)
    /\ ~operator_pause

(***************************************************************************)
(* Type invariant.                                                           *)
(***************************************************************************)
TypeOK ==
    /\ work_state \in States
    /\ chain \in 0..NumLinks
    /\ approval_state \in ApprovalStates
    /\ intent \in IntentType
    /\ intent_digest = NoDigest \/ intent_digest \in Digests
    /\ tap_digest = NoDigest \/ tap_digest \in Digests
    (* NOTE (Phase 1): disjunction with the empty digest first, because
       TLC throws (rather than returning FALSE) when an action guard
       compares a string with a tuple. Semantically
       `intent_digest \in Digests \cup {NoDigest}`. *)
    /\ session_authorised \in BOOLEAN
    /\ revision \in Nat
    /\ evidence_exists \in BOOLEAN
    /\ acceptance_passed \in BOOLEAN
    /\ execution_observed \in {"none", "success", "failure"}
    /\ failure_observed \in BOOLEAN
    /\ source_freshness \in {"fresh", "stale", "unknown"}
    /\ operator_pause \in BOOLEAN
    /\ observation_status \in {"observed", "unavailable"}
    /\ now \in Nat /\ now <= MaxNow

Init ==
    /\ work_state = "received"
    /\ chain = 0
    /\ approval_state = "none"
    /\ intent = NoIntent
    /\ intent_digest = NoDigest
    /\ tap_digest = NoDigest
    /\ session_authorised = FALSE
    /\ revision = 0
    /\ evidence_exists = FALSE
    /\ acceptance_passed = FALSE
    /\ execution_observed = "none"
    /\ failure_observed = FALSE
    /\ source_freshness = "fresh"
    /\ operator_pause = FALSE
    /\ observation_status = "observed"
    /\ blocked_cause = "none"
    /\ verification_method = "none"
    /\ now = 0

(***************************************************************************)
(* Transitions T1–T21 (Paper IV §6.2). Asterisked rows are Phase 0          *)
(* additions adopted under the §5.4 reconciliation decisions.               *)
(***************************************************************************)

(* T1. received → accepted on brief_accepted. Guard (prose): brief
   well-formed, in scope, from an authorised source (operator or
   authorised routine). Formalised here as the state change itself; the
   brief's well-formedness is a brief-contract precondition owned by the
   Phase 0 spec (§5 glossary: brief). *)
BriefAccepted ==                      \* T1
    /\ work_state = "received"
    /\ work_state' = "accepted"
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    blocked_cause, verification_method, now >>

(* T2*. received → cancelled on brief_declined. Guard (prose): brief out
   of scope or unauthorised; reason recorded. *)
BriefDeclined ==                      \* T2*
    /\ work_state = "received"
    /\ work_state' = "cancelled"
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    blocked_cause, verification_method, now >>

(* T3. accepted → in_progress on plan_created. Guard (prose): bounded
   plan exists with identified approval stops; tools selected (§6.1). *)
PlanCreated ==                        \* T3
    /\ work_state = "accepted"
    /\ work_state' = "in_progress"
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    blocked_cause, verification_method, now >>

(* T4. in_progress → awaiting_approval on approval_requested.
   The intent specifies exact action, target, effect, scope, revision,
   expiry (INV-A2); the digest binds them (INV-A3); a fresh intent
   supersedes any prior one for this revision. *)
ApprovalRequested(newIntent) ==       \* T4
    /\ work_state = "in_progress"
    /\ newIntent \in IntentType
    /\ newIntent.revision = revision
    /\ newIntent.expiry > now
    /\ work_state' = "awaiting_approval"
    /\ approval_state' = "requested"
    /\ intent' = newIntent
    /\ intent_digest' = NoDigest         \* no decision recorded yet
    /\ tap_digest' = NoDigest           \* no tap yet
    /\ session_authorised' = TRUE      \* session authorised at request time
    /\ UNCHANGED << chain, revision, evidence_exists, acceptance_passed,
                    execution_observed, failure_observed, source_freshness,
                    operator_pause, observation_status, blocked_cause,
                    verification_method, now >>

(* T5. in_progress → blocked on failure_observed (blocking). Recovery
   plausible, plan remains valid. Cause recorded as provenance (D6). *)
BlockageObserved(cause) ==            \* T5
    /\ work_state = "in_progress"
    /\ work_state' = "blocked"
    /\ blocked_cause' = cause
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    verification_method, now >>

(* T6. in_progress → verifying on artifact_produced + evidence_packet_
   created. The work claims completeness; the acceptance test is stated.
   evidence_exists set: the packet is the unit of verification (§5). *)
ArtifactProduced(method) ==           \* T6
    /\ work_state = "in_progress"
    /\ work_state' = "verifying"
    /\ evidence_exists' = TRUE
    /\ verification_method' = method   \* provenance only (D6, OQ-1)
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, acceptance_passed,
                    execution_observed, failure_observed, source_freshness,
                    operator_pause, observation_status, blocked_cause, now >>

(* Any-state failure (T7, T12, T17): evidence_of_failure interrupts normal
   flow from anywhere non-terminal; it can never produce completion
   (PO-6). T7 is in_progress → failed; T12 awaiting_approval → failed;
   T17 any state → failed. *)
FailureObserved ==                    \* T7 / T12 / T17
    /\ work_state \in NonTerminal
    /\ observation_status = "observed" \* PO-4: cannot observe a failure
                                      \* while observation is unavailable
    /\ work_state' = "failed"
    /\ failure_observed' = TRUE
    /\ operator_pause' = FALSE        \* PO-5: a failed item is not paused;
                                      \* the pause is superseded by failure
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed,
                    source_freshness, observation_status,
                    blocked_cause, verification_method, now >>

(* T8*. blocked → in_progress on blockage_cleared. Guard (prose): blocking
   condition resolved AND plan still valid against live sources — the
   guard depends on source truth, so it is unsatisfiable unless sources
   are fresh (PO-10). *)
BlockageCleared ==                    \* T8*
    /\ work_state = "blocked"
    /\ source_freshness = "fresh"
    /\ work_state' = "in_progress"
    /\ blocked_cause' = "none"
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    verification_method, now >>

(* Operator taps approve: client gesture only — NOT authority.
   A second tap for the same intent is not a second transition: it
   stutters (T9 note; idempotency key, INV-A6, Phase 4). *)
OperatorTapsApprove ==                \* tap (gesture), cf. T9
    /\ work_state = "awaiting_approval"
    /\ approval_state = "requested"
    /\ approval_state' = "tapped"
    /\ tap_digest' = DigestOf(intent) \* what the operator actually approved
    /\ UNCHANGED << work_state, chain, intent, intent_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    blocked_cause, verification_method, now >>

DuplicateTap ==                        \* T9 note: idempotent re-tap
    /\ work_state = "awaiting_approval"
    /\ approval_state \in {"tapped", "recorded"}
    /\ UNCHANGED vars                  \* recorded decision returned as-is

(* Server records the decision: the ONLY path to "recorded". Requires
   server validation of intent existence, expiry, digest, permissibility,
   session (PO-8, INV-A5). The recorded intent must match what the
   operator tapped: DigestOf(intent) = tap_digest, so a mutation between
   tap and record forces rejection (PO-3; §7.5#3). An offline tap can
   never take this path: recording is a server act, not a client act
   (illegal state 7). *)
ServerRecordsApproval ==              \* server validation, cf. T9/PO-8
    /\ work_state = "awaiting_approval"
    /\ approval_state = "tapped"
    /\ now < intent.expiry             \* INV-A4: expired approval unusable
    /\ DigestOf(intent) = tap_digest   \* PO-3: what was tapped is what is recorded
    /\ intent_digest' = DigestOf(intent)
    /\ session_authorised              \* authorised device session (PO-8)
    /\ approval_state' = "recorded"
    /\ UNCHANGED << work_state, chain, intent, tap_digest, session_authorised, revision,
                    evidence_exists, acceptance_passed, execution_observed,
                    failure_observed, source_freshness, operator_pause,
                    observation_status, blocked_cause, verification_method,
                    now >>

(* T9. awaiting_approval → executing on approval_granted, under
   can_enter_executing. "Duplicate grants return the recorded decision
   without re-transitioning" (T9 note; PO-9: two grants ⇒ at most one
   executing entry and one consequential effect). *)
ApprovalGranted ==                    \* T9
    /\ can_enter_executing
    /\ work_state' = "executing"
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    blocked_cause, verification_method, now >>

(* T10*. awaiting_approval → in_progress on approval_expired.
   ADOPTED (D5, OQ-3 — awaiting ratification): the intent lapsed without
   a decision; the work item SURVIVES and may issue a fresh intent.
   Expiry is a property of the intent, not a verdict on the work.
   Covers requested, tapped, AND recorded: a recorded-but-expired
   approval can never satisfy can_enter_executing (INV-A4 — the intent
   is dead, and the dead do not authorise), so without this the item
   would wait in awaiting_approval past expiry with no transition,
   violating PO-12. *)
ApprovalExpired ==                    \* T10*
    /\ work_state = "awaiting_approval"
    /\ approval_state \in {"requested", "tapped", "recorded"}
    /\ now >= intent.expiry
    /\ work_state' = "in_progress"
    /\ approval_state' = "expired"
    /\ UNCHANGED << chain, intent, intent_digest, tap_digest,
                    session_authorised,
                    revision, evidence_exists, acceptance_passed,
                    execution_observed, failure_observed, source_freshness,
                    operator_pause, observation_status, blocked_cause,
                    verification_method, now >>

(* T11. awaiting_approval → cancelled on approval_denied. The operator
   refused the consequence; no execution permitted; the item ends (D5). *)
ApprovalDenied ==                     \* T11
    /\ work_state = "awaiting_approval"
    /\ work_state' = "cancelled"
    /\ approval_state' = "denied"
    /\ UNCHANGED << chain, intent, intent_digest, tap_digest,
                    session_authorised,
                    revision, evidence_exists, acceptance_passed,
                    execution_observed, failure_observed, source_freshness,
                    operator_pause, observation_status, blocked_cause,
                    verification_method, now >>

(* T13. executing → verifying on execution_observed. The result is
   observed — success or failure. Dispatch without observation is NOT
   an exit: the state ends when the result is observed (RD-1, §6.1). *)
ExecutionObserved(result) ==          \* T13
    /\ work_state = "executing"
    /\ result \in {"success", "failure"}
    /\ work_state' = "verifying"
    /\ execution_observed' = result
    /\ evidence_exists' = TRUE        \* observed result joins the packet
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, acceptance_passed,
                    failure_observed, source_freshness, operator_pause,
                    observation_status, blocked_cause, verification_method,
                    now >>

(* T14. executing → failed on failure_observed (execution failed or
   retry budget exhausted). *)
ExecutionFailed ==                    \* T14
    /\ work_state = "executing"
    /\ work_state' = "failed"
    /\ failure_observed' = TRUE
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, source_freshness,
                    operator_pause, observation_status, blocked_cause,
                    verification_method, now >>

(* T15. verifying → completed on acceptance_passed, under
   can_enter_completed. The ONLY road into completed (F1; INV-C1, C2, C5).
   Completion supported by fluent text alone is unreachable: evidence
   and the passed test are both required (optimistic completion,
   illegal state 6; PO-7). *)
AcceptancePassed ==                   \* T15
    /\ can_enter_completed
    /\ work_state' = "completed"
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    blocked_cause, verification_method, now >>

(* T16. verifying → failed on failure_observed: acceptance test failed
   or required evidence missing. A failed verification never retries
   execution directly (F9): the path is verifying → failed, or back
   through awaiting_approval with a fresh intent (INV-A2, INV-A7). *)
VerificationFailed ==                 \* T16
    /\ work_state = "verifying"
    /\ work_state' = "failed"
    /\ failure_observed' = TRUE
    /\ acceptance_passed' = FALSE
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    execution_observed, source_freshness, operator_pause,
                    observation_status, blocked_cause, verification_method,
                    now >>

(* T18. any state → paused on operator_paused. The operator intends a
   stop. In-flight consequential execution is brought to a safe point;
   no NEW consequential step begins. The exact mid-executing safe-point
   semantics are OPEN pending the Phase 4 saga spec (U1, §6.2 notes). *)
OperatorPaused ==                     \* T18
    /\ work_state \in NonTerminal
    /\ observation_status = "observed" \* PO-4: cannot pause what we cannot
                                      \* observe; restore observation first
    /\ work_state' = "paused"
    /\ operator_pause' = TRUE
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, observation_status, blocked_cause,
                    verification_method, now >>

(* T19*. paused → in_progress on operator_resumed. Resumption re-
   validates the plan against live sources before work continues (§6.1
   paused), because the world may have moved while it slept. *)
OperatorResumed ==                    \* T19*
    /\ work_state = "paused"
    /\ operator_pause
    /\ work_state' = "in_progress"
    /\ operator_pause' = FALSE
    /\ source_freshness' = "fresh"    \* re-validation against live sources
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    observation_status, blocked_cause, verification_method,
                    now >>

(* T20. any state → unknown on observation_unavailable. The machine can
   always admit ignorance; unknown is forced, not chosen (INV-S1). *)
ObservationLost ==                    \* T20
    /\ work_state \in NonTerminal
    /\ work_state' = "unknown"
    /\ observation_status' = "unavailable"
    /\ operator_pause' = FALSE        \* PO-5: cannot assert a pause on a
                                      \* state we cannot observe
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, blocked_cause,
                    verification_method, now >>

(* T21*. unknown → in_progress on observation_restored. The state is
   re-established by LIVE RE-READ, never by assumption; the item resumes
   from its recorded revision. The single keyed exit from ignorance
   (F6; INV-S1, INV-S4). *)
ObservationRestored ==                \* T21*
    /\ work_state = "unknown"
    /\ observation_status = "unavailable"
    /\ work_state' = "in_progress"
    /\ observation_status' = "observed"
    /\ source_freshness' = "fresh"    \* re-read, not assumed
    /\ UNCHANGED << chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    operator_pause, blocked_cause, verification_method, now >>

(* Chain of custody: links complete strictly in order — link l+1 only
   after link l, so skipping a stage is unreachable by construction
   (Paper I doctrine chain; Paper IV §3.1). *)
AdvanceChain ==                       \* custody progression
    /\ chain < NumLinks
    /\ ChainGate(chain + 1)
    /\ chain' = chain + 1
    /\ UNCHANGED << work_state, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    blocked_cause, verification_method, now >>

(* Time advances on the server clock (D7). Bounded by MaxNow so the
   Phase 1 instance is finite; expiry is then a transition (T10), never
   a lingering condition (RD-2, OQ-3). *)
Tick ==
    /\ now < MaxNow
    /\ work_state = "executing" => now + 1 < intent.expiry
       \* PO-2: time cannot advance past the intent expiry while executing;
       \* the approval's temporal validity is preserved (fail closed: the
       \* work must complete or fail before its authorization lapses)
    /\ now' = now + 1
    /\ UNCHANGED << work_state, chain, approval_state, intent, intent_digest,
                    tap_digest,
                    session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    blocked_cause, verification_method >>

(***************************************************************************)
(* Failure-model actions (Paper IV §7.5): the model assumes failures IN    *)
(* and shows the guards hold regardless.                                   *)
(* Mutated intent (§7.5#3): "a change to any intent field between request  *)
(* and decision" — hence enabled only while approval_state is "requested"  *)
(* or "tapped". The tap_digest is NOT updated, so ServerRecordsApproval's  *)
(* DigestOf(intent) = tap_digest check fails: any mutation forces          *)
(* rejection (PO-3). After recording, the intent is server-held and        *)
(* immutable in this model, which is exactly what makes illegal state 3    *)
(* (recorded with mismatched digest) unreachable. The can_enter_executing  *)
(* guard still recomputes the digest at transition time (§7.3), so the     *)
(* "mutation arriving with the grant" adversarial case is rejected there.  *)
(***************************************************************************)
MutateIntent(mutated) ==              \* failure model: mutated intent
    /\ mutated \in IntentType
    /\ mutated /= intent
    /\ approval_state \in {"requested", "tapped"}
    /\ intent' = mutated               \* digest NOT recomputed: mismatch
    /\ UNCHANGED << work_state, chain, approval_state, intent_digest,
                    tap_digest, session_authorised, revision, evidence_exists,
                    acceptance_passed, execution_observed, failure_observed,
                    source_freshness, operator_pause, observation_status,
                    blocked_cause, verification_method, now >>

Next ==
    \/ BriefAccepted
    \/ BriefDeclined
    \/ PlanCreated
    \/ \E newIntent \in FiniteIntentType : ApprovalRequested(newIntent)
    \/ \E cause \in {"source_unreachable", "permission_missing",
                     "clarifying_unanswered", "other"} : BlockageObserved(cause)
    \/ \E method \in {"human", "machine"} : ArtifactProduced(method)
    \/ FailureObserved
    \/ BlockageCleared
    \/ OperatorTapsApprove
    \/ DuplicateTap
    \/ ServerRecordsApproval
    \/ ApprovalGranted
    \/ ApprovalExpired
    \/ ApprovalDenied
    \/ \E result \in {"success", "failure"} : ExecutionObserved(result)
    \/ ExecutionFailed
    \/ AcceptancePassed
    \/ VerificationFailed
    \/ OperatorPaused
    \/ OperatorResumed
    \/ ObservationLost
    \/ ObservationRestored
    \/ AdvanceChain
    \/ Tick
    \/ \E mutated \in FiniteIntentType : MutateIntent(mutated)

Spec == Init /\ [][Next]_vars

(***************************************************************************)
(* Safety properties — the Phase 1 proof obligations (Paper IV §7.6),      *)
(* stated as state invariants for TLC. PO-3, PO-9, PO-10, PO-11, and      *)
(* PO-12 are transition/temporal properties enforced by the action guards *)
(* and machine structure; Phase 1 renders them as temporal formulas      *)
(* (see note under SafetyInvs).                                           *)
(***************************************************************************)

(* PO-1. No completion without acceptance evidence (illegal state 1). *)
PO1_NoCompletionWithoutEvidence ==
    work_state = "completed" => (evidence_exists /\ acceptance_passed)

(* PO-2. No consequential execution without valid approval (illegal
   state 2). Holds for the LARGEST Δ for which the checker finds no
   counterexample — Δ = 60s, not 300s (Paper IV §7.8; D7). *)
PO2_NoExecutionWithoutApproval ==
    work_state = "executing" =>
        (/\ approval_state = "recorded"
         /\ now < intent.expiry
         /\ intent_digest = DigestOf(intent)
         /\ intent.revision = revision)

(* PO-4. Unknown never renders operational (illegal state 4). Rendering
   is a guarded act (Paper IV §7.3 can_render_operational). *)
PO4_UnknownNotOperational ==
    observation_status = "unavailable" => work_state = "unknown"

(* PO-5. Paused never renders as failed (illegal state 5): the
   operator's intent outranks the machine's diagnosis (Paper IV §7.3). *)
PO5_PausedNotFailed ==
    operator_pause => work_state = "paused"

(* PO-6. Failure evidence from any state leads to failed or blocked; it can
   never produce completion. Transition level: FailureObserved (T7/T12/T17)
   and ExecutionFailed/VerificationFailed (T14/T16) move to failed;
   BlockageObserved (T5) moves to blocked. State level: the
   failure_observed flag is set only on the terminal-failure paths, so it
   implies failed. *)
PO6_FailureNeverCompletes ==
    failure_observed => work_state = "failed"

(* PO-7. A delegated completion claim without a passed acceptance test
   can never satisfy can_enter_completed (illegal state 6; INV-C3). *)
PO7_NoOptimisticCompletion ==
    ~acceptance_passed => ~can_enter_completed

(* PO-8. No transition to recorded is enabled by a client gesture alone:
   recording requires server validation of intent existence, expiry,
   digest, permissibility, and session (illegal state 7; INV-A5). State
   content: the ONLY writer of "recorded" is ServerRecordsApproval, and
   post-record intent is immutable (§7.5#3 scopes mutation to between
   request and decision), so recorded always implies a matched digest. *)
PO8_RecordedImpliesServerValidated ==
    approval_state = "recorded" => intent_digest = DigestOf(intent)

(* PO-10. No guard depending on source truth is satisfiable when
   sources are not fresh. Enforced by construction: BlockageCleared is
   the only source-truth-dependent transition and its guard requires
   source_freshness = "fresh". Kept as a guard-construction obligation
   for Phase 1 rather than a state invariant (it quantifies over an
   action's enabling condition, not a state predicate). *)

(* Chain custody: stages complete strictly in order — `chain` counts
   completed links and only AdvanceChain modifies it, by exactly +1, so
   skipping a stage is unreachable by construction (Paper I doctrine
   chain; Paper IV §3.1). Gate satisfaction at completion time is
   guaranteed by AdvanceChain's ChainGate guard; the persistent
   per-link predicates are intentionally NOT asserted here, because
   paused/unknown suspend depth and would falsify them. *)
ChainCustody ==
    chain \in 0..NumLinks

SafetyInvs ==
    /\ TypeOK
    /\ PO1_NoCompletionWithoutEvidence
    /\ PO2_NoExecutionWithoutApproval
    /\ PO4_UnknownNotOperational
    /\ PO5_PausedNotFailed
    /\ PO6_FailureNeverCompletes
    /\ PO7_NoOptimisticCompletion
    /\ PO8_RecordedImpliesServerValidated
    /\ ChainCustody
(* PO-11. Terminal states are absorbing (F7): once the work item is
   terminal it never leaves the terminal set. Rendered as a temporal
   property for TLC (Phase 1). *)
PO11_TerminalAbsorbing ==
    []((work_state \in TerminalStates) => [](work_state \in TerminalStates))
(* PO-3 (mutation forces rejection), PO-9 (duplicate taps ⇒ one execution), PO-10 (source guards need
   freshness), and PO-12 (liveness: every approval request resolves; no
   item waits past intent_expiry) are transition/temporal properties
   enforced by the action guards and structure above; PO-11 is now
   rendered temporally as well. PO-12 needs fairness assumptions and is
   out of scope for Phase 1 safety checking (Paper IV §7.6, §7.8). *)

=============================================================================
