"""Phase 5 Layer 2 -- Honest-limitation controls (Q5).

Threats: T-26 (L) unverified privacy claim, T-28 (L) procedural
isolation's ceiling, per threat-catalogue.md section 9.
Controls: C-28 (no privacy property asserted in evidence);
control-matrix.md section 5 (the L0 compensations: three-plane
enforcement, key custody asserted in tests, sealed logged denials;
"what L0 cannot do" named as T-28).

Draft sections cited: threat-catalogue.md section 9 (Q5 named
threats); control-matrix.md sections 2 (C-28), 3 (honest marks), 5
(L0 compensations); isolation-upgrade-roadmap.md (the honest upgrade
path T-28 points at).

Checks:
- no privacy property is asserted from protocol-shape proofs: any
  evidence output carrying privacy vocabulary is refused (C-28, T-26)
- direct cross-plane calls raise PlaneViolation -- the one mechanical
  enforcement L0 has (compensation 2; T-28)
- every control/data component asserts it holds no ceremony key bytes
  (compensation 3)
- every refusal is a sealed, logged denial, present in the evidence
  log (compensation 4)
- the compensations are mapped to the tests that exercise them
  (documentation of coverage, not a claim of completeness)
"""

import os
import sys
import unittest
from datetime import timedelta

sys.path.insert(0, ".")
from estate import (Clock, SessionRegistry, ApprovalStore,
                    cross_plane, PlaneViolation, assert_key_custody,
                    KEY_CUSTODY_ASSERTIONS, scan_no_privacy_claim,
                    refusal_log, intent_of, Refusal)


class TestNoPrivacyPropertyAsserted(unittest.TestCase):
    """C-28, T-26 (L): protocol-shape ZK is not a control. A test that
    asserts the model refuses to claim privacy guarantees it doesn't
    have."""

    def test_zero_knowledge_claim_in_evidence_refused(self):
        with self.assertRaises(Refusal) as ctx:
            scan_no_privacy_claim(
                "the packet is zero-knowledge verified end to end",
                origin="evidence-packet-9")
        self.assertEqual(ctx.exception.cause, "privacy-property-asserted")

    def test_zk_proof_claim_in_log_refused(self):
        with self.assertRaises(Refusal):
            scan_no_privacy_claim("sealed with zk-proof guarantees",
                                  origin="session-log")

    def test_honest_evidence_passes(self):
        self.assertEqual(scan_no_privacy_claim(
            "approval digest 9f2c..., session active, read-after-write "
            "verified where supported", origin="evidence-packet-10"),
            "no-privacy-claim")


class TestPlaneViolation(unittest.TestCase):
    """Compensation 2 (control-matrix.md section 5): three-plane
    enforcement in the deployment build -- direct cross-plane calls
    raise PlaneViolation. T-28 names what L0 cannot do; this is what
    L0 CAN do, mechanically."""

    def test_tool_plane_calling_orchestrator_refused(self):
        with self.assertRaises(PlaneViolation) as ctx:
            cross_plane("tool", "orchestrator", "approve(intent-1)")
        self.assertEqual(ctx.exception.cause, "plane-violation")

    def test_subagent_plane_calling_tool_plane_refused(self):
        with self.assertRaises(PlaneViolation):
            cross_plane("subagent", "tool", "write(file)")

    def test_same_plane_call_allowed(self):
        self.assertEqual(cross_plane("orchestrator", "orchestrator",
                                     "delegate(task)"), "same-plane-ok")


class TestKeyCustody(unittest.TestCase):
    """Compensation 3 (control-matrix.md section 5): key custody
    asserted in tests -- no control/data component holds ceremony key
    bytes."""

    def test_every_component_asserts_no_key_bytes(self):
        for component in KEY_CUSTODY_ASSERTIONS:
            assertion = assert_key_custody(component)
            self.assertIn("holds no ceremony key bytes", assertion)

    def test_unasserted_component_refused(self):
        with self.assertRaises(Refusal) as ctx:
            assert_key_custody("mystery-component")
        self.assertEqual(ctx.exception.cause, "component-not-asserted")


class TestSealedLoggedDenials(unittest.TestCase):
    """Compensation 4 (control-matrix.md section 5): every refusal in
    the model is a sealed, logged denial -- the rejections log carries
    the cause of every refusal."""

    def test_refusal_lands_in_rejection_log(self):
        path = os.environ.get("PHASE5_REJECTION_LOG")
        self.assertIsNotNone(path, "run.sh must set PHASE5_REJECTION_LOG")
        clock = Clock()
        sessions = SessionRegistry(clock)
        approvals = ApprovalStore(clock, sessions)
        with self.assertRaises(Refusal):
            approvals.grant(intent_of("x", "t", "e", "s",
                                      (clock.now() +
                                       timedelta(seconds=60)).isoformat()),
                            "session-never-enrolled")
        with open(path, encoding="utf-8") as fh:
            log_text = fh.read()
        self.assertIn("unknown-session", log_text)


class TestCompensationCoverageMap(unittest.TestCase):
    """Documentation of which test exercises which L0 compensation
    (control-matrix.md section 5). This is a coverage map, not a
    completeness claim."""

    COMPENSATIONS = {
        "doctrine-as-enforcement":
            "test_elevation.py::TestCustodyBoundaries (TB-11...TB-15 "
            "crossing rules)",
        "three-plane-enforcement":
            "test_honest_limits.py::TestPlaneViolation",
        "key-custody-asserted":
            "test_honest_limits.py::TestKeyCustody",
        "sealed-logged-denials":
            "test_honest_limits.py::TestSealedLoggedDenials",
        "l0-ceiling-named":
            "threat-catalogue.md T-28 (L); upgrade path in "
            "isolation-upgrade-roadmap.md -- no mechanical test, "
            "honestly documented",
    }

    def test_every_compensation_has_a_named_exerciser(self):
        self.assertEqual(len(self.COMPENSATIONS), 5)
        for name, exerciser in self.COMPENSATIONS.items():
            self.assertTrue(exerciser, name)


if __name__ == "__main__":
    unittest.main()
