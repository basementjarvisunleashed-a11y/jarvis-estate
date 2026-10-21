"""Phase 4 — Zero-knowledge proofs: REFERENCE prover/verifier tests.

Covers each of S1/S2/S3: round-trip, false-statement refusal, tampered
proof, superseded circuit, stale proof, replay, plus registry tests and
honest §4.4 budget measurements (written to measurements.json).

REFERENCE — NOT PRODUCTION CRYPTOGRAPHY (see proofs.py).
"""
import copy
import json
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import seal
from common.clock import FakeClock
from phase4 import proofs
from phase4.proofs import Verifier, ProveError
from phase4.registry import StatementRegistry, RegistryError

MEASUREMENTS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "measurements.json")
MASTER = b"4" * 32  # TEST key only

DESCRIPTORS = {
    "S1": "This value exceeds threshold T in sealed baseline B "
          "(variance-gate alerts without exposing the baseline).",
    "S2": "An approval exists for intent digest D "
          "(actuation without re-showing the approval).",
    "S3": "This payload satisfies policy P "
          "(execution without exposing the payload).",
}


def make_registry():
    reg = StatementRegistry()
    for sid, desc in DESCRIPTORS.items():
        reg.register(sid, 1, desc)
    return reg


def register_demo_policy():
    proofs.register_policy(
        "demo-policy",
        lambda payload: (isinstance(payload, dict)
                         and payload.get("action") == "unlock"
                         and isinstance(payload.get("level"), int)
                         and payload["level"] <= 3))


class Fixtures:
    """True/false (public, witness, context) triples per statement."""

    def __init__(self):
        self.clock = FakeClock()
        register_demo_policy()
        # S1
        self.s1_bd = seal.sha256_hex(b"sealed-baseline-B")
        self.s1_public = {"threshold": 100, "baseline_digest": self.s1_bd}
        self.s1_true = {"value": 150, "baseline_digest": self.s1_bd}
        self.s1_false = {"value": 50, "baseline_digest": self.s1_bd}
        # S2
        self.intent = {"action": "actuate", "target": "arm", "effect": "move"}
        self.d = seal.intent_digest(self.intent)
        self.approval = seal.make_envelope(
            MASTER, {"intent_digest": self.d, "approver": "governance",
                     "decision": "approve"}, "governance", self.clock.now())
        self.s2_public = {"intent_digest": self.d}
        self.s2_true = {"intent_digest": self.d, "approval": self.approval}
        bad_approval = seal.make_envelope(
            MASTER, {"intent_digest": "00" * 32, "approver": "governance",
                     "decision": "approve"}, "governance", self.clock.now())
        self.s2_false = {"intent_digest": "00" * 32, "approval": bad_approval}
        self.s2_ctx = {"seal_key": MASTER}
        # S3
        self.s3_public = {"policy_id": "demo-policy",
                          "policy_digest": proofs.policy_digest("demo-policy")}
        self.s3_true = {"policy_id": "demo-policy",
                        "payload": {"action": "unlock", "level": 2}}
        self.s3_false = {"policy_id": "demo-policy",
                         "payload": {"action": "unlock", "level": 9}}

    def triple(self, sid):
        return {
            "S1": (self.s1_public, self.s1_true, self.s1_false, None),
            "S2": (self.s2_public, self.s2_true, self.s2_false, self.s2_ctx),
            "S3": (self.s3_public, self.s3_true, self.s3_false, None),
        }[sid]


class Phase4Case(unittest.TestCase):
    def setUp(self):
        self.fx = Fixtures()
        self.reg = make_registry()

    def prove_true(self, sid):
        public, witness, _, ctx = self.fx.triple(sid)
        return proofs.prove(sid, 1, public, witness, self.reg,
                            self.fx.clock, context=ctx)

    def fresh_verifier(self):
        return Verifier(self.reg, self.fx.clock)


