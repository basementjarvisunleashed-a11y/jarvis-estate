"""Phase 2, Layer 2 — property-based tests (Paper IV section 8.2).

Generated inputs, asserted invariants, over the Layer 1 guard model
(`work_item_sim.py`, built on `tests/layer1/spec_model.py`). Python 3
stdlib only: `unittest` + `random` with FIXED seeds, recorded here and
in the run log so every run is reproducible and shrinkable by hand.

  PT-1  Approval mutation fuzz        (INV-A2, INV-A3, INV-A7)
  PT-2  Expiry sweep                  (INV-A4)
  PT-3  Duplicate decision storm      (INV-A6, PO-9)
  PT-4  Random event sequences        (INV-C1–C5, INV-A1, INV-E1,
                                       PO-1, PO-2, PO-11)
  PT-5  Stale source injection        (INV-S1, INV-S4, INV-E5, PO-10)

Run:  python3 -m unittest test_layer2_properties -v   (from this dir)
or:   ./run.sh

The suite writes its rejection ledger — every illegal action the
generators attempted and the machine refused, by guard — to
tests/evidence/<YYYY-MM-DD>-layer2-rejections.log at teardown
(the filename is date-derived so a re-run never overwrites a prior
run's evidence; fixed 2026-10-21 after a hardcoded 2026-10-20 name
overwrote the previous day's local copy — the 2026-10-20 data
survives in the committed repository and the 2026-10-20 run report).
"""

import random
import unittest
from datetime import datetime
from pathlib import Path

import work_item_sim as sim
from work_item_sim import WorkItem, base_intent, render_state

EVIDENCE = Path(__file__).resolve().parents[1] / "evidence"
REJECTION_LOG = EVIDENCE / f"{datetime.now():%Y-%m-%d}-layer2-rejections.log"

# Fixed seed sets (recorded; do not change without noting it in the log).
PT1_SEEDS = (20261020, 20261021, 20261022)
PT2_SEED = 20261023
PT3_SEED = 20261024
PT4_SEEDS = (20261025, 20261026, 20261027, 20261028, 20261029)
PT5_SEED = 20261030

MUTATIONS = {
    "intent_id": "intent-999",
    "work_id": "work-999",
    "action": "delete_post",
    "target": "x/@someone_else",
    "effect": "delete",
    "scope": "all_posts",
    "revision": 99,
    "expiry": 10 ** 9,
}

YEAR = 31_536_000  # seconds, for the PT-2 expiry sweep


def fresh_item_at_gate(rng, expiry=100, now=10):
    """A work item legitimately at awaiting_approval with a live intent."""
    item = WorkItem(intent=base_intent(expiry=expiry), now=now)
    assert item.drive_to_awaiting_approval()
    return item


class TestPT1MutationFuzz(unittest.TestCase):
    """PT-1: random mutations to intent fields, applied between request
    and decision. Every mutated intent must fail the digest match; no
    `executing` transition may occur."""

    def test_mutations_between_tap_and_record_refused(self):
        attempts = 0
        for seed in PT1_SEEDS:
            rng = random.Random(seed)
            for _ in range(150):
                field = rng.choice(list(MUTATIONS))
                item = fresh_item_at_gate(rng)
                self.assertTrue(item.tap())
                item.mutate_intent(field, MUTATIONS[field])
                attempts += 1
                self.assertFalse(
                    item.record(),
                    f"seed={seed} field={field}: mutated intent recorded")
                self.assertEqual(item.approval_state, "tapped")
                # And the grant itself, attempted anyway, is refused.
                self.assertFalse(item.attempt_event("approval_granted"))
                self.assertEqual(item.executions, 0)
        self.assertEqual(attempts, 150 * len(PT1_SEEDS))

    def test_mutations_between_record_and_grant_refused(self):
        attempts = 0
        for seed in PT1_SEEDS:
            rng = random.Random(seed)
            for _ in range(150):
                field = rng.choice(list(MUTATIONS))
                item = fresh_item_at_gate(rng)
                self.assertTrue(item.tap())
                self.assertTrue(item.record())
                item.mutate_intent(field, MUTATIONS[field])
                attempts += 1
                self.assertFalse(
                    item.attempt_event("approval_granted"),
                    f"seed={seed} field={field}: mutated intent executed")
                self.assertEqual(item.executions, 0)
                self.assertEqual(item.work_state, "awaiting_approval")
        self.assertEqual(attempts, 150 * len(PT1_SEEDS))

    def test_unmutated_control_still_executes(self):
        # Positive control: the fuzz harness itself is not refusing
        # everything — an untouched intent records and executes.
        item = fresh_item_at_gate(random.Random(1))
        self.assertTrue(item.tap())
        self.assertTrue(item.record())
        self.assertTrue(item.attempt_event("approval_granted"))
        self.assertEqual(item.executions, 1)


