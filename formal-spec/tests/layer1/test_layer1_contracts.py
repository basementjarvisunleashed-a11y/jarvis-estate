"""Phase 2, Layer 1 — static contract tests.

Tests the REAL ratified artifacts (contracts/events.md,
spec/state-machine.tla) and a Python reference implementation of the
spec's guard semantics (spec_model.py). Every check fails closed.

Run:  python3 -m unittest test_layer1_contracts -v     (from this directory)
or:   ./run.sh
"""

import unittest

import spec_model as sm

EXPECTED_STATES = {
    "received", "accepted", "in_progress", "awaiting_approval",
    "executing", "verifying", "completed", "blocked", "failed",
    "paused", "unknown", "cancelled",
}

EXPECTED_EVENTS = [
    "brief_received", "brief_accepted", "brief_declined", "plan_created",
    "artifact_produced", "evidence_packet_created", "execution_started",
    "execution_observed", "acceptance_passed", "failure_observed",
    "operator_paused", "observation_unavailable", "blockage_cleared",
    "operator_resumed", "observation_restored", "approval_requested",
    "approval_granted", "approval_denied", "approval_expired",
]


def base_intent(**overrides):
    intent = {
        "action": "publish_post",
        "target": "x/@hgxengineering",
        "effect": "post_text",
        "scope": "single_post",
        "revision": 0,
        "expiry": 100,
    }
    intent.update(overrides)
    return intent


def executing_candidate(**overrides):
    """A state that satisfies can_enter_executing, unless overridden."""
    intent = overrides.pop("intent", base_intent())
    s = {
        "work_state": "awaiting_approval",
        "approval_state": "recorded",
        "now": 10,
        "intent": intent,
        "intent_digest": sm.intent_digest(intent),
        "revision": 0,
        "session_authorised": True,
        "operator_pause": False,
    }
    s.update(overrides)
    return s


def completion_candidate(**overrides):
    s = {
        "work_state": "verifying",
        "evidence_exists": True,
        "acceptance_passed": True,
        "failure_observed": False,
        "delegated_claim": False,
    }
    s.update(overrides)
    return s


class TestVocabularyAndStructure(unittest.TestCase):
    """ST: structural checks over the parsed ratified artifacts."""

    @classmethod
    def setUpClass(cls):
        cls.states = sm.parse_states()
        cls.events = sm.parse_events()
        cls.spec_transitions = sm.parse_spec_transitions()
        cls.legal, cls.by_t = sm.build_legal_table()

    def test_states_exactly_twelve(self):
        # ST-01: the spec's States set is exactly the 12 canonical states.
        self.assertEqual(len(self.states), 12)
        self.assertEqual(set(self.states), EXPECTED_STATES)

    def test_events_exactly_nineteen(self):
        # ST-02: events.md defines exactly the 19 canonical events.
        self.assertEqual(len(self.events), 19)
        self.assertEqual(self.events, EXPECTED_EVENTS)

    def test_transition_numbers_complete(self):
        # ST-03: both artifacts reference exactly T1..T21 (21 transitions).
        self.assertEqual(set(self.by_t), set(range(1, 22)))
        self.assertEqual(sm.parse_tla_t_numbers(), set(range(1, 22)))

    def test_transition_endpoints_are_canonical_states(self):
        # ST-04: every parsed spec action moves between canonical states.
        states = set(self.states)
        for action, (src, dst) in self.spec_transitions.items():
            self.assertIn(dst, states, action)
            if src != "ANY_NONTERMINAL":
                self.assertIn(src, states, action)

    def test_events_md_rows_match_spec_actions(self):
        # ST-05: the events.md transition table and the .tla actions agree.
        # Compare coverage with any-state rows expanded over NonTerminal
        # on both sides: events.md spells T7/T12 out concretely and marks
        # T17/T18/T20 "any state"; the spec realises all of them with
        # three ANY_NONTERMINAL actions (FailureObserved, OperatorPaused,
        # ObservationLost).
        nonterminal = {s for s in self.states
                       if s not in set(sm.parse_terminal_states())}
        spec_coverage = set()
        for src, dst in self.spec_transitions.values():
            if src == "ANY_NONTERMINAL":
                spec_coverage |= {(s, dst) for s in nonterminal}
            else:
                spec_coverage.add((src, dst))
        table_coverage = set()
        for _, src, dst in self.by_t.values():
            if src == "ANY":
                table_coverage |= {(s, dst) for s in nonterminal}
            else:
                table_coverage.add((src, dst))
        self.assertEqual(table_coverage, spec_coverage)

    def test_every_transition_event_is_canonical(self):
        # ST-06: every event used by the legal table is in the vocabulary.
        used = {event for (_, event, _) in self.legal if event}
        self.assertTrue(used <= set(self.events), used - set(self.events))
        self.assertEqual(used, set(self.events))

    def test_only_one_road_into_completed(self):
        # ST-07 (F1): exactly one legal event enters `completed`,
        # acceptance_passed from verifying (INV-C1, INV-C5).
        entries = {(f, e) for (f, e, t) in self.legal if t == "completed"}
        self.assertEqual(entries, {("verifying", "acceptance_passed")})

    def test_only_one_road_into_executing(self):
        # ST-08 (F2/F4/F5): exactly one legal event enters `executing`
        # from a different state: approval_granted from
        # awaiting_approval (INV-A1). (execution_started fires within
        # `executing`; it is not an entry.)
        entries = {(f, e) for (f, e, t) in self.legal
                   if t == "executing" and f != "executing"}
        self.assertEqual(entries, {("awaiting_approval", "approval_granted")})

    def test_forbidden_pairs_absent(self):
        # ST-09 (F3, F7, F8): no legal transition leaves a terminal state,
        # and executing -> completed does not exist.
        terminal = set(sm.parse_terminal_states())
        for (f, e, t) in self.legal:
            if f is not None:
                self.assertNotIn(f, terminal, f"{f} -{e}-> {t}")
        self.assertNotIn(("executing", "acceptance_passed", "completed"),
                         self.legal)

    def test_unknown_has_single_keyed_exit(self):
        # ST-10 (F6): the only exit from `unknown` to a different state
        # is observation_restored to in_progress (INV-S1 machine-level
        # discipline). FailureObserved and OperatorPaused cannot fire
        # from `unknown`: both require observation, which is unavailable
        # there by construction (PO-4; Phase 1 Fixes 4-5).
        exits = {(e, t) for (f, e, t) in self.legal
                 if f == "unknown" and t != "unknown"}
        self.assertEqual(exits, {("observation_restored", "in_progress")})


