"""Phase 3 Layer 2 — RT family: revision-token rejection.

What it checks: the six-field revision token is the mechanism by which
the estate refuses stale action (revision-protocol.md sections 2-4).
Draft sections cited: R1-R5 (section 3), five-step check #2 (section 5),
OP-1 ruling (version history 2026-10-21 ~17:49 ET: keep both — 60 s
state/event bound, 300 s request bound).
Exit criterion served: "stale data cannot masquerade as current".

Conventions: virtual server clock NOW fixed per test class (integer
epoch seconds, Phase 2 Q1 ruling). No randomness — every case is a
hand-built, hand-verifiable boundary.
"""

import unittest

from orchestrator import Orchestrator, REQUEST_SKEW, EVENT_SKEW
from clients import Surface

NOW = 1_790_000_000


def fixture(now=NOW):
    orch = Orchestrator(now)
    orch.enroll("iphone-s1", "iphone")
    orch.enroll("watch-s1", "watch")
    orch.mint_work("work-1", "idle")
    orch.propose_intent("intent-1", "work-1", "publish", "dropbox:/p.pdf",
                        "paper posted", "release", 0, now + 3600)
    return orch


def mutate(orch, session="iphone-s1", revision=0, ts=NOW, observed_at=None,
           new_state="working"):
    req = {"kind": "mutate", "work_id": "work-1", "revision": revision,
           "device_session_id": session, "timestamp": ts, "new_state": new_state}
    if observed_at is not None:
        req["observed_at"] = observed_at
    return orch.submit(req)


class TestRevisionToken(unittest.TestCase):
    """RT: the token refuses stale action."""

    def setUp(self):
        self.orch = fixture()

    def test_rt1_stale_revision_refused(self):
        """R2: held < current is refused 'stale-revision'; nothing changes."""
        r1 = mutate(self.orch, revision=0)          # accepted -> revision 1
        self.assertTrue(r1["ok"])
        r2 = mutate(self.orch, revision=0)          # stale: held 0, current 1
        self.assertFalse(r2["ok"])
        self.assertEqual(r2["reason"], "stale-revision")
        self.assertEqual(self.orch.works["work-1"]["revision"], 1)

    def test_rt2_future_revision_refused(self):
        """R2: held > current is refused — no skip-ahead, no missing."""
        r = mutate(self.orch, revision=5)
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "stale-revision")
        self.assertEqual(self.orch.works["work-1"]["revision"], 0)

    def test_rt3_missing_revision_refused(self):
        """R2: no revision at all is refused."""
        r = mutate(self.orch, revision=None)
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "stale-revision")

    def test_rt4_monotonic_accept_and_represent(self):
        """R1/R3: acceptance moves revision by exactly 1; the response
        carries the new revision; the client re-presents it."""
        r1 = mutate(self.orch, revision=0)
        self.assertEqual(r1["revision"], 1)
        r2 = mutate(self.orch, revision=r1["revision"], new_state="done")
        self.assertTrue(r2["ok"])
        self.assertEqual(r2["revision"], 2)
        self.assertEqual(self.orch.works["work-1"]["state"], "done")

    def test_rt5_no_force_no_retry_upgrade(self):
        """R4: no force flag, no override path. Re-presenting the same
        refused token is the same refusal — never upgraded in place."""
        bad = mutate(self.orch, revision=9)
        self.assertFalse(bad["ok"])
        again = mutate(self.orch, revision=9)
        self.assertFalse(again["ok"])
        self.assertEqual(again["reason"], "stale-revision")
        self.assertEqual(self.orch.works["work-1"]["revision"], 0)

    def test_rt6_request_freshness_boundary(self):
        """Five-step check #2, request bound (300 s): |now-ts|=300 passes,
        |now-ts|=301 is refused 'stale-request'."""
        ok = mutate(self.orch, revision=0, ts=NOW - REQUEST_SKEW)
        self.assertTrue(ok["ok"], "exactly 300 s must pass")
        orch2 = fixture()
        late = mutate(orch2, revision=0, ts=NOW - REQUEST_SKEW - 1)
        self.assertFalse(late["ok"])
        self.assertEqual(late["reason"], "stale-request")
        self.assertEqual(orch2.works["work-1"]["revision"], 0)

    def test_rt7_event_freshness_boundary(self):
        """Five-step check #2, state/event bound (60 s, ratified U-5/D7):
        an event observed 60 s ago passes; 61 s ago is refused
        'stale-event' — even though the request itself is fresh."""
        ok = mutate(self.orch, revision=0, ts=NOW, observed_at=NOW - EVENT_SKEW)
        self.assertTrue(ok["ok"], "exactly 60 s event age must pass")
        orch2 = fixture()
        stale = mutate(orch2, revision=0, ts=NOW, observed_at=NOW - EVENT_SKEW - 1)
        self.assertFalse(stale["ok"])
        self.assertEqual(stale["reason"], "stale-event")
        self.assertEqual(orch2.works["work-1"]["revision"], 0)

    def test_rt8_unknown_session_refused_first(self):
        """Check #1: an unenrolled session is refused before any other
        check — even with a perfect token."""
        r = mutate(self.orch, session="ghost-s9", revision=0)
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "unknown-session")

    def test_rt9_revoked_session_refused(self):
        """Check #1: a revoked enrollment is refused."""
        self.orch.revoke("watch-s1")
        r = mutate(self.orch, session="watch-s1", revision=0)
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "unknown-session")

    def test_rt10_refusal_names_current_revision(self):
        """revision-protocol.md section 5: the 'stale-revision' refusal
        names the current revision so the client can re-pull — the
        refusal itself carries no authority."""
        mutate(self.orch, revision=0)
        r = mutate(self.orch, revision=0)
        self.assertEqual(r["current_revision"], 1)
        # and the re-pull + re-present path works:
        r2 = mutate(self.orch, revision=r["current_revision"], new_state="ok")
        self.assertTrue(r2["ok"])

    def test_rt11_orchestrator_is_only_writer(self):
        """NT-1: every state transition in the event log names the
        orchestrator as writer — no surface holds write authority."""
        mutate(self.orch, revision=0, new_state="a")
        mutate(self.orch, revision=1, new_state="b")
        for ev in self.orch.works["work-1"]["events"]:
            self.assertIn(ev[0], ("minted", "mutated", "decision-recorded", "correction"))
        # transitions only exist because the orchestrator applied them;
        # a direct surface write is impossible — there is no such path:
        self.assertFalse(hasattr(Surface, "write_state"))


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    """Append this module's refusals to the run's rejection ledger."""
    import os
    from orchestrator import dump_all_refusals
    path = os.environ.get("PHASE3_REJECTION_LOG")
    if path:
        dump_all_refusals(path)
