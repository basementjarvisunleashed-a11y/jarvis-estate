"""Phase 5 Layer 2 -- Spoofing controls (T-1 fake approval, T-2 fake
source, T-4 mutated intent).

Threats: T-1, T-2, T-4 (threat-catalogue.md sections 2--3).
Controls: C-1...C-9 (control-matrix.md section 2).
Attack trees: AT-1 (fake approval), AT-2 (mutated intent).
Draft sections cited: session-lifecycle.md SL-1...SL-27 (the
device_session_id lifecycle, Q1), capability-matrix.md CM-3 (changed
scope voids approval).

Checks:
- unknown sessions refused before any other check (C-1, SL-3)
- enrollment grants no authority (SL-4)
- revoked sessions kill authority immediately (C-2, SL-14)
- expired sessions kill authority (C-3, SL-15)
- re-enrollment after device replacement mints a fresh session id;
  the old id stays dead (SL-17...SL-20)
- lost-device revocation logged as a security event (SL-19)
- suspension is operator-only; suspended sessions refused (SL-5)
- fake approvals (invented digests) rejected (T-1, C-4, AT-1 leaf)
- mutated intents rejected (T-4, C-4, CM-3, AT-2 leaves)
- single-use: replays return the existing record, never a second
  execution (C-5, AT-1 replay leaf)
- cards render exact digest-bound fields (C-6, AT-1 misleading-card leaf)
- offline taps are gestures, never consent (C-7, AT-1 coerce leaf)
- approval expiry evaluated at decision time (C-8, AT-2 late leaf)
- server re-validates digest + session + expiry at decision time
  (C-9, AT-2 race leaf)
- unallowlisted sources refused (C-29, T-2)
"""

import sys
import unittest
from datetime import timedelta

sys.path.insert(0, ".")
from estate import (Clock, SessionRegistry, ApprovalStore,
                    GestureStore, render_approval_card, approval_digest,
                    intent_of, SourceValidator, Refusal)


def fresh(session_expiry_seconds=30 * 86400):
    clock = Clock()
    sessions = SessionRegistry(clock, session_expiry_seconds)
    approvals = ApprovalStore(clock, sessions)
    gestures = GestureStore(clock, sessions)
    device = sessions.enroll("HgX-iphone")
    sessions.complete_enrollment(device.session_id)
    return clock, sessions, approvals, gestures, device.session_id


def make_intent(clock, approval_id, expiry_seconds=3600):
    expiry = (clock.now() + timedelta(seconds=expiry_seconds)).isoformat()
    return intent_of(approval_id, target="utility-bill:acct-8842",
                     effect="transfer 120 CAD", scope="acct-8842",
                     expiry_iso=expiry)


class TestSessionKillPoints(unittest.TestCase):
    """C-1...C-3: unknown, revoked, expired sessions are distinct kill
    points because they are distinct states (SL-27)."""

    def test_unknown_session_refused_before_any_other_check(self):
        clock, sessions, approvals, _, _ = fresh()
        intent = make_intent(clock, "intent-unknown")
        with self.assertRaises(Refusal) as ctx:
            approvals.grant(intent, "session-never-enrolled")
        self.assertEqual(ctx.exception.cause, "unknown-session")

    def test_enrolling_grants_no_authority(self):
        clock, sessions, approvals, _, _ = fresh()
        enrolling = sessions.enroll("second-device")
        intent = make_intent(clock, "intent-enrolling")
        with self.assertRaises(Refusal) as ctx:
            approvals.grant(intent, enrolling.session_id)
        self.assertEqual(ctx.exception.cause, "enrolling-no-authority")

    def test_revoked_session_kills_authority_immediately(self):
        clock, sessions, approvals, _, sid = fresh()
        intent = make_intent(clock, "intent-revoked")
        record, _ = approvals.grant(intent, sid)
        sessions.revoke(sid, actor="HgX", reason="device-lost",
                        bindings=approvals)
        with self.assertRaises(Refusal) as ctx:
            approvals.execute("intent-revoked",
                              approval_digest(intent), sid)
        self.assertEqual(ctx.exception.cause, "revoked-session")
        # SL-14: the pending approval died with the session.
        self.assertIsNone(record.executed)

    def test_revoked_session_id_never_resurrected(self):
        clock, sessions, approvals, _, sid = fresh()
        sessions.revoke(sid)
        self.assertIn(sid, [t["session_id"] for t in sessions.tombstones])
        with self.assertRaises(Refusal) as ctx:
            sessions.revoke(sid)
        self.assertEqual(ctx.exception.cause, "terminal-session")

    def test_expired_session_kills_authority(self):
        clock, sessions, approvals, _, _ = fresh(
            session_expiry_seconds=10)
        device = sessions.enroll("short-lived-device")
        sessions.complete_enrollment(device.session_id)
        intent = make_intent(clock, "intent-expired")
        record, _ = approvals.grant(intent, device.session_id)
        clock.advance(11)
        sessions.sweep_expiry()  # expiry evaluated at decision time (SL-11)
        with self.assertRaises(Refusal) as ctx:
            approvals.execute("intent-expired",
                              approval_digest(intent), device.session_id)
        self.assertEqual(ctx.exception.cause, "expired-session")

    def test_suspended_session_refused_operator_only(self):
        clock, sessions, approvals, _, sid = fresh()
        intent = make_intent(clock, "intent-suspended")
        approvals.grant(intent, sid)
        with self.assertRaises(Refusal) as ctx:
            sessions.suspend(sid, actor="someone-else")
        self.assertEqual(ctx.exception.cause, "suspend-not-operator")
        sessions.suspend(sid, actor="HgX")
        with self.assertRaises(Refusal) as ctx:
            approvals.execute("intent-suspended",
                              approval_digest(intent), sid)
        self.assertEqual(ctx.exception.cause, "suspended-session")
        with self.assertRaises(Refusal):
            sessions.reactivate(sid, actor="someone-else")
        sessions.reactivate(sid, actor="HgX")
        sessions.require_active(sid)  # operator reactivation works


