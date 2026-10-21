"""Phase 2, Layer 1 — contract schema example tests (v0.1 drafts).

Tests the FIVE v0.1 contract schemas drafted 2026-10-21 (approval-intent,
decision-packet, evidence-packet, artifact-manifest, watchtower) with worked
examples and failing cases. Every failing case asserts the REJECTION —
the suite checks that invalid input is refused, fail closed, not merely
absent. Schemas are read from contracts/*.schema.json at run time, so any
drift between the files and these tests fails loudly.

Run:  python3 -m unittest test_schema_examples -v     (from this directory)

The schema files carry a trailing markdown promotion-note line after the
JSON body; the loader strips everything from the last '}' onward.
"""

import copy
import hashlib
import json
import unittest
from pathlib import Path

import schema_validator as sv

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "contracts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

SCHEMA_FILES = {
    "intent": "approval-intent.schema.json",
    "packet": "decision-packet.schema.json",
    "evidence": "evidence-packet.schema.json",
    "manifest": "artifact-manifest.schema.json",
    "watchtower": "watchtower.schema.json",
}

BOUND_FIELDS = ["intent_id", "work_id", "action", "target",
                "effect", "scope", "revision", "expiry"]


def canon(obj):
    """Canonical JSON (U-1: sorted keys, no whitespace, UTF-8)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def load_schema(name):
    """Load a schema file; strip the trailing markdown promotion note."""
    text = (CONTRACTS / SCHEMA_FILES[name]).read_text(encoding="utf-8")
    body = text[: text.rindex("}") + 1]
    return json.loads(body)


def load_fixture(name):
    return json.loads((FIXTURES / (name + ".valid.json")).read_text())


def intent_digest(intent):
    return hashlib.sha256(canon({k: intent[k] for k in BOUND_FIELDS})).hexdigest()


def assert_schema(name, instance):
    """Assert instance satisfies the named schema (raises on violation)."""
    return sv.validate(load_schema(name), instance)


# ---------------------------------------------------------------------------
# Cross-instance guard validators (fail closed; assertions check refusal)
# ---------------------------------------------------------------------------

def decide(packet, intent, now):
    """Approval decision guard: raise SchemaError if the decision must not
    be honoured — digest mismatch, expired intent, or schema violation."""
    assert_schema("packet", packet)
    assert_schema("intent", intent)
    if packet["intent_id"] != intent["intent_id"]:
        sv._fail("decision", "packet answers a different intent")
    if packet["intent_digest"] != intent_digest(intent):
        sv._fail("decision", "digest mismatch — intent mutated after tap")
    if now >= intent["expiry"]:
        sv._fail("decision", "approval expired at %r (now %r)"
                 % (intent["expiry"], now))
    return True


def check_evidence_packet(packet, manifests):
    """Completion-side packet guard: raise SchemaError if the packet must
    not authorise completion — schema violation, revision mismatch (INV-E2),
    missing gaps (INV-E4), or a failed acceptance test."""
    assert_schema("evidence", packet)
    by_id = {m["artifact_id"]: m for m in manifests}
    for ref in packet["artifact_refs"]:
        if ref["revision"] != packet["revision"]:
            sv._fail("evidence", "packet revision %r != artifact revision %r "
                     "(INV-E2)" % (packet["revision"], ref["revision"]))
        m = by_id.get(ref["artifact_id"])
        if m is not None and m["digest"] != ref["digest"]:
            sv._fail("evidence", "artifact digest mismatch for %r"
                     % ref["artifact_id"])
    if any(r["result"] != "pass" for r in packet["test_results"]):
        sv._fail("evidence", "a failed test result is present — "
                 "completion not authorised")
    return True


def _iso_to_epoch(ts):
    """2026-10-21T11:00:00Z -> comparable tuple (day-bound, test-local)."""
    return tuple(int(x) for x in ts.replace("Z", "").replace("T", "-")
                 .replace(":", "-").split("-"))


def check_watchtower(report, now_iso):
    """Rendering guard: raise SchemaError on stale-at-full-confidence or
    non-operational without an impairment note."""
    assert_schema("watchtower", report)
    now = _iso_to_epoch(now_iso)
    for svc in report["services"]:
        fu = _iso_to_epoch(svc["freshness"]["fresh_until"])
        if now > fu and svc.get("confidence", 0) >= 1.0:
            sv._fail("watchtower", "stale reading for %r rendered at full "
                     "confidence — downgrade, don't guess" % svc["service_id"])
        if svc["state"] != "operational" and not svc.get("note"):
            sv._fail("watchtower", "non-operational state %r without "
                     "impairment note" % svc["state"])
    return True


def rejected(fn, *args, **kwargs):
    """Assert fn raises SchemaError (the fail-closed rejection)."""
    try:
        fn(*args, **kwargs)
    except sv.SchemaError:
        return True
    raise AssertionError("expected rejection, input was accepted")


class TestApprovalIntentSchema(unittest.TestCase):
    """SCH-AI: approval-intent.schema.json (v0.1-draft)."""

    def test_sch_ai_01_valid_example_passes(self):
        assert_schema("intent", load_fixture("approval-intent"))

    def test_sch_ai_02_mutated_digest_rejected(self):
        bad = load_fixture("approval-intent")
        bad["intent_digest"] = "not-a-digest"
        rejected(assert_schema, "intent", bad)

    def test_sch_ai_03_missing_required_field_rejected(self):
        bad = load_fixture("approval-intent")
        del bad["intent_digest"]
        rejected(assert_schema, "intent", bad)

    def test_sch_ai_04_unknown_enum_value_rejected(self):
        bad = load_fixture("approval-intent")
        bad["risk_class"] = "apocalyptic"
        rejected(assert_schema, "intent", bad)

    def test_sch_ai_05_expiry_string_rejected(self):
        # Draft choice (OQ-1): expiry is integer epoch seconds.
        bad = load_fixture("approval-intent")
        bad["expiry"] = "2026-10-21T12:00:00Z"
        rejected(assert_schema, "intent", bad)

    def test_sch_ai_06_revision_string_rejected(self):
        # Draft choice (OQ-2): revision is integer.
        bad = load_fixture("approval-intent")
        bad["revision"] = "3"
        rejected(assert_schema, "intent", bad)


class TestDecisionPacketSchema(unittest.TestCase):
    """SCH-DP: decision-packet.schema.json (v0.1-draft) + decision guard."""

    def test_sch_dp_01_valid_decision_honoured(self):
        intent = load_fixture("approval-intent")
        packet = load_fixture("decision-packet")
        self.assertTrue(decide(packet, intent, now=1793025000))

    def test_sch_dp_02_digest_mismatch_rejected(self):
        intent = load_fixture("approval-intent")
        packet = load_fixture("decision-packet")
        packet["intent_digest"] = "0" * 64
        rejected(decide, packet, intent, 1793025000)

    def test_sch_dp_03_expired_approval_rejected(self):
        intent = load_fixture("approval-intent")
        packet = load_fixture("decision-packet")
        # now == expiry is refused (matches CT-A4 boundary semantics).
        rejected(decide, packet, intent, now=intent["expiry"])

    def test_sch_dp_04_missing_required_field_rejected(self):
        bad = load_fixture("decision-packet")
        del bad["server_recorded_at"]
        rejected(assert_schema, "packet", bad)


class TestEvidencePacketSchema(unittest.TestCase):
    """SCH-EP: evidence-packet.schema.json (v0.1-draft) + packet guard."""

    def manifests(self):
        return [load_fixture("artifact-manifest")]

    def test_sch_ep_01_valid_packet_authorises(self):
        self.assertTrue(check_evidence_packet(
            load_fixture("evidence-packet"), self.manifests()))

    def test_sch_ep_02_missing_gaps_rejected(self):
        # INV-E4: omission of the required gaps field is a schema violation.
        bad = load_fixture("evidence-packet")
        del bad["gaps"]
        rejected(check_evidence_packet, bad, self.manifests())

    def test_sch_ep_03_revision_mismatch_rejected(self):
        # INV-E2: packet revision must match the artifact revision.
        bad = load_fixture("evidence-packet")
        bad["artifact_refs"][0]["revision"] = 2
        rejected(check_evidence_packet, bad, self.manifests())

    def test_sch_ep_04_failed_test_result_rejected(self):
        bad = load_fixture("evidence-packet")
        bad["test_results"][0]["result"] = "fail"
        rejected(check_evidence_packet, bad, self.manifests())


class TestArtifactManifestSchema(unittest.TestCase):
    """SCH-AM: artifact-manifest.schema.json (v0.1-draft)."""

    def test_sch_am_01_valid_manifest_passes(self):
        assert_schema("manifest", load_fixture("artifact-manifest"))

    def test_sch_am_02_malformed_digest_rejected(self):
        bad = load_fixture("artifact-manifest")
        bad["digest"] = "f" * 63 + "g"
        rejected(assert_schema, "manifest", bad)

    def test_sch_am_03_missing_provenance_rejected(self):
        bad = load_fixture("artifact-manifest")
        del bad["provenance"]
        rejected(assert_schema, "manifest", bad)


class TestWatchtowerSchema(unittest.TestCase):
    """SCH-WT: watchtower.schema.json (v0.1-draft) + rendering guard."""

    def test_sch_wt_01_valid_report_passes(self):
        self.assertTrue(check_watchtower(
            load_fixture("watchtower"), "2026-10-21T11:30:00Z"))

    def test_sch_wt_02_paused_renders_paused(self):
        # Operator-paused reads as paused, never down (INV-S2 substrate).
        report = load_fixture("watchtower")
        states = {s["service_id"]: s["state"] for s in report["services"]}
        self.assertEqual(states["course-bot"], "paused")

    def test_sch_wt_03_unknown_enum_value_rejected(self):
        bad = load_fixture("watchtower")
        bad["services"][0]["state"] = "broken"
        rejected(check_watchtower, bad, "2026-10-21T11:30:00Z")

    def test_sch_wt_04_stale_at_full_confidence_rejected(self):
        bad = load_fixture("watchtower")
        bad["services"][0]["confidence"] = 1.0
        # Reading is past fresh_until (12:00Z) at now 13:00Z.
        rejected(check_watchtower, bad, "2026-10-21T13:00:00Z")

    def test_sch_wt_05_stale_downgraded_confidence_accepted(self):
        ok = load_fixture("watchtower")
        for svc in ok["services"]:
            svc["confidence"] = 0.4
        self.assertTrue(check_watchtower(ok, "2026-10-21T13:00:00Z"))

    def test_sch_wt_06_degraded_without_note_rejected(self):
        bad = load_fixture("watchtower")
        bad["services"][0]["state"] = "degraded"
        bad["services"][0].pop("note", None)
        rejected(check_watchtower, bad, "2026-10-21T11:30:00Z")


if __name__ == "__main__":
    unittest.main()
