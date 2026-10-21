"""Phase 3 Layer 2 — FV family: first-valid-decision-wins.

What it checks: conflict-resolution.md CR-2 — two devices attempt
approval for the same intent under adversarial timing. The first request
to pass all five checks is recorded; the loser's request returns the
existing decision as a READ (not recorded, not executed, not an error
the principal must resolve). The loser's path follows sequence-diagrams.md
(b): refuse (stale-revision, naming current) -> re-pull -> render the
recorded decision as a read.
Exit criterion served: "approval conflicts resolve deterministically".
"""

import unittest

from orchestrator import Orchestrator
from clients import Surface

NOW = 1_790_000_000


def fixture(now=NOW):
    orch = Orchestrator(now)
    orch.enroll("iphone-s1", "iphone")
    orch.enroll("watch-s1", "watch")
    orch.mint_work("work-1", "idle")
    orch.propose_intent("intent-1", "work-1", "publish", "dropbox:/p.pdf",
                        "paper posted", "release", 0, now + 3600)
    return orch


def decide(orch, session, digest, revision=0, ts=NOW):
    return orch.submit({"kind": "decide", "intent_id": "intent-1",
                        "work_id": "work-1", "revision": revision,
                        "digest_seen": digest,
                        "device_session_id": session, "timestamp": ts})


class TestFirstValidDecisionWins(unittest.TestCase):
    """FV: exactly one decision exists per intent, deterministically."""

    def setUp(self):
        self.orch = fixture()
        self.d = self.orch.intents["intent-1"]["digest"]

    def test_fv1_iphone_first_watch_second(self):
        """iPhone's valid decision records; the Watch's later decision —
        valid on its own card but stale on revision — is refused
        'stale-revision' naming current r+1, then re-pulls the recorded
        decision as a read (sequence (b))."""
        r1 = decide(self.orch, "iphone-s1", self.d, revision=0)
        self.assertEqual(r1["status"], "recorded")
        r2 = decide(self.orch, "watch-s1", self.d, revision=0)
        self.assertFalse(r2["ok"])
        self.assertEqual(r2["reason"], "stale-revision")
        self.assertEqual(r2["current_revision"], 1)
        # the loser's re-pull path: the recorded decision as a read:
        watch = Surface(self.orch, "watch-s1", "watch")
        read = watch.pull_status("work-1", 1, NOW)
        self.assertTrue(read["ok"])
        self.assertEqual(len(self.orch.decisions), 1)

    def test_fv2_watch_first_iphone_second(self):
        """Symmetric: the Watch wins the race; the iPhone reads."""
        r1 = decide(self.orch, "watch-s1", self.d, revision=0)
        self.assertEqual(r1["status"], "recorded")
        self.assertEqual(r1["decision"]["by"], "watch-s1")
        r2 = decide(self.orch, "iphone-s1", self.d, revision=0)
        self.assertEqual(r2["reason"], "stale-revision")

    def test_fv3_both_invalid_nothing_recorded(self):
        """If neither passes the five checks, nothing is recorded."""
        decide(self.orch, "iphone-s1", "0" * 64, revision=0)   # digest lapse
        decide(self.orch, "watch-s1", self.d, revision=99)     # stale revision
        self.assertNotIn("intent-1", self.orch.decisions)

    def test_fv4_validity_not_arrival_order(self):
        """The first ARRIVAL that is invalid does not block the first
        VALID decision: 'valid' is decided by the orchestrator's checks."""
        bad = decide(self.orch, "watch-s1", self.d, revision=0, ts=NOW - 10_000)
        self.assertEqual(bad["reason"], "stale-request")
        good = decide(self.orch, "iphone-s1", self.d, revision=0)
        self.assertEqual(good["status"], "recorded")

    def test_fv5_duplicate_taps_one_device(self):
        """Duplicate taps on one device return the existing decision —
        exactly one recorded decision and exactly one execution
        (revision-protocol.md section 6)."""
        r1 = decide(self.orch, "iphone-s1", self.d, revision=0)
        r2 = decide(self.orch, "iphone-s1", self.d, revision=1)
        self.assertEqual(r2["status"], "already-recorded")
        self.assertEqual(r2["decision"]["intent_id"], "intent-1")
        executions = [e for e in self.orch.sealed_log if e[0] == "decision-recorded"]
        self.assertEqual(len(executions), 1)
        self.assertEqual(len(self.orch.decisions), 1)

    def test_fv6_loser_path_refuse_name_current_repull(self):
        """Sequence (b), step by step: refuse names the current revision;
        the re-pull carries the recorded decision; the render is a read,
        never a second approval."""
        decide(self.orch, "iphone-s1", self.d, revision=0)
        r2 = decide(self.orch, "watch-s1", self.d, revision=0)
        self.assertEqual(r2["current_revision"], 1)          # refuse, name current
        watch = Surface(self.orch, "watch-s1", "watch")
        pulled = watch.pull_card("intent-1", "work-1", 1, NOW)
        self.assertTrue(pulled["ok"])
        # the recorded decision is visible; tapping again is a read:
        r3 = decide(self.orch, "watch-s1", self.d, revision=1)
        self.assertEqual(r3["status"], "already-recorded")
        self.assertEqual(self.orch.works["work-1"]["revision"], 1)


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    from orchestrator import dump_all_refusals
    path = os.environ.get("PHASE3_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