class TestPT2ExpirySweep(unittest.TestCase):
    """PT-2: expiry timestamps from one year past to one year future,
    decision attempts at random offsets. Any attempt with
    now >= intent_expiry is rejected; no late grant is honoured."""

    def test_expiry_sweep(self):
        rng = random.Random(PT2_SEED)
        base_now = 1_000_000
        late = early = 0
        for _ in range(3000):
            expiry = base_now + rng.randint(-YEAR, YEAR)
            now = expiry + rng.randint(-3600, 3600)
            item = WorkItem(intent=base_intent(expiry=expiry), now=now)
            self.assertTrue(item.drive_to_awaiting_approval())
            self.assertTrue(item.tap())
            if now >= expiry:
                late += 1
                self.assertFalse(
                    item.record(),
                    f"now={now} expiry={expiry}: late tap recorded")
                self.assertFalse(item.attempt_event("approval_granted"))
                self.assertEqual(item.executions, 0)
            else:
                early += 1
                self.assertTrue(
                    item.record(),
                    f"now={now} expiry={expiry}: live tap refused")
                self.assertTrue(item.attempt_event("approval_granted"))
                self.assertEqual(item.executions, 1)
        # Both branches must actually have been exercised at volume.
        self.assertGreater(late, 1000)
        self.assertGreater(early, 1000)

    def test_boundary_exactly_at_expiry_refused(self):
        # The boundary is strict (spec: now < expiry): an attempt at
        # exactly now == expiry is already late.
        item = WorkItem(intent=base_intent(expiry=500), now=500)
        self.assertTrue(item.drive_to_awaiting_approval())
        self.assertTrue(item.tap())
        self.assertFalse(item.record())
        self.assertFalse(item.attempt_event("approval_granted"))


class TestPT3DuplicateStorm(unittest.TestCase):
    """PT-3: 1–50 duplicate approval_granted deliveries per intent,
    multiplied again by network-level duplication. Exactly one recorded
    decision per intent; at most one consequential execution."""

    def test_duplicate_decision_storm(self):
        rng = random.Random(PT3_SEED)
        total_refused_duplicates = 0
        for _ in range(120):
            item = fresh_item_at_gate(rng)
            self.assertTrue(item.tap())
            self.assertTrue(item.record())
            duplicates = rng.randint(1, 50)
            network_multiplier = rng.randint(1, 3)
            deliveries = duplicates * network_multiplier
            grants = 0
            for _ in range(deliveries):
                grants += 1
                if item.attempt_event("approval_granted"):
                    self.assertEqual(grants, 1,
                                     "a duplicate grant executed")
                else:
                    total_refused_duplicates += 1
                # Interleaved duplicate taps and record retries are
                # likewise refused any power over the machine.
                if rng.random() < 0.5:
                    self.assertFalse(item.duplicate_tap())
                    total_refused_duplicates += 1
                if rng.random() < 0.3:
                    self.assertFalse(item.record())
                    total_refused_duplicates += 1
            self.assertEqual(item.recorded_decisions, 1)
            self.assertEqual(item.executions, 1)
        self.assertGreater(total_refused_duplicates, 1000)