class TestApprovalGuards(unittest.TestCase):
    """CT-A: the approval gate, mirroring can_enter_executing and
    ServerRecordsApproval in spec/state-machine.tla."""

    def test_valid_approval_enters_executing(self):
        # CT-A1 positive control: recorded, unexpired, digest-matched,
        # revision-current, authorised, unpaused -> allowed.
        self.assertTrue(sm.can_enter_executing(executing_candidate()))

    def test_missing_approval_refused(self):
        # (c) CT-A1: no recorded approval -> execution refused, for every
        # pre-record approval state.
        for approval_state in ("none", "requested", "tapped"):
            s = executing_candidate(approval_state=approval_state)
            self.assertFalse(sm.can_enter_executing(s), approval_state)

    def test_expired_approval_refused(self):
        # (b) CT-A4: now >= expiry -> refused at the gate (INV-A4).
        s = executing_candidate(now=100)
        self.assertFalse(sm.can_enter_executing(s))
        s = executing_candidate(now=250)
        self.assertFalse(sm.can_enter_executing(s))

    def test_expired_approval_cannot_be_recorded(self):
        # CT-A4: expiry is checked at record time too — a late tap is
        # never recorded, let alone honoured.
        intent = base_intent()
        s = {"approval_state": "tapped", "now": 100, "intent": intent,
             "tap_digest": sm.intent_digest(intent), "session_authorised": True}
        self.assertFalse(sm.server_record_approval(s))

    def test_mutated_digest_refused_at_gate(self):
        # (a) CT-A3: intent mutated after recording; the stored digest no
        # longer matches the recomputed digest -> refused (INV-A3).
        original = base_intent()
        mutated = base_intent(target="x/@someone_else")
        s = executing_candidate(intent=mutated,
                                intent_digest=sm.intent_digest(original))
        self.assertFalse(sm.can_enter_executing(s))

    def test_mutation_between_tap_and_record_refused(self):
        # (a) CT-A3: mutation between tap and record -> the server cannot
        # record the decision (what was tapped is not what is recorded).
        original = base_intent()
        mutated = base_intent(effect="delete_post")
        s = {"approval_state": "tapped", "now": 10, "intent": mutated,
             "tap_digest": sm.intent_digest(original),
             "session_authorised": True}
        self.assertFalse(sm.server_record_approval(s))

    def test_each_bound_field_mutation_changes_digest(self):
        # CT-A2: the digest binds all six fields; mutating any one of them
        # changes the digest (INV-A2, INV-A3).
        base = sm.intent_digest(base_intent())
        mutations = {
            "action": "delete_post",
            "target": "x/@other",
            "effect": "delete",
            "scope": "all_posts",
            "revision": 1,
            "expiry": 200,
        }
        for field, value in mutations.items():
            digest = sm.intent_digest(base_intent(**{field: value}))
            self.assertNotEqual(digest, base, field)

    def test_revision_mismatch_refused(self):
        # CT-A2: an approval recorded against an older revision cannot
        # authorise the current revision.
        s = executing_candidate(revision=1)
        self.assertFalse(sm.can_enter_executing(s))

    def test_tap_alone_is_not_authority(self):
        # CT-A5: a client tap (even a genuine one) is a gesture until the
        # server records it; a tapped-but-unrecorded approval cannot
        # execute (INV-A5).
        intent = base_intent()
        tap = {"approval_state": "tapped", "now": 10, "intent": intent,
               "tap_digest": sm.intent_digest(intent),
               "session_authorised": True}
        self.assertTrue(sm.server_record_approval(tap))  # server MAY record
        s = executing_candidate(approval_state="tapped")
        self.assertFalse(sm.can_enter_executing(s))      # but tap != recorded

    def test_unauthorised_session_refused(self):
        # CT-A5/PO-8: no authorised session -> neither recording nor
        # execution.
        intent = base_intent()
        tap = {"approval_state": "tapped", "now": 10, "intent": intent,
               "tap_digest": sm.intent_digest(intent),
               "session_authorised": False}
        self.assertFalse(sm.server_record_approval(tap))
        s = executing_candidate(session_authorised=False)
        self.assertFalse(sm.can_enter_executing(s))

    def test_operator_pause_blocks_the_gate(self):
        # CT-A1: a paused item cannot pass the approval gate.
        s = executing_candidate(operator_pause=True)
        self.assertFalse(sm.can_enter_executing(s))

    def test_adjacent_intent_not_authorised(self):
        # CT-A7: a recorded approval for intent X does not authorise
        # intent Y (different revision of the same work).
        x = base_intent()
        y = base_intent(revision=1, expiry=200)
        s = executing_candidate(intent=y, intent_digest=sm.intent_digest(x),
                                revision=1)
        self.assertFalse(sm.can_enter_executing(s))


