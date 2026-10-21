"""Phase 3 Layer 3 — SK family: adversarial clock skew.

OP-1 (HgX's word, 2026-10-21 ~17:49 ET): 300 s request bound, 60 s
state/event bound — both probed at their exact boundaries and one second
beyond, in both directions. Asserted: beyond-bound requests are refused;
beyond-bound events are refused; skew grants no authority (it cannot
bypass the other four gate checks, and it cannot mint a decision); a race
run under adversarial skew still resolves to exactly one decision.

Draft sections cited: revision-protocol.md section 5 (five-step gate,
OP-1); freshness-policy.md section 4; consistency-model.md NT-2
(age honesty).
Exit criteria served: "behavior tested under clock skew";
"stale data cannot masquerade as current".
"""

import unittest

from chaos import (NOW, assert_loser_path, assert_no_decision,
                   assert_single_decision, decide, fixture, mutate,
                   record_verdict, run_interleavings)
from clients import Surface


class TestClockSkew(unittest.TestCase):
    """SK: the bounds hold at their edges, and skew buys nothing."""

    def test_sk1_request_bound_exact(self):
        """|now - ts| = 300 s is accepted; 301 s is refused — both
        directions. The refused mutation changes nothing."""
        cases = [("plus300", NOW + 300, True), ("plus301", NOW + 301, False),
                 ("minus300", NOW - 300, True), ("minus301", NOW - 301, False)]
        for name, ts, ok in cases:
            orch = fixture()
            r = mutate(orch, "iphone-s1", "armed", ts=ts)
            if ok:
                self.assertTrue(r["ok"], name)
                self.assertEqual(r["revision"], 1, name)
            else:
                self.assertEqual(r["reason"], "stale-request", name)
                self.assertEqual(orch.works["work-1"]["revision"], 0, name)
            record_verdict("SK-1/" + name,
                           ["OP-1 (300 s request bound, exact boundary)",
                            "exit: behavior tested under clock skew"])

    def test_sk2_event_bound_exact(self):
        """Event age 60 s is accepted; 61 s is refused stale-event — the
        state/event bound from Phase 0 U-5/D7."""
        for name, oa, ok in (("age60", NOW - 60, True),
                             ("age61", NOW - 61, False)):
            orch = fixture()
            r = mutate(orch, "iphone-s1", "armed", observed_at=oa)
            if ok:
                self.assertTrue(r["ok"], name)
            else:
                self.assertEqual(r["reason"], "stale-event", name)
                self.assertEqual(orch.works["work-1"]["revision"], 0, name)
            record_verdict("SK-2/" + name,
                           ["OP-1 (60 s state/event bound, exact boundary)",
                            "exit: behavior tested under clock skew"])

    def test_sk3_skew_cannot_mint_decision(self):
        """A client 400 s out in either direction cannot get a decision
        recorded: stale-request, nothing recorded, work untouched."""
        for name, ts in (("plus400", NOW + 400), ("minus400", NOW - 400)):
            orch = fixture()
            r = decide(orch, "iphone-s1", ts=ts)
            self.assertEqual(r["reason"], "stale-request", name)
            assert_no_decision(self, orch)
            record_verdict("SK-3/" + name,
                           ["OP-1", "revision-protocol.md section 5",
                            "exit: behavior tested under clock skew",
                            "exit: no device can become a source of truth"])

    def test_sk4a_skew_does_not_bypass_revision(self):
        """In-bound skew (+250 s) with a stale revision: refused for the
        revision, not the clock — skew does not waive the other checks."""
        orch = fixture()
        r = decide(orch, "iphone-s1", revision=99, ts=NOW + 250)
        self.assertEqual(r["reason"], "stale-revision")
        assert_no_decision(self, orch)
        record_verdict("SK-4a",
                       ["revision-protocol.md section 5 (check order)",
                        "exit: behavior tested under clock skew"])

    def test_sk4b_skew_does_not_bypass_digest(self):
        """In-bound skew (-250 s) with a wrong digest: digest-lapse, no
        execution — the binding holds under skew."""
        orch = fixture()
        r = decide(orch, "iphone-s1", digest="0" * 64, ts=NOW - 250)
        self.assertEqual(r["reason"], "digest-lapse")
        self.assertEqual(len(orch.lapses), 1)
        assert_no_decision(self, orch)
        record_verdict("SK-4b",
                       ["revision-protocol.md section 5 step 5",
                        "exit: behavior tested under clock skew"])

    def test_sk5_race_under_skew(self):
        """Both racers skewed to opposite in-bound edges (+250 / -250):
        every order still resolves to exactly one decision."""
        builders = [
            ("iphone-skewed", lambda o: decide(o, "iphone-s1", ts=NOW + 250)),
            ("watch-skewed", lambda o: decide(o, "watch-s1", ts=NOW - 250)),
        ]

        def check(tc, orch, results, order):
            assert_single_decision(tc, orch)
            assert_loser_path(tc, results[order[1]])

        run_interleavings(self, "SK-5", builders, check,
                          ["CR-2", "OP-1",
                           "exit: approval conflicts resolve deterministically",
                           "exit: behavior tested under clock skew"])

    def test_sk6_skewed_pull_renders_unknown(self):
        """A pull whose request clock is 400 s out is refused; the surface
        holds nothing and renders unknown — never a stale value."""
        for name, skew in (("plus400", 400), ("minus400", -400)):
            orch = fixture()
            watch = Surface(orch, "watch-s1", "watch")
            r = watch.pull_status("work-1", 0, NOW + skew)
            self.assertFalse(r["ok"], name)
            self.assertEqual(r["reason"], "stale-request", name)
            self.assertIsNone(watch.cached)
            render, _prov = watch.render_cached(NOW)
            self.assertEqual(render, "unknown", name)
            record_verdict("SK-6/" + name,
                           ["CR-3", "cache-policy.md section 4",
                            "exit: stale data cannot masquerade as current",
                            "exit: behavior tested under clock skew"])

    def test_sk7_future_event_grants_nothing(self):
        """A future-dated observed_at passes the event check but buys no
        authority: the stale revision is still refused."""
        orch = fixture()
        r = mutate(orch, "iphone-s1", "armed", revision=99,
                   observed_at=NOW + 1000)
        self.assertEqual(r["reason"], "stale-revision")
        self.assertEqual(orch.works["work-1"]["revision"], 0)
        record_verdict("SK-7",
                       ["revision-protocol.md section 5 (check order)",
                        "exit: behavior tested under clock skew"])


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    from orchestrator import dump_all_refusals
    path = os.environ.get("PHASE3_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
