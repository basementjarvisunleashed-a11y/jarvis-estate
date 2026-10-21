"""Phase 2, Layer 3 — chaos tests (Paper IV section 8.2, CH-1..CH-10).

Fault injection into running work items, asserting that the invariants
hold and the failure is visible. The scenarios run against the Layer 2
work-item simulator (the spec's guards, mechanised) plus the Layer 3
contract models in `chaos_model.py` (completion writer, router
reference, client rendering).

Honest scope, stated once here and repeated per scenario: this suite
injects faults at the CONTRACT level — replayed decisions, mutated
intents, stale readings, malformed packets — because the estate's
devices, clients, and router are runtimes outside this repository.
Where a scenario's full form needs that runtime, the test asserts the
closest contract-level equivalent and the gap is recorded in the run
report. A scenario is never silently replaced by an easier one.

Run:  python3 -m unittest test_layer3_chaos -v   (from this directory)
or:   ./run.sh
"""

import unittest

import chaos_model as cm
from chaos_model import RouterReference, WorkItem, base_intent, \
    client_render, completion_writer, make_packet, render_state


def item_at_gate(expiry=100, now=10, **intent_overrides):
    item = WorkItem(intent=base_intent(expiry=expiry, **intent_overrides),
                    now=now)
    assert item.drive_to_awaiting_approval()
    return item


def item_in_verifying(with_evidence=True, acceptance=True):
    item = WorkItem(intent=base_intent(), now=10)
    assert item.attempt_event("brief_received")
    assert item.attempt_event("brief_accepted")
    assert item.attempt_event("plan_created")
    # T6 is a JOINT firing (artifact_produced + evidence_packet_created
    # together, events.md section 3); the cross-built legal table
    # represents it as one transition, so one firing stands for the pair.
    assert item.attempt_event("artifact_produced")
    assert item.work_state == "verifying"
    if with_evidence:
        item.submit_evidence()
    item.set_acceptance_result(acceptance)
    return item


