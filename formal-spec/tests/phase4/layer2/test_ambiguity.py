"""Phase 4 Layer 2 — AB family: ambiguity visibility.

What it checks: ambiguous consequential outcomes are never silently
completed (AP1) and never auto-retried (AP2); they are verified
externally if possible (AP3) or marked execution_unknown and escalated
with the next safe option (AP4); the unknown is surfaced on the next
pull with safe options enumerated plus an escalated notification hint
that carries no state (Q4/AP5/AP6). Worker-prepared intents are signed
by the orchestrator after recompute (Q1/S7); consequential
compensation needs a fresh ceremony (Q5/S6).
Draft sections cited: AP1-AP6 (ambiguity-protocol.md sections 2,4),
ER4, RF8, S6-S8.
Exit criteria served: "ambiguous consequential actions become visible
unknown/failed"; "network loss cannot silently complete".

Conventions: virtual server clock NOW fixed (integer epoch seconds).
No randomness — every case is hand-built, hand-verifiable.
"""

import unittest

from idem import IdemOrchestrator, compute_key, dump_all_refusals
from idem import approval_digest

NOW = 1_790_000_000


def mk_intent(iid="intent-1", rev=0, action="send", target="ops@example.com"):
    record = {"intent_id": iid, "work_id": "work-1", "action": action,
              "target": target, "effect": "message sent",
              "scope": "comms", "revision": rev, "expiry": NOW + 3600}
    return record, approval_digest(record)


def mk_key(record, digest, rev, opclass="execute"):
    return compute_key(record["work_id"], record["intent_id"], digest,
                       record["action"], record["target"], record["scope"],
                       rev, opclass)


def fixture():
    return IdemOrchestrator(NOW)


def approved(orch, key, ref="approval-1", opclass="execute"):
    orch.prepare(key, opclass)
    orch.approve(key, ref)


