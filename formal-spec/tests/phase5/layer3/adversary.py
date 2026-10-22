"""Phase 5, Layer 3 -- adversarial harness.

Extends the Layer 2 estate model (tests/phase5/layer2/estate.py) with
adversarial-side machinery for the four agent-specific threats:
T-22 prompt injection, T-23 stale-state manipulation, T-24 approval
fatigue, T-25 subagent deception. The cases attack along the leaves of
attack-trees.md: AT-2 (mutated intent / stale approvals), AT-3
(prompt-injection egress), AT-4 (approval fatigue).

Python 3 stdlib only. Deterministic: fixed virtual clocks, hand-built
cases, systematic permutation enumeration (itertools), no randomness,
no network. This module EXTENDS the Layer 2 model -- it does not
reimplement or duplicate it -- and it touches nothing under spec/ or
contracts/ (read-only).

Verdicts: every adversarial case records a machine-checkable verdict
(case ID, threat ID, control ID, verdict category, detail) to the
JSONL file named by PHASE5_VERDICTS_FILE, mirroring the
PHASE5_REJECTION_LOG convention from Layer 2.

Stated operational judgments (not modeled, not claimed as proof):
- FRESHNESS_TTL_SECONDS: a reading older than this is stale.
- The risk classifier: high-risk is derived from the digest-bound
  intent's effect+scope hints, never from an attacker-supplied label.
- The ConsequentialGate's canonical order: re-read -> validate ->
  execute. Validation must cover the reading it authorizes; execute
  never precedes either. This strictness is a harness choice, stated
  here, tested as stated.
"""

import itertools  # noqa: F401  (used by test modules' permutations)
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone  # noqa: F401

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "layer2"))
import estate  # noqa: E402
from estate import (Clock, Refusal, record_refusal, refuse,  # noqa: E402
                    intent_of, approval_digest, render_approval_card,
                    scan_untrusted, SessionRegistry, ApprovalStore,
                    Attention, AppendOnlyLog, ArtifactStore,
                    EvidencePacket, MemoryStore)

# ---------------------------------------------------------------------------
# Verdicts: machine-checkable per-case outcomes.
# ---------------------------------------------------------------------------

VERDICTS_PATH = os.environ.get("PHASE5_VERDICTS_FILE")

HELD_REFUSED = "held-refused"    # attack refused with a named cause
HELD_FLAGGED = "held-flagged"    # attack neutralized and logged as flagged
HELD_BACKSTOP = "held-backstop"  # heuristic missed, deeper control held
CLEAN_PASS = "clean-pass"        # benign control case behaved correctly
FINDING = "finding"              # a control broke under pressure

_VERDICT_CATEGORIES = (HELD_REFUSED, HELD_FLAGGED, HELD_BACKSTOP,
                       CLEAN_PASS, FINDING)

verdicts = []  # in-process copy; the JSONL file is the record