class TestChaosScenarios(unittest.TestCase):

    def test_ch01_device_offline_during_approval(self):
        # CH-1 (INV-A5, INV-S2): the tap is queued offline and replayed
        # on reconnect. The server validates the replayed decision
        # against CURRENT intent state; an offline gesture is never
        # authority by itself.
        # (a) Intent expired while the device was offline -> replay
        # rejected.
        item = item_at_gate(expiry=100, now=10)
        self.assertTrue(item.tap())            # the offline tap (queued)
        item.tick(200)                         # time passes; now=210
        self.assertFalse(item.record())        # replay on reconnect
        self.assertEqual(item.record_failure_guard(), "approval-expired")
        self.assertNotEqual(item.approval_state, "recorded")
        self.assertFalse(item.attempt_event("approval_granted"))
        self.assertEqual(item.executions, 0)
        # (b) Intent mutated while offline -> replay rejected.
        item = item_at_gate(expiry=100, now=10)
        self.assertTrue(item.tap())
        item.mutate_intent("target", "x/@someone_else")
        self.assertFalse(item.record())
        self.assertEqual(item.record_failure_guard(), "digest-mismatch")
        # (c) Nothing changed -> the replay is validated and recorded;
        # authority comes from the server's validation, not the tap:
        # before the replay, a grant attempt is refused.
        item = item_at_gate(expiry=100, now=10)
        self.assertTrue(item.tap())
        self.assertFalse(item.attempt_event("approval_granted"))
        self.assertTrue(item.record())         # replay accepted by server
        self.assertTrue(item.attempt_event("approval_granted"))
        # (d) INV-S2 aspect: a paused item renders as paused, never
        # failed — including while observation is degraded.
        self.assertEqual(render_state("paused", "observed", "fresh",
                                      operator_pause=True), "paused")
        self.assertEqual(render_state("paused", "observed", "stale",
                                      operator_pause=True), "paused")

    def test_ch02_approval_expiry_mid_review(self):
        # CH-2 (INV-A4): the operator is reading the card when expiry
        # passes; the grant arrives one second after expiry. Expected:
        # grant rejected, item transitions to in_progress per T10, a
        # fresh intent may be issued, and the refusal carries its
        # reason (the contract-level form of "the operator is told the
        # intent lapsed").
        item = item_at_gate(expiry=50, now=49)
        self.assertTrue(item.tap())
        self.assertTrue(item.record())
        item.tick(2)                           # now = 51 = expiry + 1
        self.assertEqual(item.gate_failure_guard(), "approval-expired")
        self.assertFalse(item.attempt_event("approval_granted"))
        self.assertEqual(item.executions, 0)
        self.assertTrue(item.attempt_event("approval_expired"))  # T10
        self.assertEqual(item.work_state, "in_progress")
        # A fresh intent (new revision) may be issued and approved.
        item.new_intent(base_intent(revision=1, expiry=500))
        self.assertTrue(item.attempt_event("approval_requested"))
        self.assertTrue(item.tap())
        self.assertTrue(item.record())
        self.assertTrue(item.attempt_event("approval_granted"))
        self.assertEqual(item.executions, 1)

    def test_ch03_intent_change_after_card_render(self):
        # CH-3 (INV-A3): card rendered from revision N; intent revised
        # to N+1 (target corrected) before the tap lands. The tap
        # carries digest(N); the server recomputes against N+1 and
        # rejects; the new revision is what a new card must render.
        # The race, replayed exactly: tap first (digest of revision 0
        # captured), intent revised second, record attempted third.
        item = item_at_gate(expiry=100, now=10)   # revision 0
        self.assertTrue(item.tap())               # digest(0) captured
        item.intent = base_intent(revision=1,
                                  target="x/@corrected_target",
                                  expiry=100)
        item.revision = 1
        self.assertFalse(item.record())
        self.assertEqual(item.record_failure_guard(), "digest-mismatch")
        self.assertFalse(item.attempt_event("approval_granted"))
        self.assertEqual(item.executions, 0)
        # The current (N+1) intent is exposed for the new card.
        self.assertEqual(item.intent["revision"], 1)
        self.assertEqual(item.intent["target"], "x/@corrected_target")

    def test_ch04_duplicate_tap(self):
        # CH-4 (INV-A6): operator taps twice; the network duplicates
        # one tap, delivering three grants. One recorded decision, one
        # execution at most; later grants return the recorded outcome.
        item = item_at_gate(expiry=100, now=10)
        self.assertTrue(item.tap())
        self.assertTrue(item.record())
        self.assertTrue(item.attempt_event("approval_granted"))   # 1st
        self.assertFalse(item.attempt_event("approval_granted"))  # 2nd
        self.assertFalse(item.attempt_event("approval_granted"))  # 3rd
        self.assertFalse(item.duplicate_tap())   # stutter: recorded
        # outcome returned, nothing changes
        self.assertEqual(item.recorded_decisions, 1)
        self.assertEqual(item.executions, 1)
        self.assertEqual(item.work_state, "executing")

    def test_ch05_backend_change_before_client_refresh(self):
        # CH-5 (INV-C4, INV-S4, INV-E2). Full form needs the Paper III
        # client and its revision-token refresh protocol — no such
        # artifact exists in this repository (INV-C4 is catalogue-
        # pending for exactly this reason). Contract-level equivalents
        # asserted here:
        # (a) A cached `operational` rendering never overrides the
        # authoritative state on read: backend now says failed.
        self.assertEqual(
            client_render("operational", "failed", "observed", "fresh"),
            "failed")
        # (b) Authoritative state moved on and data aged: the client
        # renders reduced confidence, not the cached full confidence.
        self.assertEqual(
            client_render("operational", "in_progress", "observed",
                          "stale"),
            "reduced_confidence")
        # (c) Revision binding (INV-E2): a packet written against
        # revision 1 cannot complete an artifact now at revision 2.
        item = item_in_verifying()
        packet = make_packet(revision=1)
        accepted, errors = completion_writer(
            item, packet, ("t1", "t2", "t3"), artifact_revision=2,
            now=10)
        self.assertFalse(accepted)
        self.assertIn("packet-revision-mismatch", errors)
        accepted, errors = completion_writer(
            item, make_packet(revision=2), ("t1", "t2", "t3"),
            artifact_revision=2, now=10)
        self.assertTrue(accepted, errors)

    def test_ch06_router_backend_down(self):
        # CH-6 (INV-R1, INV-R5). Full form needs the estate usage
        # router — runtime outside this repository (INV-R1/R5 are
        # catalogue-pending; spec/router-policy.md is a planned Phase 6
        # artifact). Contract-level equivalents asserted here:
        router = RouterReference()
        rec = router.recommend("work-1")
        self.assertEqual(rec["policy"], "external-backend")
        router.backend_up = False                     # the fault
        rec = router.recommend("work-2")
        # Fallback to local policy, and the fallback is logged.
        self.assertEqual(rec["policy"], "local-policy")
        self.assertEqual(router.fallback_events, ["work-2"])
        # No item is routed without a policy, and a recommendation —
        # from either policy — never crosses the consequence boundary:
        # an item holding only a recommendation cannot execute.
        item = item_at_gate(expiry=100, now=10)
        item.router_recommendation = rec              # all it holds
        self.assertFalse(item.attempt_event("approval_granted"))
        self.assertEqual(item.gate_failure_guard(),
                         "approval-not-recorded")
        self.assertEqual(item.executions, 0)

    def test_ch07_stale_live_source(self):
        # CH-7 (INV-S1, INV-S4, INV-E3, INV-E5): the source stops
        # updating; readings age past fresh_until during verification.
        # The renderer downgrades, source-dependent guards fail closed,
        # and the packet marks the observation stale rather than
        # omitting it.
        item = WorkItem(intent=base_intent(), now=10)
        self.assertTrue(item.attempt_event("brief_received"))
        self.assertTrue(item.attempt_event("brief_accepted"))
        self.assertTrue(item.attempt_event("plan_created"))
        self.assertTrue(item.attempt_event("failure_observed",
                                           reading="blocking"))
        self.assertEqual(item.work_state, "blocked")
        item.set_freshness("stale")                   # the fault
        self.assertFalse(item.attempt_event("blockage_cleared"))
        self.assertEqual(
            render_state(item.work_state, "observed", "stale"),
            "reduced_confidence")
        # Packet side: an unmarked stale observation is a violation;
        # a marked one is the honest packet.
        stale_obs = [{"source": "live-feed", "observed_at": 5,
                      "fresh_until": 8, "status": "fresh"}]
        errors = cm.validate_evidence_packet(
            make_packet(observations=stale_obs), ("t1", "t2", "t3"),
            now=10)
        self.assertIn("unmarked-stale-observation", errors)
        marked_obs = [dict(stale_obs[0], status="stale")]
        errors = cm.validate_evidence_packet(
            make_packet(observations=marked_obs), ("t1", "t2", "t3"),
            now=10)
        self.assertNotIn("unmarked-stale-observation", errors)

    def test_ch08_subagent_completion_without_evidence(self):
        # CH-8 (INV-C3, INV-C5): the worker emits a fluent completion
        # claim with no artifact and no packet. The claim moves the
        # item to verifying at most; the completion guard fails; the
        # orchestrator is escalated with "claim without proof".
        item = WorkItem(intent=base_intent(), now=10)
        self.assertTrue(item.attempt_event("brief_received"))
        self.assertTrue(item.attempt_event("brief_accepted"))
        self.assertTrue(item.attempt_event("plan_created"))
        self.assertTrue(item.delegated_claim())       # the fault
        self.assertIn("claim without proof", item.escalations)
        # The claim alone has no road to completed from in_progress.
        self.assertFalse(item.attempt_event("acceptance_passed"))
        self.assertEqual(item.work_state, "in_progress")
        # At most, the T6 joint firing (artifact + packet asserted)
        # moves it to verifying — where the guard still refuses: no
        # evidence on file, no acceptance passed.
        self.assertTrue(item.attempt_event("artifact_produced"))
        self.assertEqual(item.work_state, "verifying")
        self.assertFalse(item.attempt_event("acceptance_passed"))
        self.assertEqual(item.completion_failure_guard(),
                         "completion-no-evidence")
        self.assertEqual(item.completions, 0)

    def test_ch09_digest_mismatch(self):
        # CH-9 (INV-A3): a single character flips in the intent's
        # target field in transit. The server's recomputed digest
        # mismatches, the decision is rejected, the attempt is logged
        # as a tamper signal, and no execution occurs. (The Phase 5
        # tripwire itself is future work; the signal it would consume
        # is produced and asserted here.)
        item = item_at_gate(expiry=100, now=10)
        self.assertTrue(item.tap())
        original = item.intent["target"]
        flipped = original[:-1] + ("G" if original[-1] != "G" else "g")
        self.assertEqual(len(flipped), len(original))
        self.assertNotEqual(flipped, original)
        item.intent = dict(item.intent, target=flipped)   # in transit
        if not item.record() \
                and item.record_failure_guard() == "digest-mismatch":
            item.tamper_signals.append(
                {"field": "target", "guard": "digest-mismatch"})
        self.assertEqual(len(item.tamper_signals), 1)
        self.assertFalse(item.attempt_event("approval_granted"))
        self.assertEqual(item.executions, 0)

    def test_ch10_missing_tests_in_evidence_packet(self):
        # CH-10 (INV-C2, INV-E4): three acceptance tests; the packet
        # arrives with results for two and the third absent. The
        # completion writer rejects the transition; the packet is
        # returned for completion — a guard failure, not a
        # documentation gap.
        required = ("t1", "t2", "t3")
        item = item_in_verifying()
        packet = make_packet(tests=("t1", "t2"))   # t3 section absent
        accepted, errors = completion_writer(
            item, packet, required, artifact_revision=0, now=10)
        self.assertFalse(accepted)
        self.assertIn("missing-test-result:t3", errors)
        # A failed test in the packet is likewise a guard failure.
        packet = make_packet()
        packet["test_results"]["t2"] = "failed"
        accepted, errors = completion_writer(
            item, packet, required, artifact_revision=0, now=10)
        self.assertFalse(accepted)
        self.assertIn("test-not-passed:t2", errors)
        # The `gaps` field omitted entirely: schema violation (INV-E4).
        packet = make_packet()
        del packet["gaps"]
        accepted, errors = completion_writer(
            item, packet, required, artifact_revision=0, now=10)
        self.assertFalse(accepted)
        self.assertIn("missing-field:gaps", errors)
        # Positive control: the complete packet completes.
        accepted, errors = completion_writer(
            item, make_packet(), required, artifact_revision=0, now=10)
        self.assertTrue(accepted, errors)
        self.assertTrue(item.attempt_event("acceptance_passed"))
        self.assertEqual(item.completions, 1)


if __name__ == "__main__":
    unittest.main()