class TestCompletionGuard(unittest.TestCase):
    """CT-C / CT-E1: the completion gate, mirroring can_enter_completed."""

    def test_valid_completion_allowed(self):
        # CT-C1 positive control: verifying + evidence + acceptance
        # passed + no failure observed -> allowed.
        self.assertTrue(sm.can_enter_completed(completion_candidate()))

    def test_completion_without_evidence_refused(self):
        # (d) CT-C1 / CT-E1: no evidence packet -> no completion.
        s = completion_candidate(evidence_exists=False)
        self.assertFalse(sm.can_enter_completed(s))

    def test_completion_without_acceptance_refused(self):
        # (e) CT-C2: evidence present but the acceptance test has not
        # passed -> no completion.
        s = completion_candidate(acceptance_passed=False)
        self.assertFalse(sm.can_enter_completed(s))

    def test_completion_with_failure_observed_refused(self):
        # CT-C2: a failure observed against the item blocks completion
        # even with evidence and a passed test recorded.
        s = completion_candidate(failure_observed=True)
        self.assertFalse(sm.can_enter_completed(s))

    def test_delegated_claim_cannot_complete(self):
        # CT-C3: a delegated completion claim is not an input to the
        # guard; with no passed acceptance test it cannot complete, and
        # with one, the claim adds nothing (INV-C3).
        s = completion_candidate(delegated_claim=True, acceptance_passed=False)
        self.assertFalse(sm.can_enter_completed(s))
        s = completion_candidate(delegated_claim=True)
        self.assertTrue(sm.can_enter_completed(s))

    def test_completion_only_from_verifying(self):
        # CT-C5: completion is reachable only from verifying; fluent
        # claims from any other state fail (INV-C5).
        for state in ("in_progress", "executing", "accepted"):
            s = completion_candidate(work_state=state)
            self.assertFalse(sm.can_enter_completed(s), state)


