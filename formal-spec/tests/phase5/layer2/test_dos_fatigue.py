"""Phase 5 Layer 2 -- Denial-of-service and fatigue controls
(T-14...T-17, T-23, T-24).

Threats: T-14 (attention exhaustion), T-15 (loop waste), T-16 (cost
explosion), T-17 (source outage), T-23 (stale-state manipulation),
T-24 (approval fatigue), per threat-catalogue.md sections 6 and 8.
Controls: C-17 (silent-by-default), C-18 (no bulk approval), C-19
(risk classes; high-risk requires local auth and exact rendering),
C-25 (router denies loops; budgets; no retry on unknown), C-26 (live
re-read; freshness; unknown on observation failure)
(control-matrix.md section 2). Attack tree: AT-4 (approval fatigue).

C-20 is honestly marked NON-mechanically-testable (control-matrix.md
section 3): no test can prove a fatigue curve. The check here verifies
its documented verification method holds where checkable -- the review
procedure exists in Layer 2, states thresholds as operational judgment
(not a modeled curve), and the attention-budget log it reviews is
exportable.

Draft sections cited: trust-boundaries.md TB-9 (silent-by-default);
capability-matrix.md CM-9 (notify.hint is the only attention action;
no capability for bulk notification); control-matrix.md section 5
(L0 compensations).

Checks:
- routine requests stay silent; HgX is not notified (C-17)
- bulk approval is refused, even under pressure (C-18; AT-4 leaf)
- high-risk requires local auth and exact target+effect rendering (C-19)
- approval barrages beyond budget are refused/queued (T-24; AT-4 flood)
- the router denies repeated no-progress action (C-25; T-15)
- no retry on unknown; call budgets enforced (C-25; T-16)
- live re-read before consequence; stale/unknown cannot consequence;
  outages render as unknown, never a stale substitution (C-26; T-17/T-23)
"""

import os
import sys
import unittest
from datetime import timedelta

sys.path.insert(0, ".")
from estate import (Clock, SessionRegistry, ApprovalStore, Attention,
                    Router, SourceValidator, LiveSource,
                    consequential_on_reading, render_approval_card,
                    intent_of, Refusal)


def fresh():
    clock = Clock()
    sessions = SessionRegistry(clock)
    approvals = ApprovalStore(clock, sessions)
    device = sessions.enroll("HgX-iphone")
    sessions.complete_enrollment(device.session_id)
    return clock, sessions, approvals, device.session_id


def intent_for(clock, approval_id):
    expiry = (clock.now() + timedelta(seconds=3600)).isoformat()
    return intent_of(approval_id, target="utility-bill:acct-8842",
                     effect="transfer 120 CAD", scope="acct-8842",
                     expiry_iso=expiry)


class TestSilenceByDefault(unittest.TestCase):
    """C-17: silent-by-default; tiered escalation (AT-4 routine leaf)."""

    def test_routine_request_stays_silent(self):
        clock = Clock()
        attention = Attention(clock)
        intent = intent_for(clock, "intent-routine")
        self.assertEqual(attention.request_approval(intent, risk="standard"),
                         "silent")
        self.assertEqual(attention.requested, [])  # never even logged


class TestNoBulkApproval(unittest.TestCase):
    """C-18: each intent approved singly (AT-4 bulk-pressure leaf)."""

    def test_bulk_approve_refused(self):
        clock = Clock()
        attention = Attention(clock)
        intents = [intent_for(clock, f"intent-{i}") for i in range(5)]
        with self.assertRaises(Refusal) as ctx:
            attention.bulk_approve(intents)
        self.assertEqual(ctx.exception.cause, "bulk-approval-refused")


class TestHighRisk(unittest.TestCase):
    """C-19: risk classes; high-risk requires local auth and exact
    rendering (AT-4 disguised-high-risk leaf)."""

    def test_high_risk_without_local_auth_refused_at_grant(self):
        clock, sessions, approvals, sid = fresh()
        intent = intent_for(clock, "intent-high")
        with self.assertRaises(Refusal) as ctx:
            approvals.grant(intent, sid, risk="high", local_auth=False)
        self.assertEqual(ctx.exception.cause,
                         "high-risk-requires-local-auth")

    def test_high_risk_without_exact_card_refused_at_gate(self):
        clock = Clock()
        attention = Attention(clock)
        intent = intent_for(clock, "intent-high-2")
        with self.assertRaises(Refusal) as ctx:
            attention.request_approval(intent, risk="high",
                                       card={"fake": "card"})
        self.assertEqual(ctx.exception.cause, "high-risk-not-exact")

    def test_high_risk_with_local_auth_and_exact_card_requested(self):
        clock = Clock()
        attention = Attention(clock)
        intent = intent_for(clock, "intent-high-3")
        card = render_approval_card(intent)  # exact, from the digest-bound
        # intent itself (C-6); the gate compares, it does not trust.
        self.assertEqual(attention.request_approval(intent, risk="high",
                                                    card=card),
                         "requested")