class TestAmbiguity(unittest.TestCase):
    def test_ab1_ambiguous_never_silently_completed(self):
        # AP1/AP2/RF8: opaque tool, receipt lost -> execution_unknown,
        # never completed, never auto-retried, flag false.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["dropped"])
        approved(orch, key)
        r = orch.request_execution(key)
        self.assertEqual(r["reason"], "execution-unknown")
        rec = orch.records[key]
        self.assertEqual(rec["execution_state"], "execution_unknown")
        self.assertNotEqual(rec["execution_state"], "completed")  # AP1
        self.assertFalse(rec["safe_to_retry"])                    # RF8
        self.assertEqual(rec["attempt_count"], 1)                  # AP2: no auto-retry

    def test_ab2_unknown_surfaced_on_pull_with_hint(self):
        # Q4/AP5/AP6: next pull surfaces the unknown with safe options;
        # the escalated hint points at the record and carries no state.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["dropped"])
        approved(orch, key)
        orch.request_execution(key)
        p = orch.pull(key)
        self.assertTrue(p["ok"])
        self.assertEqual(p["record"]["execution_state"], "execution_unknown")
        self.assertIn("cancel", p["record"]["safe_options"])      # AP4/AP5
        self.assertTrue(p["record"]["hint_emitted"])
        self.assertEqual(len(orch.hints), 1)
        hint = orch.hints[0]
        self.assertEqual(hint["state"], "execution_unknown")
        self.assertNotIn("observed_result", hint)                  # AP6: no state
        self.assertNotIn("effect", hint)

    def test_ab3_unknown_never_auto_retries(self):
        # AP2: nothing in the model fires on its own; the retry path is
        # the only retry, and it is refused while unsafe.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["dropped"])
        approved(orch, key)
        orch.request_execution(key)
        rr = orch.retry(key)
        self.assertFalse(rr["ok"])
        self.assertEqual(rr["reason"], "unsafe-retry")
        self.assertEqual(orch.tool.effect_count(key), 1)

    def test_ab4_external_verification_resolves_unknown(self):
        # AP3: "present" completes the record; "absent" makes retry safe.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["dropped"])
        approved(orch, key)
        orch.request_execution(key)
        v = orch.verify_external(key, "present")
        self.assertTrue(v["ok"])
        self.assertEqual(v["record"]["execution_state"], "completed")
        # and the absent path:
        orch2 = fixture()
        record2, digest2 = mk_intent(iid="intent-2")
        key2 = mk_key(record2, digest2, 0)
        orch2.tool.set(key2, ["lost"])
        approved(orch2, key2)
        orch2.request_execution(key2)
        v2 = orch2.verify_external(key2, "absent")
        self.assertTrue(v2["ok"])
        self.assertTrue(orch2.records[key2]["safe_to_retry"])   # RF7

    def test_ab5_compensation_needs_fresh_ceremony(self):
        # Q5/S6/S8: riding the original key/approval is refused; a fresh
        # ceremony (own key, own approval) proceeds.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        approved(orch, key)
        orch.request_execution(key)
        bad = orch.request_compensation(key, key, "approval-1")
        self.assertFalse(bad["ok"])
        self.assertEqual(bad["reason"], "needs-fresh-ceremony")  # S8
        self.assertEqual(len(orch.records), 1)  # nothing new created
        # fresh ceremony:
        crec, cdigest = mk_intent(iid="intent-comp", action="revoke",
                                  target="ops@example.com")
        ckey = mk_key(crec, cdigest, 0, opclass="compensate")
        orch.tool.set(ckey, ["receipt"])
        good = orch.request_compensation(key, ckey, "approval-comp")
        self.assertTrue(good["ok"])
        self.assertEqual(good["record"]["execution_state"], "completed")
        self.assertNotEqual(ckey, key)  # own key (S6)

    def test_ab6_worker_intent_signed_by_orchestrator(self):
        # Q1/S7: correct worker digest -> orchestrator signature +
        # provenance; tampered digest -> refused.
        orch = fixture()
        record, digest = mk_intent(iid="intent-w")
        claimed = dict(record, digest=digest)
        r = orch.propose_worker_intent("worker-7", claimed)
        self.assertTrue(r["ok"])
        self.assertEqual(r["intent"]["signature"]["by"], "orchestrator")  # S7
        self.assertEqual(r["intent"]["signature"]["digest"], digest)
        self.assertEqual(r["intent"]["provenance"]["prepared_by"], "worker-7")
        # tampered:
        bad_claim = dict(record, digest="0" * 64)
        rb = orch.propose_worker_intent("worker-7", bad_claim)
        self.assertFalse(rb["ok"])
        self.assertEqual(rb["reason"], "digest-mismatch")

    def test_ab7_all_record_states_exercised(self):
        # L2 gate: every execution-record state is visited by at least
        # one transition in this suite.
        orch = fixture()
        record, digest = mk_intent()
        key = mk_key(record, digest, 0)
        orch.tool.set(key, ["lost", "receipt"])
        orch.prepare(key, "execute")            # prepared
        orch.approve(key, "approval-1")        # approved
        orch.request_execution(key)            # requested -> started -> unknown
        orch.verify_external(key, "absent")    # stays unknown, flag set
        orch.retry(key)                        # approved -> requested -> started -> observed -> completed
        record2, digest2 = mk_intent(iid="intent-2")
        key2 = mk_key(record2, digest2, 0)
        orch.tool.set(key2, ["failed"])
        orch.prepare(key2, "execute")
        orch.approve(key2, "approval-2")
        orch.request_execution(key2)           # -> execution_failed
        record3, digest3 = mk_intent(iid="intent-3")
        key3 = mk_key(record3, digest3, 0)
        orch.tool.set(key3, ["lost"])
        orch.prepare(key3, "execute")
        orch.approve(key3, "approval-3")
        orch.request_execution(key3)           # -> unknown
        orch.cancel(key3)                      # -> cancelled
        visited = {s for _, _, s, _ in
                   [e for e in orch.sealed_log if e[0] == "transition"]}
        for state in ("prepared", "approved", "execution_requested",
                      "execution_started", "execution_observed",
                      "execution_failed", "execution_unknown",
                      "completed", "cancelled"):
            # prepared is logged as ("prepared", ...) not ("transition", ...)
            if state == "prepared":
                self.assertTrue(any(e[0] == "prepared" for e in orch.sealed_log))
            else:
                self.assertIn(state, visited, "state never visited: %s" % state)


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    path = os.environ.get("PHASE4_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
