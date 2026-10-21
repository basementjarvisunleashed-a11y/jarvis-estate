"""Phase 3 — Complete handshake (paper Section 5).

Tests the six steps, the Section 5.5 worked trace, the five Section 5.4
failure behaviours, the state machine, digest binding, nonce burn, and
plane enforcement. The suite acts as auditor: it holds the TEST ceremony
keys and verifies every artifact seal.
"""
import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import seal, planes
from common.clock import FakeClock
from common.seal import SealError
from phase3.handshake import (
    Harness, Handshake,
    HandshakeError, InvalidTransition, ExpiredError, CardExpired,
    CardInvalid, OfflineError, DigestMismatch, TokenReplay, TokenInvalid,
    TRACE_T0, TRACE_INTENT, CARD_TTL,
)

MUTATED_INTENT = {
    "target": {"kind": "people", "count": 5},   # 4 -> 5: D must change
    "effect": "send_message",
    "content": "Running 10 min late",
}


def fresh_harness():
    return Harness(clock=FakeClock(TRACE_T0))


class Phase3Base(unittest.TestCase):
    def setUp(self):
        self.h = fresh_harness()

    def tearDown(self):
        if getattr(self.h, "_tmp", None):
            shutil.rmtree(self.h._tmp, ignore_errors=True)

    def drive_to_authorized(self):
        """Steps 1-4 at the trace timestamps. Returns (hs, token_env)."""
        h, ck = self.h, self.h.clock
        hs = h.step1_propose(dict(TRACE_INTENT))
        ck.advance(2)
        card_env = h.step2_present(hs)
        ck.advance(5)
        h.step3_decide(hs, card_env)
        ck.advance(1)
        token_env = h.step4_mint(hs)
        self.assertEqual(hs.state, "AUTHORIZED")
        return hs, token_env

    def drive_to_evidenced(self):
        hs, token_env = self.drive_to_authorized()
        h, ck = self.h, self.h.clock
        ck.advance(1)
        actuation = h.step5_execute(
            hs, token_env, {"intent": dict(TRACE_INTENT), "action": "send"})
        ck.advance(2)
        h.step6_seal_evidence(hs, actuation, "Sent to 4 people · 09:38")
        self.assertEqual(hs.state, "EVIDENCED")
        return hs, token_env


class TestHappyPath(Phase3Base):
    def test_six_steps_with_seal_verification_at_every_step(self):
        h, ck, K = self.h, self.h.clock, self.h.keys
        D = seal.intent_digest(TRACE_INTENT)

        # Step 1: intent formation — verifier is the intent log lease.
        hs = h.step1_propose(dict(TRACE_INTENT))
        self.assertEqual(hs.state, "PROPOSED")
        self.assertTrue(seal.verify_envelope(K["master"], hs.lease))
        self.assertEqual(hs.lease["content"]["content"]["digest"], D)
        self.assertEqual(hs.digest, D)

        # Step 2: presentation — verifier is the device seal check.
        ck.advance(2)
        card_env = h.step2_present(hs)
        self.assertEqual(hs.state, "PRESENTED")
        self.assertTrue(
            seal.verify_envelope(K["surface:watch"], card_env))
        card = card_env["content"]
        self.assertEqual(card["intent"], TRACE_INTENT)  # exact intent
        self.assertEqual(card["intent_digest"], D)
        self.assertEqual(card["expires"], ck.now() + CARD_TTL)

        # Step 3: signed decision — verifier is the orchestrator.
        ck.advance(5)
        decision_env = h.step3_decide(hs, card_env)
        self.assertEqual(hs.state, "DECIDED")
        self.assertTrue(
            seal.verify_envelope(K["surface:watch"], decision_env))
        dec = decision_env["content"]
        self.assertEqual(
            (dec["decision"], dec["intent_digest"], dec["expiry"]),
            ("approve", D, card["expires"]))

        # Step 4: token minting — verifier is the trust root.
        ck.advance(1)
        token_env = h.step4_mint(hs)
        self.assertEqual(hs.state, "AUTHORIZED")
        self.assertTrue(
            seal.verify_envelope(K["surface:edge"], token_env))
        tok = token_env["content"]
        self.assertEqual(tok["intent_digest"], D)
        self.assertEqual(tok["caveats"], [{"kind": "intent_digest",
                                           "value": D}])
        self.assertEqual(tok["expiry"], card["expires"])
        self.assertEqual(len(tok["nonce"]), 32)

        # Step 5: actuation check — verifier is the edge token verify.
        ck.advance(1)
        nonce = tok["nonce"]
        self.assertTrue(h.nonce_store.is_fresh(nonce))
        actuation = h.step5_execute(
            hs, token_env, {"intent": dict(TRACE_INTENT), "action": "send"})
        self.assertEqual(actuation["intent_digest"], D)
        self.assertFalse(h.nonce_store.is_fresh(nonce))  # burned on use
        self.assertIn(nonce, h.nonce_store.burned)

        # Step 6: sealed evidence — verifier is the intent log seal.
        ck.advance(2)
        entry = h.step6_seal_evidence(hs, actuation,
                                      "Sent to 4 people · 09:38")
        self.assertEqual(hs.state, "EVIDENCED")
        self.assertTrue(seal.verify_envelope(K["master"], entry))
        self.assertEqual(entry["content"]["content"]["summary"],
                         "Sent to 4 people · 09:38")
        self.assertTrue(h.intent_log.verify_chain())

        # Tail of the trace: the phone pulls the packet and verifies it.
        packet = h.phone.pull_packet(entry["content"]["seq"])
        self.assertEqual(packet["summary"], "Sent to 4 people · 09:38")
        self.assertEqual(packet["intent_digest"], D)


