"""Phase 5 Layer 3 -- adversarial stale-state scenarios (T-23).

Threat: T-23 (stale-state manipulation: a raced or cached state
becoming a consequence); T-4 (mutated intent: let the approval
expire, execute late). Controls: C-26 (live re-read before
consequence; freshness stamps; unknown on observation failure),
C-9 (server re-validates intent digest + session + expiry at
decision time), C-4 (intent digest binding; superseded revisions),
C-8 (approval expiry evaluated at decision time), C-2 (revoked
session kills authority). Attack tree: AT-2.

Every ordering of re-read / validate / execute is enumerated: only
the canonical order fires. Boundary cases are pinned at the exact
freshness TTL and the exact approval expiry.

Cases SS-01..SS-08. Every case names its threat ID and control ID
and logs its verdict via record_verdict.
"""

import itertools
import sys
import unittest

sys.path.insert(0, ".")
from adversary import (fresh_estate, grant_intent, RacedSource,
                       ConsequentialGate, SupersessionTracker,
                       record_verdict, HELD_REFUSED, CLEAN_PASS,
                       FRESHNESS_TTL_SECONDS)
from estate import Refusal


class TestStaleStateAdversarial(unittest.TestCase):
    """T-23 under fire; AT-2 stale leaves."""

    def test_ss01_raced_state_midflight_refused(self):
        """SS-01 | T-23 | C-26 | AT-2 race leaf.

        The world flips between approval and execution. The
        decision-time live re-read disagrees with the approved
        reading: refused, nothing fires."""
        clock, sessions, approvals, sid = fresh_estate()
        _intent, record = grant_intent(
            clock, approvals, sid, "appr-ss01",
            target="bill:acct-8842", effect="pay 120 CAD",
            scope="acct-8842")
        source = RacedSource(clock)
        gate = ConsequentialGate(clock, approvals, source)
        gate.re_read()
        gate.validate("appr-ss01", record.digest, sid)
        source.arm_flip(5)
        clock.advance(10)  # the world moves while we deliberate
        fired = []
        with self.assertRaises(Refusal) as cm:
            gate.execute(lambda: fired.append(True))
        self.assertEqual(cm.exception.cause,
                         "stale-state-cannot-consequence")
        self.assertEqual(fired, [])
        record_verdict("SS-01", "T-23", "C-26", HELD_REFUSED,
                       "state raced mid-flight; decision-time re-read "
                       "disagrees: stale-state-cannot-consequence; "
                       "action did not fire")

    def test_ss02_observation_failure_renders_unknown(self):
        """SS-02 | T-23 | C-26 | observation-failure leaf.

        The source dies between re-read and execution. The action
        renders unknown and refuses -- never a stale substitution."""
        clock, sessions, approvals, sid = fresh_estate()
        _intent, record = grant_intent(
            clock, approvals, sid, "appr-ss02",
            target="bill:acct-8842", effect="pay 120 CAD",
            scope="acct-8842")
        source = RacedSource(clock)
        gate = ConsequentialGate(clock, approvals, source)
        gate.re_read()
        gate.validate("appr-ss02", record.digest, sid)
        source.alive = False  # observation fails at decision time
        fired = []
        with self.assertRaises(Refusal) as cm:
            gate.execute(lambda: fired.append(True))
        self.assertEqual(cm.exception.cause,
                         "stale-state-cannot-consequence")
        self.assertEqual(fired, [])
        record_verdict("SS-02", "T-23", "C-26", HELD_REFUSED,
                       "observation failure at decision time renders "
                       "unknown: stale-state-cannot-consequence; no "
                       "stale substitution")

    def test_ss03_superseded_revision_presented_as_current(self):
        """SS-03 | T-23 | C-4 | AT-2 mutate-after-approval leaf.

        A v0.1 approval whose digest is still valid is superseded by
        v0.2. Presenting v0.1 as current is refused."""
        clock, sessions, approvals, sid = fresh_estate()
        _i1, rec1 = grant_intent(
            clock, approvals, sid, "appr-bill-v1",
            target="bill:acct-8842", effect="pay 120 CAD",
            scope="acct-8842", revision="v0.1")
        _i2, _rec2 = grant_intent(
            clock, approvals, sid, "appr-bill-v2",
            target="bill:acct-8842", effect="pay 120 CAD",
            scope="acct-8842", revision="v0.2")
        tracker = SupersessionTracker()
        tracker.publish("bill-8842", "v0.2")
        # the v0.1 digest is still valid...
        approvals.validate("appr-bill-v1", rec1.digest, sid)
        # ...but presenting it as current is refused:
        with self.assertRaises(Refusal) as cm:
            tracker.check_current("bill-8842", "v0.1")
        self.assertEqual(cm.exception.cause, "superseded-revision")
        tracker.check_current("bill-8842", "v0.2")  # current passes
        record_verdict("SS-03", "T-23", "C-4", HELD_REFUSED,
                       "superseded revision presented as current "
                       "refused: superseded-revision, even though the "
                       "v0.1 digest still validates")

    def test_ss04_freshness_boundary_exact(self):
        """SS-04 | T-23 | C-26 | boundary case.

        TTL = 300s (stated operational judgment). A reading 299s old
        executes; at exactly 300s and at 301s it refuses."""
        self.assertEqual(FRESHNESS_TTL_SECONDS, 300)
        clock, sessions, approvals, sid = fresh_estate()
        _intent, record = grant_intent(
            clock, approvals, sid, "appr-ss04",
            target="bill:acct-8842", effect="pay 120 CAD",
            scope="acct-8842")
        source = RacedSource(clock)

        fired = []

        def attempt(age_seconds):
            gate = ConsequentialGate(clock, approvals, source)
            gate.re_read()
            clock.advance(age_seconds)
            gate.validate("appr-ss04", record.digest, sid)
            return gate.execute(lambda: fired.append(age_seconds))

        # 299s: fresh -> executes
        attempt(299)
        self.assertEqual(fired, [299])

        # 300s: exactly at the TTL -> refused
        with self.assertRaises(Refusal) as cm:
            attempt(300)
        self.assertEqual(cm.exception.cause,
                         "stale-state-cannot-consequence")

        # 301s: past the TTL -> refused
        with self.assertRaises(Refusal):
            attempt(301)

        self.assertEqual(fired, [299])  # the stale ones never fired
        record_verdict("SS-04", "T-23", "C-26", HELD_REFUSED,
                       "freshness boundary pinned: 299s executes, "
                       "300s and 301s refused "
                       "(stale-state-cannot-consequence); TTL=300s "
                       "stated as operational judgment")

    def test_ss05_approval_expiry_boundary_exact(self):
        """SS-05 | T-4 | C-8 | AT-2 expire-then-execute leaf.

        Approval expiry is evaluated at decision time: valid at
        T-1s, refused at exactly T and at T+1s."""
        clock, sessions, approvals, sid = fresh_estate()
        _intent, record = grant_intent(
            clock, approvals, sid, "appr-ss05",
            target="bill:acct-8842", effect="pay 120 CAD",
            scope="acct-8842", ttl_seconds=600)
        clock.advance(599)
        approvals.validate("appr-ss05", record.digest, sid)  # T-1s: ok
        clock.advance(1)  # exactly at expiry
        with self.assertRaises(Refusal) as cm:
            approvals.validate("appr-ss05", record.digest, sid)
        self.assertEqual(cm.exception.cause, "approval-expired")
        clock.advance(1)  # T+1s
        with self.assertRaises(Refusal):
            approvals.validate("appr-ss05", record.digest, sid)
        record_verdict("SS-05", "T-4", "C-8", HELD_REFUSED,
                       "expiry boundary pinned: valid at T-1s, "
                       "refused at T and T+1s (approval-expired)")

    def test_ss06_operation_orderings_enumerated(self):
        """SS-06 | T-23 | C-9 | systematic permutation enumeration.

        All 6 orderings of re-read / validate / execute: only the
        canonical order fires; every other ordering refuses."""
        outcomes = {}
        for ordering in itertools.permutations(
                ["re-read", "validate", "execute"]):
            clock, sessions, approvals, sid = fresh_estate()
            _intent, record = grant_intent(
                clock, approvals, sid, "appr-ss06",
                target="bill:acct-8842", effect="pay 120 CAD",
                scope="acct-8842")
            source = RacedSource(clock)
            gate = ConsequentialGate(clock, approvals, source)
            fired = []
            try:
                for op in ordering:
                    if op == "re-read":
                        gate.re_read()
                    elif op == "validate":
                        gate.validate("appr-ss06", record.digest, sid)
                    else:
                        gate.execute(lambda: fired.append(True))
                outcomes[ordering] = "executed" if fired else "no-fire"
            except Refusal as exc:
                outcomes[ordering] = f"refused:{exc.cause}"
        self.assertEqual(outcomes[("re-read", "validate", "execute")],
                         "executed")
        for ordering, outcome in outcomes.items():
            if ordering != ("re-read", "validate", "execute"):
                self.assertTrue(outcome.startswith("refused:"),
                                f"{ordering} -> {outcome}")
        record_verdict("SS-06", "T-23", "C-9", HELD_REFUSED,
                       "6/6 orderings enumerated: only [re-read, "
                       "validate, execute] fires; 5 refused "
                       "(stale-state-cannot-consequence)")

    def test_ss07_session_revoked_between_grant_and_execution(self):
        """SS-07 | T-23 | C-9/C-2 | stale-authority leaf.

        The session is revoked between approval grant and execution.
        Decision-time re-validation refuses before anything fires."""
        clock, sessions, approvals, sid = fresh_estate()
        _intent, record = grant_intent(
            clock, approvals, sid, "appr-ss07",
            target="bill:acct-8842", effect="pay 120 CAD",
            scope="acct-8842")
        source = RacedSource(clock)
        gate = ConsequentialGate(clock, approvals, source)
        gate.re_read()
        sessions.revoke(sid, bindings=approvals)  # authority dies here
        with self.assertRaises(Refusal) as cm:
            gate.validate("appr-ss07", record.digest, sid)
        self.assertEqual(cm.exception.cause, "revoked-session")
        record_verdict("SS-07", "T-23", "C-9", HELD_REFUSED,
                       "session revoked mid-flight; decision-time "
                       "re-validation refuses: revoked-session (SL-14)")

    def test_ss08_fresh_path_executes(self):
        """SS-08 | T-23 | C-26 | control case.

        The honest path -- fresh re-read, valid approval, live
        source -- executes exactly once."""
        clock, sessions, approvals, sid = fresh_estate()
        _intent, record = grant_intent(
            clock, approvals, sid, "appr-ss08",
            target="bill:acct-8842", effect="pay 120 CAD",
            scope="acct-8842")
        source = RacedSource(clock)
        gate = ConsequentialGate(clock, approvals, source)
        gate.re_read()
        gate.validate("appr-ss08", record.digest, sid)
        fired = []
        result = gate.execute(lambda: fired.append(True) or "done")
        self.assertEqual(result, "done")
        self.assertEqual(fired, [True])
        record_verdict("SS-08", "T-23", "C-26", CLEAN_PASS,
                       "fresh re-read + valid approval + live source "
                       "executes exactly once")


if __name__ == "__main__":
    unittest.main()
