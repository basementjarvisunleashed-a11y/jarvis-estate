"""Phase 3 Layer 3 — RP family: replay and duplication.

The burned-slot semantic: a recorded decision consumes its slot — every
replay of the same approval returns the existing decision as a read (or a
refusal naming current), never a second execution (revision-protocol.md
section 6, exactly-once). Replays of refused requests stay refused and
change nothing; each replay is logged with its cause. Duplicated pulls
are idempotent. An expired intent's replay stays invalid.

Draft sections cited: revision-protocol.md section 6 (exactly-once);
conflict-resolution.md CR-2; sequence-diagrams.md (d).
Exit criteria served: "approval conflicts resolve deterministically"
(exactly one execution under replay); "no device can become a source of
truth".
"""

import unittest

from chaos import (ChaosLink, NOW, assert_no_decision, assert_single_decision,
                   decide, fixture, record_verdict)
from clients import Surface


class TestReplay(unittest.TestCase):
    """RP: the slot burns once; replays change nothing."""

    def test_rp1_replay_recorded_decision(self):
        """Byte-identical replays of a recorded approval are refused
        stale-revision; re-taps at the current revision return the
        existing decision as a read. Six replays, still one decision,
        one execution."""
        orch = fixture()
        r1 = decide(orch, "iphone-s1")
        self.assertEqual(r1.get("status"), "recorded")
        for i in range(3):
            r = decide(orch, "iphone-s1", revision=0)
            self.assertEqual(r["reason"], "stale-revision", i)
        for i in range(3):
            r = decide(orch, "iphone-s1", revision=1)
            self.assertEqual(r.get("status"), "already-recorded", i)
        assert_single_decision(self, orch)
        record_verdict("RP-1",
                       ["revision-protocol.md section 6 (exactly-once)", "CR-2",
                        "exit: approval conflicts resolve deterministically"])

    def test_rp2_replay_under_partition(self):
        """Replays sent while partitioned are dropped by the network; the
        replay after the heal returns the recorded decision as a read.
        Still one decision, one execution."""
        orch = fixture()
        r1 = decide(orch, "iphone-s1")
        self.assertEqual(r1.get("status"), "recorded")
        link = ChaosLink("watch-link")
        link.severed = True
        for i in range(3):
            r = link.send("replay-%d" % i,
                          lambda: decide(orch, "watch-s1", revision=1))
            self.assertEqual(r["reason"], "partition-lost", i)
        link.severed = False
        r = decide(orch, "watch-s1", revision=1)
        self.assertEqual(r.get("status"), "already-recorded")
        assert_single_decision(self, orch)
        record_verdict("RP-2",
                       ["revision-protocol.md section 6 (exactly-once)",
                        "exit: approval conflicts resolve deterministically",
                        "exit: behavior tested under network loss"])

    def test_rp3_replay_of_refusal(self):
        """A refused request replayed three times is refused three times —
        one ledger row per replay, no state change, no decision."""
        orch = fixture()
        for i in range(3):
            r = decide(orch, "watch-s1", revision=99)
            self.assertEqual(r["reason"], "stale-revision", i)
        self.assertEqual(orch.works["work-1"]["revision"], 0)
        assert_no_decision(self, orch)
        n = sum(1 for (reason, _k, _r, _d) in orch.refusals
                if reason == "stale-revision")
        self.assertEqual(n, 3)
        record_verdict("RP-3",
                       ["revision-protocol.md section 5 (every refusal logged)",
                        "exit: approval conflicts resolve deterministically"])

    def test_rp4_duplicated_pulls_idempotent(self):
        """The same pull twice: identical state, identical revision, no
        mutation — pulls never write."""
        orch = fixture()
        iphone = Surface(orch, "iphone-s1", "iphone")
        r1 = iphone.pull_status("work-1", 0, NOW)
        r2 = iphone.pull_status("work-1", 0, NOW)
        self.assertTrue(r1["ok"] and r2["ok"])
        self.assertEqual(r1["revision"], r2["revision"])
        self.assertEqual(r1["state"], r2["state"])
        self.assertEqual(orch.works["work-1"]["revision"], 0)
        record_verdict("RP-4",
                       ["consistency-model.md NT-1 (reads never write)",
                        "exit: no device can become a source of truth"])

    def test_rp5_expired_intent_replay(self):
        """An intent past expiry, replayed: intent-invalid both times,
        nothing recorded — expiry is not waived by repetition."""
        orch = fixture()
        orch.propose_intent("intent-x", "work-1", "publish", "dropbox:/x.pdf",
                            "x", "release", 0, NOW + 5)
        orch.now = NOW + 10
        dx = orch.intents["intent-x"]["digest"]
        for i in range(2):
            r = orch.submit({"kind": "decide", "intent_id": "intent-x",
                             "work_id": "work-1", "revision": 0,
                             "digest_seen": dx, "device_session_id": "watch-s1",
                             "timestamp": NOW + 10})
            self.assertEqual(r["reason"], "intent-invalid", i)
        assert_no_decision(self, orch)
        record_verdict("RP-5",
                       ["revision-protocol.md section 5 (intent liveness)",
                        "exit: approval conflicts resolve deterministically"])

    def test_rp6_burned_across_reconnect(self):
        """Sequence (d) meets the burned slot: the Watch taps offline
        (gesture only, discarded on reconnect), then replays the old
        card's bytes — refused stale-revision. No second execution."""
        orch = fixture()
        r1 = decide(orch, "iphone-s1")
        self.assertEqual(r1.get("status"), "recorded")
        watch = Surface(orch, "watch-s1", "watch")
        watch.offline = True
        watch.tap({"intent_id": "intent-1"}, NOW)
        rc = watch.reconnect(NOW + 5)
        self.assertEqual(rc["discarded_gestures"], 1)
        r = decide(orch, "watch-s1", revision=0, ts=NOW + 5)
        self.assertEqual(r["reason"], "stale-revision")
        assert_single_decision(self, orch)
        record_verdict("RP-6",
                       ["sequence-diagrams.md (d)",
                        "revision-protocol.md section 6 (exactly-once)",
                        "exit: offline taps cannot become approvals",
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
