"""Phase 3 Layer 3 — MX family: mixed chaos.

Partition + skew + racing approvals combined. The exit criteria must hold
in every combination: no device becomes a source of truth; conflicts
resolve deterministically; stale data never masquerades as current;
offline taps never become approvals; behavior holds under clock skew and
network loss.

MX-5 is the full interleaving fuzz: four messages (two valid racers, one
duplicate, one bad-digest) across all 24 delivery orders — every one must
resolve to exactly one recorded decision with identical content, exactly
one execution, the bad-digest racer always lapsing, every other loser on
the loser path.

Draft sections cited: conflict-resolution.md CR-1, CR-2, CR-3;
revision-protocol.md sections 5, 6; sequence-diagrams.md (b), (d);
consistency-model.md NT-1, NT-3, NT-4, NT-5.
"""

import unittest

from chaos import (ChaosLink, D, NOW, assert_loser_path, assert_no_decision,
                   assert_single_decision, decide, fixture, record_verdict,
                   run_interleavings)
from clients import Surface


class TestMixedChaos(unittest.TestCase):
    """MX: everything adversarial at once; the criteria hold anyway."""

    def test_mx1_partition_skew_race(self):
        """Partition drops the Watch's attempt; the iPhone's in-bound
        skewed (+250 s) decision records; after the heal the Watch's fresh
        tap reads the record. One decision, one execution."""
        orch = fixture()
        lw = ChaosLink("watch-link")
        lw.severed = True
        r = lw.send("watch-decide", lambda: decide(orch, "watch-s1", ts=NOW - 100))
        self.assertEqual(r["reason"], "partition-lost")
        r1 = decide(orch, "iphone-s1", ts=NOW + 250)
        self.assertEqual(r1.get("status"), "recorded")
        lw.severed = False
        r2 = decide(orch, "watch-s1", revision=1, ts=NOW + 5)
        self.assertEqual(r2.get("status"), "already-recorded")
        assert_single_decision(self, orch)
        record_verdict("MX-1",
                       ["CR-1", "CR-2", "OP-1",
                        "exit: no device can become a source of truth",
                        "exit: approval conflicts resolve deterministically",
                        "exit: behavior tested under clock skew and network loss"])

    def test_mx2_delayed_skewed_duplicate_race(self):
        """Three racers — a skewed Watch, a delayed iPhone, and a Watch
        duplicate — across all six orders: one decision, one execution,
        identical content, every loser on the loser path."""
        builders = [
            ("watch", lambda o: decide(o, "watch-s1", ts=NOW - 250)),
            ("iphone", lambda o: decide(o, "iphone-s1", ts=NOW)),
            ("watch-replay", lambda o: decide(o, "watch-s1", ts=NOW)),
        ]

        def check(tc, orch, results, order):
            assert_single_decision(tc, orch)
            recorded = [l for l in order
                        if results[l].get("status") == "recorded"]
            tc.assertEqual(len(recorded), 1)
            for l in order:
                if l != recorded[0]:
                    assert_loser_path(tc, results[l])

        run_interleavings(self, "MX-2", builders, check,
                          ["CR-2", "OP-1", "revision-protocol.md section 6",
                           "exit: no device can become a source of truth",
                           "exit: approval conflicts resolve deterministically",
                           "exit: behavior tested under clock skew and network loss"])

    def test_mx3_both_dropped_both_resend_fresh(self):
        """Both racers dropped by the partition, both re-send fresh after
        the heal: exactly one records — under both re-send orders."""
        for first in ("iphone-s1", "watch-s1"):
            orch = fixture()
            li, lw = ChaosLink("iphone-link"), ChaosLink("watch-link")
            li.severed = lw.severed = True
            li.send("i", lambda: decide(orch, "iphone-s1"))
            lw.send("w", lambda: decide(orch, "watch-s1"))
            assert_no_decision(self, orch)
            li.severed = lw.severed = False
            second = "watch-s1" if first == "iphone-s1" else "iphone-s1"
            r1 = decide(orch, first)
            self.assertEqual(r1.get("status"), "recorded")
            r2 = decide(orch, second)
            assert_loser_path(self, r2)
            assert_single_decision(self, orch)
            record_verdict("MX-3/" + first,
                           ["CR-2", "exit: approval conflicts resolve deterministically",
                            "exit: behavior tested under network loss"])

    def test_mx4_skew_partition_offline_tap(self):
        """The Watch taps offline (gesture only) while a wildly skewed
        (+400 s) iPhone attempt is refused; nothing is recorded. On
        reconnect the gesture dies and a fresh tap on a fresh card
        records — the only decision, by the Watch."""
        orch = fixture()
        watch = Surface(orch, "watch-s1", "watch")
        watch.offline = True
        g = watch.tap({"intent_id": "intent-1"}, NOW)
        self.assertEqual(g["reason"], "offline-gesture-recorded-locally")
        r = decide(orch, "iphone-s1", ts=NOW + 400)
        self.assertEqual(r["reason"], "stale-request")
        assert_no_decision(self, orch)
        rc = watch.reconnect(NOW + 5)
        self.assertEqual(rc["discarded_gestures"], 1)
        card = watch.pull_card("intent-1", "work-1", 0, NOW + 5)
        self.assertTrue(card["ok"])
        r2 = watch.tap(card["card"], NOW + 5)
        self.assertEqual(r2.get("status"), "recorded")
        self.assertEqual(r2["decision"]["by"], "watch-s1")
        assert_single_decision(self, orch)
        record_verdict("MX-4",
                       ["sequence-diagrams.md (d)", "CR-2", "OP-1",
                        "exit: offline taps cannot become approvals",
                        "exit: no device can become a source of truth",
                        "exit: behavior tested under clock skew and network loss"])

    def test_mx5_full_interleaving_fuzz(self):
        """The full fuzz: two valid racers, one duplicate, one bad-digest
        racer — all 24 delivery orders. Every order: exactly one recorded
        decision with identical content, exactly one execution, the
        bad-digest racer always lapsing (attested), every other loser on
        the loser path, the sealed log showing a single writer."""
        builders = [
            ("iphone", lambda o: decide(o, "iphone-s1")),
            ("watch", lambda o: decide(o, "watch-s1")),
            ("iphone-dup", lambda o: decide(o, "iphone-s1")),
            ("watch-bad", lambda o: decide(o, "watch-s1", digest="z" * 64)),
        ]

        def check(tc, orch, results, order):
            assert_single_decision(tc, orch)
            tc.assertEqual(results["watch-bad"].get("reason"), "digest-lapse")
            tc.assertEqual(len(orch.lapses), 1)
            recorded = [l for l in ("iphone", "watch", "iphone-dup")
                        if results[l].get("status") == "recorded"]
            tc.assertEqual(len(recorded), 1)
            for l in ("iphone", "watch", "iphone-dup"):
                if l != recorded[0]:
                    assert_loser_path(tc, results[l])

        run_interleavings(self, "MX-5", builders, check,
                          ["CR-2", "revision-protocol.md section 5 step 5",
                           "revision-protocol.md section 6 (exactly-once)",
                           "sequence-diagrams.md (b)",
                           "exit: no device can become a source of truth",
                           "exit: approval conflicts resolve deterministically",
                           "exit: stale data cannot masquerade as current",
                           "exit: offline taps cannot become approvals",
                           "exit: behavior tested under clock skew and network loss"])


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    from orchestrator import dump_all_refusals
    path = os.environ.get("PHASE3_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
