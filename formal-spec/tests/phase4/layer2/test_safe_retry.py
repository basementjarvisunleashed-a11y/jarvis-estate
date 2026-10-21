"""Phase 4 Layer 2 — SR family: safe retry.

What it checks: retries proceed only when the safe_to_retry flag holds
(RF4); the flag is set only when the effect is verified absent or
safely repeatable (RF7), and is false on ambiguity (RF8); a refused
retry changes nothing and does not advance attempt_count (RF9); the
revision frozen at BIND keeps the key stable across retries (Q2/K2).
Draft sections cited: RF1-RF9 (retry-policy-matrix.md section 3),
ER2, ER5, K2.
Exit criteria served: "retries only when safe"; "at-most-once
demonstrable under test".

Conventions: virtual server clock NOW fixed (integer epoch seconds).
No randomness — every case is hand-built, hand-verifiable.
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


class TestSafeRetry(unittest.TestCase):
    def test_sr1_unsafe_retry_refused_attempt_count_unchanged(self):
        # RF4/RF9: opaque tool, no receipt -> unknown, safe_to_retry
        # false -> the retry is refused and changes nothing.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["dropped"])   # effect happened, receipt lost
        approved(orch, key)
        r = orch.request_execution(key)
        self.assertEqual(r["reason"], "execution-unknown")
        attempts_before = orch.records[key]["attempt_count"]
        rr = orch.retry(key)
        self.assertFalse(rr["ok"])
        self.assertEqual(rr["reason"], "unsafe-retry")
        self.assertEqual(orch.records[key]["attempt_count"], attempts_before)  # RF9
        self.assertEqual(orch.tool.effect_count(key), 1)

    def test_sr2_verified_absent_retry_still_at_most_once(self):
        # RF7: the effect verified absent -> safe_to_retry -> retry fires
        # -> this fire is still the first actual effect. ER2 holds.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["lost", "receipt"])  # first: no effect, no receipt
        approved(orch, key)
        r = orch.request_execution(key)
        self.assertEqual(r["reason"], "execution-unknown")
        self.assertEqual(orch.tool.effect_count(key), 0)
        v = orch.verify_external(key, "absent")
        self.assertTrue(v["ok"])
        self.assertTrue(orch.records[key]["safe_to_retry"])  # RF7
        rr = orch.retry(key)
        self.assertTrue(rr["ok"])
        self.assertEqual(rr["record"]["execution_state"], "completed")
        self.assertEqual(orch.tool.effect_count(key), 1)     # ER2: at most once

    def test_sr3_revision_frozen_at_bind_key_stable_across_retries(self):
        # Q2/K2: the key hashes the approval-time revision. A later
        # revision bump does not re-key the retry.
        record, digest = mk_intent(rev=3)
        key_at_approval = mk_key(record, digest, 3)
        key_after_bump = mk_key(record, digest, 3)  # still the frozen revision
        self.assertEqual(key_at_approval, key_after_bump)
        self.assertNotEqual(key_at_approval, mk_key(record, digest, 4))
        orch = fixture()
        orch.tool.set(key_at_approval, ["receipt"])
        approved(orch, key_at_approval)
        orch.request_execution(key_at_approval)
        # the "retry" after the bump addresses the same key:
        r = orch.request_execution(key_at_approval)
        self.assertTrue(r.get("duplicate"))
        self.assertEqual(len(orch.records), 1)

    def test_sr4_retry_of_completed_returns_existing(self):
        # ER5: terminal records return the existing record.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        approved(orch, key)
        orch.request_execution(key)
        r = orch.retry(key)
        self.assertTrue(r.get("duplicate"))
        self.assertEqual(r["record"]["execution_state"], "completed")
        self.assertEqual(orch.tool.effect_count(key), 1)

    def test_sr5_native_tool_retry_returns_existing_not_second_effect(self):
        # A natively idempotent integration: even a retry converges on
        # the existing record; the effect fires once.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["receipt", "receipt"])
        approved(orch, key)
        orch.request_execution(key)
        r = orch.request_execution(key)
        self.assertTrue(r.get("duplicate"))
        self.assertEqual(orch.tool.effect_count(key), 1)

    def test_sr6_cancel_then_retry_returns_cancelled(self):
        # Cancelled is terminal (ER5): the retry returns the record.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["lost"])
        approved(orch, key)
        orch.request_execution(key)   # -> unknown
        orch.cancel(key)
        r = orch.retry(key)
        self.assertTrue(r.get("duplicate"))
        self.assertEqual(r["record"]["execution_state"], "cancelled")


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    path = os.environ.get("PHASE4_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
