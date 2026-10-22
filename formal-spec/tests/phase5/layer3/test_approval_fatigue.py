"""Phase 5 Layer 3 -- adversarial approval-fatigue scenarios (T-24/T-14).

Threats: T-24 (approval fatigue, attack: barrage of approvals
degrading judgment), T-14 (attention exhaustion). Controls: C-17
(silent-by-default), C-18 (no bulk approval), C-19 (risk classes;
high-risk requires local auth and exact rendering), C-20 (attention
budget monitored with human review -- honestly non-mechanically-
testable; the suite verifies the verification method).
Attack tree: AT-4.

Barrages of valid, invalid, and mixed approval requests; the
exact-target/effect rule holds for every single one; bulk approval
never happens; attention-budget exhaustion refuses/queues rather
than auto-approving; a fatigued-looking rapid sequence still binds
each approval to its own digest.

Cases AF-01..AF-08. Every case names its threat ID and control ID
and logs its verdict via record_verdict.
"""

import itertools
import os
import sys
import unittest
from datetime import timedelta

sys.path.insert(0, ".")
from adversary import (fresh_estate, grant_intent, classify_risk,
                       request_with_classification,
                       record_verdict, HELD_REFUSED, CLEAN_PASS)
from estate import (Clock, Attention, Refusal, intent_of,
                    render_approval_card)

_LAYER2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "layer2")


def high_risk_intent(clock, approval_id):
    expiry = (clock.now() + timedelta(seconds=3600)).isoformat()
    return intent_of(approval_id, target="vendor:acme",
                     effect="transfer 120 CAD", scope="acct-8842",
                     expiry_iso=expiry)


def routine_intent(clock, approval_id):
    expiry = (clock.now() + timedelta(seconds=3600)).isoformat()
    return intent_of(approval_id, target="digest:weekly",
                     effect="generate weekly summary", scope="internal",
                     expiry_iso=expiry)