def record_verdict(case_id, threat, control, verdict, detail=""):
    """Log one adversarial case's verdict (threat ID + control ID
    mandatory)."""
    if verdict not in _VERDICT_CATEGORIES:
        raise ValueError(f"unknown verdict category: {verdict}")
    if not threat or not control:
        raise ValueError("every case must name its threat ID and control ID")
    entry = {"case": case_id, "threat": threat, "control": control,
             "verdict": verdict, "detail": detail}
    verdicts.append(entry)
    if VERDICTS_PATH:
        with open(VERDICTS_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    return entry


# ---------------------------------------------------------------------------
# Test-side estate fixtures (thin wrappers over the Layer 2 model).
# ---------------------------------------------------------------------------


def fresh_estate():
    """A live session, an approval store, and the virtual clock."""
    clock = Clock()
    sessions = SessionRegistry(clock)
    approvals = ApprovalStore(clock, sessions)
    device = sessions.enroll("HgX-iphone")
    sessions.complete_enrollment(device.session_id)
    return clock, sessions, approvals, device.session_id


def grant_intent(clock, approvals, session_id, approval_id, target,
                 effect, scope, revision="v0.1", risk="standard",
                 local_auth=False, ttl_seconds=3600):
    """Grant a digest-bound approval for a canonical intent."""
    expiry = (clock.now() + timedelta(seconds=ttl_seconds)).isoformat()
    intent = intent_of(approval_id, target=target, effect=effect,
                       scope=scope, expiry_iso=expiry, revision=revision)
    record, _ = approvals.grant(intent, session_id, risk=risk,
                                local_auth=local_auth)
    return intent, record


# ---------------------------------------------------------------------------
# Credential quarantine: credential-shaped strings in external content
# are redacted BEFORE anything is echoed (refusal details, tool-call
# args, logs). C-16, TB-7.
# ---------------------------------------------------------------------------

CREDENTIAL_PATTERNS = [
    (r"sk-live-[A-Za-z0-9_\-]{8,}", "[REDACTED-CREDENTIAL]"),
    (r"AKIA[0-9A-Z]{16}", "[REDACTED-CREDENTIAL]"),
    (r"xoxb-[A-Za-z0-9\-]{8,}", "[REDACTED-CREDENTIAL]"),
    (r"ghp_[A-Za-z0-9]{8,}", "[REDACTED-CREDENTIAL]"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
     "[REDACTED-CREDENTIAL-BLOCK]"),
]


def quarantine_credentials(text):
    """Replace credential-shaped substrings with a redaction token.
    Returns (quarantined_text, was_redacted)."""
    out = text
    redacted = False
    for pattern, token in CREDENTIAL_PATTERNS:
        if re.search(pattern, out):
            redacted = True
            out = re.sub(pattern, token, out)
    return out, redacted


def assert_no_credential_shape(text):
    """Test-side assertion: a credential-shaped string must never
    appear in the examined text. Raises AssertionError (a FINDING) if
    one does."""
    for pattern, _token in CREDENTIAL_PATTERNS:
        match = re.search(pattern, text)
        if match:
            raise AssertionError(
                f"credential-shaped string leaked: pattern {pattern!r}")
    return True


# ---------------------------------------------------------------------------
# External-content ingestion: multi-field content is JOINED before
# scanning (split-across-fields injection cannot evade), credentials
# are quarantined first, then the Layer 2 untrusted-data discipline
# applies. C-11 (TB-6), C-16 (TB-7).
# ---------------------------------------------------------------------------


def ingest_external_content(content, source, actor="orchestrator"):
    """Ingest external content as untrusted data. `content` may be a
    string or a mapping of fields (joined in key order before
    scanning). Returns "data-only" or raises Refusal."""
    if isinstance(content, dict):
        joined = " ".join(str(v) for _k, v in sorted(content.items()))
    elif isinstance(content, (list, tuple)):
        joined = " ".join(str(v) for v in content)
    else:
        joined = str(content)
    quarantined, was_redacted = quarantine_credentials(joined)
    if was_redacted:
        record_refusal(actor, "credential-quarantined",
                       f"{source}: credential-shaped string in external "
                       "content redacted; never echoed into tool calls "
                       "(C-16)")
    return scan_untrusted(quarantined, source, actor)


def render_card_resisting_injection(intent, hostile_text,
                                    actor="card-render"):
    """Render an approval card while an attacker appends instruction
    text to the display. C-6: the card renders ONLY digest-bound
    fields; the hostile tail is dropped and flagged, never rendered."""
    card = render_approval_card(intent)
    try:
        scan_untrusted(hostile_text, "card-display-tail", actor)
    except Refusal:
        record_refusal(actor, "injected-instruction-in-card-display",
                       "hostile text dropped from card display; card "
                       "renders digest-bound fields only (C-6)")
        return card, "flagged"
    return card, "clean"


# ---------------------------------------------------------------------------
# Freshness: raced sources, the decision-time gate, supersession.
# T-23, C-26, C-9, C-4, C-8; AT-2.
# ---------------------------------------------------------------------------

# A reading older than this is stale. Stated operational judgment, not
# a derived constant; the boundary tests pin the behavior at it.
FRESHNESS_TTL_SECONDS = 300


class RacedSource:
    """A live source whose value can flip while the orchestrator
    deliberates -- the stale-state adversary's weapon."""

    def __init__(self, clock, alive=True):
        self.clock = clock
        self.alive = alive
        self._version = 0
        self._flip_at = None

    def arm_flip(self, seconds_from_now):
        self._flip_at = self.clock.now() + timedelta(seconds=seconds_from_now)

    def read(self):
        if not self.alive:
            return {"source": "raced-source", "state": "unknown",
                    "reason": "observation failure (C-26)"}
        if self._flip_at is not None and \
                self.clock.now() >= self._flip_at:
            self._flip_at = None
            self._version += 1
        return {"source": "raced-source", "at": self.clock.iso(),
                "version": self._version, "fresh": True}


class ConsequentialGate:
    """The stale-state discipline at decision time (T-23; C-26, C-9).

    Canonical order: re-read -> validate -> execute. Validation must
    cover the reading it authorizes. execute() performs its own live
    re-read: the action fires only if (a) a prior re-read exists and
    is within TTL, (b) validation happened after that re-read, and
    (c) the decision-time re-read agrees with the earlier reading
    (source alive, version unchanged). Anything else refuses with
    stale-state-cannot-consequence.
    """

    def __init__(self, clock, approvals, source,
                 ttl=FRESHNESS_TTL_SECONDS):
        self.clock = clock
        self.approvals = approvals
        self.source = source
        self.ttl = ttl
        self.calls = []
        self._reading = None
        self._validated = False

    def re_read(self):
        self._reading = self.source.read()
        self._validated = False
        self.calls.append("re-read")
        return self._reading

    def validate(self, approval_id, digest, session_id):
        if self._reading is None:
            # C-9 still works without a reading; the freshness
            # discipline is enforced in execute().
            record = self.approvals.validate(approval_id, digest,
                                             session_id)
        else:
            record = self.approvals.validate(approval_id, digest,
                                             session_id)
        self._validated = True
        self.calls.append("validate")
        return record

    def execute(self, action_fn):
        self.calls.append("execute")
        if self.calls[-3:] != ["re-read", "validate", "execute"]:
            refuse("freshness-gate", "stale-state-cannot-consequence",
                   f"execute not preceded by re-read then validate "
                   f"(order {self.calls[-3:]}); consequence refused "
                   "(T-23, C-26/C-9)")
        if self._reading.get("state") == "unknown":
            refuse("freshness-gate", "stale-state-cannot-consequence",
                   "unknown on observation failure (T-23, C-26)")
        age = (self.clock.now() -
               datetime.fromisoformat(self._reading["at"])).total_seconds()
        if age >= self.ttl:
            refuse("freshness-gate", "stale-state-cannot-consequence",
                   f"reading age {age:.0f}s >= TTL {self.ttl}s: live "
                   "re-read required before consequence (T-23, C-26)")
        current = self.source.read()
        if current.get("state") == "unknown":
            refuse("freshness-gate", "stale-state-cannot-consequence",
                   "observation failed at decision time; unknown "
                   "(T-23, C-26)")
        if current.get("version") != self._reading.get("version"):
            refuse("freshness-gate", "stale-state-cannot-consequence",
                   "state raced mid-flight; decision-time re-read "
                   "disagrees with the approved reading (T-23, C-26)")
        return action_fn()


class SupersessionTracker:
    """Revisions: a stale approval (superseded revision) presented as
    current is refused, even when its digest is still valid. C-4."""

    def __init__(self):
        self.current = {}  # work_key -> revision

    def publish(self, work_key, revision):
        self.current[work_key] = revision

    def check_current(self, work_key, revision):
        if self.current.get(work_key) != revision:
            refuse("supersession", "superseded-revision",
                   f"{work_key} {revision} superseded by "
                   f"{self.current.get(work_key)}: stale approval "
                   "presented as current (C-4)")


# ---------------------------------------------------------------------------
# Approval fatigue: risk classification from the digest-bound intent,
# never from an attacker-supplied label. T-24/T-14; C-17, C-18, C-19;
# AT-4.
# ---------------------------------------------------------------------------

HIGH_RISK_EFFECT_HINTS = ("transfer", "delete", "publish", "send",
                          "wire", "share")


def classify_risk(intent):
    """Derive the risk class from the digest-bound intent itself
    (C-19). Operational judgment: consequential effects against an
    account are high-risk. The claimer's label is ignored."""
    effect = str(intent.get("effect", "")).lower()
    scope = str(intent.get("scope", "")).lower()
    if any(h in effect for h in HIGH_RISK_EFFECT_HINTS) and \
            any(a in scope for a in ("acct", "account", "iban")):
        return "high"
    return "standard"


def request_with_classification(attention, intent, claimed_risk,
                                card=None, actor="attention"):
    """Route an approval request through classification first: a
    high-risk intent disguised as routine is escalated (flagged) and
    then handled as high-risk -- exact card required."""
    actual = classify_risk(intent)
    if actual == "high" and claimed_risk != "high":
        record_refusal(actor, "risk-class-escalated",
                       f"{intent['intent_id']}: claimed '{claimed_risk}', "
                       "digest-bound intent classifies high (C-19)")
    return attention.request_approval(intent, risk=actual, card=card)


# ---------------------------------------------------------------------------
# Subagent deception: reports are verification input. T-25/T-3;
# C-13, C-30, C-10, C-22, C-23; AT-3 inject-via-subagent leaf.
# ---------------------------------------------------------------------------


class SubagentReport:
    def __init__(self, report_id, subagent, summary_text, claims,
                 evidence_refs):
        self.report_id = report_id
        self.subagent = subagent
        self.summary_text = summary_text
        self.claims = claims              # list of (kind, detail)
        self.evidence_refs = evidence_refs  # list of (artifact_id, digest)
        self.received = False
        self.evidence_ok = False
        self.log_ok = False


class Orchestrator:
    """The TB-4 orchestrator: subagent output is verification input.
    No proof, no done."""

    def __init__(self, clock, artifacts, log, evidence):
        self.clock = clock
        self.artifacts = artifacts
        self.log = log
        self.evidence = evidence

    # -- verification primitives (order-enumerable in tests) ------------
    def verify_evidence(self, report):
        for artifact_id, digest in report.evidence_refs:
            self.artifacts.verify(artifact_id, digest)  # C-10
        report.evidence_ok = True
        return True

    def check_log(self, report):
        for kind, detail in report.claims:
            if kind != "outcome":
                continue
            packet_id, claimed = detail
            matching = [e for e in self.log.records
                        if e["kind"] == "execution" and
                        e["body"].get("packet_id") == packet_id]
            if not matching:
                refuse("orchestrator", "no-proof-no-done",
                       f"{report.report_id}: outcome claimed for "
                       f"{packet_id} with no sealed execution record; "
                       "the log is the authority (C-30, C-22)")
            sealed = matching[-1]["body"]["outcome"]
            if sealed != claimed:
                refuse("orchestrator", "log-contradicts-claim",
                       f"{report.report_id}: sealed log says "
                       f"'{sealed}' for {packet_id}; report claims "
                       f"'{claimed}' -- the log wins (C-22)")
        report.log_ok = True
        return True

    def receive(self, report):
        """Intake: scan for instructions (C-13), verify evidence
        (C-10), check claims against the sealed log (C-22)."""
        scan_untrusted(report.summary_text,
                       f"subagent-report:{report.report_id}",
                       "orchestrator")
        self.verify_evidence(report)
        self.check_log(report)
        report.received = True
        return True

    def mark_done(self, report, packet_id=None):
        """Done requires verified evidence AND a sealed evidence
        packet. C-30: no proof, no done."""
        if not (report.evidence_ok and report.log_ok):
            refuse("orchestrator", "no-proof-no-done",
                   f"{report.report_id}: unverified report cannot be "
                   "marked done (C-30)")
        packet = self.evidence.packets.get(packet_id)
        if packet is None:
            refuse("orchestrator", "no-proof-no-done",
                   f"{report.report_id}: no sealed evidence packet; "
                   "no proof, no done (C-30)")
        return True


def fresh_orchestrator():
    clock = Clock()
    artifacts = ArtifactStore(clock)
    log = AppendOnlyLog(clock)
    evidence = EvidencePacket(clock, artifacts, owner="orchestrator")
    return Orchestrator(clock, artifacts, log, evidence), artifacts, log, \
        evidence
