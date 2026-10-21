"""Phase 3 Layer 3 — adversarial chaos driver.

Deterministic chaos for the consistency model: no randomness, no threads,
no wall-clock. Adversarial timing is modeled as explicit, systematically
enumerated delivery permutations, each run against a fresh fixture
(itertools.permutations — the enumeration order is fixed). Partitions are
severable ChaosLinks that drop messages the orchestrator never sees. Clock
skew is an explicit per-client offset applied to the timestamps the client
puts on its requests.

Reuses the Layer 2 harness (orchestrator.py, clients.py, digest.py) —
extended, not duplicated. Python 3 standard library only.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "layer2"))

from orchestrator import Orchestrator  # noqa: E402
from clients import Surface  # noqa: E402

NOW = 1_790_000_000

# Probe once for the fixture's intent digest (deterministic — the fixture
# below is fixed, so the digest is fixed too).
_PROBE = Orchestrator(NOW)
_PROBE.enroll("iphone-s1", "iphone")
_PROBE.enroll("watch-s1", "watch")
_PROBE.mint_work("work-1", "idle")
_PROBE.propose_intent("intent-1", "work-1", "publish", "dropbox:/p.pdf",
                      "paper posted", "release", 0, NOW + 3600)
D = _PROBE.intents["intent-1"]["digest"]


def fixture(now=NOW):
    """Fresh estate: two enrolled sessions, one work item at revision 0,
    one live intent. Identical to the Layer 2 fixture."""
    orch = Orchestrator(now)
    orch.enroll("iphone-s1", "iphone")
    orch.enroll("watch-s1", "watch")
    orch.mint_work("work-1", "idle")
    orch.propose_intent("intent-1", "work-1", "publish", "dropbox:/p.pdf",
                        "paper posted", "release", 0, now + 3600)
    return orch


def decide(orch, session, digest=D, revision=0, ts=NOW, observed_at=None):
    req = {"kind": "decide", "intent_id": "intent-1", "work_id": "work-1",
           "revision": revision, "digest_seen": digest,
           "device_session_id": session, "timestamp": ts}
    if observed_at is not None:
        req["observed_at"] = observed_at
    return orch.submit(req)


def mutate(orch, session, new_state, revision=0, ts=NOW, observed_at=None):
    req = {"kind": "mutate", "work_id": "work-1", "revision": revision,
           "new_state": new_state, "device_session_id": session,
           "timestamp": ts}
    if observed_at is not None:
        req["observed_at"] = observed_at
    return orch.submit(req)


def record_verdict(case_id, invariants):
    """One row per adversarial case: case id, PASS, the invariants it
    defended. Written to PHASE3_L3_VERDICTS (set by run.sh)."""
    path = os.environ.get("PHASE3_L3_VERDICTS")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write("%s\tPASS\t%s\n" % (case_id, "; ".join(invariants)))


class ChaosLink:
    """A severable device<->orchestrator link. While severed, sends are
    dropped (recorded in .lost) and the sender gets a partition-lost
    pseudo-response — the orchestrator never sees the message, so a
    dropped decision can neither execute late nor be "replayed" by the
    network."""

    def __init__(self, name):
        self.name = name
        self.severed = False
        self.lost = []
        self.delivered = []

    def send(self, label, thunk):
        if self.severed:
            self.lost.append(label)
            return {"ok": False, "reason": "partition-lost", "label": label}
        resp = thunk()
        self.delivered.append(label)
        return resp


def run_interleavings(testcase, case_id, builders, check, invariants):
    """Every delivery permutation of builders [(label, fn)] runs against a
    fresh fixture; check(tc, orch, results, order) asserts the invariants;
    one verdict row is recorded per permutation."""
    n = 0
    for perm in itertools.permutations(range(len(builders))):
        n += 1
        orch = fixture()
        results, order = {}, []
        for i in perm:
            label, fn = builders[i]
            order.append(label)
            results[label] = fn(orch)
        check(testcase, orch, results, order)
        record_verdict("%s/p%02d" % (case_id, n), invariants)


def assert_single_decision(testcase, orch, digest=D):
    """The chaos invariants for one intent: exactly one recorded decision,
    exactly one execution, the recorded content identical under every
    interleaving, history append-only from the single writer."""
    testcase.assertEqual(len(orch.decisions), 1,
                         "more than one decision recorded: %r" % (orch.decisions,))
    d = orch.decisions["intent-1"]
    testcase.assertEqual(d["digest"], digest)
    testcase.assertEqual(d["intent_id"], "intent-1")
    recs = [e for e in orch.sealed_log if e[0] == "decision-recorded"]
    testcase.assertEqual(len(recs), 1, "executions: %d" % len(recs))
    testcase.assertEqual(orch.works["work-1"]["revision"], 1)
    testcase.assertEqual(set(orch.works["work-1"]["history"].keys()), {0, 1})


def assert_no_decision(testcase, orch):
    """Nothing recorded, nothing executed, work untouched."""
    testcase.assertEqual(len(orch.decisions), 0)
    recs = [e for e in orch.sealed_log if e[0] == "decision-recorded"]
    testcase.assertEqual(recs, [])
    testcase.assertEqual(orch.works["work-1"]["revision"], 0)


def assert_loser_path(testcase, resp):
    """The loser's only legal outcomes: refused naming the current revision
    (then re-pull), or the existing decision returned as a read — never a
    second execution, never a second record."""
    ok = (not resp.get("ok") and resp.get("reason") == "stale-revision"
          and resp.get("current_revision") == 1) or \
         (resp.get("ok") and resp.get("status") == "already-recorded")
    testcase.assertTrue(ok, "illegal loser outcome: %r" % (resp,))
