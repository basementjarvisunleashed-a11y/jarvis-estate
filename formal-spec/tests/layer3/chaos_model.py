"""Layer 3 contract-level models for the chaos scenarios.

Two estate mechanisms the canonical scenarios exercise have no runtime
artifact in this repository yet — the evidence-packet completion writer
and the usage router. This module implements their CONTRACTS, grounded
in the ratified texts, so the scenarios can run against something real
and fail:

- The completion writer (Paper IV section 8.2, Layer 1 rule 5; packet
  fields from `contracts/events.md` section 4, event 6 / Paper IV
  section 6.6): the writer validates packet completeness against the
  brief's acceptance tests atomically with the `verifying -> completed`
  transition. A packet missing a required field, missing a required
  test result, carrying a failed test, mismatched to the artifact
  revision (INV-E2), or hiding a stale observation instead of marking
  it (INV-E3) is rejected — returned for completion, never accepted as
  complete.
- The router reference (INV-R1, INV-R5): a router returns
  recommendations under a named policy, never approvals. If the
  external backend is unreachable, routing falls back to local policy
  and the fallback is logged; no work item is ever routed without a
  policy, and a recommendation is not an input to any guard.

The gaps are stated where they live: these are contract-level models of
runtime mechanisms, not the runtime. The scenarios that depend on real
clients, devices, or the estate router (CH-5's refresh protocol, CH-6's
backend) say so in their docstrings and in the run report.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "layer1"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "layer2"))

import spec_model as sm  # noqa: E402,F401  (re-exported for the suite)
from work_item_sim import WorkItem, base_intent, render_state  # noqa: E402,F401

# Packet fields per contracts/events.md section 4 (evidence_packet_created
# payload) — every one required; `gaps` is a required field by name
# (INV-E4: its omission is a schema violation, not a style choice).
REQUIRED_PACKET_FIELDS = (
    "packet_id", "work_id", "revision", "artifact_refs",
    "source_observations", "test_results", "approval_refs", "gaps",
    "created_at",
)


def make_packet(work_id="work-1", revision=0, tests=("t1", "t2", "t3"),
                observations=None, **overrides):
    """A complete, valid evidence packet, unless overridden."""
    packet = {
        "packet_id": "pkt-1",
        "work_id": work_id,
        "revision": revision,
        "artifact_refs": ["artifact://work-1/rev-0"],
        "source_observations": observations if observations is not None
        else [{"source": "live-feed", "observed_at": 90,
               "fresh_until": 10 ** 9, "status": "fresh"}],
        "test_results": {t: "passed" for t in tests},
        "approval_refs": ["decision://work-1/1"],
        "gaps": [],
        "created_at": 95,
    }
    packet.update(overrides)
    return packet


def validate_evidence_packet(packet, required_tests, now):
    """Return the list of contract violations in the packet (empty =
    valid). Fail-closed: absence is a violation, never a default."""
    errors = []
    for field in REQUIRED_PACKET_FIELDS:
        if field not in packet:
            errors.append(f"missing-field:{field}")
    results = packet.get("test_results")
    if isinstance(results, dict):
        for t in required_tests:
            if t not in results:
                errors.append(f"missing-test-result:{t}")
            elif results[t] != "passed":
                errors.append(f"test-not-passed:{t}")
    for obs in packet.get("source_observations") or []:
        # A stale observation must be MARKED stale in the packet
        # (INV-E3); an unmarked stale reading is a violation.
        if obs.get("fresh_until", now) < now \
                and obs.get("status") != "stale":
            errors.append("unmarked-stale-observation")
    return errors


def completion_writer(item, packet, required_tests, artifact_revision,
                      now):
    """Attempt the atomic completion write: packet validation and the
    spec's completion guard together. Returns (accepted, errors)."""
    errors = validate_evidence_packet(packet, required_tests, now)
    if packet.get("revision") != artifact_revision:
        errors.append("packet-revision-mismatch")
    if errors:
        return False, errors
    if not sm.can_enter_completed({
            "work_state": item.work_state,
            "evidence_exists": item.evidence_exists,
            "acceptance_passed": item.acceptance_result,
            "failure_observed": item.failure_observed,
            "delegated_claim": item.claim_asserted}):
        return False, ["completion-guard"]
    return True, []


class RouterReference:
    """The usage router's contract in miniature (INV-R1, INV-R5)."""

    def __init__(self):
        self.backend_up = True
        self.fallback_events = []

    def recommend(self, work_id):
        """Return a recommendation under a named policy. Never an
        approval; never policy-less."""
        if self.backend_up:
            return {"policy": "external-backend", "kind": "recommendation",
                    "work_id": work_id}
        self.fallback_events.append(work_id)
        return {"policy": "local-policy", "kind": "recommendation",
                "work_id": work_id}


def client_render(cached_render, authoritative_state, observation_status,
                  source_freshness, operator_pause=False):
    """The client rendering contract (INV-C4): on read, the
    authoritative backend state governs. A cached rendering — however
    fresh it felt when stored — never overrides it."""
    return render_state(authoritative_state, observation_status,
                        source_freshness, operator_pause)