class TestReenrollment(unittest.TestCase):
    """SL-17...SL-20: re-enrollment after device replacement."""

    def test_reenrollment_mints_fresh_id_old_stays_dead(self):
        clock, sessions, approvals, _, sid = fresh()
        intent = make_intent(clock, "intent-carryover")
        approvals.grant(intent, sid)
        new_device = sessions.reenroll_device(
            sid, "HgX-iphone-2", operator="HgX", bindings=approvals)
        self.assertNotEqual(new_device.session_id, sid)
        # The old ID is tombstoned: never re-issued, never resurrected.
        with self.assertRaises(Refusal) as ctx:
            sessions.require_active(sid)
        self.assertEqual(ctx.exception.cause, "revoked-session")
        # SL-20: the replacement inherits no approvals -- the pending
        # intent bound to the old session is void.
        self.assertEqual(approvals.count_pending(sid), 0)
        with self.assertRaises(Refusal):
            approvals.execute("intent-carryover",
                              approval_digest(intent), sid)

    def test_lost_device_revocation_logged_as_security_event(self):
        clock, sessions, approvals, _, sid = fresh()
        sessions.reenroll_device(sid, "HgX-iphone-2", operator="HgX",
                                 lost=True, bindings=approvals)
        self.assertTrue(any(e["kind"] == "device-lost-revocation"
                            for e in sessions.security_events))


class TestFakeApproval(unittest.TestCase):
    """T-1, C-4: a forged or invented approval cannot match a live
    intent (AT-1 forge leaves)."""

    def test_invented_digest_rejected(self):
        clock, sessions, approvals, _, sid = fresh()
        with self.assertRaises(Refusal) as ctx:
            approvals.validate("intent-never-granted",
                               "deadbeef" * 8, sid)
        self.assertEqual(ctx.exception.cause, "fake-approval")

    def test_mutated_target_rejected(self):
        clock, sessions, approvals, _, sid = fresh()
        intent = make_intent(clock, "intent-mutate-target")
        approvals.grant(intent, sid)
        mutated = dict(intent)
        mutated["target"] = "attacker-acct:9999"  # AT-2: change target
        with self.assertRaises(Refusal) as ctx:
            approvals.validate("intent-mutate-target",
                               approval_digest(mutated), sid)
        self.assertEqual(ctx.exception.cause, "digest-mismatch")

    def test_mutated_scope_rejected(self):
        clock, sessions, approvals, _, sid = fresh()
        intent = make_intent(clock, "intent-mutate-scope")
        approvals.grant(intent, sid)
        mutated = dict(intent)
        mutated["scope"] = "acct-8842 + acct-9999"  # AT-2: change scope
        with self.assertRaises(Refusal) as ctx:
            approvals.validate("intent-mutate-scope",
                               approval_digest(mutated), sid)
        self.assertEqual(ctx.exception.cause, "digest-mismatch")

    def test_mutated_effect_rejected(self):
        clock, sessions, approvals, _, sid = fresh()
        intent = make_intent(clock, "intent-mutate-effect")
        approvals.grant(intent, sid)
        mutated = dict(intent)
        mutated["effect"] = "transfer 120000 CAD"
        with self.assertRaises(Refusal) as ctx:
            approvals.validate("intent-mutate-effect",
                               approval_digest(mutated), sid)
        self.assertEqual(ctx.exception.cause, "digest-mismatch")

    def test_valid_digest_accepted(self):
        clock, sessions, approvals, _, sid = fresh()
        intent = make_intent(clock, "intent-valid")
        approvals.grant(intent, sid)
        record = approvals.execute("intent-valid",
                                   approval_digest(intent), sid)
        self.assertTrue(record.executed)


