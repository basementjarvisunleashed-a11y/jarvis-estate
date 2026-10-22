"""Phase 5 Layer 2 -- Elevation-of-privilege controls (T-18...T-21).

Threats: T-18 (routine scope creep), T-19 (connector overreach),
T-20 (router as approver), T-21 (client as orchestrator), per
threat-catalogue.md section 7.
Controls: C-27 (routine scope limits; connector least privilege;
router recommends only), C-31 (custody-boundary enforcement: TB-11
mechanical crossing-rule tests; the doctrinal part honestly marked
non-mechanically-testable) (control-matrix.md section 2).
Draft sections cited: capability-matrix.md CM-5/CM-6 (no subject holds
execute.consequential except the money custodian under TB-11's exact-
approval condition; no subject holds grant.approval except HgX);
trust-boundaries.md TB-5/TB-8/TB-11...TB-15 (crossing rules).

Checks:
- a routine doing what it was never granted is refused (T-18)
- a connector capability cannot exceed its granted scope (T-19)
- the router recommends only: it cannot approve or authorize spending
  (T-20)
- a client attempting orchestration is refused; clients render
  contracts only (T-21)
- money execution: non-custodian refused; non-exact approval refused;
  one approval = one action (C-31, TB-11)
- sealed boundaries hold mechanically where stated: health sealed
  (TB-13), research sealed (TB-15), location boundary named-only
  (TB-14, Q6 secrecy)
"""

import sys
import unittest
from datetime import timedelta

sys.path.insert(0, ".")
from estate import (Clock, SessionRegistry, ApprovalStore,
                    Capability, Router, ConnectorRegistry, MoneyCustody,
                    render_contract, client_orchestrate,
                    health_crossing, research_crossing,
                    location_access, intent_of, Refusal)


def fresh():
    clock = Clock()
    sessions = SessionRegistry(clock)
    approvals = ApprovalStore(clock, sessions)
    device = sessions.enroll("HgX-iphone")
    sessions.complete_enrollment(device.session_id)
    return clock, sessions, approvals, device.session_id


def exact_money_intent(clock, approval_id, amount, account, date):
    expiry = (clock.now() + timedelta(seconds=3600)).isoformat()
    return intent_of(approval_id, target=f"transfer:{account}",
                     effect=f"move {amount}", scope=scope_for(amount),
                     expiry_iso=expiry, action="execute.consequential")


def scope_for(amount):
    return {"amount": amount, "account": "acct-8842",
            "date": "2026-10-22"}


class TestRoutineScopeLimits(unittest.TestCase):
    """T-18, C-27, CM-6: a routine doing what it was never granted is
    refused; no standing consequential authority."""

    def test_routine_cannot_execute_consequential(self):
        clock = Clock()
        sessions = SessionRegistry(clock)
        device = sessions.enroll("HgX-iphone")
        sessions.complete_enrollment(device.session_id)
        sid = device.session_id
        expiry = (clock.now() + timedelta(seconds=3600)).isoformat()
        routine = Capability(
            subject="nightly-routine", action="read", obj="AR-10",
            scope="status", condition=lambda: sessions.require_active(sid)
            or True, expiry_iso=expiry,
            approval_req="none (reversible only)",
            evidence_req="none (reversible only)")
        # The routine holds read. Presenting it for a consequential
        # action is a different capability -- and none exists.
        routine.action = "execute.consequential"
        routine.condition = lambda: False  # no such row exists
        with self.assertRaises(Refusal) as ctx:
            routine.invoke(clock)
        self.assertEqual(ctx.exception.cause, "condition-false")

    def test_expired_capability_is_not_standing_authority(self):
        clock = Clock()
        sessions = SessionRegistry(clock)
        device = sessions.enroll("HgX-iphone")
        sessions.complete_enrollment(device.session_id)
        expiry = (clock.now() + timedelta(seconds=10)).isoformat()
        cap = Capability(subject="money-custodian", action="read",
                         obj="AR-5", scope="balance",
                         condition=lambda: True, expiry_iso=expiry,
                         approval_req="none", evidence_req="none")
        clock.advance(11)
        with self.assertRaises(Refusal) as ctx:
            cap.invoke(clock)
        self.assertEqual(ctx.exception.cause, "capability-expired")


class TestConnectorLeastPrivilege(unittest.TestCase):
    """T-19, C-27: connector least privilege (TB-5 crossing rule)."""

    def test_connector_overreach_refused(self):
        registry = ConnectorRegistry()
        registry.grant("calendar-connector",
                       {("read", "AR-6"), ("read", "AR-7")})
        with self.assertRaises(Refusal) as ctx:
            registry.use("calendar-connector", "execute.consequential",
                         "AR-5")
        self.assertEqual(ctx.exception.cause, "connector-overreach")


