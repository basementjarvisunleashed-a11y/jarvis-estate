"""Phase 3 Layer 3 — PT family: network partition.

A severed ChaosLink drops messages the orchestrator never sees. Asserted:
no decision is lost without recourse (the principal retries to exactly
one record); no stale or late decision executes (late arrivals are
refused naming current); stale caches render unknown while the network is
down (CR-3); a pre-partition decision stays authoritative after the heal
(CR-1: server state wins); an offline tap stays a gesture and dies on
reconnect (sequence-diagrams.md (d)).

Draft sections cited: conflict-resolution.md CR-1, CR-2, CR-3 (and its
test-scope note on CR-2 under partition); sequence-diagrams.md (d);
consistency-model.md NT-3, NT-4, NT-5; cache-policy.md section 4.
Exit criteria served: "behavior tested under ... network loss";
"offline taps cannot become approvals"; "stale data cannot masquerade
as current"; "no device can become a source of truth".
"""

import unittest

from chaos import (ChaosLink, D, NOW, assert_loser_path, assert_no_decision,
                   assert_single_decision, decide, fixture, record_verdict)
from clients import Surface


class TestPartition(unittest.TestCase):
    """PT: the partition takes messages, never authority."""

    def test_pt1_dropped_decide_retried_once(self):
        """The Watch's decision is dropped by the partition: the
        orchestrator never sees it (no record, no execution). After the
        heal the principal retries with a fresh tap -> exactly one
        recorded decision."""
        orch = fixture()
        link = ChaosLink("watch-link")
        link.severed = True
        r = link.send("watch-decide", lambda: decide(orch, "watch-s1"))
        self.assertEqual(r["reason"], "partition-lost")
        self.assertEqual(link.lost, ["watch-decide"])
        assert_no_decision(self, orch)
        link.severed = False
        r2 = link.send("watch-decide-retry", lambda: decide(orch, "watch-s1"))
        self.assertEqual(r2.get("status"), "recorded")
        assert_single_decision(self, orch)
        record_verdict("PT-1",
                       ["CR-2 test-scope note (partitioned device cannot approve)",
                        "exit: behavior tested under network loss",
                        "exit: no device can become a source of truth"])

    def test_pt2_late_arrival_after_rival_records(self):
        """The Watch's decision is delayed by the partition and surfaces
        after the iPhone's already recorded: it is refused stale-revision
        naming current — no double execution, no lost update."""
        orch = fixture()
        delayed = lambda: decide(orch, "watch-s1")
        r1 = decide(orch, "iphone-s1")
        self.assertEqual(r1.get("status"), "recorded")
        r2 = delayed()
        self.assertFalse(r2["ok"])
        self.assertEqual(r2["reason"], "stale-revision")
        self.assertEqual(r2["current_revision"], 1)
        assert_single_decision(self, orch)
        record_verdict("PT-2",
                       ["CR-2", "sequence-diagrams.md (b) loser path",
                        "exit: approval conflicts resolve deterministically",
                        "exit: behavior tested under network loss"])

    def test_pt3_both_dropped_both_resend(self):
        """Both devices' decisions are dropped mid-ceremony; after the heal
        both re-send: exactly one records, the other takes the loser path
        — under both re-send orders."""
        for order in (("iphone", "watch"), ("watch", "iphone")):
            orch = fixture()
            li, lw = ChaosLink("iphone-link"), ChaosLink("watch-link")
            li.severed = lw.severed = True
            li.send("iphone-decide", lambda: decide(orch, "iphone-s1"))
            lw.send("watch-decide", lambda: decide(orch, "watch-s1"))
            assert_no_decision(self, orch)
            li.severed = lw.severed = False
            first, second = order
            s1 = "iphone-s1" if first == "iphone" else "watch-s1"
            s2 = "watch-s1" if first == "iphone" else "iphone-s1"
            r1 = decide(orch, s1)
            self.assertEqual(r1.get("status"), "recorded")
            r2 = decide(orch, s2)
            assert_loser_path(self, r2)
            assert_single_decision(self, orch)
            record_verdict("PT-3/" + "-".join(order),
                           ["CR-2", "exit: approval conflicts resolve deterministically",
                            "exit: behavior tested under network loss"])

    def test_pt4_stale_cache_unknown_during_partition(self):
        """CR-3 under partition: the Watch's cached status ages past its
        horizon while the refresh pull is lost — it renders unknown with
        the tap disabled. The disabled tap never reaches the orchestrator.
        After the heal a fresh pull renders current with its age."""
        orch = fixture()
        watch = Surface(orch, "watch-s1", "watch")
        pulled = watch.pull_status("work-1", 0, NOW)
        self.assertTrue(pulled["ok"])
        # Time passes — for the server clock as well as the surface: the
        # cache ages past its horizon while the refresh pull is lost.
        orch.now = NOW + 31
        render, prov = watch.render_cached(NOW + 31)
        self.assertEqual(render, "unknown")
        self.assertTrue(prov["tap_disabled"])
        n_refusals = len(orch.refusals)
        tap = watch.tap({"intent_id": "intent-1"}, NOW + 31)
        self.assertEqual(tap["reason"], "tap-disabled-unknown-card")
        self.assertEqual(len(orch.refusals), n_refusals)
        assert_no_decision(self, orch)
        ok = watch.pull_status("work-1", 0, NOW + 31)
        self.assertTrue(ok["ok"])
        render2, prov2 = watch.render_cached(NOW + 31)
        self.assertEqual(render2, "current")
        self.assertEqual(prov2["revision"], 0)
        record_verdict("PT-4",
                       ["CR-3", "cache-policy.md section 4",
                        "exit: stale data cannot masquerade as current",
                        "exit: behavior tested under network loss"])

    def test_pt5_recorded_decision_survives_partition(self):
        """CR-1: a decision recorded before the partition stays
        authoritative through it. The Watch's partitioned attempt is lost;
        after the heal its re-pull returns the recorded decision as a
        read — server state wins."""
        orch = fixture()
        r1 = decide(orch, "iphone-s1")
        self.assertEqual(r1.get("status"), "recorded")
        link = ChaosLink("watch-link")
        link.severed = True
        r = link.send("watch-decide", lambda: decide(orch, "watch-s1"))
        self.assertEqual(r["reason"], "partition-lost")
        link.severed = False
        r2 = decide(orch, "watch-s1", revision=1)
        self.assertEqual(r2.get("status"), "already-recorded")
        assert_single_decision(self, orch)
        record_verdict("PT-5",
                       ["CR-1 (server state wins)", "CR-2",
                        "exit: behavior tested under network loss",
                        "exit: no device can become a source of truth"])

    def test_pt6_flapping_partition(self):
        """The link flaps mid-race: dropped attempt, rival records, dropped
        retry, then a fresh tap after the final heal -> the recorded
        decision as a read. Exactly one decision across the flaps."""
        orch = fixture()
        lw = ChaosLink("watch-link")
        lw.severed = True
        lw.send("w1", lambda: decide(orch, "watch-s1"))
        lw.severed = False
        r1 = decide(orch, "iphone-s1")
        self.assertEqual(r1.get("status"), "recorded")
        lw.severed = True
        r = lw.send("w2", lambda: decide(orch, "watch-s1"))
        self.assertEqual(r["reason"], "partition-lost")
        lw.severed = False
        r2 = decide(orch, "watch-s1", revision=1)
        self.assertEqual(r2.get("status"), "already-recorded")
        assert_single_decision(self, orch)
        self.assertEqual(lw.lost, ["w1", "w2"])
        record_verdict("PT-6",
                       ["CR-1", "CR-2", "exit: behavior tested under network loss",
                        "exit: approval conflicts resolve deterministically"])


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    from orchestrator import dump_all_refusals
    path = os.environ.get("PHASE3_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
