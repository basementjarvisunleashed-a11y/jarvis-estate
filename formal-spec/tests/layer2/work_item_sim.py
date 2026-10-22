"""Layer 2 work-item simulator for the J.A.R.V.I.S. Phase 2 suite.

A step-machine over the ratified artifacts, built on the Layer 1
reference model (`tests/layer1/spec_model.py`): the legal-transition
table is the one cross-built from `contracts/events.md` and
`spec/state-machine.tla`, and the two gates are the spec's own guard
semantics (`can_enter_executing`, `ServerRecordsApproval`,
`can_enter_completed`). Nothing here modifies the artifacts.

Every attempted action — legal-table event or environment action —
either changes the machine or is refused, and every refusal is counted
in the module-level REJECTIONS ledger under a guard name. The Layer 2
suite drains that ledger into the rejection-log evidence file: an
invariant that has never rejected anything is a claim, not a control
(PHASE-2-PLAN, Layer 2 gate).
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "layer1"))
import spec_model as sm  # noqa: E402

LEGAL, BY_T = sm.build_legal_table()
EVENTS = sm.parse_events()
EVENT_SET = set(EVENTS)
STATES = sm.parse_states()
TERMINAL = set(sm.parse_terminal_states())

# ---------------------------------------------------------------------------
# Rejection ledger (drained by the suite into the evidence log)
# ---------------------------------------------------------------------------

REJECTIONS = Counter()   # guard name -> refused attempts
ATTEMPTS = Counter()     # action name -> attempts
ACCEPTED = Counter()     # action name -> accepted attempts


def note_rejection(guard):
    REJECTIONS[guard] += 1


def reset_ledger():
    REJECTIONS.clear()
    ATTEMPTS.clear()
    ACCEPTED.clear()


# ---------------------------------------------------------------------------
# Intents (same six bound fields as Layer 1 / Paper IV section 5.6)
# ---------------------------------------------------------------------------

def base_intent(**overrides):
    intent = {
        "intent_id": "intent-001",
        "work_id": "work-001",
        "action": "publish_post",
        "target": "x/@hgxengineering",
        "effect": "post_text",
        "scope": "single_post",
        "revision": 0,
        "expiry": 100,
    }
    intent.update(overrides)
    return intent


# ---------------------------------------------------------------------------
# State rendering (contract-level reference for INV-S1/S2/S4, PT-5)
#
# The rendering contract (Paper IV section 7.3; Paper III): a surface may
# render `operational` only for a state that is observed and fresh.
# Observation unavailable forces `unknown`; stale data renders at reduced
# confidence, never operational at full confidence; an operator pause
# renders as `paused`, never as `failed`.
# ---------------------------------------------------------------------------

def render_state(work_state, observation_status, source_freshness,
                 operator_pause=False):
    if observation_status == "unavailable":
        return "unknown"
    if work_state == "unknown":
        return "unknown"
    if operator_pause or work_state == "paused":
        return "paused"
    if work_state in TERMINAL:
        return work_state  # terminal states render as themselves
    if source_freshness != "fresh":
        return "reduced_confidence"
    return "operational"


# ---------------------------------------------------------------------------
# The work item
# ---------------------------------------------------------------------------

class WorkItem:
    """One work item driven through the machine by attempted actions.

    Attempt methods return True when the action was accepted (the
    machine changed or a fact was recorded) and False when it was
    refused; every refusal is entered in the rejection ledger under the
    guard that refused it.
    """

    def __init__(self, intent=None, now=0):
        self.created = False
        self.work_state = None
        self.approval_state = "none"     # none|requested|tapped|recorded
        self.intent = intent if intent is not None else base_intent()
        self.intent_digest = None        # digest stored at record time
        self.tap_digest = None           # digest the operator saw at tap
        self.revision = self.intent["revision"]
        self.now = now
        self.session_authorised = True
        self.operator_pause = False
        self.evidence_exists = False
        self.acceptance_result = False   # acceptance test outcome (fact)
        self.failure_observed = False
        self.claim_asserted = False
        self.source_freshness = "fresh"
        self.observation_status = "observed"
        self.executions = 0
        self.executions_by_digest = Counter()
        self.recorded_decisions = 0
        self.completions = 0
        self.tamper_signals = []
        self.escalations = []
        # Snapshot taken at the moment of entering `executing`, so tests
        # can assert the gate's preconditions from recorded values.
        self.executing_entry = None
        # Snapshot taken at the moment of entering `completed`, for the
        # same reason: PO-1/INV-C1/C2 bind the transition's preconditions
        # at completion time. Environment facts (an acceptance result
        # recorded later against another item of work, a source going
        # stale) may change afterwards; the terminal state does not.
        self.completion_entry = None

    # -- guard state views (same shapes as spec_model expects) ----------

    def _gate_view(self):
        return {
            "work_state": self.work_state,
            "approval_state": self.approval_state,
            "now": self.now,
            "intent": self.intent,
            "intent_digest": self.intent_digest,
            "revision": self.revision,
            "session_authorised": self.session_authorised,
            "operator_pause": self.operator_pause,
        }

    def _record_view(self):
        return {
            "approval_state": self.approval_state,
            "now": self.now,
            "intent": self.intent,
            "tap_digest": self.tap_digest,
            "session_authorised": self.session_authorised,
        }

    def _completion_view(self):
        return {
            "work_state": self.work_state,
            "evidence_exists": self.evidence_exists,
            "acceptance_passed": self.acceptance_result,
            "failure_observed": self.failure_observed,
            "delegated_claim": self.claim_asserted,
        }

    # -- failure classification -----------------------------------------

    def gate_failure_guard(self):
        """Name the conjunct of can_enter_executing that fails, in the
        spec's own order, so rejections are attributed to a guard."""
        if self.work_state != "awaiting_approval":
            return "gate-wrong-state"
        if self.approval_state != "recorded":
            return "approval-not-recorded"
        if self.intent is None:
            return "no-intent"
        if not self.now < self.intent["expiry"]:
            return "approval-expired"
        if self.intent_digest != sm.intent_digest(self.intent):
            return "digest-mismatch"
        if self.intent["revision"] != self.revision:
            return "revision-mismatch"
        if not self.session_authorised:
            return "session-unauthorised"
        if self.operator_pause:
            return "operator-pause"
        return None  # gate passes

    def record_failure_guard(self):
        if self.approval_state != "tapped":
            return "record-without-tap"
        if self.intent is None:
            return "no-intent"
        if not self.now < self.intent["expiry"]:
            return "approval-expired"
        if sm.intent_digest(self.intent) != self.tap_digest:
            return "digest-mismatch"
        if not self.session_authorised:
            return "session-unauthorised"
        return None

    def completion_failure_guard(self):
        if self.work_state != "verifying":
            return "completion-wrong-state"
        if not self.evidence_exists:
            return "completion-no-evidence"
        if not self.acceptance_result:
            return "completion-acceptance-not-passed"
        if self.failure_observed:
            return "completion-failure-observed"
        return None

    # -- event attempts (legal table + gates) ----------------------------

    def attempt_event(self, event, reading=None):
        """Attempt one canonical (or bogus) event. Returns True iff the
        machine accepted it.

        `reading` disambiguates the one event the artifacts bind to two
        transitions from the same state: `failure_observed` from
        `in_progress` is T5 (blocked — a required condition unavailable,
        recovery plausible) in its "blocking" reading, and T7 (failed)
        in its default reading (events.md section 4, event 10 and the
        T5/T7 rows). Every other (state, event) pair in the cross-built
        legal table has exactly one target.
        """
        ATTEMPTS[event] += 1
        if event not in EVENT_SET:
            note_rejection("unknown-event")
            return False
        if not self.created:
            if event == "brief_received":
                self.created = True
                self.work_state = "received"
                ACCEPTED[event] += 1
                return True
            note_rejection("illegal-transition")
            return False
        targets = {t for (f, e, t) in LEGAL
                   if f == self.work_state and e == event}
        if not targets:
            note_rejection("illegal-transition")
            return False
        if len(targets) > 1:
            if event == "failure_observed" and self.work_state == "in_progress":
                target = "blocked" if reading == "blocking" else "failed"
            else:  # pragma: no cover - the table has no other ambiguity
                raise AssertionError(
                    f"ambiguous legal targets for {self.work_state} "
                    f"-{event}-> {targets}")
        else:
            target = next(iter(targets))

        # Gated transitions: the legal table admits the shape; the spec's
        # guards decide.
        if event == "approval_granted":
            guard = self.gate_failure_guard()
            if guard is not None:
                note_rejection(guard)
                return False
            self.executing_entry = {
                "approval_state": self.approval_state,
                "now": self.now,
                "expiry": self.intent["expiry"],
                "digest_matched":
                    self.intent_digest == sm.intent_digest(self.intent),
                "executions_by_digest_before":
                    self.executions_by_digest[self.intent_digest],
            }
            self.executions += 1
            self.executions_by_digest[self.intent_digest] += 1
        elif event == "acceptance_passed":
            guard = self.completion_failure_guard()
            if guard is not None:
                note_rejection(guard)
                return False
            self.completion_entry = {
                "evidence_exists": self.evidence_exists,
                "acceptance_result": self.acceptance_result,
                "failure_observed": self.failure_observed,
            }
            self.completions += 1
        elif event == "blockage_cleared":
            # T8 is the one source-truth-dependent transition; its guard
            # requires fresh sources (PO-10). Stale data cannot satisfy it.
            if self.source_freshness != "fresh":
                note_rejection("stale-source")
                return False
        elif event == "approval_expired":
            # T10 fires when the intent's expiry has passed.
            if self.intent is None or self.now < self.intent["expiry"]:
                note_rejection("approval-not-expired")
                return False
            self.approval_state = "none"
            self.intent_digest = None
            self.tap_digest = None
        elif event == "approval_denied":
            self.approval_state = "none"

        self.work_state = target

        # Side effects recorded by the spec's actions.
        if event == "approval_requested":
            self.approval_state = "requested"
        elif event == "failure_observed":
            # The flag is set only on the terminal-failure paths; the
            # T5 blocking reading records a blockage, not a failure
            # (spec note under PO-6).
            if target == "failed":
                self.failure_observed = True
        elif event == "operator_paused":
            self.operator_pause = True
        elif event == "operator_resumed":
            self.operator_pause = False
            self.source_freshness = "fresh"   # T19 re-validates (PO-10)
        elif event == "observation_unavailable":
            self.observation_status = "unavailable"
            self.operator_pause = False       # spec Fix 3 (PO-5)
        elif event == "observation_restored":
            self.observation_status = "observed"
            self.source_freshness = "fresh"   # T21 re-reads (INV-S4)
        ACCEPTED[event] += 1
        return True

    # -- environment / operator actions ----------------------------------

    def tap(self):
        """Operator taps Approve. A gesture only: records what the
        operator saw (the digest of the intent as rendered), never
        authority (INV-A5)."""
        ATTEMPTS["tap"] += 1
        if self.approval_state != "requested" or self.intent is None:
            note_rejection("tap-without-request")
            return False
        self.approval_state = "tapped"
        self.tap_digest = sm.intent_digest(self.intent)
        ACCEPTED["tap"] += 1
        return True

    def record(self):
        """Server validates the tap (ServerRecordsApproval). The only
        path to `recorded`."""
        ATTEMPTS["record"] += 1
        if sm.server_record_approval(self._record_view()):
            self.approval_state = "recorded"
            self.intent_digest = self.tap_digest
            self.recorded_decisions += 1
            ACCEPTED["record"] += 1
            return True
        note_rejection(self.record_failure_guard())
        return False

    def duplicate_tap(self):
        """A repeated tap after the decision is recorded: a stutter.
        It returns the recorded outcome and changes nothing (spec
        DuplicateTap; INV-A6). Counted in the ledger as a refused
        duplicate — refused, precisely, the power to change anything."""
        ATTEMPTS["duplicate_tap"] += 1
        if self.approval_state == "recorded":
            note_rejection("duplicate-tap-noop")
            return False
        return self.tap()

    def mutate_intent(self, field, value):
        """The intent changes under the operator's feet (failure model
        MutateIntent). A fact about the world, not a machine action:
        always 'accepted'; the guards are what refuse its consequences."""
        ATTEMPTS["mutate_intent"] += 1
        if self.intent is None:
            note_rejection("no-intent")
            return False
        self.intent = dict(self.intent, **{field: value})
        ACCEPTED["mutate_intent"] += 1
        return True

    def tick(self, steps=1):
        ATTEMPTS["tick"] += 1
        self.now += steps
        ACCEPTED["tick"] += 1
        return True

    def submit_evidence(self):
        ATTEMPTS["submit_evidence"] += 1
        self.evidence_exists = True
        ACCEPTED["submit_evidence"] += 1
        return True

    def set_acceptance_result(self, passed):
        ATTEMPTS["acceptance_result"] += 1
        self.acceptance_result = bool(passed)
        ACCEPTED["acceptance_result"] += 1
        return True

    def delegated_claim(self):
        """A sub-agent asserts completion (failure model F5). The claim
        is recorded; it is not an input to any guard (INV-C3)."""
        ATTEMPTS["delegated_claim"] += 1
        self.claim_asserted = True
        if not self.evidence_exists:
            self.escalations.append("claim without proof")
        ACCEPTED["delegated_claim"] += 1
        return True

    def set_freshness(self, freshness):
        ATTEMPTS["set_freshness"] += 1
        self.source_freshness = freshness
        ACCEPTED["set_freshness"] += 1
        return True

    def new_intent(self, intent):
        """A fresh intent is issued for the item (new revision): the
        approval cycle resets. This is a new authorisation question,
        never a continuation of the old one (INV-A7)."""
        ATTEMPTS["new_intent"] += 1
        self.intent = intent
        self.revision = intent["revision"]
        self.approval_state = "none"
        self.intent_digest = None
        self.tap_digest = None
        ACCEPTED["new_intent"] += 1
        return True

    # -- convenience driver ----------------------------------------------

    def drive_to_awaiting_approval(self):
        """Walk the happy path received -> accepted -> in_progress ->
        awaiting_approval. Returns True iff every step was accepted."""
        ok = self.attempt_event("brief_received")
        ok = self.attempt_event("brief_accepted") and ok
        ok = self.attempt_event("plan_created") and ok
        ok = self.attempt_event("approval_requested") and ok
        return ok