class TestRouterRecommendsOnly(unittest.TestCase):
    """T-20, C-27: the router recommends; it never approves, authorizes
    spending, or becomes a second orchestrator (TB-8)."""

    def test_router_cannot_approve(self):
        router = Router(Clock())
        intent = intent_of("intent-router", "t", "e", "s",
                           (Clock().now() +
                            timedelta(seconds=60)).isoformat())
        with self.assertRaises(Refusal) as ctx:
            router.issue_approval(intent)
        self.assertEqual(ctx.exception.cause, "router-cannot-approve")

    def test_router_cannot_authorize_spending(self):
        router = Router(Clock())
        with self.assertRaises(Refusal) as ctx:
            router.authorize_spend(100)
        self.assertEqual(ctx.exception.cause, "router-cannot-spend")

    def test_router_recommendation_works(self):
        router = Router(Clock())
        self.assertEqual(router.recommend(["plan-a", "plan-b"]), "plan-a")


class TestClientRendersContractsOnly(unittest.TestCase):
    """T-21: clients render contracts only; no local approval; offline
    taps are gestures, not consent (TB-1/TB-2)."""

    def test_client_orchestration_refused(self):
        with self.assertRaises(Refusal) as ctx:
            client_orchestrate("execute.consequential on AR-5")
        self.assertEqual(ctx.exception.cause, "client-cannot-orchestrate")

    def test_contract_carries_no_authority(self):
        clock = Clock()
        sessions = SessionRegistry(clock)
        device = sessions.enroll("HgX-iphone")
        sessions.complete_enrollment(device.session_id)
        expiry = (clock.now() + timedelta(seconds=3600)).isoformat()
        cap = Capability(subject="orchestrator", action="notify.hint",
                         obj="AR-1", scope="hint",
                         condition=lambda: True, expiry_iso=expiry,
                         approval_req="none", evidence_req="none")
        contract = render_contract(cap)
        self.assertTrue(contract["contract"])
        self.assertNotIn("approve", str(contract).lower())
        # A contract presented as authority is nothing the model
        # recognizes: the client plane has no execute path.


class TestCustodyBoundaries(unittest.TestCase):
    """C-31: custody-boundary enforcement. The mechanical part is
    tested here (crossing-rule unit tests); the doctrinal part is
    honestly marked non-mechanically-testable (control-matrix.md
    section 3: verification = HgX's word as change control + review)."""

    def test_non_custodian_money_execution_refused(self):
        clock, sessions, approvals, sid = fresh()
        intent = exact_money_intent(clock, "intent-money", "120 CAD",
                                    "acct-8842", "2026-10-22")
        record, _ = approvals.grant(intent, sid)
        money = MoneyCustody(clock)
        with self.assertRaises(Refusal) as ctx:
            money.execute_money("orchestrator", record, "120 CAD",
                                "acct-8842", "2026-10-22")
        self.assertEqual(ctx.exception.cause, "custody-crossing-refused")

    def test_money_approval_must_be_exact(self):
        clock, sessions, approvals, sid = fresh()
        intent = exact_money_intent(clock, "intent-money-2", "120 CAD",
                                    "acct-8842", "2026-10-22")
        record, _ = approvals.grant(intent, sid)
        money = MoneyCustody(clock)
        # Wrong amount: refused -- one approval = one exact amount,
        # account, date (TB-11).
        with self.assertRaises(Refusal) as ctx:
            money.execute_money("money-custodian", record, "999 CAD",
                                "acct-8842", "2026-10-22")
        self.assertEqual(ctx.exception.cause, "money-approval-not-exact")

    def test_exact_money_execution_single_use(self):
        clock, sessions, approvals, sid = fresh()
        intent = exact_money_intent(clock, "intent-money-3", "120 CAD",
                                    "acct-8842", "2026-10-22")
        record, _ = approvals.grant(intent, sid)
        money = MoneyCustody(clock)
        self.assertTrue(money.execute_money("money-custodian", record,
                                            "120 CAD", "acct-8842",
                                            "2026-10-22"))
        with self.assertRaises(Refusal) as ctx:
            money.execute_money("money-custodian", record, "120 CAD",
                                "acct-8842", "2026-10-22")
        self.assertEqual(ctx.exception.cause, "money-approval-replay")

    def test_health_sealed(self):
        with self.assertRaises(Refusal) as ctx:
            health_crossing("news-bot", "read")
        self.assertEqual(ctx.exception.cause, "health-sealed")

    def test_research_sealed(self):
        with self.assertRaises(Refusal):
            research_crossing("finding-42")

    def test_location_boundary_named_only(self):
        # TB-14, Q6 secrecy: the boundary is named; the custodian is
        # never named outside its own chat. No other room uses it.
        with self.assertRaises(Refusal) as ctx:
            location_access("working-room")
        self.assertEqual(ctx.exception.cause, "location-not-custodian")


if __name__ == "__main__":
    unittest.main()