class TestSection55Trace(Phase3Base):
    def test_worked_trace_reproduces_exactly(self):
        h, K = self.h, self.h.keys
        report = h.run_trace_55()

        # D is computed by the implementation, never hardcoded.
        self.assertEqual(report["digest"],
                         seal.intent_digest(TRACE_INTENT))
        self.assertEqual(len(report["digest"]), 64)

        # Exact timestamps (America/Toronto).
        self.assertEqual(report["proposed_ts"], TRACE_T0)            # 09:38:00
        self.assertEqual(report["card"]["presented_ts"], TRACE_T0 + 2)
        self.assertEqual(report["card"]["expires"], TRACE_T0 + 602)  # 09:48
        self.assertEqual(report["decision"]["signed_ts"], TRACE_T0 + 7)
        self.assertEqual(
            (report["decision"]["decision"],
             report["decision"]["intent_digest"],
             report["decision"]["expiry"]),
            ("approve", report["digest"], TRACE_T0 + 602))
        self.assertEqual(report["token"]["minted_ts"], TRACE_T0 + 8)
        self.assertEqual(report["token"]["intent_digest"], report["digest"])
        self.assertEqual(report["token"]["expiry"], TRACE_T0 + 602)
        self.assertEqual(report["actuation"]["executed_ts"], TRACE_T0 + 9)
        self.assertEqual(report["evidence"]["sealed_ts"], TRACE_T0 + 11)
        self.assertEqual(report["evidence"]["summary"],
                         "Sent to 4 people · 09:38")
        self.assertEqual(report["evidence"]["packet_summary"],
                         "Sent to 4 people · 09:38")
        self.assertEqual(report["final_state"], "EVIDENCED")
        self.assertEqual(
            [s for s, _ts in report["history"]],
            ["PROPOSED", "PRESENTED", "DECIDED", "AUTHORIZED", "EVIDENCED"])

        # Every artifact seal verifies with the ceremony keys.
        arts = report["artifacts"]
        for key_name, env in (
                ("master", arts["lease"]),
                ("surface:watch", arts["card_env"]),
                ("surface:watch", arts["decision_env"]),
                ("surface:edge", arts["token_env"]),
                ("master", arts["entry"])):
            self.assertTrue(seal.verify_envelope(K[key_name], env),
                            "seal failed for %s" % key_name)
        self.assertTrue(h.intent_log.verify_chain())

        # Six steps, each verified by a different party than the actor.
        verifiers = [s["verifier"] for s in h.steps]
        self.assertEqual(len(h.steps), 6)
        self.assertEqual(len(set(verifiers)), 6)


