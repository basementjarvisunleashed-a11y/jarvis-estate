"""Phase 3 Layer 2 — CT family: the conflict table's remaining rows.

What it checks: every conflict-resolution.md row is exercised by at
least one Layer 2 test (the Phase 3 plan's Layer 1 gate). CR-2 is
covered by the FV family; CR-8 by the DA family. This file covers
CR-1, CR-3, CR-4, CR-5, CR-6, CR-7.
Exit criteria served: "approval conflicts resolve deterministically";
"stale data cannot masquerade as current".
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
    return orch


class TestConflictTable(unittest.TestCase):
    """CT: each conflict resolves deterministically."""

    def setUp(self):
        self.orch = fixture()

    def test_ct1_two_surfaces_disagree_server_wins(self):
        """CR-1: iPhone renders r0, Watch renders r1 (S1 != S2). Both
        re-pull; the orchestrator's current revision is authoritative —
        no negotiation between surfaces (NT-3)."""
        iphone = Surface(self.orch, "iphone-s1", "iphone")
        watch = Surface(self.orch, "watch-s1", "watch")
        r0 = iphone.pull_status("work-1", 0, NOW)
        self.assertTrue(r0["ok"])
        self.orch.submit({"kind": "mutate", "work_id": "work-1", "revision": 0,
                          "device_session_id": "iphone-s1", "timestamp": NOW,
                          "new_state": "working"})
        # watch still renders its r0 copy: disagreement
        render, _prov = watch.render_cached(NOW)
        # both re-pull; the server's current revision wins:
        cur = self.orch.works["work-1"]["revision"]
        self.assertEqual(cur, 1)
        fresh = watch.pull_status("work-1", cur, NOW)
        self.assertTrue(fresh["ok"])
        self.assertEqual(fresh["state"], "working")
        self.assertEqual(fresh["revision"], cur)

    def test_ct2_expired_cache_renders_unknown(self):
        """CR-3 / cache-policy.md section 4: the Watch's cache says
        'operational' but fresh_until has passed and the pull fails —
        the surface renders unknown, never the expired value as current."""
        watch = Surface(self.orch, "watch-s1", "watch")
        watch.cached = ({"state": "operational"},
                        {"observed_at": NOW - 120, "fresh_until": NOW - 90,
                         "revision": 0})
        watch.offline = True
        render, prov = watch.render_cached(NOW)
        self.assertEqual(render, "unknown")
        self.assertTrue(prov["tap_disabled"])
        self.assertNotIn("operational", str(render))

    def test_ct3_live_source_beats_memory(self):
        """CR-4 / HC-6: durable memory holds X; the live source says Y.
        The decision uses Y, read at decision time — X stays in history,
        flagged superseded, inadmissible for action."""
        self.orch.set_live_fact("work-1", "X")
        self.orch.set_live_fact("work-1", "Y")          # live moved on
        self.assertEqual(self.orch.memory["work-1"], "X")
        self.orch.propose_intent("intent-x", "work-1", "act", "t",
                                 "do X", "s", 0, NOW + 3600,
                                 live_predicate={"work_id": "work-1",
                                                 "expected": "X"})
        d = self.orch.intents["intent-x"]["digest"]
        r = self.orch.submit({"kind": "decide", "intent_id": "intent-x",
                              "work_id": "work-1", "revision": 0,
                              "digest_seen": d,
                              "device_session_id": "iphone-s1",
                              "timestamp": NOW})
        self.assertEqual(r["reason"], "intent-invalid")
        self.assertIn("live source moved", r["detail"])
        # a fresh intent predicated on Y decides cleanly:
        self.orch.propose_intent("intent-y", "work-1", "act", "t",
                                 "do Y", "s", 0, NOW + 3600,
                                 live_predicate={"work_id": "work-1",
                                                 "expected": "Y"})
        d2 = self.orch.intents["intent-y"]["digest"]
        r2 = self.orch.submit({"kind": "decide", "intent_id": "intent-y",
                               "work_id": "work-1", "revision": 0,
                               "digest_seen": d2,
                               "device_session_id": "iphone-s1",
                               "timestamp": NOW})
        self.assertEqual(r2["status"], "recorded")

    def test_ct4_orchestrator_reconciles_contradiction(self):
        """CR-5: a durable contradiction is reconciled by the
        orchestrator as a proposed correction citing both antecedents —
        append-only, never a silent overwrite; surfaces never reconcile
        against each other (no such path on the client)."""
        r = self.orch.submit({"kind": "reconcile", "work_id": "work-1",
                              "revision": 0,
                              "correction": "reconciled-state",
                              "antecedents": ["record-A", "record-B"],
                              "device_session_id": "iphone-s1",
                              "timestamp": NOW})
        self.assertTrue(r["ok"])
        self.assertEqual(r["antecedents"], ["record-A", "record-B"])
        w = self.orch.works["work-1"]
        self.assertEqual(w["history"][0], "idle")       # history intact
        self.assertEqual(w["history"][1], "reconciled-state")
        self.assertFalse(hasattr(Surface, "reconcile"))

    def test_ct5_notification_is_hint_not_truth(self):
        """CR-6 / HC-8: a hint describing S_old arrives after the
        orchestrator moved to S_new — the surface discards the hint's
        content and pulls current state."""
        watch = Surface(self.orch, "watch-s1", "watch")
        hint = self.orch.emit_hint("work-1")            # S_old = idle
        self.orch.submit({"kind": "mutate", "work_id": "work-1", "revision": 0,
                          "device_session_id": "iphone-s1", "timestamp": NOW,
                          "new_state": "working"})
        watch.receive_hint(hint)
        pulled = watch.pull_after_hint("work-1", 1, NOW)
        self.assertTrue(pulled["ok"])
        self.assertEqual(pulled["state"], "working")     # S_new, not the hint's
        self.assertIsNone(getattr(watch, "_hint", None))

    def test_ct6_evidence_new_revision_old_immutable(self):
        """CR-7: evidence packet updated — new revision sealed, old
        immutable and still addressable; renders pin to a revision."""
        p0 = self.orch.seal_evidence("work-1", {"packet_id": "p", "checks": ["a"]})
        p1 = self.orch.seal_evidence("work-1", {"packet_id": "p", "checks": ["a", "b"]})
        self.assertEqual((p0, p1), (0, 1))
        old = self.orch.read_evidence("work-1", 0)
        new = self.orch.read_evidence("work-1", 1)
        self.assertTrue(old["ok"] and new["ok"])
        self.assertEqual(old["packet"]["packet"]["checks"], ["a"])   # immutable
        self.assertEqual(new["packet"]["packet"]["checks"], ["a", "b"])
        bad = self.orch.read_evidence("work-1", 9)
        self.assertFalse(bad["ok"])


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    from orchestrator import dump_all_refusals
    path = os.environ.get("PHASE3_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
