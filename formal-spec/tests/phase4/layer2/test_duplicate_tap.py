"""Phase 4 Layer 2 — DT family: duplicate taps.

What it checks: the first tap validates and records; the second tap
returns the existing decision and state — never a second execution
(ROADMAP.md section 7; idempotency-key-spec.md K1-K6; saga-spec.md S4).
Two devices, one intent, one key, one execution (Q3/K3).
Draft sections cited: K1-K6 (key spec sections 2-3), S4, ER1, ER2, ER5,
RF3.
Exit criteria served: "duplicate taps cannot duplicate effects";
"at-most-once demonstrable under test".

Conventions: virtual server clock NOW fixed per test class (integer
epoch seconds, Phase 2 Q1 ruling). No randomness — every case is
hand-built, hand-verifiable.
"""

import unittest

from idem import IdemOrchestrator, compute_key, dump_all_refusals
from idem import approval_digest

NOW = 1_790_000_000


def mk_intent(iid="intent-1", rev=0):
    record = {"intent_id": iid, "work_id": "work-1", "action": "send",
              "target": "ops@example.com", "effect": "message sent",
              "scope": "comms", "revision": rev, "expiry": NOW + 3600}
    return record, approval_digest(record)


def mk_key(record, digest, rev, opclass="execute"):
    return compute_key(record["work_id"], record["intent_id"], digest,
                       record["action"], record["target"], record["scope"],
                       rev, opclass)


def fixture():
    return IdemOrchestrator(NOW)


def approved(orch, key, ref="approval-1"):
    orch.prepare(key, "execute")
    orch.approve(key, ref)
    return key


class TestDuplicateTap(unittest.TestCase):
    def test_dt1_second_tap_same_device_never_executes_twice(self):
        # K5/K6 + S4 + ER2: the second tap returns the existing record.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        approved(orch, key)
        r1 = orch.request_execution(key)
        r2 = orch.request_execution(key)
        self.assertTrue(r1["ok"] and not r1.get("duplicate"))
        self.assertTrue(r2.get("duplicate"))
        self.assertEqual(r2["record"]["execution_state"], "completed")
        self.assertEqual(orch.tool.effect_count(key), 1)  # ER2: at most once
        self.assertEqual(len(orch.records), 1)            # ER1: one record

    def test_dt2_two_devices_one_intent_one_key_one_execution(self):
        # Q3/K3: the key excludes device_session_id — two devices
        # tapping the same intent converge on one key and one execution.
        orch = fixture()
        record, digest = mk_intent()
        key_iphone = mk_key(record, digest, 0)
        key_watch = mk_key(record, digest, 0)   # no session in the formula
        self.assertEqual(key_iphone, key_watch)  # K3
        approved(orch, key_iphone)
        orch.request_execution(key_iphone)
        r = orch.request_execution(key_watch)    # the Watch's tap
        self.assertTrue(r.get("duplicate"))
        self.assertEqual(orch.tool.effect_count(key_iphone), 1)

    def test_dt3_duplicate_after_completed_returns_record(self):
        # ER5: terminal records return the existing record.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        approved(orch, key)
        orch.request_execution(key)
        r = orch.request_execution(key)
        self.assertTrue(r.get("duplicate"))
        self.assertEqual(r["record"]["execution_state"], "completed")
        self.assertEqual(orch.tool.effect_count(key), 1)

    def test_dt4_duplicate_approval_returns_same_decision(self):
        # RF3: approvals recorded once.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.prepare(key, "execute")
        a1 = orch.approve(key, "approval-1")
        a2 = orch.approve(key, "approval-1")
        self.assertTrue(a2.get("duplicate"))
        self.assertEqual(a2["record"]["approval_ref"], "approval-1")
        self.assertFalse(a1.get("duplicate"))

    def test_dt5_key_stable_for_same_approved_intent(self):
        # K5: the same approved intent always yields the same key.
        record, digest = mk_intent()
        self.assertEqual(mk_key(record, digest, 0), mk_key(record, digest, 0))

    def test_dt6_changed_intent_is_a_different_key(self):
        # K6: a changed intent cannot ride an old key.
        record, digest = mk_intent()
        record2 = dict(record, target="other@example.com")
        digest2 = approval_digest(record2)
        self.assertNotEqual(mk_key(record, digest, 0),
                            mk_key(record2, digest2, 0))

    def test_dt7_execute_without_approval_refused(self):
        # S4: execution needs a valid approval.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.prepare(key, "execute")   # prepared, not approved
        r = orch.request_execution(key)
        self.assertTrue(r.get("duplicate"))  # returned, never executed
        self.assertEqual(orch.tool.effect_count(key), 0)


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    path = os.environ.get("PHASE4_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
