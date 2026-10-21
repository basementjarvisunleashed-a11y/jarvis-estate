"""Phase 4 Layer 3 — NL family: network loss mid-execution.

What it checks: when the link dies between execution_started and
observation, the record must show execution_unknown or a verified
outcome — never a silent completion; reconnect must not double-execute.
The ChaosLink severs the request/receipt path; the orchestrator's
ambiguity handling is what's under test.
Draft sections cited: AP1-AP4, ER2, ER4, RF4/RF7.
Exit criteria served: "network loss cannot silently complete";
"at-most-once demonstrable under test".

Deterministic: fixed virtual clock, hand-severed links, no randomness.
"""

import unittest

from chaos import (mk_intent, mk_key, ChaosLink, assert_at_most_once,
                   assert_visible_unknown_or_settled)
from idem import IdemOrchestrator, dump_all_refusals

NOW = 1_790_000_000


def fixture():
    orch = IdemOrchestrator(NOW)
    link = ChaosLink(orch)
    orig_fire = orch.tool.fire

    def fire_via_link(key):
        r = link.fire_through(key)
        if r == "severed":
            # From the orchestrator's view: no receipt, no observable
            # effect — indistinguishable from "lost". That indistinction
            # is the ambiguity the protocol must handle honestly.
            return "lost"
        return r

    orch.tool.fire = fire_via_link
    return orch, link


def approved(orch, key, ref="approval-1"):
    orch.prepare(key, "execute")
    orch.approve(key, ref)


class TestNetworkLoss(unittest.TestCase):
    def test_nl1_severed_mid_execution_never_silently_completes(self):
        orch, link = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        approved(orch, key)
        link.sever()                       # the link dies mid-flight
        r = orch.request_execution(key)
        self.assertEqual(r["reason"], "execution-unknown")
        st = assert_visible_unknown_or_settled(orch, key)
        self.assertEqual(st, "execution_unknown")
        assert_at_most_once(orch, key)
        self.assertNotEqual(orch.records[key]["execution_state"], "completed")

    def test_nl2_reconnect_verify_absent_retry_completes_once(self):
        orch, link = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        approved(orch, key)
        link.sever()
        orch.request_execution(key)        # -> unknown
        link.heal()                        # reconnect
        # A blind retry is still refused: the unknown is unresolved.
        rr = orch.retry(key)
        self.assertFalse(rr["ok"])
        self.assertEqual(rr["reason"], "unsafe-retry")
        # External verification observes absence -> retry is safe.
        orch.verify_external(key, "absent")
        rr2 = orch.retry(key)
        self.assertTrue(rr2["ok"])
        self.assertEqual(rr2["record"]["execution_state"], "completed")
        assert_at_most_once(orch, key)

    def test_nl3_reconnect_verify_present_no_refire(self):
        # The effect happened; only the receipt was lost. Verification
        # observes presence -> completed with NO second fire.
        orch, link = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["dropped"])    # effect happened, receipt lost
        approved(orch, key)
        orch.request_execution(key)        # -> unknown
        orch.verify_external(key, "present")
        rec = orch.records[key]
        self.assertEqual(rec["execution_state"], "completed")
        self.assertEqual(orch.tool.effect_count(key), 1)
        assert_at_most_once(orch, key)

    def test_nl4_flapping_link_duplicate_taps_still_one_record(self):
        orch, link = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        approved(orch, key)
        link.sever()
        orch.request_execution(key)        # -> unknown
        link.heal()
        orch.request_execution(key)        # duplicate tap after reconnect
        link.sever()
        orch.request_execution(key)        # another duplicate
        link.heal()
        self.assertEqual(len(orch.records), 1)   # ER1
        assert_at_most_once(orch, key)
        assert_visible_unknown_or_settled(orch, key)

    def test_nl5_severed_before_first_fire_no_phantom_effect(self):
        # The link dies before the fire: the orchestrator still records
        # unknown (it cannot know), but no effect occurred and a
        # verified retry completes exactly once.
        orch, link = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        approved(orch, key)
        link.sever()
        r = orch.request_execution(key)
        self.assertEqual(r["reason"], "execution-unknown")
        link.heal()
        orch.verify_external(key, "absent")
        rr = orch.retry(key)
        self.assertEqual(rr["record"]["execution_state"], "completed")
        assert_at_most_once(orch, key)
        self.assertEqual(orch.tool.effect_count(key), 1)


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    import os
    path = os.environ.get("PHASE4_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
