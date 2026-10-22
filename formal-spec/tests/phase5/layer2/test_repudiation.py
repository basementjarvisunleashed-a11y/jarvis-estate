"""Phase 5 Layer 2 -- Repudiation controls (T-9 denied authorship).

Threat: T-9 (threat-catalogue.md section 4).
Controls: C-21 (approval objects with digest + timestamp; one
accountable owner per handoff), C-30 (no proof, no done: unevidenced
completion claims refused) (control-matrix.md section 2).
Draft sections cited: capability-matrix.md CM-4 (the evidence
requirement names the evidence packet content that must exist before
the work can be called complete); trust-boundaries.md TB-4 (the
orchestrator is accountable for every handoff).

Checks:
- approval objects carry the digest and timestamp, sealed with one
  accountable owner (C-21)
- a consequential action without a sealed evidence packet is refused
  (C-30; T-3's no-proof-no-done control)
- an evidence packet bound to a different intent is refused
  (the packet must be non-repudiable: digest-bound)
"""

import sys
import unittest
from datetime import timedelta

sys.path.insert(0, ".")
from estate import (Clock, SessionRegistry, ApprovalStore,
                    ArtifactStore, EvidencePacket, approval_digest,
                    intent_of, Refusal)


def fresh():
    clock = Clock()
    sessions = SessionRegistry(clock)
    approvals = ApprovalStore(clock, sessions)
    artifacts = ArtifactStore(clock)
    evidence = EvidencePacket(clock, artifacts, owner="orchestrator")
    device = sessions.enroll("HgX-iphone")
    sessions.complete_enrollment(device.session_id)
    return clock, sessions, approvals, artifacts, evidence, \
        device.session_id


def grant_intent(approvals, clock, approval_id="intent-rep",
                 sid=None):
    expiry = (clock.now() + timedelta(seconds=3600)).isoformat()
    intent = intent_of(approval_id, target="t", effect="e", scope="s",
                       expiry_iso=expiry)
    record, _ = approvals.grant(intent, sid)
    return record


class TestApprovalObjects(unittest.TestCase):
    """C-21: approval objects with digest + timestamp; one accountable
    owner per handoff."""

    def test_packet_carries_digest_and_timestamp(self):
        clock, sessions, approvals, artifacts, evidence, sid = fresh()
        record = grant_intent(approvals, clock, sid=sid)
        digest = artifacts.seal("artifact-r1", "observation", revision="v1")
        packet = evidence.seal_packet("packet-1", record,
                                      [("artifact-r1", digest)],
                                      observation="tool executed, observed")
        self.assertEqual(packet["approval_digest"], record.digest)
        self.assertEqual(packet["approval_timestamp"], record.timestamp)
        self.assertEqual(packet["owner"], "orchestrator")
        # The artifact digest inside the packet matches the sealed one:
        # the packet cannot later disown its contents.
        self.assertEqual(packet["artifact_refs"][0][1], digest)

    def test_packet_with_tampered_artifact_refused(self):
        clock, sessions, approvals, artifacts, evidence, sid = fresh()
        record = grant_intent(approvals, clock, sid=sid)
        digest = artifacts.seal("artifact-r2", "observation", revision="v1")
        artifacts.artifacts["artifact-r2"]["content"] = "changed"
        with self.assertRaises(Refusal) as ctx:
            evidence.seal_packet("packet-2", record,
                                 [("artifact-r2", digest)],
                                 observation="observation")
        self.assertEqual(ctx.exception.cause, "artifact-digest-mismatch")


class TestEvidencePacketRequirement(unittest.TestCase):
    """C-30, CM-4: no proof, no done."""

    def test_consequential_without_packet_refused(self):
        clock, sessions, approvals, artifacts, evidence, sid = fresh()
        record = grant_intent(approvals, clock, sid=sid)
        with self.assertRaises(Refusal) as ctx:
            evidence.execute_consequential(record, "packet-never-sealed")
        self.assertEqual(ctx.exception.cause, "no-proof-no-done")

    def test_consequential_with_packet_executes(self):
        clock, sessions, approvals, artifacts, evidence, sid = fresh()
        record = grant_intent(approvals, clock, sid=sid)
        digest = artifacts.seal("artifact-r3", "observation", revision="v1")
        evidence.seal_packet("packet-3", record,
                             [("artifact-r3", digest)],
                             observation="observed")
        packet = evidence.execute_consequential(record, "packet-3")
        self.assertEqual(packet["packet_id"], "packet-3")

    def test_packet_bound_to_different_intent_refused(self):
        clock, sessions, approvals, artifacts, evidence, sid = fresh()
        record = grant_intent(approvals, clock, approval_id="intent-a",
                              sid=sid)
        other = grant_intent(approvals, clock, approval_id="intent-b",
                             sid=sid)
        digest = artifacts.seal("artifact-r4", "observation", revision="v1")
        evidence.seal_packet("packet-4", record,
                             [("artifact-r4", digest)],
                             observation="observed")
        with self.assertRaises(Refusal) as ctx:
            evidence.execute_consequential(other, "packet-4")
        self.assertEqual(ctx.exception.cause, "packet-digest-mismatch")


if __name__ == "__main__":
    unittest.main()