class TestRoundTrip(Phase4Case):
    def test_reference_tag_present(self):
        for sid in ("S1", "S2", "S3"):
            p = self.prove_true(sid)
            self.assertEqual(p["reference"], proofs.REFERENCE_TAG)

    def test_s1_roundtrip(self):
        self.assertTrue(self.fresh_verifier().verify(self.prove_true("S1")))

    def test_s2_roundtrip(self):
        self.assertTrue(self.fresh_verifier().verify(self.prove_true("S2")))

    def test_s3_roundtrip(self):
        self.assertTrue(self.fresh_verifier().verify(self.prove_true("S3")))

    def test_verifier_learns_only_one_bit(self):
        # The proof carries no witness material: no value, payload, or
        # approval content on the wire — only digests and the bit.
        p = self.prove_true("S1")
        wire = json.dumps(p)
        self.assertNotIn("150", wire)
        p2 = self.prove_true("S3")
        wire2 = json.dumps(p2)
        self.assertNotIn("unlock", wire2)


class TestFalseStatement(Phase4Case):
    def test_prover_refuses_false_s1(self):
        public, _, false_w, _ = self.fx.triple("S1")
        with self.assertRaises(ProveError):
            proofs.prove("S1", 1, public, false_w, self.reg, self.fx.clock)

    def test_prover_refuses_false_s2(self):
        public, _, false_w, ctx = self.fx.triple("S2")
        with self.assertRaises(ProveError):
            proofs.prove("S2", 1, public, false_w, self.reg, self.fx.clock,
                         context=ctx)

    def test_prover_refuses_false_s3(self):
        public, _, false_w, _ = self.fx.triple("S3")
        with self.assertRaises(ProveError):
            proofs.prove("S3", 1, public, false_w, self.reg, self.fx.clock)

    def test_prover_refuses_s2_without_seal_key(self):
        public, witness, _, _ = self.fx.triple("S2")
        with self.assertRaises(ProveError):
            proofs.prove("S2", 1, public, witness, self.reg, self.fx.clock,
                         context=None)

    def test_prover_refuses_tampered_approval_seal(self):
        public, witness, _, ctx = self.fx.triple("S2")
        bad = copy.deepcopy(witness)
        bad["approval"]["content"]["decision"] = "deny"  # breaks the seal
        with self.assertRaises(ProveError):
            proofs.prove("S2", 1, public, bad, self.reg, self.fx.clock,
                         context=ctx)

    def test_wrong_witness_digest_fails_verify(self):
        # A proof whose committed witness was swapped for a false one:
        # the commitment no longer opens -> verify fails.
        for sid in ("S1", "S2", "S3"):
            p = self.prove_true(sid)
            p["witness_digest"] = "ff" * 32
            self.assertFalse(self.fresh_verifier().verify(p),
                             "wrong witness digest accepted for %s" % sid)

    def test_wrong_public_params_fail_verify(self):
        # Public statement is bound in the Fiat-Shamir transcript.
        p = self.prove_true("S1")
        p["public"] = {"threshold": 1000,
                       "baseline_digest": self.fx.s1_bd}
        self.assertFalse(self.fresh_verifier().verify(p))


class TestTamperedProof(Phase4Case):
    def test_mutated_response_fails(self):
        for sid in ("S1", "S2", "S3"):
            p = self.prove_true(sid)
            mo = p["masked_opening"]
            # flip the last hex digit
            p["masked_opening"] = mo[:-1] + ("0" if mo[-1] != "0" else "1")
            self.assertFalse(self.fresh_verifier().verify(p),
                             "mutated response accepted for %s" % sid)

    def test_mutated_commitment_fails(self):
        p = self.prove_true("S1")
        p["commitment"] = "00" * 32
        self.assertFalse(self.fresh_verifier().verify(p))

    def test_mutated_challenge_fails(self):
        p = self.prove_true("S1")
        p["challenge"] = "00" * 32
        self.assertFalse(self.fresh_verifier().verify(p))

    def test_cleared_attestation_fails(self):
        p = self.prove_true("S1")
        p["attestation"] = False
        self.assertFalse(self.fresh_verifier().verify(p))

    def test_garbage_proof_fails_closed(self):
        v = self.fresh_verifier()
        self.assertFalse(v.verify({}))
        self.assertFalse(v.verify({"statement_id": "S1"}))
        self.assertFalse(v.verify(None))


