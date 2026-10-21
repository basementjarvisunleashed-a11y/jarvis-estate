"""Phase 4 Layer 3 — AX family: ambiguous outcomes under chaos.

What it checks: externally unverifiable consequential actions under
partition and loss all become VISIBLE unknown/failed — never silently
complete, never silently stuck. Every unknown is surfaced on pull with
safe options and an escalated hint.
Draft sections cited: AP1-AP6, ER4, RF8.
Exit criteria served: "ambiguous consequential actions become visible
unknown/failed"; "network loss cannot silently complete".

Deterministic: fixed outcome scripts per key, no randomness.
"""

import unittest

from chaos import (mk_intent, mk_key, assert_at_most_once,
                   assert_visible_unknown_or_settled)
from idem import IdemOrchestrator, dump_all_refusals

NOW = 1_790_000_000


def approved(orch, key, ref="approval-1"):
    orch.prepare(key, "execute")
    orch.approve(key, ref)


class TestAmbiguousChaos(unittest.TestCase):
    def test_ax1_opaque_tools_all_become_visible_unknown(self):
        # Five keys, all opaque: every one ends visible-unknown, none
        # silently completed, none silently stuck.
        orch = IdemOrchestrator(NOW)
        keys = []
        for i in range(5):
            record, digest = mk_intent(iid="intent-%d" % i)
            key = mk_key(record, digest, 0)
            orch.tool.set(key, ["dropped"])
            approved(orch, key, ref="approval-%d" % i)
            orch.request_execution(key)
            keys.append(key)
        for key in keys:
            st = assert_visible_unknown_or_settled(orch, key)
            self.assertEqual(st, "execution_unknown")
            assert_at_most_once(orch, key)
        self.assertEqual(len(orch.hints), 5)  # one hint per unknown (Q4)

    def test_ax2_mixed_outcomes_each_resolved_per_its_kind(self):
        # receipt -> completed; failed -> execution_failed; dropped/lost
        # -> visible unknown. No silent completions anywhere.
        orch = IdemOrchestrator(NOW)
        plan = {"intent-a": "receipt", "intent-b": "failed",
                "intent-c": "dropped", "intent-d": "lost"}
        keys = {}
        for iid, outcome in plan.items():
            record, digest = mk_intent(iid=iid)
            key = mk_key(record, digest, 0)
            orch.tool.set(key, [outcome])
            approved(orch, key, ref="approval-" + iid)
            orch.request_execution(key)
            keys[iid] = key
        self.assertEqual(orch.records[keys["intent-a"]]["execution_state"], "completed")
        self.assertEqual(orch.records[keys["intent-b"]]["execution_state"], "execution_failed")
        for iid in ("intent-c", "intent-d"):
            st = assert_visible_unknown_or_settled(orch, keys[iid])
            self.assertEqual(st, "execution_unknown")
            assert_at_most_once(orch, keys[iid])

    def test_ax3_unknown_then_verify_present_under_flap(self):
        # Unknown under a flapping path, then external verification
        # observes presence: completed with no second fire.
        orch = IdemOrchestrator(NOW)
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["dropped", "dropped"])
        approved(orch, key)
        orch.request_execution(key)          # -> unknown
        orch.request_execution(key)          # duplicate tap: existing record
        p = orch.pull(key)
        self.assertTrue(p["record"]["hint_emitted"])
        orch.verify_external(key, "present")
        rec = orch.records[key]
        self.assertEqual(rec["execution_state"], "completed")
        self.assertEqual(orch.tool.effect_count(key), 1)  # ER2
        assert_at_most_once(orch, key)

    def test_ax4_failed_executions_retry_safely_never_duplicate(self):
        # Definitive failure: the tool observed non-occurrence (RF7), so
        # a retry is safe — and still never a duplicate effect.
        orch = IdemOrchestrator(NOW)
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["failed", "receipt"])
        approved(orch, key)
        r = orch.request_execution(key)
        self.assertEqual(r["reason"], "execution-failed")
        self.assertEqual(orch.tool.effect_count(key), 0)
        self.assertTrue(orch.records[key]["safe_to_retry"])  # RF7
        rr = orch.retry(key)
        self.assertTrue(rr["ok"])
        self.assertEqual(rr["record"]["execution_state"], "completed")
        assert_at_most_once(orch, key)
        self.assertEqual(orch.tool.effect_count(key), 1)  # ER2

    def test_ax5_many_keys_chaos_sweep(self):
        # Twelve keys with a fixed mixed script: the sweep asserts the
        # invariants hold for every key regardless of outcome.
        orch = IdemOrchestrator(NOW)
        script = (["receipt"] * 3 + ["dropped"] * 3 + ["lost"] * 3
                  + ["failed"] * 3)
        keys = []
        for i, outcome in enumerate(script):
            record, digest = mk_intent(iid="sweep-%d" % i)
            key = mk_key(record, digest, 0)
            orch.tool.set(key, [outcome])
            approved(orch, key, ref="approval-sweep-%d" % i)
            orch.request_execution(key)
            orch.request_execution(key)      # duplicate tap on every key
            keys.append((key, outcome))
        for key, outcome in keys:
            assert_at_most_once(orch, key)
            st = assert_visible_unknown_or_settled(orch, key)
            if outcome == "receipt":
                self.assertEqual(st, "completed")
            elif outcome == "failed":
                self.assertEqual(st, "execution_failed")
            else:
                self.assertEqual(st, "execution_unknown")
        # every unknown emitted exactly one hint
        unknowns = [k for k, o in keys if o in ("dropped", "lost")]
        self.assertEqual(len(orch.hints), len(unknowns))


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    import os
    path = os.environ.get("PHASE4_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