class TestAttentionBudget(unittest.TestCase):
    """T-24, AT-4: flood leaves are stopped by the budget."""

    def test_barrage_beyond_budget_refused_or_queued(self):
        clock = Clock()
        attention = Attention(clock, budget_per_hour=3)
        for i in range(3):
            intent = intent_for(clock, f"intent-flood-{i}")
            card = render_approval_card(intent)
            self.assertEqual(attention.request_approval(
                intent, risk="high", card=card), "requested")
        intent = intent_for(clock, "intent-flood-3")
        card = render_approval_card(intent)
        with self.assertRaises(Refusal) as ctx:
            attention.request_approval(intent, risk="high", card=card)
        self.assertEqual(ctx.exception.cause, "attention-budget-exceeded")


class TestRouterDenials(unittest.TestCase):
    """C-25: the router denies repeated no-progress action; budgets;
    no retry on unknown (T-15/T-16)."""

    def test_router_denies_loop(self):
        clock = Clock()
        router = Router(clock, call_budget=50)
        router.action("retry-fetch", progress_made=False, known=True)
        router.action("retry-fetch", progress_made=False, known=True)
        with self.assertRaises(Refusal) as ctx:
            router.action("retry-fetch", progress_made=False, known=True)
        self.assertEqual(ctx.exception.cause, "router-denies-loop")

    def test_progress_resets_the_loop_guard(self):
        clock = Clock()
        router = Router(clock, call_budget=50)
        router.action("fetch", progress_made=False, known=True)
        router.action("fetch", progress_made=True, known=True)
        # Progress was made: not a no-progress loop.
        self.assertEqual(router.action("fetch", progress_made=False,
                                       known=True), "ran")

    def test_no_retry_on_unknown(self):
        clock = Clock()
        router = Router(clock)
        with self.assertRaises(Refusal) as ctx:
            router.action("opaque-call", progress_made=False, known=False)
        self.assertEqual(ctx.exception.cause, "no-retry-on-unknown")

    def test_call_budget_enforced(self):
        clock = Clock()
        router = Router(clock, call_budget=2)
        router.recommend(["a"])
        router.recommend(["b"])
        with self.assertRaises(Refusal) as ctx:
            router.recommend(["c"])
        self.assertEqual(ctx.exception.cause, "call-budget-exceeded")


class TestFreshness(unittest.TestCase):
    """C-26: live re-read before consequence; freshness stamps; unknown
    on observation failure (T-17/T-23)."""

    def test_outage_renders_unknown_never_stale(self):
        clock = Clock()
        validator = SourceValidator(["bank.example.com"])
        source = LiveSource(validator, clock)
        reading = source.read_or_unknown("bank.example.com", alive=False)
        self.assertEqual(reading["state"], "unknown")
        self.assertNotIn("fresh", reading)

    def test_unknown_reading_cannot_consequence(self):
        reading = {"source": "bank.example.com", "state": "unknown",
                   "reason": "observation failure"}
        with self.assertRaises(Refusal) as ctx:
            consequential_on_reading(reading, lambda: "executed")
        self.assertEqual(ctx.exception.cause,
                         "stale-state-cannot-consequence")

    def test_fresh_reading_consequences(self):
        clock = Clock()
        validator = SourceValidator(["bank.example.com"])
        source = LiveSource(validator, clock)
        reading = source.read("bank.example.com")
        self.assertEqual(consequential_on_reading(reading,
                                                 lambda: "executed"),
                         "executed")


class TestAttentionBudgetReviewProcedure(unittest.TestCase):
    """C-20 -- honestly non-mechanically-testable. This test verifies
    the documented verification method holds where checkable: the
    review procedure exists in Layer 2, states its thresholds as
    operational judgment (never a modeled fatigue curve), and the
    attention-budget log it reviews is exportable."""

    def test_review_procedure_documented(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "review-procedure.md")
        self.assertTrue(os.path.isfile(path),
                        "C-20's verification procedure must be documented "
                        "in Layer 2 (control-matrix.md section 2)")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("operational judgment", text)
        # The procedure states the honest limit plainly: thresholds are
        # judgment, never a modeled fatigue curve.
        self.assertIn("not a modeled fatigue curve", text)

    def test_budget_log_exportable(self):
        clock = Clock()
        attention = Attention(clock)
        intent = intent_for(clock, "intent-logged")
        card = render_approval_card(intent)
        attention.request_approval(intent, risk="high", card=card)
        log = attention.export_budget_log()
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["intent_id"], "intent-logged")


if __name__ == "__main__":
    unittest.main()
