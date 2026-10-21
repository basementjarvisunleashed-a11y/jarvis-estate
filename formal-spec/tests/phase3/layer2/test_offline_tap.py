"""Phase 3 Layer 2 — OT family: offline taps.

What it checks: the Phase 3 exit criterion "offline taps cannot become
approvals", diagrammed in sequence-diagrams.md (d) and asserted in
consistency-model.md NT-4/NT-5: the offline tap records a LOCAL pending
gesture only — not consent, not a decision, never transmitted as one.
On reconnect the gesture is discarded; re-approval requires a fresh tap
on a fresh card. A surface offline for any duration holds no authority
on reconnect: it pulls, it does not assert.
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


class TestOfflineTap(unittest.TestCase):
    """OT: an offline tap records nothing, ever."""

    def setUp(self):
        self.orch = fixture()
        self.watch = Surface(self.orch, "watch-s1", "watch")
        pulled = self.watch.pull_card("intent-1", "work-1", 0, NOW)
        self.assertTrue(pulled["ok"])
        self.card = pulled["card"]

    def test_ot1_offline_tap_never_reaches_orchestrator(self):
        """The tap while offline: one local gesture, zero orchestrator
        contact — no decision, no request, no execution."""
        self.watch.offline = True
        r = self.watch.tap(self.card, NOW + 5)
        self.assertEqual(r["reason"], "offline-gesture-recorded-locally")
        self.assertEqual(len(self.watch.gesture_log), 1)
        self.assertEqual(self.watch.gesture_log[0]["type"], "pending-gesture")
        self.assertNotIn("intent-1", self.orch.decisions)
        self.assertEqual(len(self.orch.refusals), 0)
        self.assertEqual(len(self.orch.sealed_log), 0)

    def test_ot2_reconnect_discards_gesture_fresh_tap_required(self):
        """On reconnect the pending gesture is discarded — never
        transmitted as a decision. Re-approval needs a fresh tap on a
        fresh card (sequence (d))."""
        self.watch.offline = True
        self.watch.tap(self.card, NOW + 5)
        rc = self.watch.reconnect(NOW + 30)
        self.assertEqual(rc["discarded_gestures"], 1)
        self.assertEqual(self.watch.gesture_log, [])
        self.assertNotIn("intent-1", self.orch.decisions)
        # fresh card, fresh tap:
        pulled = self.watch.pull_card("intent-1", "work-1", 0, NOW + 30)
        r = self.watch.tap(pulled["card"], NOW + 31)
        self.assertTrue(r["ok"])
        self.assertEqual(r["status"], "recorded")

    def test_ot3_reconnect_after_expiry_discards_and_renders_current(self):
        """If the intent expired while offline, the gesture dies and the
        card renders disabled (freshness-policy.md section 4: past
        expires_at the card is disabled) — the tap never reaches the
        server. And the server, asked directly, refuses 'intent-invalid'."""
        self.watch.offline = True
        self.watch.tap(self.card, NOW + 5)
        self.orch.now = NOW + 7200          # past the intent's expiry
        rc = self.watch.reconnect(self.orch.now)
        self.assertEqual(rc["discarded_gestures"], 1)
        pulled = self.watch.pull_card("intent-1", "work-1", 0, self.orch.now)
        r = self.watch.tap(pulled["card"], self.orch.now)
        self.assertEqual(r["reason"], "tap-disabled-unknown-card")
        self.assertNotIn("intent-1", self.orch.decisions)
        # belt and braces: a direct submit is refused by the server too:
        d = self.orch.intents["intent-1"]["digest"]
        r2 = self.orch.submit({"kind": "decide", "intent_id": "intent-1",
                               "work_id": "work-1", "revision": 0,
                               "digest_seen": d,
                               "device_session_id": "watch-s1",
                               "timestamp": self.orch.now})
        self.assertEqual(r2["reason"], "intent-invalid")

    def test_ot4_long_offline_no_authority_on_reconnect(self):
        """NT-4: a surface offline for any duration holds no authority
        on reconnect — it pulls, it does not assert."""
        self.watch.offline = True
        for i in range(3):
            self.watch.tap(self.card, NOW + i)
        self.assertEqual(len(self.watch.gesture_log), 3)
        # meanwhile the world moved on without the watch:
        self.orch.now = NOW + 100
        self.orch.submit({"kind": "mutate", "work_id": "work-1", "revision": 0,
                          "device_session_id": "iphone-s1",
                          "timestamp": self.orch.now, "new_state": "moved-on"})
        self.watch.reconnect(self.orch.now)
        self.assertEqual(self.watch.gesture_log, [])
        self.assertNotIn("intent-1", self.orch.decisions)
        self.assertEqual(self.orch.works["work-1"]["revision"], 1)

    def test_ot5_tap_on_unknown_card_is_disabled(self):
        """cache-policy.md section 4: an approval action on an unknown
        (stale) card is disabled — the tap cannot become consent."""
        self.watch.cached = ({"intent_id": "intent-1"},  # forged stale entry
                             {"observed_at": NOW - 1000, "fresh_until": NOW - 900,
                              "revision": 0})
        r = self.watch.tap({"intent_id": "intent-1", "work_id": "work-1",
                            "revision": 0, "digest": "x"}, NOW)
        self.assertEqual(r["reason"], "tap-disabled-unknown-card")
        self.assertNotIn("intent-1", self.orch.decisions)


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    from orchestrator import dump_all_refusals
    path = os.environ.get("PHASE3_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