class TestSection54Failures(Phase3Base):
    def test_intent_mutates_mid_presentation(self):
        """Card invalidates; a new card is issued for the new digest."""
        h, ck = self.h, self.h.clock
        hs = h.step1_propose(dict(TRACE_INTENT))
        ck.advance(2)
        old_card = h.step2_present(hs)
        D1 = hs.digest

        h.orch.mutate_intent(hs, dict(MUTATED_INTENT))
        D2 = hs.digest
        self.assertNotEqual(D1, D2)
        self.assertEqual(hs.state, "PROPOSED")  # back for a fresh pull
        self.assertFalse(hs.card_valid)

        # The old card no longer binds: the device refuses to sign on it.
        with self.assertRaises(CardInvalid):
            h.watch.tap_approve(old_card)

        # A new card is issued for the mutated intent.
        ck.advance(1)
        new_card_env = h.step2_present(hs)
        new_card = h.watch.present(new_card_env)
        self.assertEqual(new_card["intent_digest"], D2)
        self.assertEqual(new_card["intent"], MUTATED_INTENT)
        self.assertTrue(seal.verify_envelope(
            h.keys["surface:watch"], new_card_env))
        self.assertEqual(hs.state, "PRESENTED")

    def test_card_expiry_disables_controls_and_offers_representation(self):
        h, ck = self.h, self.h.clock
        hs = h.step1_propose(dict(TRACE_INTENT))
        ck.advance(2)
        card_env = h.step2_present(hs)
        expiry = hs.card_body["expires"]

        ck.advance(CARD_TTL + 5)  # past 09:48
        self.assertGreater(ck.now(), expiry)
        # Controls disabled: the tap is refused.
        with self.assertRaises(CardExpired):
            h.watch.tap_approve(card_env)
        # Expiry lapses the handshake.
        with self.assertRaises(ExpiredError):
            hs.check_expiry(ck.now())
        self.assertEqual(hs.state, "LAPSED")
        self.assertFalse(hs.controls_enabled)

        # Re-presentation is offered: a fresh handshake over the same
        # intent, same D, new expiry.
        hs2 = h.orch.re_present(hs, "watch")
        self.assertEqual(hs2.digest, hs.digest)
        self.assertEqual(hs2.state, "PROPOSED")
        card2_env = h.step2_present(hs2)
        card2 = h.watch.present(card2_env)
        self.assertEqual(card2["intent_digest"], hs.digest)
        self.assertEqual(card2["expires"], ck.now() + CARD_TTL)
        self.assertGreater(card2["expires"], expiry)
        self.assertTrue(seal.verify_envelope(
            h.keys["surface:watch"], card2_env))

    def test_offline_tap_records_nothing(self):
        """Offline tap: NO local approval recorded, ever."""
        h, ck = self.h, self.h.clock
        hs = h.step1_propose(dict(TRACE_INTENT))
        ck.advance(2)
        card_env = h.step2_present(hs)
        log_len = len(h.intent_log)

        h.watch.offline = True
        with self.assertRaises(OfflineError):
            h.watch.tap_approve(card_env)

        # NOTHING is recorded: no decision on the device, no log entry,
        # no state change.
        self.assertEqual(h.watch.outbox, [])
        self.assertEqual(len(h.intent_log), log_len)
        self.assertEqual(hs.state, "PRESENTED")
        self.assertIsNone(hs.decision)
        # And the orchestrator finds no decision to pull.
        with self.assertRaises(HandshakeError):
            h.orch.pull_decision(hs)

    def test_digest_mismatch_at_edge(self):
        """Refused; denial sealed; re-propose required."""
        h, ck = self.h, self.h.clock
        hs, token_env = self.drive_to_authorized()
        nonce = hs.token_body["nonce"]

        tampered = {"intent": dict(MUTATED_INTENT), "action": "send"}
        with self.assertRaises(DigestMismatch):
            h.edge.execute(token_env, tampered)

        # The denial is sealed in the intent log.
        counts = h.log_counts()
        self.assertEqual(counts.get("DENIAL"), 1)
        denial = h.intent_log.entries[-1]
        self.assertTrue(seal.verify_envelope(h.keys["master"], denial))
        self.assertTrue(h.intent_log.verify_chain())

        # The handshake is NOT evidenced; the nonce did NOT burn on a
        # refused attempt, so the legitimate work order can still run.
        self.assertEqual(hs.state, "AUTHORIZED")
        self.assertTrue(h.nonce_store.is_fresh(nonce))

    def test_token_replay_refused_and_incident_logged(self):
        hs, token_env = self.drive_to_evidenced()
        h = self.h
        nonce = hs.token_body["nonce"]
        self.assertIn(nonce, h.nonce_store.burned)

        with self.assertRaises(TokenReplay):
            h.edge.execute(token_env,
                           {"intent": dict(TRACE_INTENT), "action": "send"})

        counts = h.log_counts()
        self.assertEqual(counts.get("DENIAL"), 1)
        incident = h.intent_log.entries[-1]
        self.assertTrue(seal.verify_envelope(h.keys["master"], incident))
        self.assertEqual(incident["content"]["content"]["kind"], "replay")
        self.assertTrue(h.intent_log.verify_chain())
        self.assertEqual(hs.state, "EVIDENCED")  # unchanged