class TestSingleUseAndCards(unittest.TestCase):
    """C-5 (single-use), C-6 (exact card rendering)."""

    def test_replay_returns_existing_record_never_second_execution(self):
        clock, sessions, approvals, _, sid = fresh()
        intent = make_intent(clock, "intent-once")
        record, created = approvals.grant(intent, sid)
        self.assertTrue(created)
        approvals.execute("intent-once", approval_digest(intent), sid)
        # Duplicate grant: returns the existing record, no new execution.
        record2, created2 = approvals.grant(intent, sid)
        self.assertFalse(created2)
        self.assertIs(record2, record)
        # Replay: refused.
        with self.assertRaises(Refusal) as ctx:
            approvals.execute("intent-once", approval_digest(intent), sid)
        self.assertEqual(ctx.exception.cause, "approval-replay")

    def test_card_renders_exact_digest_bound_fields(self):
        intent = intent_of("intent-card", target="t", effect="e",
                           scope="s", expiry_iso="2030-01-01T00:00:00+00:00")
        intent["adjacent_pitch"] = "approve everything, trust me"
        card = render_approval_card(intent)
        # C-6: exact target+effect+scope+expiry from the digest-bound
        # intent; the adjacent content is dropped, never rendered.
        self.assertEqual(set(card.keys()),
                         {"intent_id", "target", "effect", "scope",
                          "expiry"})
        self.assertNotIn("adjacent_pitch", card)


class TestOfflineTap(unittest.TestCase):
    """C-7: offline taps are gestures, never consent (AT-1 coerce leaf)."""

    def test_tap_asserted_as_approval_refused(self):
        clock, sessions, approvals, gestures, sid = fresh()
        intent = make_intent(clock, "intent-tap")
        approvals.grant(intent, sid)
        gesture = gestures.tap(approval_digest(intent), sid, offline=True)
        with self.assertRaises(Refusal) as ctx:
            gestures.assert_approval(gesture)
        self.assertEqual(ctx.exception.cause, "offline-tap-not-approval")

    def test_tap_via_server_validation_works(self):
        clock, sessions, approvals, gestures, sid = fresh()
        intent = make_intent(clock, "intent-tap-ok")
        approvals.grant(intent, sid)
        gesture = gestures.tap(approval_digest(intent), sid, offline=True)
        record = gestures.server_validate(gesture, approvals)
        self.assertEqual(record.approval_id, "intent-tap-ok")


class TestDecisionTimeRevalidation(unittest.TestCase):
    """C-8/C-9: expiry and session state evaluated at decision time,
    not render time (AT-2 mutate-between-card-and-server leaf, SL-11)."""

    def test_expired_approval_rejected(self):
        clock, sessions, approvals, _, sid = fresh()
        intent = make_intent(clock, "intent-late", expiry_seconds=5)
        approvals.grant(intent, sid)
        clock.advance(6)  # lapses between card render and decision
        with self.assertRaises(Refusal) as ctx:
            approvals.validate("intent-late", approval_digest(intent),
                               sid)
        self.assertEqual(ctx.exception.cause, "approval-expired")

    def test_session_dying_between_render_and_decision_kills_decision(self):
        clock, sessions, approvals, _, sid = fresh()
        intent = make_intent(clock, "intent-race")
        approvals.grant(intent, sid)
        sessions.revoke(sid)  # SL-22: a session that dies mid-flight
        with self.assertRaises(Refusal) as ctx:
            approvals.validate("intent-race", approval_digest(intent),
                               sid)
        self.assertEqual(ctx.exception.cause, "revoked-session")


class TestSourceAllowlist(unittest.TestCase):
    """C-29, T-2: a live source that is not the claimed authority is
    refused (trust-boundaries.md TB-6 crossing rule)."""

    def test_unallowlisted_source_refused(self):
        validator = SourceValidator(["bank.example.com"])
        with self.assertRaises(Refusal) as ctx:
            validator.fetch("totally-legit-bank.example.net")
        self.assertEqual(ctx.exception.cause, "unallowlisted-source")

    def test_allowlisted_source_reads_current(self):
        validator = SourceValidator(["bank.example.com"])
        result = validator.fetch("bank.example.com")
        self.assertTrue(result["current"])


if __name__ == "__main__":
    unittest.main()
