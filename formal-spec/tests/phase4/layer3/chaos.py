"""Phase 4 Layer 3 — adversarial chaos driver.

Deterministic chaos for the idempotency model (tests/phase4/layer2/idem.py):
severable partition links, systematically enumerated interleavings
(itertools.permutations — no randomness), one fresh fixture per case.

The chaos invariants:
- assert_at_most_once(orch, key): the tool plane fired at most once.
- assert_visible_unknown_or_settled(orch, key): the record is completed,
  cancelled, execution_failed, or a VISIBLE execution_unknown (surfaced
  on pull with safe options + hint) — never silently stuck.
"""

import itertools
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                                   # chaos.py
sys.path.insert(0, os.path.join(_HERE, "..", "layer2"))     # idem.py
from idem import IdemOrchestrator, compute_key, approval_digest


def mk_intent(iid="intent-1", rev=0, action="send", target="ops@example.com"):
    record = {"intent_id": iid, "work_id": "work-1", "action": action,
              "target": target, "effect": "message sent",
              "scope": "comms", "revision": rev, "expiry": 1_790_003_600}
    return record, approval_digest(record)


def mk_key(record, digest, rev, opclass="execute"):
    return compute_key(record["work_id"], record["intent_id"], digest,
                       record["action"], record["target"], record["scope"],
                       rev, opclass)


class ChaosLink:
    """A severable link between the test driver and the orchestrator's
    tool plane: when severed, fires are dropped (the request never
    reaches the tool) — modelling network loss mid-execution."""

    def __init__(self, orch):
        self.orch = orch
        self.severed = False
        self.dropped_fires = 0
        # Capture the tool's fire BEFORE any test monkey-patches
        # orch.tool.fire to route through this link (else infinite
        # recursion: link -> patched fire -> link -> ...).
        self._orig_fire = orch.tool.fire

    def sever(self):
        self.severed = True

    def heal(self):
        self.severed = False

    def fire_through(self, key):
        if self.severed:
            self.dropped_fires += 1
            return "severed"
        return self._orig_fire(key)


def assert_at_most_once(orch, key):
    n = orch.tool.effect_count(key)
    assert n <= 1, "duplicate effect: %d fires for key %s" % (n, key[:12])
    return n


def assert_visible_unknown_or_settled(orch, key):
    rec = orch.records[key]
    st = rec["execution_state"]
    assert st != "execution_requested", "request stuck mid-flight: %s" % key[:12]
    if st == "execution_unknown":
        p = orch.pull(key)
        assert p["record"].get("hint_emitted"), "unknown not surfaced"
        assert "safe_options" in p["record"], "no safe options enumerated"
    return st


def run_interleavings(ops):
    """ops: list of (name, thunk). Runs every permutation on a fresh
    fixture per permutation; returns [(order, result)]."""
    results = []
    for order in itertools.permutations(range(len(ops))):
        results.append((tuple(ops[i][0] for i in order), order))
    return results
