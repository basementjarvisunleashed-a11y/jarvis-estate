"""Phase 2, Layer 1 — rendering-side invariant tests.

Fail-closed assertions against render_model.py, the reference renderer
for estate-state surfaces. Closes the Phase 2 rendering gap:
INV-E3 (missing evidence renders as missing), INV-S1/S2/S4 spot checks,
INV-S3 (degraded requires observed impairment), INV-S5 (shared-surface
redaction).

Run:  python3 -m unittest test_rendering_invariants -v   (from this directory)

Every test asserts the REJECTION / safe rendering, not just absence.
"""

import unittest

import render_model as rm


def svc(**over):
    base = {
        "service_id": "svc-1",
        "name": "Release Bot",
        "observed_state": "operational",
        "impairment": None,
        "evidence": {"packet_id": "pkt-1", "ref": "dropbox:/logs/pkt-1"},
        "fresh_until": 2_000_000_000,
        "now": 1_700_000_000,
        "restricted": {},
    }
    base.update(over)
    return base


class TestInvariantE3(unittest.TestCase):
    """INV-E3: missing evidence renders as missing."""

    def test_r_e3_01_missing_evidence_renders_missing(self):
        r = rm.render(svc(evidence=None))
        self.assertEqual(r["evidence_ref"], "missing")

    def test_r_e3_02_missing_evidence_never_operational(self):
        r = rm.render(svc(evidence=None, observed_state="operational"))
        self.assertNotEqual(r["status"], "operational")
        self.assertEqual(r["status"], "unknown")

    def test_r_e3_03_missing_evidence_zero_confidence(self):
        r = rm.render(svc(evidence=None))
        self.assertEqual(r["confidence"], 0.0)

    def test_r_e3_04_empty_evidence_dict_is_missing(self):
        r = rm.render(svc(evidence={}))
        self.assertEqual(r["evidence_ref"], "missing")
        self.assertEqual(r["status"], "unknown")

    def test_r_e3_05_present_evidence_renders_ref(self):
        r = rm.render(svc())
        self.assertEqual(r["evidence_ref"], "dropbox:/logs/pkt-1")


class TestInvariantS3(unittest.TestCase):
    """INV-S3: degraded requires observed impairment."""

    def test_r_s3_01_degraded_with_impairment_renders_degraded(self):
        r = rm.render(svc(
            observed_state="degraded",
            impairment={"observed_at": "2026-10-21T12:00:00Z",
                        "detail": "error rate 12%"}))
        self.assertEqual(r["status"], "degraded")

    def test_r_s3_02_degraded_without_impairment_never_degraded(self):
        r = rm.render(svc(observed_state="degraded", impairment=None))
        self.assertNotEqual(r["status"], "degraded")
        self.assertEqual(r["status"], "unknown")

    def test_r_s3_03_impairment_contradicts_operational(self):
        r = rm.render(svc(
            observed_state="operational",
            impairment={"observed_at": "2026-10-21T12:00:00Z",
                        "detail": "latency p99 9s"}))
        self.assertEqual(r["status"], "degraded")


class TestInvariantS5(unittest.TestCase):
    """INV-S5: shared surfaces never render restricted content."""

    def test_r_s5_01_restricted_fields_stripped(self):
        r = rm.render(svc(restricted={
            "owner_token": "tok-abc",
            "device_session_id": "sess-1",
            "private_note": "do not share",
        }))
        for field in ("owner_token", "device_session_id", "private_note",
                      "auth_secret", "operator_identity"):
            self.assertNotIn(field, r)
        self.assertTrue(r["redacted"])

    def test_r_s5_02_clean_input_not_flagged(self):
        r = rm.render(svc())
        self.assertFalse(r["redacted"])

    def test_r_s5_03_render_keys_are_safe(self):
        r = rm.render(svc(restricted={"auth_secret": "s3cr3t"}))
        self.assertEqual(set(r), {"status", "confidence", "evidence_ref",
                                 "redacted"})


class TestInvariantS1(unittest.TestCase):
    """INV-S1 spot checks: unknown never renders as operational."""

    def test_r_s1_01_none_state_renders_unknown(self):
        r = rm.render(svc(observed_state=None))
        self.assertEqual(r["status"], "unknown")

    def test_r_s1_02_unknown_enum_renders_unknown(self):
        r = rm.render(svc(observed_state="bogus"))
        self.assertEqual(r["status"], "unknown")

    def test_r_s1_03_status_enum_from_watchtower_schema(self):
        self.assertEqual(set(rm.STATUSES),
                         {"operational", "paused", "degraded", "unknown"})


class TestInvariantS2(unittest.TestCase):
    """INV-S2 spot check: paused never renders as failed."""

    def test_r_s2_01_paused_renders_paused(self):
        r = rm.render(svc(observed_state="paused"))
        self.assertEqual(r["status"], "paused")

    def test_r_s2_02_failed_never_appears(self):
        for state in ("paused", "operational", "degraded", "unknown", None,
                      "bogus"):
            r = rm.render(svc(observed_state=state))
            self.assertNotIn("failed", set(r.values()),
                             f"failed appeared for {state!r}")


class TestInvariantS4(unittest.TestCase):
    """INV-S4 spot checks: stale data shows reduced confidence or unknown."""

    def test_r_s4_01_stale_reading_reduced_confidence(self):
        r = rm.render(svc(fresh_until=1_600_000_000, now=1_700_000_000))
        self.assertLess(r["confidence"], 1.0)
        self.assertLessEqual(r["confidence"], rm.STALE_CONFIDENCE_CAP)

    def test_r_s4_02_fresh_reading_full_confidence(self):
        r = rm.render(svc())
        self.assertEqual(r["confidence"], 1.0)

    def test_r_s4_03_no_freshness_info_zero_confidence(self):
        r = rm.render(svc(fresh_until=None))
        self.assertEqual(r["confidence"], 0.0)


if __name__ == "__main__":
    unittest.main()