class TestSupersededCircuit(Phase4Case):
    def test_old_version_rejected_after_supersede(self):
        for sid in ("S1", "S2", "S3"):
            reg = make_registry()
            fx = Fixtures()
            public, witness, _, ctx = fx.triple(sid)
            old = proofs.prove(sid, 1, public, witness, reg, fx.clock,
                               context=ctx)
            self.assertTrue(Verifier(reg, fx.clock).verify(old))
            reg.supersede(sid, 2)
            self.assertFalse(Verifier(reg, fx.clock).verify(old),
                             "superseded v1 proof accepted for %s" % sid)

    def test_prover_refuses_superseded_version(self):
        self.reg.supersede("S1", 2)
        public, witness, _, _ = self.fx.triple("S1")
        with self.assertRaises(ProveError):
            proofs.prove("S1", 1, public, witness, self.reg, self.fx.clock)

    def test_new_version_verifies(self):
        self.reg.supersede("S2", 2)
        public, witness, _, ctx = self.fx.triple("S2")
        p = proofs.prove("S2", 2, public, witness, self.reg, self.fx.clock,
                         context=ctx)
        self.assertEqual(p["circuit_version"], 2)
        self.assertTrue(self.fresh_verifier().verify(p))

    def test_unknown_statement_rejected(self):
        public, witness, _, _ = self.fx.triple("S1")
        with self.assertRaises(ProveError):
            proofs.prove("S9", 1, public, witness, self.reg, self.fx.clock)


class TestFreshness(Phase4Case):
    def test_fresh_proof_accepted(self):
        self.assertTrue(self.fresh_verifier().verify(self.prove_true("S1")))

    def test_boundary_300s_accepted(self):
        p = self.prove_true("S1")
        self.fx.clock.advance(300)
        self.assertTrue(self.fresh_verifier().verify(p))

    def test_stale_301s_rejected(self):
        for sid in ("S1", "S2", "S3"):
            fx = Fixtures()
            reg = make_registry()
            public, witness, _, ctx = fx.triple(sid)
            p = proofs.prove(sid, 1, public, witness, reg, fx.clock,
                             context=ctx)
            fx.clock.advance(301)
            self.assertFalse(Verifier(reg, fx.clock).verify(p),
                             "stale proof accepted for %s" % sid)

    def test_future_ts_outside_window_rejected(self):
        p = self.prove_true("S1")
        p["ts"] = p["ts"] + 301  # breaks challenge binding too -> reject
        self.assertFalse(self.fresh_verifier().verify(p))


class TestReplay(Phase4Case):
    def test_same_nonce_twice_rejected(self):
        for sid in ("S1", "S2", "S3"):
            fx = Fixtures()
            reg = make_registry()
            public, witness, _, ctx = fx.triple(sid)
            p = proofs.prove(sid, 1, public, witness, reg, fx.clock,
                             context=ctx)
            v = Verifier(reg, fx.clock)
            self.assertTrue(v.verify(p))
            self.assertFalse(v.verify(p),
                             "replayed proof accepted for %s" % sid)

    def test_distinct_proofs_both_accepted(self):
        v = self.fresh_verifier()
        self.assertTrue(v.verify(self.prove_true("S1")))
        self.assertTrue(v.verify(self.prove_true("S1")))


