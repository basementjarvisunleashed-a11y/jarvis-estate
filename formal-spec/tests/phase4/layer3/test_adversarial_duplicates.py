"""Phase 4 Layer 3 — AD family: adversarial duplicate submissions.

What it checks: racing duplicate execution requests, duplicate
approvals, and replayed requests under every delivery interleaving —
at-most-once holds in all of them (ER2), one record per key (ER1).
Draft sections cited: ER1, ER2, S4, RF3, K5.
Exit criteria served: "duplicate taps cannot duplicate effects";
"at-most-once demonstrable under test".

Deterministic: itertools.permutations over the op list, one fresh
fixture per permutation — every serialization the orchestrator could
observe is exercised (the orchestrator serializes arrivals; the chaos
enumerates every serialization).
"""

import itertools
import unittest

from chaos import mk_intent, mk_key, assert_at_most_once
from idem import IdemOrchestrator, dump_all_refusals

NOW = 1_790_000_000


def fresh(key, tool_outcomes=("receipt",)):
    orch = IdemOrchestrator(NOW)
    orch.tool.set(key, list(tool_outcomes))
    orch.prepare(key, "execute")
    orch.approve(key, "approval-1")
    return orch


class TestAdversarialDuplicates(unittest.TestCase):
    def _run_orders(self, key, ops, tool_outcomes=("receipt",)):
        """Run every permutation of ops on a fresh fixture; assert the
        invariants after each. Returns the number of orders run."""
        n = 0
        for order in itertools.permutations(range(len(ops))):
            orch = fresh(key, tool_outcomes)
            for i in order:
                ops[i](orch, key)
            rec = orch.records[key]
            self.assertIn(rec["execution_state"],
                          ("completed", "execution_unknown", "execution_failed"),
                          "order %s left record in %s" % (order, rec["execution_state"]))
            assert_at_most_once(orch, key)
            self.assertEqual(len(orch.records), 1)  # ER1
            n += 1
        return n

    def test_ad1_racing_duplicate_executes_all_interleavings(self):
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        ops = [lambda o, k: o.request_execution(k),
               lambda o, k: o.request_execution(k)]
        n = self._run_orders(key, ops)
        self.assertEqual(n, 2)  # 2! orders

    def test_ad2_duplicate_approvals_race(self):
        # RF3 under race: one decision, duplicates return it.
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        n = 0
        for order in itertools.permutations([0, 1]):
            orch = IdemOrchestrator(NOW)
            orch.prepare(key, "execute")
            for _ in order:
                orch.approve(key, "approval-1")
            self.assertEqual(orch.records[key]["approval_ref"], "approval-1")
            n += 1
        self.assertEqual(n, 2)

    def test_ad3_replayed_execution_request_thrice(self):
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch = fresh(key)
        for _ in range(3):
            r = orch.request_execution(key)
        self.assertTrue(r.get("duplicate"))
        assert_at_most_once(orch, key)
        self.assertEqual(orch.tool.effect_count(key), 1)

    def test_ad4_three_way_race_execute_execute_retry(self):
        # Six orders of (execute, execute, retry): the retry is refused
        # or returns existing — it never becomes a second effect.
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        ops = [lambda o, k: o.request_execution(k),
               lambda o, k: o.request_execution(k),
               lambda o, k: o.retry(k)]
        n = self._run_orders(key, ops)
        self.assertEqual(n, 6)  # 3! orders

    def test_ad5_race_execute_vs_cancel(self):
        # Cancel racing execution: either the execution won (completed)
        # or the cancel won (cancelled) — never both, never a duplicate.
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        n = 0
        for order in itertools.permutations(["exec", "cancel"]):
            orch = fresh(key)
            for op in order:
                if op == "exec":
                    orch.request_execution(key)
                else:
                    orch.cancel(key)
            st = orch.records[key]["execution_state"]
            self.assertIn(st, ("completed", "cancelled"))
            assert_at_most_once(orch, key)
            n += 1
        self.assertEqual(n, 2)


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    import os
    path = os.environ.get("PHASE4_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