class TestPT4RandomSequences(unittest.TestCase):
    """PT-4: arbitrary event sequences over the 19-event vocabulary plus
    environment actions (taps, records, mutations, clock ticks, evidence,
    acceptance outcomes, delegated claims, staleness), asserting after
    every accepted step: no completion without evidence and acceptance;
    no execution without a recorded valid approval; at most one
    execution; terminal states are never left."""

    ACTIONS = (
        list(sim.EVENTS)
        + ["tap", "record", "duplicate_tap", "mutate", "tick",
           "submit_evidence", "acceptance_pass", "acceptance_fail",
           "delegated_claim", "go_stale", "go_fresh"]
    )

    # State-aware generation (standard property-test practice): when the
    # item sits in `executing` or `verifying`, half the draws come from
    # the progress set for that state, so the completion path is
    # exercised at volume instead of being reached only by luck. The
    # other half — and every draw in raw sequences and other states —
    # stays uniform over the full action pool, failures included.
    PROGRESS = {
        "executing": ["execution_observed", "execution_started",
                      "failure_observed"],
        "verifying": ["submit_evidence", "acceptance_pass",
                      "acceptance_passed", "failure_observed"],
    }

    def pick_action(self, rng, item, guided):
        if guided and item.work_state in self.PROGRESS \
                and rng.random() < 0.5:
            return rng.choice(self.PROGRESS[item.work_state])
        return rng.choice(self.ACTIONS)

    def run_sequence(self, rng, steps, guided):
        intent = base_intent(
            expiry=rng.choice([30, 60, 100, 10 ** 6]),
            revision=0,
        )
        item = WorkItem(intent=intent, now=rng.randint(0, 20))
        if guided:
            # Half the sequences are driven down the happy path to the
            # approval gate first (tap + record included), so the random
            # tail exercises the deep states — executing, verifying,
            # terminal — and not only the shallow ones. The other half
            # are raw from birth: arbitrary order, arbitrary nonsense.
            item.drive_to_awaiting_approval()
            item.tap()
            item.record()
        terminal_state = None
        for _ in range(steps):
            action = self.pick_action(rng, item, guided)
            before = item.work_state
            if action in sim.EVENT_SET:
                item.attempt_event(action)
            elif action == "tap":
                item.tap()
            elif action == "record":
                item.record()
            elif action == "duplicate_tap":
                item.duplicate_tap()
            elif action == "mutate":
                field = rng.choice(list(MUTATIONS))
                item.mutate_intent(field, MUTATIONS[field])
            elif action == "tick":
                item.tick(rng.randint(1, 40))
            elif action == "submit_evidence":
                item.submit_evidence()
            elif action == "acceptance_pass":
                item.set_acceptance_result(True)
            elif action == "acceptance_fail":
                item.set_acceptance_result(False)
            elif action == "delegated_claim":
                item.delegated_claim()
            elif action == "go_stale":
                item.set_freshness("stale")
            elif action == "go_fresh":
                item.set_freshness("fresh")

            # --- invariants, asserted on the machine as it stands ---
            # Completion is judged on the snapshot taken at the
            # completion transition: PO-1 binds the preconditions at
            # that moment, and environment facts may legitimately
            # change afterwards without un-completing terminal work.
            if item.work_state == "completed":
                snap = item.completion_entry
                self.assertIsNotNone(snap)
                self.assertTrue(snap["evidence_exists"],
                                "completed without evidence (INV-C1)")
                self.assertTrue(snap["acceptance_result"],
                                "completed without acceptance (INV-C2)")
                self.assertFalse(snap["failure_observed"],
                                 "completed with a failure observed "
                                 "(INV-C2)")
                self.assertGreaterEqual(item.completions, 1)
            if item.work_state == "executing":
                entry = item.executing_entry
                self.assertIsNotNone(entry)
                self.assertEqual(entry["approval_state"], "recorded",
                                 "executing without recorded approval "
                                 "(INV-A1)")
                self.assertLess(entry["now"], entry["expiry"],
                                "executing on an expired approval "
                                "(INV-A4)")
                self.assertTrue(entry["digest_matched"],
                                "executing on a mutated intent (INV-A3)")
                self.assertEqual(entry["executions_by_digest_before"], 0,
                                 "second execution under one intent "
                                 "(INV-A6)")
            self.assertLessEqual(item.executions, 1,
                                 "more than one execution (PO-9)")
            if terminal_state is not None:
                self.assertEqual(item.work_state, terminal_state,
                                 "terminal state left (PO-11)")
            elif item.work_state in sim.TERMINAL:
                terminal_state = item.work_state
            _ = before
        return item

    def test_random_event_sequences(self):
        sequences = steps = completions = executions = 0
        for seed in PT4_SEEDS:
            rng = random.Random(seed)
            for i in range(400):
                n = rng.randint(8, 48)
                item = self.run_sequence(rng, n, guided=(i % 2 == 0))
                sequences += 1
                steps += n
                completions += item.completions
                executions += item.executions
        self.assertEqual(sequences, 400 * len(PT4_SEEDS))
        # The generator must actually reach the interesting states, or
        # the assertions above are vacuous.
        self.assertGreater(executions, 100)
        self.assertGreater(completions, 20)
        print(f"\nPT-4 totals: {sequences} sequences, {steps} attempted "
              f"steps, {executions} executions, {completions} completions "
              f"(all invariant assertions held)")