class TestRegistry(unittest.TestCase):
    def test_register_and_lookup(self):
        reg = StatementRegistry()
        reg.register("S1", 1, "desc")
        self.assertEqual(reg.current_version("S1"), 1)
        self.assertEqual(reg.descriptor("S1"), "desc")
        self.assertTrue(reg.is_current("S1", 1))
        self.assertFalse(reg.is_current("S1", 2))

    def test_duplicate_register_rejected(self):
        reg = StatementRegistry()
        reg.register("S1", 1, "desc")
        with self.assertRaises(RegistryError):
            reg.register("S1", 1, "other")

    def test_supersede_moves_version(self):
        reg = StatementRegistry()
        reg.register("S1", 1, "desc")
        reg.supersede("S1", 2)
        self.assertEqual(reg.current_version("S1"), 2)
        self.assertTrue(reg.is_current("S1", 2))
        self.assertFalse(reg.is_current("S1", 1))
        self.assertEqual(reg.history("S1"), [1, 1])

    def test_supersede_unknown_rejected(self):
        reg = StatementRegistry()
        with self.assertRaises(RegistryError):
            reg.supersede("S9", 2)

    def test_supersede_non_increasing_rejected(self):
        reg = StatementRegistry()
        reg.register("S1", 2, "desc")
        with self.assertRaises(RegistryError):
            reg.supersede("S1", 2)
        with self.assertRaises(RegistryError):
            reg.supersede("S1", 1)

    def test_unknown_statement_not_current(self):
        reg = StatementRegistry()
        self.assertFalse(reg.is_current("S9", 1))
        with self.assertRaises(RegistryError):
            reg.current_version("S9")

    def test_exactly_three_statements_registered(self):
        reg = make_registry()
        self.assertEqual(reg.statement_ids(), ["S1", "S2", "S3"])


class TestBudgets(Phase4Case):
    N = 200

    def measure(self, sid):
        public, witness, _, ctx = self.fx.triple(sid)
        reg = make_registry()
        clock = FakeClock()
        # warm up
        p0 = proofs.prove(sid, 1, public, witness, reg, clock, context=ctx)
        nbytes = proofs.proof_size_bytes(p0)
        v = Verifier(reg, clock)
        t0 = time.perf_counter()
        for _ in range(self.N):
            proofs.prove(sid, 1, public, witness, reg, clock, context=ctx)
        prove_ms = (time.perf_counter() - t0) / self.N * 1000.0
        v.reset_replay_cache()
        t0 = time.perf_counter()
        for _ in range(self.N):
            p = proofs.prove(sid, 1, public, witness, reg, clock, context=ctx)
            assert v.verify(p)
        verify_ms = (time.perf_counter() - t0) / self.N * 1000.0
        # verify_ms above includes proving; measure verify alone:
        proofs_list = [proofs.prove(sid, 1, public, witness, reg, clock,
                                    context=ctx) for _ in range(self.N)]
        v.reset_replay_cache()
        t0 = time.perf_counter()
        for p in proofs_list:
            assert v.verify(p)
        verify_only_ms = (time.perf_counter() - t0) / self.N * 1000.0
        return {"prove_ms": prove_ms, "verify_ms": verify_only_ms,
                "proof_bytes": nbytes, "iterations": self.N}

    def test_measurements_within_budgets(self):
        results = {}
        for sid in ("S1", "S2", "S3"):
            m = self.measure(sid)
            results[sid] = m
            print("MEASURE %s prove_ms=%.3f verify_ms=%.3f proof_bytes=%d"
                  % (sid, m["prove_ms"], m["verify_ms"], m["proof_bytes"]))
            self.assertLessEqual(
                m["prove_ms"], proofs.PROVING_TIME_BUDGET_S * 1000.0,
                "proving budget exceeded for %s" % sid)
            self.assertLessEqual(
                m["verify_ms"], proofs.VERIFY_TIME_BUDGET_MS,
                "verification budget exceeded for %s" % sid)
            self.assertLessEqual(
                m["proof_bytes"], proofs.PROOF_SIZE_BUDGET_BYTES,
                "STARK proof-size budget exceeded for %s" % sid)
        with open(MEASUREMENTS_PATH, "w", encoding="utf-8") as fh:
            json.dump({
                "reference": proofs.REFERENCE_TAG,
                "freshness_window_s": proofs.FRESHNESS_WINDOW_S,
                "budgets": {
                    "proving_time_s": proofs.PROVING_TIME_BUDGET_S,
                    "verify_time_ms": proofs.VERIFY_TIME_BUDGET_MS,
                    "proof_size_stark_bytes": proofs.PROOF_SIZE_BUDGET_BYTES,
                    "proof_size_snark_bytes": proofs.SNARK_SIZE_BUDGET_BYTES,
                },
                "statements": results,
            }, fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
