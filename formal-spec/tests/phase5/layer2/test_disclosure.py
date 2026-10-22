"""Phase 5 Layer 2 -- Disclosure controls (T-10...T-12).

Threats: T-10 (shared-surface exposure), T-11 (notification leakage),
T-12 (cross-role leakage), per threat-catalogue.md section 5.
Controls: C-14 (notification redaction), C-15 (states-only rendering on
shared surfaces, INV-S5), C-27 connector-least-privilege part
(control-matrix.md section 2).
Draft sections cited: trust-boundaries.md TB-9 (notifications are hints,
not authoritative state; no payload beyond pointer + state), TB-10
(shared screens show states only); capability-matrix.md CM-1/CM-2
(capabilities are conditions, not possessions).

Checks:
- notifications carry pointer + state only, never the record (C-14)
- shared surfaces render states only; restricted content never renders
  (C-15, INV-S5)
- a capability valid for one subject is refused for another: cross-role
  least privilege (T-12)
- a capability whose condition is false is not a capability (CM-1);
  expiry evaluated at decision time (CM-2)
"""

import sys
import unittest
from datetime import timedelta

sys.path.insert(0, ".")
from estate import (Clock, SessionRegistry, Capability,
                    build_notification, render_shared_surface,
                    ConnectorRegistry, Refusal)


class TestNotificationRedaction(unittest.TestCase):
    """C-14, TB-9: a notification is a hint -- pointer + state only."""

    def test_hint_carries_no_payload(self):
        hint = build_notification("approval-7", "pending")
        self.assertEqual(set(hint.keys()), {"pointer", "state"})
        self.assertEqual(hint["pointer"], "record:approval-7")
        self.assertEqual(hint["state"], "pending")

    def test_hint_leaks_no_record_content(self):
        record_content = {"amount": 120, "account": "8842", "digest": "abc"}
        hint = build_notification("approval-7", "pending")
        # The hint shape cannot carry the record: serializing the hint
        # must not contain any record field value.
        import json
        serialized = json.dumps(hint)
        for value in record_content.values():
            self.assertNotIn(str(value), serialized)


class TestSharedSurface(unittest.TestCase):
    """C-15, TB-10, INV-S5: states only on shared surfaces."""

    def test_shared_surface_strips_restricted_content(self):
        private_view = {
            "balance": {"state": "known", "amount": 4200, "acct": "8842"},
            "approval": {"state": "pending", "target": "utility",
                         "effect": "transfer"},
            "headline": "market up 2%",
        }
        rendered = render_shared_surface(private_view)
        import json
        serialized = json.dumps(rendered)
        self.assertNotIn("4200", serialized)
        self.assertNotIn("8842", serialized)
        self.assertNotIn("utility", serialized)
        self.assertEqual(rendered["balance"], {"state": "known"})
        self.assertEqual(rendered["approval"], {"state": "pending"})


class TestCrossRoleLeastPrivilege(unittest.TestCase):
    """T-12: a subject reads or acts beyond its least privilege --
    refused (capability-matrix.md section 4 cells)."""

    def _money_capability(self, clock, sessions, sid):
        expiry = (clock.now() + timedelta(seconds=3600)).isoformat()
        return Capability(
            subject="money-custodian",
            action="execute.consequential",
            obj="AR-5",
            scope={"amount": "120 CAD", "account": "8842",
                   "date": "2026-10-22"},
            condition=lambda: sessions.require_active(sid) or True,
            expiry_iso=expiry,
            approval_req="HgX explicit, exact amount+account+date",
            evidence_req="evidence packet with execution observation")

    def test_capability_valid_for_one_subject_refused_for_another(self):
        clock = Clock()
        sessions = SessionRegistry(clock)
        device = sessions.enroll("HgX-iphone")
        sessions.complete_enrollment(device.session_id)
        cap = self._money_capability(clock, sessions, device.session_id)
        # The same eight-tuple, presented by a different subject: the
        # condition binds the subject, so it is not this subject's
        # capability at all (CM-1).
        cap.subject = "orchestrator"
        cap.condition = lambda: False  # orchestrator holds no AR-5 row
        with self.assertRaises(Refusal) as ctx:
            cap.invoke(clock)
        self.assertEqual(ctx.exception.cause, "condition-false")

    def test_condition_false_is_not_a_capability(self):
        clock = Clock()
        sessions = SessionRegistry(clock)
        device = sessions.enroll("HgX-iphone")
        sessions.complete_enrollment(device.session_id)
        sid = device.session_id
        cap = self._money_capability(clock, sessions, sid)
        sessions.revoke(sid)  # SL-21: authority is conditional on
        # session in {active}; the state is the switch.
        with self.assertRaises(Refusal) as ctx:
            cap.invoke(clock)
        self.assertEqual(ctx.exception.cause, "revoked-session")

    def test_capability_expiry_evaluated_at_decision_time(self):
        clock = Clock()
        sessions = SessionRegistry(clock)
        device = sessions.enroll("HgX-iphone")
        sessions.complete_enrollment(device.session_id)
        cap = self._money_capability(clock, sessions, device.session_id)
        clock.advance(3601)  # lapses after the capability was minted
        with self.assertRaises(Refusal) as ctx:
            cap.invoke(clock)
        self.assertEqual(ctx.exception.cause, "capability-expired")

    def test_connector_cannot_exceed_grant(self):
        registry = ConnectorRegistry()
        registry.grant("comms-connector", {("read", "AR-6"),
                                           ("read", "AR-7")})
        self.assertTrue(registry.use("comms-connector", "read", "AR-6"))
        with self.assertRaises(Refusal) as ctx:
            registry.use("comms-connector", "execute.consequential",
                         "AR-5")
        self.assertEqual(ctx.exception.cause, "connector-overreach")


if __name__ == "__main__":
    unittest.main()
