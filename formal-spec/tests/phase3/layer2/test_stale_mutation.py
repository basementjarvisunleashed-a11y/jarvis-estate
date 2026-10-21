"""Phase 3 Layer 2 — SM family: stale-mutation rejection order.

What it checks: the five-step rejection order (revision-protocol.md
section 5) is fail-closed at the first failure, in sequence: session ->
freshness -> intent liveness -> revision currency -> digest binding. A
refused mutation changes nothing, and a mutated work item is re-proposed
as a new intent, never silently applied.
Exit criteria served: "approval conflicts resolve deterministically";
"stale data cannot masquerade as current".
"""

import unittest

from orchestrator import Orchestrator
from digest import approval_digest

NOW = 1_790_000_000


def fixture(now=NOW):
    orch = Orchestrator(now)
    orch.enroll("iphone-s1", "iphone")
    orch.mint_work("work-1", "idle")
    orch.propose_intent("intent-1", "work-1", "publish", "dropbox:/p.pdf",
                        "paper posted", "release", 0, now + 3600)
    return orch


def base_req(**kw):
    req = {"kind": "mutate", "work_id": "work-1", "revision": 0,
           "intent_id": "intent-1",
           "device_session_id": "iphone-s1", "timestamp": NOW,
           "new_state": "working"}
    req.update(kw)
    return req


class TestStaleMutationOrder(unittest.TestCase):
    """SM: the gate fails closed, in order, at the first failure."""

    def setUp(self):
        self.orch = fixture()

    def test_sm1_order_session_before_all(self):
        """A request failing session AND freshness AND liveness AND
        currency reports 'unknown-session' — the earliest failure."""
        r = self.orch.submit(base_req(device_session_id="ghost",
                                      timestamp=NOW - 10_000,
                                      intent_id="nope", revision=99))
        self.assertEqual(r["reason"], "unknown-session")

    def test_sm2_order_freshness_before_liveness(self):
        """Failing freshness + liveness reports 'stale-request'."""
        r = self.orch.submit(base_req(timestamp=NOW - 10_000, intent_id="nope"))
        self.assertEqual(r["reason"], "stale-request")

    def test_sm3_order_liveness_before_currency(self):
        """Failing liveness + currency reports 'intent-invalid'."""
        r = self.orch.submit(base_req(intent_id="nope", revision=99))
        self.assertEqual(r["reason"], "intent-invalid")

    def test_sm4_order_currency_before_digest(self):
        """Failing currency + digest reports 'stale-revision' — the
        digest is never even compared (decide path)."""
        r = self.orch.submit({"kind": "decide", "intent_id": "intent-1",
                              "work_id": "work-1", "revision": 99,
                              "digest_seen": "wrong",
                              "device_session_id": "iphone-s1",
                              "timestamp": NOW})
        self.assertEqual(r["reason"], "stale-revision")

    def test_sm5_each_step_individually(self):
        """Every step, failed alone, yields its own reason."""
        cases = [
            (base_req(device_session_id="ghost"), "unknown-session"),
            (base_req(timestamp=NOW - 10_000), "stale-request"),
            (base_req(intent_id="nope"), "intent-invalid"),
            (base_req(revision=99), "stale-revision"),
        ]
        for req, want in cases:
            with self.subTest(want=want):
                self.assertEqual(self.orch.submit(req)["reason"], want)

    def test_sm6_refused_mutation_changes_nothing(self):
        """A refused mutation changes nothing: revision, state, and log
        length are identical before and after."""
        w = self.orch.works["work-1"]
        before = (w["revision"], w["state"], len(w["events"]), len(self.orch.sealed_log))
        self.orch.submit(base_req(revision=99))
        after = (w["revision"], w["state"], len(w["events"]))
        self.assertEqual(before[:3], after)
        # ...except the refusal itself is a sealed, logged event:
        self.assertEqual(len(self.orch.sealed_log), before[3] + 1)
        self.assertEqual(self.orch.sealed_log[-1][1], "stale-revision")

    def test_sm7_mutated_intent_reproposed_not_updated(self):
        """A changed target is never 'updated in place': the old intent
        is refused 'intent-invalid'; a NEW intent is proposed and works."""
        it = self.orch.intents["intent-1"]
        it["record"]["target"] = "dropbox:/OTHER.pdf"   # mutation between proposal and decision
        r = self.orch.submit({"kind": "decide", "intent_id": "intent-1",
                              "work_id": "work-1", "revision": 0,
                              "digest_seen": it["digest"],
                              "device_session_id": "iphone-s1", "timestamp": NOW})
        self.assertEqual(r["reason"], "intent-invalid")
        self.assertNotIn("intent-1", self.orch.decisions)
        # new intent, fresh proposal:
        self.orch.propose_intent("intent-2", "work-1", "publish", "dropbox:/OTHER.pdf",
                                 "paper posted", "release", 0, NOW + 3600)
        d = self.orch.intents["intent-2"]["digest"]
        r2 = self.orch.submit({"kind": "decide", "intent_id": "intent-2",
                               "work_id": "work-1", "revision": 0,
                               "digest_seen": d,
                               "device_session_id": "iphone-s1", "timestamp": NOW})
        self.assertTrue(r2["ok"])
        self.assertEqual(r2["status"], "recorded")

    def test_sm8_expired_intent_refused_at_boundary(self):
        """Expiry is integer epoch seconds (Phase 2 Q1); now == expiry is
        refused — the exact boundary fails closed."""
        self.orch.propose_intent("intent-x", "work-1", "publish", "t",
                                 "e", "s", 0, NOW)   # expires exactly now
        d = self.orch.intents["intent-x"]["digest"]
        r = self.orch.submit({"kind": "decide", "intent_id": "intent-x",
                              "work_id": "work-1", "revision": 0,
                              "digest_seen": d, "device_session_id": "iphone-s1",
                              "timestamp": NOW})
        self.assertEqual(r["reason"], "intent-invalid")


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    from orchestrator import dump_all_refusals
    path = os.environ.get("PHASE3_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