class TestStateMachine(Phase3Base):
    def test_legal_transitions_in_order(self):
        h, ck = self.h, self.h.clock
        hs = h.step1_propose(dict(TRACE_INTENT))
        self.assertEqual(hs.state, "PROPOSED")
        ck.advance(2)
        card_env = h.step2_present(hs)
        self.assertEqual(hs.state, "PRESENTED")
        ck.advance(5)
        h.step3_decide(hs, card_env)
        self.assertEqual(hs.state, "DECIDED")
        ck.advance(1)
        token_env = h.step4_mint(hs)
        self.assertEqual(hs.state, "AUTHORIZED")
        ck.advance(1)
        actuation = h.step5_execute(
            hs, token_env, {"intent": dict(TRACE_INTENT), "action": "send"})
        self.assertEqual(hs.state, "AUTHORIZED")  # evidence still pending
        ck.advance(2)
        h.step6_seal_evidence(hs, actuation, "Sent to 4 people · 09:38")
        self.assertEqual(hs.state, "EVIDENCED")

    def test_lapsed_on_expiry_from_proposed(self):
        h, ck = self.h, self.h.clock
        hs = h.step1_propose(dict(TRACE_INTENT))
        ck.advance(CARD_TTL + 1)
        with self.assertRaises(ExpiredError):
            hs.check_expiry(ck.now())
        self.assertEqual(hs.state, "LAPSED")

    def test_lapsed_on_expiry_from_presented(self):
        h, ck = self.h, self.h.clock
        hs = h.step1_propose(dict(TRACE_INTENT))
        ck.advance(2)
        h.step2_present(hs)
        ck.advance(CARD_TTL + 1)
        with self.assertRaises(ExpiredError):
            hs.check_expiry(ck.now())
        self.assertEqual(hs.state, "LAPSED")
        # No further transition is possible from LAPSED.
        with self.assertRaises(InvalidTransition):
            h.orch.mint_token(hs, edge="edge")

    def test_lapsed_on_expiry_from_decided(self):
        h, ck = self.h, self.h.clock
        hs = h.step1_propose(dict(TRACE_INTENT))
        ck.advance(2)
        card_env = h.step2_present(hs)
        ck.advance(5)
        h.step3_decide(hs, card_env)
        self.assertEqual(hs.state, "DECIDED")
        ck.advance(CARD_TTL + 1)
        with self.assertRaises(ExpiredError):
            hs.check_expiry(ck.now())
        self.assertEqual(hs.state, "LAPSED")

    def test_no_unpulled_transitions(self):
        h, ck = self.h, self.h.clock
        hs = h.step1_propose(dict(TRACE_INTENT))
        # Nothing advances without its pull.
        self.assertEqual(hs.state, "PROPOSED")
        with self.assertRaises(InvalidTransition):
            h.orch.mint_token(hs, edge="edge")  # DECIDED required
        with self.assertRaises(InvalidTransition):
            hs.on_executed({}, ck.now())   # AUTHORIZED required
        with self.assertRaises(InvalidTransition):
            hs.on_token_minted({}, {}, ck.now())
        # A second card pull finds nothing proposed.
        ck.advance(2)
        h.step2_present(hs)
        with self.assertRaises(HandshakeError):
            h.step2_present(hs)
        # Terminal states accept no transitions.
        hs2, _tok = self.drive_to_authorized()
        with self.assertRaises(InvalidTransition):
            hs2.on_card_issued({}, {}, ck.now())