class TestApprovalFatigueAdversarial(unittest.TestCase):
    """T-24/T-14 under fire; AT-4 leaves."""

    def test_af01_barrage_of_valid_requests_hits_budget(self):
        """AF-01 | T-24 | C-18 | AT-4 flood leaf.

        Six valid high-risk requests in one hour: the first three
        are requested, the rest are refused/queued -- never
        bulk-approved, never auto-approved."""
        attention = Attention(Clock())  # budget 3/hour
        results = []
        for i in range(6):
            intent = high_risk_intent(attention.clock, f"intent-af01-{i}")
            try:
                results.append(attention.request_approval(
                    intent, risk="high",
                    card=render_approval_card(intent)))
            except Refusal as exc:
                results.append(f"refused:{exc.cause}")
        self.assertEqual(results[:3], ["requested"] * 3)
        self.assertEqual(results[3:],
                         ["refused:attention-budget-exceeded"] * 3)
        record_verdict("AF-01", "T-24", "C-18", HELD_REFUSED,
                       "barrage of 6 valid high-risk requests: 3 "
                       "requested, 3 refused "
                       "(attention-budget-exceeded); no bulk approval")

    def test_af02_barrage_of_invalid_requests(self):
        """AF-02 | T-24 | C-19 | AT-4 lookalike leaf.

        Six requests with inexact cards: every one refused with a
        named cause; none consumes budget."""
        attention = Attention(Clock())
        for i in range(6):
            intent = high_risk_intent(attention.clock, f"intent-af02-{i}")
            wrong = high_risk_intent(attention.clock, "intent-af02-wrong")
            with self.assertRaises(Refusal) as cm:
                attention.request_approval(
                    intent, risk="high",
                    card=render_approval_card(wrong))
            self.assertEqual(cm.exception.cause, "high-risk-not-exact")
        self.assertEqual(attention.requested, [])
        record_verdict("AF-02", "T-24", "C-19", HELD_REFUSED,
                       "barrage of 6 inexact-card requests: all refused "
                       "high-risk-not-exact; budget untouched")

    def test_af03_mixed_barrage_orderings_invariant(self):
        """AF-03 | T-24 | C-18/C-19 | systematic permutation
        enumeration.

        2 valid + 2 invalid requests in all 24 orderings: the verdict
        per request is identical in every ordering -- the barrage
        cannot sneak an invalid request through by position."""
        base = Clock()
        specs = [("v0", high_risk_intent(base, "intent-af03-v0"), True),
                 ("v1", high_risk_intent(base, "intent-af03-v1"), True),
                 ("x0", high_risk_intent(base, "intent-af03-x0"), False),
                 ("x1", high_risk_intent(base, "intent-af03-x1"), False)]
        first = None
        for ordering in itertools.permutations(range(4)):
            attention = Attention(Clock())  # budget 3 > 2 valid
            outcomes = {}
            for idx in ordering:
                rid, intent, valid = specs[idx]
                card = render_approval_card(intent) if valid else \
                    render_approval_card(specs[0][1])
                try:
                    outcomes[rid] = attention.request_approval(
                        intent, risk="high", card=card)
                except Refusal as exc:
                    outcomes[rid] = f"refused:{exc.cause}"
            if first is None:
                first = outcomes
            self.assertEqual(outcomes, first, f"ordering {ordering}")
        self.assertEqual(first["v0"], "requested")
        self.assertEqual(first["v1"], "requested")
        self.assertEqual(first["x0"], "refused:high-risk-not-exact")
        self.assertEqual(first["x1"], "refused:high-risk-not-exact")
        record_verdict("AF-03", "T-24", "C-19", HELD_REFUSED,
                       "24/24 orderings identical: valid->requested, "
                       "invalid->refused(high-risk-not-exact); position "
                       "confers no advantage")

    def test_af04_bulk_approve_always_refused(self):
        """AF-04 | T-24 | C-18 | AT-4 bulk-pressure leaf.

        'Approve all' is refused even when every intent is valid; one
        approval never covers two intents; replays never execute
        twice."""
        clock, sessions, approvals, sid = fresh_estate()
        attention = Attention(Clock())
        intents = [high_risk_intent(Clock(), f"intent-af04-{i}")
                   for i in range(6)]
        with self.assertRaises(Refusal) as cm:
            attention.bulk_approve(intents)
        self.assertEqual(cm.exception.cause, "bulk-approval-refused")

        intent_a, rec_a = grant_intent(
            clock, approvals, sid, "appr-af04-a",
            target="vendor:acme", effect="transfer 120 CAD",
            scope="acct-8842")
        approvals.execute("appr-af04-a", rec_a.digest, sid)  # once: ok
        with self.assertRaises(Refusal) as cm:
            approvals.execute("appr-af04-a", rec_a.digest, sid)
        self.assertEqual(cm.exception.cause, "approval-replay")
        # one approval cannot be stretched over a second intent:
        with self.assertRaises(Refusal) as cm:
            approvals.validate("appr-af04-b", rec_a.digest, sid)
        self.assertEqual(cm.exception.cause, "fake-approval")
        record_verdict("AF-04", "T-24", "C-18", HELD_REFUSED,
                       "bulk_approve refused (bulk-approval-refused); "
                       "one approval = one action (approval-replay on "
                       "second use; fake-approval for a second intent)")

    def test_af05_fatigued_rapid_sequence_binds_every_digest(self):
        """AF-05 | T-24 | C-4/C-5 | fatigued-principal leaf.

        Eight approvals granted one second apart (a fatigued-looking
        rapid sequence). All 56 cross-presentations are refused: each
        approval binds its own digest, and each executes at most
        once."""
        clock, sessions, approvals, sid = fresh_estate()
        records = []
        for i in range(8):
            _intent, rec = grant_intent(
                clock, approvals, sid, f"appr-af05-{i}",
                target=f"vendor:acme-{i}", effect="transfer 120 CAD",
                scope="acct-8842")
            records.append((f"appr-af05-{i}", rec))
            clock.advance(1)
        mismatches = 0
        for i, (idi, reci) in enumerate(records):
            for j, (idj, _recj) in enumerate(records):
                if i == j:
                    continue
                with self.assertRaises(Refusal) as cm:
                    approvals.validate(idj, reci.digest, sid)
                self.assertEqual(cm.exception.cause, "digest-mismatch")
                mismatches += 1
        self.assertEqual(mismatches, 56)
        for idi, reci in records:
            approvals.execute(idi, reci.digest, sid)  # each once: ok
        with self.assertRaises(Refusal) as cm:
            approvals.execute(records[0][0], records[0][1].digest, sid)
        self.assertEqual(cm.exception.cause, "approval-replay")
        record_verdict("AF-05", "T-24", "C-4", HELD_REFUSED,
                       "8 rapid approvals: 56/56 cross-presentations "
                       "refused (digest-mismatch); 8/8 correct digests "
                       "executed once; replay refused "
                       "(approval-replay)")

    def test_af06_high_risk_disguised_as_routine(self):
        """AF-06 | T-24 | C-19 | AT-4 desensitize-with-lookalikes leaf.

        A high-risk intent claimed as 'standard' is escalated by the
        digest-bound classification (flagged), then handled as
        high-risk: exact card required."""
        clock = Clock()
        expiry = (clock.now() + timedelta(seconds=3600)).isoformat()
        intent = intent_of("intent-af06", target="vendor:acme",
                           effect="transfer 50000 CAD",
                           scope="acct-8842, iban-DE89370400440532013000",
                           expiry_iso=expiry)
        self.assertEqual(classify_risk(intent), "high")  # not "standard"

        attention = Attention(Clock())
        with self.assertRaises(Refusal) as cm:
            request_with_classification(attention, intent,
                                        claimed_risk="standard")
        self.assertEqual(cm.exception.cause, "high-risk-not-exact")

        attention2 = Attention(Clock())
        result = request_with_classification(
            attention2, intent, claimed_risk="standard",
            card=render_approval_card(intent))
        self.assertEqual(result, "requested")
        record_verdict("AF-06", "T-24", "C-19", HELD_REFUSED,
                       "disguised high-risk escalated (flagged: "
                       "risk-class-escalated); without exact card "
                       "refused (high-risk-not-exact); with exact "
                       "card requested singly")

    def test_af07_routine_requests_stay_silent_under_barrage(self):
        """AF-07 | T-14 | C-17 | AT-4 routine-flood leaf.

        Six routine requests under barrage conditions stay silent:
        HgX is not notified for routine work."""
        attention = Attention(Clock())
        for i in range(6):
            intent = routine_intent(attention.clock, f"intent-af07-{i}")
            self.assertEqual(classify_risk(intent), "standard")
            self.assertEqual(
                attention.request_approval(intent, risk="standard"),
                "silent")
        self.assertEqual(attention.requested, [])
        record_verdict("AF-07", "T-14", "C-17", CLEAN_PASS,
                       "6 routine requests under barrage stay silent; "
                       "HgX not notified (silent-by-default)")

    def test_af08_budget_log_exportable_for_human_review(self):
        """AF-08 | T-27 | C-20 | honest mark.

        C-20 is non-mechanically-testable: no test proves a fatigue
        curve. What the suite checks is the verification method --
        the review procedure exists, states thresholds as operational
        judgment, and the budget log it reviews is exportable and
        carries the barrage (requested and refused) for a reviewer."""
        attention = Attention(Clock())
        for i in range(5):
            intent = high_risk_intent(attention.clock, f"intent-af08-{i}")
            try:
                attention.request_approval(
                    intent, risk="high",
                    card=render_approval_card(intent))
            except Refusal:
                pass
        log = attention.export_budget_log()
        self.assertEqual(len(log), 3)  # the 3 requested, for review
        self.assertTrue(all(e["risk"] == "high" for e in log))
        proc_path = os.path.join(_LAYER2, "review-procedure.md")
        with open(proc_path, encoding="utf-8") as fh:
            proc = fh.read()
        self.assertIn("operational judgment", proc)
        self.assertIn("No test can", proc)
        record_verdict("AF-08", "T-27", "C-20", CLEAN_PASS,
                       "review procedure exists and states thresholds "
                       "as operational judgment; budget log exportable "
                       "(3 requested entries); refused barrages in the "
                       "rejection log for the reviewer")


if __name__ == "__main__":
    unittest.main()