class TestPT5StaleSourceInjection(unittest.TestCase):
    """PT-5: source readings with fresh_until in the past, mixed with
    fresh readings. The renderer never outputs `operational` for a
    stale reading, and no source-dependent guard is satisfied by stale
    data."""

    def test_stale_readings_never_render_operational(self):
        rng = random.Random(PT5_SEED)
        stale = fresh = 0
        for _ in range(2000):
            freshness = rng.choice(["fresh", "stale"])
            state = rng.choice(
                ["in_progress", "verifying", "blocked", "executing"])
            rendered = render_state(state, "observed", freshness)
            if freshness == "stale":
                stale += 1
                self.assertNotEqual(rendered, "operational",
                                    "stale reading rendered operational "
                                    "(INV-S4)")
                self.assertEqual(rendered, "reduced_confidence")
            else:
                fresh += 1
                self.assertEqual(rendered, "operational")
        self.assertGreater(stale, 500)
        self.assertGreater(fresh, 500)

    def test_unavailable_observation_renders_unknown(self):
        # INV-S1: whatever the freshness, an unobservable state renders
        # as unknown — never operational.
        for freshness in ("fresh", "stale"):
            self.assertEqual(
                render_state("in_progress", "unavailable", freshness),
                "unknown")

    def test_stale_source_cannot_satisfy_guard(self):
        # PO-10: BlockageCleared (T8) is source-truth-dependent; with
        # stale sources it fails closed, with fresh sources it passes.
        rng = random.Random(PT5_SEED)
        refused = allowed = 0
        for _ in range(200):
            # Route: received -> accepted -> in_progress -> blocked
            # (failure_observed in its T5 blocking reading).
            item = WorkItem(intent=base_intent(), now=10)
            self.assertTrue(item.attempt_event("brief_received"))
            self.assertTrue(item.attempt_event("brief_accepted"))
            self.assertTrue(item.attempt_event("plan_created"))
            self.assertTrue(item.attempt_event("failure_observed",
                                              reading="blocking"))
            self.assertEqual(item.work_state, "blocked")
            item.set_freshness(rng.choice(["fresh", "stale"]))
            if item.source_freshness == "stale":
                self.assertFalse(item.attempt_event("blockage_cleared"))
                refused += 1
            else:
                self.assertTrue(item.attempt_event("blockage_cleared"))
                allowed += 1
        self.assertGreater(refused, 50)
        self.assertGreater(allowed, 50)


def tearDownModule():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 2 — Layer 2 REJECTION LOG (evidence)",
        "# Produced by tests/layer2/test_layer2_properties.py at teardown:",
        "# every action the generators attempted that the machine refused,",
        "# counted by the guard that refused it. A guard with a count here",
        "# has demonstrably rejected something; a guard absent from this",
        "# list was never exercised by refusal in this run.",
        f"# Written: {datetime.now().astimezone().isoformat()}",
        f"# Seeds: PT-1 {PT1_SEEDS}, PT-2 {PT2_SEED}, PT-3 {PT3_SEED}, "
        f"PT-4 {PT4_SEEDS}, PT-5 {PT5_SEED}",
        "",
        f"TOTAL REFUSED: {sum(sim.REJECTIONS.values())}",
        "",
        "By guard:",
    ]
    for guard, count in sim.REJECTIONS.most_common():
        lines.append(f"  {guard}: {count}")
    lines += ["", "Attempts / accepted, by action:"]
    for action in sorted(sim.ATTEMPTS):
        lines.append(f"  {action}: attempted {sim.ATTEMPTS[action]}, "
                     f"accepted {sim.ACCEPTED[action]}")
    REJECTION_LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