class TestBinding(Phase3Base):
    def test_mutated_work_order_refused_at_edge(self):
        """Section 5.2: the principal approved D, not the description."""
        h = self.h
        hs, token_env = self.drive_to_authorized()
        D1 = hs.digest
        D2 = seal.intent_digest(MUTATED_INTENT)
        self.assertNotEqual(D1, D2)  # target 4 -> 5 changes D

        with self.assertRaises(DigestMismatch):
            h.edge.execute(token_env,
                           {"intent": dict(MUTATED_INTENT), "action": "send"})
        # The token still binds the original D; nothing burned.
        self.assertEqual(hs.token_body["intent_digest"], D1)
        self.assertTrue(
            h.nonce_store.is_fresh(hs.token_body["nonce"]))

    def test_mint_refuses_mutated_intent_with_old_decision(self):
        h = self.h
        hs, _tok = self.drive_to_authorized()
        # The trust root re-verifies D at mint: a mutated intent with the
        # old signed decision does not mint.
        with self.assertRaises(DigestMismatch):
            h.gateway.pull(
                h.orch, planes.Plane.GOVERNANCE,
                {"query": "mint_token", "decision": hs.decision,
                 "intent": dict(MUTATED_INTENT), "edge": "edge"},
                h.transport_key)


class TestNonceBurn(Phase3Base):
    def test_nonce_burns_on_first_use_only(self):
        h, ck = self.h, self.h.clock
        hs, token_env = self.drive_to_authorized()
        nonce = hs.token_body["nonce"]
        self.assertTrue(h.nonce_store.is_fresh(nonce))
        self.assertNotIn(nonce, h.nonce_store.burned)

        ck.advance(1)
        h.step5_execute(hs, token_env,
                        {"intent": dict(TRACE_INTENT), "action": "send"})
        self.assertIn(nonce, h.nonce_store.burned)
        self.assertFalse(h.nonce_store.is_fresh(nonce))

        # Second use: refused, incident logged.
        with self.assertRaises(TokenReplay):
            h.edge.execute(token_env,
                           {"intent": dict(TRACE_INTENT), "action": "send"})
        self.assertEqual(h.log_counts().get("DENIAL"), 1)


class TestPlaneEnforcement(Phase3Base):
    def test_direct_cross_plane_call_raises(self):
        h = self.h
        # control -> governance
        with self.assertRaises(planes.PlaneViolation):
            h.orch.call(h.watch, "pull_pending_approvals")
        # governance -> control
        with self.assertRaises(planes.PlaneViolation):
            h.watch.call(h.orch, "propose", {}, "watch")
        # data -> governance
        with self.assertRaises(planes.PlaneViolation):
            h.edge.call(h.trust, "serve_pull", {})
        # governance -> data
        with self.assertRaises(planes.PlaneViolation):
            h.trust.call(h.log_server, "serve_pull", {})

    def test_same_plane_via_gateway_raises(self):
        h = self.h
        with self.assertRaises(planes.PlaneViolation):
            h.gateway.pull(h.orch, planes.Plane.CONTROL,
                           {"query": "pending_approvals"},
                           h.transport_key)
        with self.assertRaises(planes.PlaneViolation):
            h.gateway.pull(h.edge, planes.Plane.DATA,
                           {"query": "get_entry", "seq": 0},
                           h.transport_key)

    def test_same_plane_direct_call_allowed(self):
        h = self.h
        # data -> data: edge burns the nonce via the nonce store.
        self.assertFalse(h.edge.call(h.nonce_store, "is_fresh", "nope"))
        # governance -> governance: trust root serves the phone's packet.
        self.assertIsNotNone(h.trust.call(h.watch, "next_decision", "nope"))

    def test_components_declare_exactly_one_plane(self):
        h = self.h
        self.assertEqual(
            {c.plane for c in (h.orch, h.log_server, h.trust, h.watch,
                               h.phone, h.edge, h.nonce_store)},
            {"control", "data", "governance"})
        self.assertEqual(h.orch.plane, "control")
        self.assertEqual(h.trust.plane, "governance")
        self.assertEqual(h.log_server.plane, "data")


if __name__ == "__main__":
    unittest.main()
