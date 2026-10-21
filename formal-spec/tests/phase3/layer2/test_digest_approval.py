"""Phase 3 Layer 2 — DA family: digest-bound approval.

What it checks: the approval binds the exact intent — digest equality is
the binding (revision-protocol.md section 5 step 5; conflict-resolution.md
CR-8). D_seen != D lapses the ceremony: no execution, attested lapse.
Matching digests bind. An artifact changed after approval invalidates
the approval; a new approval requires a fresh intent.
Draft digest: the eight-field approval digest (spec/approval-digest.md,
Phase 2 Q3/Q4 rulings) — recomputed here independently via digest.py.
Exit criteria served: "approval conflicts resolve deterministically".
"""

import unittest

from orchestrator import Orchestrator
from digest import approval_digest

NOW = 1_790_000_000


def fixture(now=NOW):
    orch = Orchestrator(now)
    orch.enroll("iphone-s1", "iphone")
    orch.enroll("watch-s1", "watch")
    orch.mint_work("work-1", "idle")
    orch.propose_intent("intent-1", "work-1", "publish", "dropbox:/p.pdf",
                        "paper posted", "release", 0, now + 3600)
    orch.record_artifact("artifact-1", "sha256:aaa")
    return orch


def decide(orch, intent_id, digest_seen, session="iphone-s1", revision=0, ts=NOW):
    return orch.submit({"kind": "decide", "intent_id": intent_id,
                        "work_id": "work-1", "revision": revision,
                        "digest_seen": digest_seen,
                        "device_session_id": session, "timestamp": ts})


class TestDigestBoundApproval(unittest.TestCase):
    """DA: executed D == approved D, always."""

    def setUp(self):
        self.orch = fixture()
        self.d = self.orch.intents["intent-1"]["digest"]

    def test_da1_matching_digest_binds(self):
        """D_seen == D: the decision is recorded exactly once, executed
        exactly once."""
        r = decide(self.orch, "intent-1", self.d)
        self.assertTrue(r["ok"])
        self.assertEqual(r["status"], "recorded")
        self.assertTrue(r["decision"]["executed"])
        self.assertEqual(r["decision"]["digest"], self.d)

    def test_da2_mismatch_lapses_no_execution(self):
        """D_seen != D: the ceremony LAPSES — no execution, attested
        lapse, nothing recorded (revision-protocol.md section 5 step 5)."""
        r = decide(self.orch, "intent-1", "0" * 64)
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "digest-lapse")
        self.assertNotIn("intent-1", self.orch.decisions)
        self.assertEqual(len(self.orch.lapses), 1)
        self.assertEqual(self.orch.lapses[0]["intent_id"], "intent-1")
        self.assertEqual(self.orch.works["work-1"]["revision"], 0)

    def test_da3_independent_digest_agreement(self):
        """The digest the model computed matches an independent
        recomputation over the eight bound fields (no shared code path
        beyond the ratified procedure)."""
        rec = self.orch.intents["intent-1"]["record"]
        self.assertEqual(approval_digest(rec), self.d)
        # and any single-field mutation changes it:
        mutated = dict(rec, target="dropbox:/q.pdf")
        self.assertNotEqual(approval_digest(mutated), self.d)

    def test_da4_mutation_between_tap_and_record_refused(self):
        """The card is tapped with digest D; the intent mutates before
        the decision reaches the orchestrator: D_seen != recomputed D.
        The stricter failure governs — refused, lapsed, no execution."""
        seen = self.d
        self.orch.intents["intent-1"]["record"]["effect"] = "DIFFERENT effect"
        r = decide(self.orch, "intent-1", seen)
        self.assertFalse(r["ok"])
        self.assertIn(r["reason"], ("digest-lapse", "intent-invalid"))
        self.assertNotIn("intent-1", self.orch.decisions)

    def test_da5_artifact_change_invalidates_approval(self):
        """CR-8: an approval recorded against artifact digest D1; the
        artifact's bytes change to D2 — the approval is invalid and a
        NEW approval requires a fresh intent."""
        self.orch.intents["intent-1"]["record"]["target"] = "artifact-1"
        d = approval_digest(self.orch.intents["intent-1"]["record"])
        self.orch.intents["intent-1"]["digest"] = d
        r = decide(self.orch, "intent-1", d)
        self.assertEqual(r["status"], "recorded")
        self.orch.decisions["intent-1"]["artifact_id"] = "artifact-1"
        # the artifact changes after approval:
        self.orch.change_artifact("artifact-1", "sha256:bbb")
        dec = self.orch.decisions["intent-1"]
        self.assertTrue(dec.get("superseded_by_artifact_change"))
        # the old approval remains in the log, marked — never deleted:
        self.assertIn("intent-1", self.orch.decisions)
        r2 = decide(self.orch, "intent-1", d, revision=1)
        self.assertEqual(r2["reason"], "intent-invalid")
        # ...a fresh intent is proposed and approved afresh:
        self.orch.propose_intent("intent-2", "work-1", "publish", "artifact-1",
                                 "paper posted v2", "release", 1, NOW + 3600)
        d2 = self.orch.intents["intent-2"]["digest"]
        r3 = decide(self.orch, "intent-2", d2, revision=1)
        self.assertEqual(r3["status"], "recorded")

    def test_da6_lapse_is_attested_and_sealed(self):
        """The lapse is not silent: it is attested (lapses ledger) and
        sealed (sealed_log carries the lapse event)."""
        decide(self.orch, "intent-1", "0" * 64)
        self.assertTrue(any(e[0] == "lapsed" and e[1] == "intent-1"
                            for e in self.orch.sealed_log))


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    from orchestrator import dump_all_refusals
    path = os.environ.get("PHASE3_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
