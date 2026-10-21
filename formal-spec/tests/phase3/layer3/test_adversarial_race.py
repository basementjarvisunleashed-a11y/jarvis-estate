"""Phase 3 Layer 3 — AR family: adversarial conflicting approvals.

conflict-resolution.md CR-2 ("First valid decision recorded wins") under
systematically enumerated delivery interleavings — the plan's head-start
note named this "the genuinely open item" and Layer 3's core work.

Determinism asserted per interleaving: exactly one recorded decision,
exactly one execution, the recorded content (intent_id, digest) identical
under every interleaving, the loser always on the refuse/name-current/
re-pull or already-recorded path (sequence-diagrams.md (b)).

Draft sections cited: conflict-resolution.md CR-2; revision-protocol.md
section 5 (five-step gate), section 6 (exactly-once); sequence-diagrams.md
(b); consistency-model.md NT-1.
Exit criteria served: "approval conflicts resolve deterministically";
"no device can become a source of truth".
"""

import unittest

from chaos import (D, NOW, assert_loser_path, assert_no_decision,
                   assert_single_decision, decide, fixture, record_verdict,
                   run_interleavings)


class TestAdversarialRace(unittest.TestCase):
    """AR: the deterministic winner under every interleaving."""

    def test_ar1_two_valid_same_digest(self):
        """Both devices' valid approvals, identical timestamps: every
        delivery order -> exactly one recorded, one execution, identical
        content; the loser re-sends at the current revision -> read."""
        builders = [
            ("iphone", lambda o: decide(o, "iphone-s1")),
            ("watch", lambda o: decide(o, "watch-s1")),
        ]

        def check(tc, orch, results, order):
            assert_single_decision(tc, orch)
            loser = order[1]
            assert_loser_path(tc, results[loser])
            sess = "watch-s1" if loser == "watch" else "iphone-s1"
            reread = decide(orch, sess, revision=1)
            tc.assertEqual(reread.get("status"), "already-recorded")
            assert_single_decision(tc, orch)

        run_interleavings(self, "AR-1", builders, check,
                          ["CR-2", "sequence-diagrams.md (b)",
                           "exit: approval conflicts resolve deterministically",
                           "exit: no device can become a source of truth"])

    def test_ar2_valid_vs_invalid_digest(self):
        """One device's card is stale on digest: the valid decision records
        under BOTH arrival orders; the invalid one always digest-lapses
        (attested lapse, no execution) — validity is decided by the
        orchestrator's checks, not by arrival order."""
        for bad_sess, bad_label in (("iphone-s1", "iphone"),
                                    ("watch-s1", "watch")):
            good_sess = "watch-s1" if bad_sess == "iphone-s1" else "iphone-s1"
            builders = [
                ("bad", lambda o, s=bad_sess: decide(o, s, digest="f" * 64)),
                ("good", lambda o, s=good_sess: decide(o, s)),
            ]

            def check(tc, orch, results, order):
                assert_single_decision(tc, orch)
                bad = results["bad"]
                tc.assertFalse(bad.get("ok"))
                tc.assertEqual(bad.get("reason"), "digest-lapse")
                tc.assertEqual(len(orch.lapses), 1)

            run_interleavings(self, "AR-2-" + bad_label, builders, check,
                              ["CR-2", "revision-protocol.md section 5 step 5",
                               "exit: approval conflicts resolve deterministically"])

    def test_ar3_both_invalid_nothing_recorded(self):
        """Neither racer passes the checks: nothing is recorded, both lapse,
        the work is untouched — under both orders."""
        builders = [
            ("iphone", lambda o: decide(o, "iphone-s1", digest="a" * 64)),
            ("watch", lambda o: decide(o, "watch-s1", digest="b" * 64)),
        ]

        def check(tc, orch, results, order):
            assert_no_decision(tc, orch)
            tc.assertEqual(len(orch.lapses), 2)
            for label in ("iphone", "watch"):
                tc.assertEqual(results[label].get("reason"), "digest-lapse")

        run_interleavings(self, "AR-3", builders, check,
                          ["CR-2 (neither valid -> nothing recorded)",
                           "exit: approval conflicts resolve deterministically"])

    def test_ar4_three_way_with_duplicate(self):
        """A duplicate inside the race (iPhone taps twice): all six orders
        -> exactly one recorded, one execution; every loser on the loser
        path."""
        builders = [
            ("iphone", lambda o: decide(o, "iphone-s1")),
            ("watch", lambda o: decide(o, "watch-s1")),
            ("iphone-dup", lambda o: decide(o, "iphone-s1")),
        ]

        def check(tc, orch, results, order):
            assert_single_decision(tc, orch)
            for label in order[1:]:
                assert_loser_path(tc, results[label])

        run_interleavings(self, "AR-4", builders, check,
                          ["CR-2", "revision-protocol.md section 6 (exactly-once)",
                           "exit: approval conflicts resolve deterministically"])

    def test_ar5_race_at_request_bound(self):
        """One racer's timestamp sits exactly on the 300 s request bound
        (still valid per OP-1): the race still resolves to exactly one
        decision under both orders."""
        builders = [
            ("iphone-edge", lambda o: decide(o, "iphone-s1", ts=NOW + 300)),
            ("watch", lambda o: decide(o, "watch-s1", ts=NOW)),
        ]

        def check(tc, orch, results, order):
            assert_single_decision(tc, orch)
            assert_loser_path(tc, results[order[1]])

        run_interleavings(self, "AR-5", builders, check,
                          ["CR-2", "OP-1 (300 s request bound, exact)",
                           "exit: approval conflicts resolve deterministically",
                           "exit: behavior tested under clock skew"])

    def test_ar6_stale_request_vs_valid(self):
        """A racer 301 s out cannot win by arriving first: the stale request
        is refused and the valid decision records — under both orders."""
        builders = [
            ("iphone-stale", lambda o: decide(o, "iphone-s1", ts=NOW + 301)),
            ("watch", lambda o: decide(o, "watch-s1", ts=NOW)),
        ]

        def check(tc, orch, results, order):
            assert_single_decision(tc, orch)
            tc.assertEqual(results["iphone-stale"].get("reason"), "stale-request")
            tc.assertEqual(orch.decisions["intent-1"]["by"], "watch-s1")

        run_interleavings(self, "AR-6", builders, check,
                          ["CR-2", "OP-1 (300 s request bound, beyond)",
                           "exit: approval conflicts resolve deterministically",
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