class TestTransitionValidation(unittest.TestCase):
    """Fail-closed validation of (from, event, to) against the legal
    table built from the two ratified artifacts."""

    @classmethod
    def setUpClass(cls):
        cls.states = sm.parse_states()
        cls.events = sm.parse_events()
        cls.legal, _ = sm.build_legal_table()

    def apply(self, f, e, t):
        return sm.apply_transition(self.legal, self.events, self.states,
                                   f, e, t)

    def test_legal_transitions_accepted(self):
        # Positive controls across the table.
        self.assertTrue(self.apply("received", "brief_accepted", "accepted"))
        self.assertTrue(self.apply("in_progress", "approval_requested",
                                   "awaiting_approval"))
        self.assertTrue(self.apply("awaiting_approval", "approval_granted",
                                   "executing"))
        self.assertTrue(self.apply("verifying", "acceptance_passed",
                                   "completed"))
        self.assertTrue(self.apply("unknown", "observation_restored",
                                   "in_progress"))

    def test_unknown_event_rejected(self):
        # (f) an event outside the canonical vocabulary fails closed.
        with self.assertRaises(sm.Rejected):
            self.apply("received", "brief_approved", "accepted")
        with self.assertRaises(sm.Rejected):
            self.apply("verifying", "work_completed", "completed")

    def test_unknown_state_rejected(self):
        # (g) a state outside the canonical set fails closed, on either
        # side of the transition.
        with self.assertRaises(sm.Rejected):
            self.apply("sleeping", "brief_accepted", "accepted")
        with self.assertRaises(sm.Rejected):
            self.apply("verifying", "acceptance_passed", "done")

    def test_illegal_transition_failed_to_completed(self):
        # (h) F8: failed -> completed is forbidden, on any event.
        with self.assertRaises(sm.Rejected):
            self.apply("failed", "acceptance_passed", "completed")
        with self.assertRaises(sm.Rejected):
            self.apply("failed", "failure_observed", "completed")

    def test_illegal_transition_executing_to_completed(self):
        # (h) F3: execution is not verification.
        with self.assertRaises(sm.Rejected):
            self.apply("executing", "acceptance_passed", "completed")

    def test_illegal_transition_bypassing_approval(self):
        # (h) F4/F5: in_progress -> executing and paused -> executing
        # bypass the approval gate and are forbidden (INV-A1).
        with self.assertRaises(sm.Rejected):
            self.apply("in_progress", "approval_granted", "executing")
        with self.assertRaises(sm.Rejected):
            self.apply("paused", "approval_granted", "executing")

    def test_second_grant_is_not_a_second_transition(self):
        # CT-A6 (machine level): once approval_granted has moved the
        # item to executing, a duplicate grant has no legal transition;
        # it cannot produce a second execution (INV-A6).
        self.assertTrue(self.apply("awaiting_approval", "approval_granted",
                                   "executing"))
        with self.assertRaises(sm.Rejected):
            self.apply("executing", "approval_granted", "executing")


class TestFreshnessStructure(unittest.TestCase):
    """CT-E5 / CT-S4 (structural): source-truth guards in the spec text."""

    @classmethod
    def setUpClass(cls):
        cls.defs = sm._definitions(sm.TLA.read_text(encoding="utf-8"))

    def test_blockage_cleared_requires_fresh_sources(self):
        # T8's guard is unsatisfiable unless sources are fresh (PO-10).
        self.assertIn('source_freshness = "fresh"',
                      self.defs["BlockageCleared"])

    def test_resumption_revalidates_against_live_sources(self):
        # T19: resumption sets freshness by re-validation, not assumption.
        self.assertIn('source_freshness\' = "fresh"',
                      self.defs["OperatorResumed"])

    def test_observation_restored_re_reads(self):
        # T21: leaving unknown requires a live re-read (freshness set
        # fresh by the restoration, never assumed) (INV-S4).
        self.assertIn('source_freshness\' = "fresh"',
                      self.defs["ObservationRestored"])

    def test_duplicate_tap_changes_nothing(self):
        # CT-A6 (structural): DuplicateTap is a stutter — it assigns no
        # work_state' and returns the recorded decision as-is.
        self.assertNotIn("work_state'", self.defs["DuplicateTap"])


if __name__ == "__main__":
    unittest.main()
