"""Phase 1 tests — pull protocol, orchestrator loop, chaos.

One test per pull-discipline rule (5), signed-request verification,
long-poll behavior, denial auditability, plane enforcement, the
orchestrator tick, and three chaos cases (partition, replay, clock skew).
All five rules are asserted under every chaos case.

Python 3 stdlib only (unittest). No network.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import seal, keys
from common.clock import FakeClock
from common.planes import Plane, PlaneViolation
from common.seal import SealError

import pull
from pull import (Phase1Gateway, PartitionError, PullServer, PullClient,
                  GovernanceServer, DataServer, GovernedLog, TRANSPORT_KEY,
                  MAX_SKEW)
from loop import Orchestrator

T0 = 1_700_000_000
PUSH_LIKE = ("push", "send", "notify", "chase")


class Harness:
    """Fresh Phase-1 wiring per test. TEST keys via the Phase-0 ceremony."""

    def __init__(self, server_cls=PullServer):
        self.tmp = tempfile.mkdtemp(prefix="phase1-")
        self.clock = FakeClock(start=T0)
        key_dir = os.path.join(self.tmp, "keys")
        self.keyset = keys.ceremony_generate(key_dir,
                                             surfaces=("phone", "watch"))
        assert keys.is_test_keyset(key_dir), "ceremony must mark TEST keys"
        self.gateway = Phase1Gateway(self.clock)
        self.gov = GovernanceServer("governance", self.keyset)
        self.data = DataServer("data-plane")
        self.server = server_cls("pull-server", self.clock)
        self.gateway.serve(Plane.GOVERNANCE, self.gov)
        self.gateway.serve(Plane.DATA, self.data)
        self.gateway.serve(Plane.CONTROL, self.server)
        for c in (self.gov, self.data, self.server):
            c.wire(self.gateway)
        self.log = GovernedLog(os.path.join(self.tmp, "intent.log"),
                               self.gateway, self.server, self.clock)
        self.server.log = self.log
        self.orch = Orchestrator("orchestrator", self.server, self.log,
                                 self.clock)
        self.orch.wire(self.gateway)
        self.client = PullClient("surface:phone", "phone",
                                 self.keyset["surface:phone"],
                                 FakeClock(start=T0))
        self.client.wire(self.gateway)
        self.client2 = PullClient("surface:watch", "watch",
                                  self.keyset["surface:watch"],
                                  FakeClock(start=T0))
        self.client2.wire(self.gateway)
        self.seal_fixture("k1", {"value": 42, "label": "answer"})

    def seal_fixture(self, key, data):
        env = self.gateway.pull(
            self.server, Plane.GOVERNANCE,
            {"op": "seal", "key_name": "master", "content": data,
             "origin": "data-plane", "ts": self.clock.now(),
             "req_id": "fixture-%s" % key}, key=TRANSPORT_KEY)
        self.data.store(key, data, env["content"]["envelope"])

    def push_sample(self, value, key="k1"):
        data = {"value": value, "key": key}
        env = self.gateway.pull(
            self.server, Plane.GOVERNANCE,
            {"op": "seal", "key_name": "master", "content": data,
             "origin": "data-plane", "ts": self.clock.now(),
             "req_id": "sample"}, key=TRANSPORT_KEY)
        self.data.push_sample(data, env["content"]["envelope"])

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class PullTestBase(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def tearDown(self):
        self.h.close()

    def five_rules_hold(self, h, denial_req_id=None):
        """All five pull-discipline rules, against a live harness."""
        gw = h.gateway
        # Rule 1: every interaction began with a client pull — each audit
        # record is a pull carrying its originator's req_id, and no
        # push-like path exists anywhere.
        for rec in gw.audit:
            self.assertNotEqual(rec.req_id, "req-?",
                                "unaudited interaction: %r" % (rec,))
            self.assertNotEqual(rec.from_plane, rec.to_plane)
        for obj in (h.server, h.orch, h.client):
            for name in PUSH_LIKE:
                self.assertFalse(hasattr(obj, name),
                                 "push-like path %r exists" % name)
        # Rule 2: every response the client holds is sealed.
        for env in h.client.received:
            self.assertTrue(seal.verify_envelope(h.client.key, env),
                            "un-sealed response reached the client")
        # Rule 3: nothing renders before its seal verifies.
        if h.client.received:
            tampered = json.loads(json.dumps(h.client.received[-1]))
            tampered["seal"] = "0" * 64
            with self.assertRaises(SealError):
                h.client.render(tampered)
        # Rule 4: denials are sealed and auditable.
        if denial_req_id is not None:
            denials = [e for e in h.log.entries
                       if e["content"]["type"] == "DENIAL"
                       and e["content"]["content"].get("req_id")
                       == denial_req_id]
            self.assertEqual(len(denials), 1,
                             "denial not audited exactly once")
            self.assertTrue(h.log.verify_chain(),
                            "intent-log chain does not verify")
        # Rule 5: timeouts/retries are the client's business — the server
        # has no retry/backoff machinery at all.
        for attr in dir(h.server):
            low = attr.lower()
            self.assertNotIn("retry", low)
            self.assertNotIn("backoff", low)


# ---------------------------------------------------------------- rules

class TestPullRules(PullTestBase):
    def test_rule1_every_interaction_begins_with_client_pull(self):
        h = self.h
        resp = h.client.pull({"key": "k1"})
        h.client.render(resp)
        for rec in h.gateway.audit:
            self.assertNotEqual(rec.req_id, "req-?")
        # The idle surface received nothing: nothing was ever pushed.
        self.assertEqual(h.client2.received, [])
        self.assertEqual(len(h.client.received), 1)

    def test_rule2_every_response_is_sealed(self):
        h = self.h
        resp = h.client.pull({"key": "k1"})
        self.assertTrue(seal.verify_envelope(h.client.key, resp))
        # The transport envelope was verified inside pull(); the inner
        # response seal verifies here, before render.
        content = h.client.render(resp)
        self.assertEqual(content["body"], {"value": 42, "label": "answer"})

    def test_rule3_nothing_renders_before_seal_verifies(self):
        h = self.h
        resp = h.client.pull({"key": "k1"})
        tampered = json.loads(json.dumps(resp))
        tampered["content"]["body"] = {"value": 999}
        with self.assertRaises(SealError):
            h.client.render(tampered)
        tampered2 = json.loads(json.dumps(resp))
        tampered2["seal"] = "f" * 64
        with self.assertRaises(SealError):
            h.client.render(tampered2)
        # Untouched seal renders fine.
        self.assertEqual(h.client.render(resp)["body"]["value"], 42)

    def test_rule4_denials_are_sealed_and_auditable(self):
        h = self.h
        env = h.client._request_envelope({"key": "k1"}, "r1")
        bad = json.loads(json.dumps(env))
        bad["content"]["query"] = {"key": "k2"}  # break the signature
        req_id = bad["content"]["req_id"]
        resp_env = h.gateway.pull(h.client, Plane.CONTROL,
                                  {"request": bad, "req_id": req_id},
                                  key=h.client.key)
        inner = seal.open_envelope(h.client.key, resp_env)[0]["response"]
        # The denial itself is sealed and verifies with the surface key.
        self.assertTrue(seal.verify_envelope(h.client.key, inner))
        denied = h.client.render(inner)
        self.assertEqual(denied["reason"], "bad-signature")
        self.assertEqual(denied["req_id"], req_id)
        # ...and it is audited: exactly one DENIAL entry, chain verifies.
        self.five_rules_hold(h, denial_req_id=req_id)

    def test_rule5_timeouts_and_retries_are_clients_business(self):
        h = self.h
        h.gateway.partition = True
        before = len(h.gateway.audit)
        with self.assertRaises(PartitionError):
            h.client.pull_with_retry({"key": "k1"}, max_attempts=3)
        self.assertEqual(h.client.attempts, 3)   # the CLIENT retried
        self.assertEqual(len(h.gateway.audit), before)  # drops aren't served
        self.assertEqual(h.server.served_journal, [])   # server never chases
        # No retry/backoff machinery on the server, in attributes or source.
        with open(pull.__file__, encoding="utf-8") as fh:
            src = fh.read().lower()
        server_src = src[src.index("class pullserver"):
                         src.index("class pullclient")]
        self.assertNotIn("retry", server_src)
        self.assertNotIn("backoff", server_src)
        self.assertNotIn("chase", server_src)


# ------------------------------------------------------- signed requests

class TestSignedRequests(PullTestBase):
    def test_good_signature_accepted(self):
        h = self.h
        resp = h.client.pull({"key": "k1"}, revision="r3")
        content = h.client.render(resp)
        self.assertEqual(content["revision"], "r3")
        self.assertEqual(content["body"], {"value": 42, "label": "answer"})
        # Proof verified before trust (runs inside governance).
        self.assertTrue(h.client.trust(resp))

    def test_bad_signature_refused_with_sealed_denial(self):
        h = self.h
        env = h.client._request_envelope({"key": "k1"}, "r1")
        bad = json.loads(json.dumps(env))
        bad["content"]["query"] = {"key": "evil"}
        req_id = bad["content"]["req_id"]
        resp_env = h.gateway.pull(h.client, Plane.CONTROL,
                                  {"request": bad, "req_id": req_id},
                                  key=h.client.key)
        inner = seal.open_envelope(h.client.key, resp_env)[0]["response"]
        self.assertTrue(seal.verify_envelope(h.client.key, inner))
        denied = h.client.render(inner)
        self.assertEqual(denied["reason"], "bad-signature")
        denials = [e for e in h.log.entries
                   if e["content"]["type"] == "DENIAL"]
        self.assertEqual(len(denials), 1)
        self.assertEqual(denials[0]["content"]["content"]["req_id"], req_id)
        self.assertTrue(h.log.verify_chain())


# ---------------------------------------------------------------- long-poll

class TestLongPoll(PullTestBase):
    def test_long_poll_data_arrives(self):
        box = {}

        class InjectingServer(PullServer):
            def _wait_tick(self, n):
                if n == 2:
                    box["h"].seal_fixture("k2", {"value": 7})
                super()._wait_tick(n)

        h = Harness(server_cls=InjectingServer)
        box["h"] = h
        self.addCleanup(h.close)
        resp = h.client.pull({"key": "k2"}, wait_deadline=T0 + 100)
        content = h.client.render(resp)
        self.assertFalse(content.get("timeout", False))
        self.assertEqual(content["body"], {"value": 7})
        self.assertTrue(h.client.trust(resp))

    def test_long_poll_deadline_returns_sealed_timeout(self):
        h = self.h
        resp = h.client.pull({"key": "missing"}, wait_deadline=T0 + 5)
        # Sealed (rule 2) even though empty.
        self.assertTrue(seal.verify_envelope(h.client.key, resp))
        content = h.client.render(resp)
        self.assertTrue(content.get("timeout"))
        self.assertIsNone(content["body"])
        self.assertTrue(h.client.trust(resp))  # nothing claimed: nothing to prove

    def test_long_poll_server_initiates_nothing(self):
        h = self.h
        req_id_holder = []
        orig = h.client._request_envelope

        def spy(query, revision):
            env = orig(query, revision)
            req_id_holder.append(env["content"]["req_id"])
            return env
        h.client._request_envelope = spy
        resp = h.client.pull({"key": "missing"}, wait_deadline=T0 + 4)
        h.client.render(resp)
        req_id = req_id_holder[0]
        # Every gateway record traces to the fixture setup or this one
        # client pull — the server opened no conversation of its own.
        req_ids = {r.req_id for r in h.gateway.audit}
        self.assertEqual(req_ids, {"fixture-k1", req_id, "log-0"})
        # No surface received anything it did not pull for.
        self.assertEqual(h.client2.received, [])
        self.assertEqual(len(h.client.received), 1)


# ---------------------------------------------------------- denial audit

class TestDenialAudit(PullTestBase):
    def test_denials_in_log_verify(self):
        h = self.h
        # Two refusals: bad signature, then a malformed (unsigned) request.
        env = h.client._request_envelope({"key": "k1"}, "r1")
        bad = json.loads(json.dumps(env))
        bad["content"]["query"] = {"key": "evil"}
        h.gateway.pull(h.client, Plane.CONTROL,
                       {"request": bad,
                        "req_id": bad["content"]["req_id"]},
                       key=h.client.key)
        h.gateway.pull(h.client, Plane.CONTROL,
                       {"request": {}, "req_id": "malformed-1"},
                       key=h.client.key)
        denials = [e for e in h.log.entries
                   if e["content"]["type"] == "DENIAL"]
        self.assertEqual(len(denials), 2)
        self.assertTrue(h.log.verify_chain())

    def test_denial_is_information(self):
        h = self.h
        resp = h.client.pull({"key": "nope"})
        denied = h.client.render(resp)
        self.assertEqual(denied["req_id"], "phone-%d" % h.client.counter)
        self.assertEqual(denied["reason"], "no-data")
        self.assertIn("ts", denied)
        entry = [e for e in h.log.entries
                 if e["content"]["type"] == "DENIAL"][0]
        self.assertEqual(entry["content"]["content"]["reason"], "no-data")

    def test_denial_envelope_shape(self):
        h = self.h
        resp = h.client.pull({"key": "nope"})
        denied = h.client.render(resp)
        # Spec denial envelope: {req_id, reason, ts, seal}.
        self.assertEqual(set(denied), {"req_id", "reason", "ts"})
        self.assertIn("seal", resp)


# ---------------------------------------------------------- plane enforcement

class TestPlaneEnforcement(PullTestBase):
    def test_direct_cross_plane_call_raises(self):
        h = self.h
        with self.assertRaises(PlaneViolation):
            h.client.call(h.server, "serve_pull", {})   # data -> control
        with self.assertRaises(PlaneViolation):
            h.server.call(h.data, "serve_pull", {})     # control -> data
        with self.assertRaises(PlaneViolation):
            h.orch.call(h.gov, "serve_pull", {})        # control -> governance

    def test_gateway_bypass_raises(self):
        h = self.h
        with self.assertRaises(PlaneViolation):
            h.data.serve_pull({"op": "read", "key": "k1"})
        with self.assertRaises(PlaneViolation):
            h.gov.serve_pull({"op": "verify", "key_name": "master",
                              "envelope": {}})
        with self.assertRaises(PlaneViolation):
            h.server.serve_pull({"request": {}})

    def test_all_cross_plane_traffic_uses_gateway(self):
        h = self.h
        h.client.pull({"key": "k1"})
        h.orch.tick()
        self.assertGreater(len(h.gateway.audit), 0)
        for rec in h.gateway.audit:
            self.assertNotEqual(rec.from_plane, rec.to_plane)
            self.assertIn(rec.from_plane, Plane.ALL)
            self.assertIn(rec.to_plane, Plane.ALL)


# ------------------------------------------------------------------- chaos

class TestChaosPartition(PullTestBase):
    def test_partition_client_retries_server_never_chases(self):
        h = self.h
        h.gateway.partition = True
        audit_before = len(h.gateway.audit)
        with self.assertRaises(PartitionError):
            h.client.pull_with_retry({"key": "k1"}, max_attempts=3,
                                     backoff=2)
        self.assertEqual(h.client.attempts, 3)
        self.assertEqual(len(h.gateway.audit), audit_before)
        self.assertEqual(h.server.served_journal, [])
        self.assertEqual(h.server.seen, {})
        # Partition heals: the very next client pull succeeds.
        h.gateway.partition = False
        resp = h.client.pull_with_retry({"key": "k1"}, max_attempts=3)
        self.assertEqual(h.client.render(resp)["body"]["value"], 42)

    def test_five_rules_hold_under_partition(self):
        h = self.h
        h.gateway.partition = True
        with self.assertRaises(PartitionError):
            h.client.pull_with_retry({"key": "k1"}, max_attempts=2)
        h.gateway.partition = False
        resp = h.client.pull({"key": "k1"})
        h.client.render(resp)
        # Force a denial under the healed partition, then check all rules.
        env = h.client._request_envelope({"key": "k1"}, "r1")
        bad = json.loads(json.dumps(env))
        bad["content"]["query"] = {"key": "evil"}
        req_id = bad["content"]["req_id"]
        h.gateway.pull(h.client, Plane.CONTROL,
                       {"request": bad, "req_id": req_id}, key=h.client.key)
        self.five_rules_hold(h, denial_req_id=req_id)


class TestChaosReplay(PullTestBase):
    def _send_raw(self, h, req_env):
        return h.gateway.pull(
            h.client, Plane.CONTROL,
            {"request": req_env, "req_id": req_env["content"]["req_id"]},
            key=h.client.key)

    def test_replay_is_idempotent_single_effect(self):
        h = self.h
        env = h.client._request_envelope({"key": "k1"}, "r1")
        req_id = env["content"]["req_id"]
        r1 = self._send_raw(h, env)
        r2 = self._send_raw(h, env)  # identical bytes, resent
        inner1 = r1["content"]["response"]
        inner2 = r2["content"]["response"]
        # Identical sealed bytes back...
        self.assertEqual(seal.canonical(inner1), seal.canonical(inner2))
        self.assertTrue(r2["content"].get("duplicate"))
        # ...and exactly one effect: one data read, one log entry.
        self.assertEqual(h.data.read_counts.get("k1"), 1)
        evidenced = [e for e in h.log.entries
                     if e["content"]["type"] == "EVIDENCE"
                     and e["content"]["content"].get("req_id") == req_id]
        self.assertEqual(len(evidenced), 1)
        self.assertTrue(h.log.verify_chain())

    def test_req_id_reuse_with_different_bytes_is_denied(self):
        h = self.h
        env1 = h.client._request_envelope({"key": "k1"}, "r1")
        req_id = env1["content"]["req_id"]
        self._send_raw(h, env1)
        # Same req_id, different bytes, validly re-sealed.
        h.client.clock.advance(5)
        env2 = h.client._request_envelope({"key": "k1"}, "r1")
        env2["content"]["req_id"] = req_id
        env2 = seal.make_envelope(h.client.key, env2["content"],
                                  env2["origin"], env2["ts"])
        r2 = self._send_raw(h, env2)
        inner2 = r2["content"]["response"]
        self.assertTrue(seal.verify_envelope(h.client.key, inner2))
        self.assertEqual(h.client.render(inner2)["reason"], "req-id-reuse")

    def test_five_rules_hold_under_replay(self):
        h = self.h
        env = h.client._request_envelope({"key": "k1"}, "r1")
        self._send_raw(h, env)
        self._send_raw(h, env)
        bad = json.loads(json.dumps(h.client._request_envelope(
            {"key": "k1"}, "r1")))
        bad["content"]["query"] = {"key": "evil"}
        req_id = bad["content"]["req_id"]
        self._send_raw(h, bad)
        self.five_rules_hold(h, denial_req_id=req_id)


class TestChaosSkew(PullTestBase):
    def test_stale_requests_refused_with_sealed_denial(self):
        h = self.h
        for delta in (-(MAX_SKEW + 1), MAX_SKEW + 1):
            h.client.clock.t = T0 + delta
            resp = h.client.pull({"key": "k1"})
            self.assertTrue(seal.verify_envelope(h.client.key, resp))
            denied = h.client.render(resp)
            self.assertEqual(denied["reason"], "stale-request",
                             "delta=%d" % delta)
        denials = [e for e in h.log.entries
                   if e["content"]["type"] == "DENIAL"]
        self.assertEqual(len(denials), 2)
        self.assertTrue(h.log.verify_chain())

    def test_fresh_requests_accepted(self):
        h = self.h
        for delta in (-MAX_SKEW, 0, MAX_SKEW):
            h.client.clock.t = T0 + delta
            resp = h.client.pull({"key": "k1"})
            content = h.client.render(resp)
            self.assertEqual(content["body"]["value"], 42, "delta=%d" % delta)

    def test_five_rules_hold_under_skew(self):
        h = self.h
        h.client.clock.t = T0 - (MAX_SKEW + 1)
        stale = h.client.pull({"key": "k1"})
        stale_id = h.client.render(stale)["req_id"]
        h.client.clock.t = T0
        fresh = h.client.pull({"key": "k1"})
        h.client.render(fresh)
        h.client.trust(fresh)
        self.five_rules_hold(h, denial_req_id=stale_id)


# ------------------------------------------------------- orchestrator loop

class TestOrchestratorLoop(PullTestBase):
    def test_tick_runs_five_phases_in_order(self):
        h = self.h
        h.orch.tick()
        self.assertEqual(h.orch.phases_run,
                         ["serve", "sense", "queue", "review", "maintain"])

    def test_phases_do_their_jobs(self):
        h = self.h
        resp = h.client.pull({"key": "k1"})
        req_id = h.client.render(resp)["req_id"]
        for v in (10.0, 11.0, 9.0, 50.0):  # the last one is a surprise
            h.push_sample(v)
        h.orch.leases = {"engine-brief": T0 + 30}
        for _ in range(4):  # SENSE ingests one sample per tick
            h.orch.tick()
        # SERVE drained the journal into the pipeline...
        self.assertEqual(h.server.served_journal, [])
        # ...SENSE updated the baseline and deep-pulled on surprise...
        self.assertEqual(h.orch.baseline["count"], 4)
        surprises = [e for e in h.log.entries
                     if e["content"]["type"] == "EVIDENCE"
                     and e["content"]["content"].get("surprise")]
        self.assertEqual(len(surprises), 1)
        deep_pulls = [r for r in h.gateway.audit
                      if r.req_id.startswith("sense-deep-")]
        self.assertEqual(len(deep_pulls), 1)
        # ...QUEUE briefed the engine for the pulled work...
        self.assertEqual(len(h.orch.engine_briefs), 1)
        self.assertEqual(h.orch.engine_briefs[0]["req_id"], req_id)
        # ...REVIEW checked provenance/contract/boundary...
        self.assertEqual(len(h.orch.verdicts), 1)
        verdict = h.orch.verdicts[0]
        self.assertTrue(verdict["provenance"])
        self.assertTrue(verdict["contract"])
        self.assertTrue(verdict["boundary"])
        self.assertTrue(verdict["trusted"])
        # ...MAINTAIN renewed the lease and updated the scorecard.
        self.assertEqual(h.orch.leases["engine-brief"], T0 + 600)
        self.assertEqual(h.orch.scorecards["phone"]["served"], 1)
        self.assertTrue(h.log.verify_chain())

    def test_loop_never_pushes(self):
        h = self.h
        for _ in range(3):
            h.orch.tick()
        # No surface received anything it did not pull for.
        self.assertEqual(h.client.received, [])
        self.assertEqual(h.client2.received, [])
        # Everything the loop did was a pull of data or governance.
        for rec in h.gateway.audit:
            self.assertIn(rec.to_plane, (Plane.DATA, Plane.GOVERNANCE))
        for obj in (h.orch, h.server):
            for name in PUSH_LIKE:
                self.assertFalse(hasattr(obj, name))


if __name__ == "__main__":
    unittest.main(verbosity=2)
