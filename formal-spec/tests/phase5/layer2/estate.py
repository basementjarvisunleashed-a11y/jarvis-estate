"""Phase 5, Layer 2 — estate model under test.

A test-side reimplementation of the v0.1 drafts (the Phase 3 Layer 2
pattern: tests exercise an independent model; agreement with the drafts
is what the tests assert). Python 3 stdlib only, deterministic (fixed
virtual clock, hand-built cases, no randomness, no network).

Drafts under test: threat-catalogue.md (T-1...T-28),
control-matrix.md (C-1...C-31), session-lifecycle.md (SL-1...SL-27),
capability-matrix.md (CM-1...CM-14), trust-boundaries.md (TB-1...TB-15),
attack-trees.md (AT-1...AT-4). Intent digests use the ratified Phase 2
procedure re-derived from tests/phase3/layer2/digest.py.

Every refusal is a sealed, logged denial (control-matrix.md section 5,
compensation 4): it raises Refusal and is appended to the rejection
log.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

REJECTION_LOG_PATH = os.environ.get("PHASE5_REJECTION_LOG")

# ---------------------------------------------------------------------------
# Refusals: sealed, logged denials.
# ---------------------------------------------------------------------------


class Refusal(Exception):
    """A refusal with a machine-checkable cause and a human detail."""

    def __init__(self, cause, detail=""):
        super().__init__(f"{cause}: {detail}")
        self.cause = cause
        self.detail = detail


refusal_log = []


def record_refusal(actor, cause, detail=""):
    entry = {"actor": actor, "cause": cause, "detail": detail}
    refusal_log.append(entry)
    if REJECTION_LOG_PATH:
        with open(REJECTION_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(f"{actor} REFUSED: {cause} -- {detail}\n")
    return entry


def refuse(actor, cause, detail=""):
    record_refusal(actor, cause, detail)
    raise Refusal(cause, detail)


# ---------------------------------------------------------------------------
# Virtual clock: fixed, explicit, deterministic.
# ---------------------------------------------------------------------------

CLOCK_START = datetime(2026, 10, 22, 8, 5, 0, tzinfo=timezone.utc)


class Clock:
    def __init__(self):
        self._now = CLOCK_START

    def now(self):
        return self._now

    def advance(self, seconds):
        self._now = self._now + timedelta(seconds=seconds)

    def iso(self):
        return self._now.isoformat()


# ---------------------------------------------------------------------------
# Digest: the ratified eight-field approval digest, re-derived from
# tests/phase3/layer2/digest.py (Unicode code-point key order,
# exact (',', ':') separators, UTF-8, ensure_ascii=False, SHA-256).
# ---------------------------------------------------------------------------

_INTENT_FIELDS = ("intent_id", "work_id", "action", "target", "effect",
                  "scope", "revision", "expiry")


def approval_digest(record):
    bound = {k: record[k] for k in _INTENT_FIELDS}
    payload = json.dumps(bound, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def intent_of(approval_id, target, effect, scope, expiry_iso,
              action="execute.consequential", revision="v0.1",
              work_id="work-phase5"):
    """Build a canonical intent record bound by the digest."""
    return {"intent_id": approval_id, "work_id": work_id, "action": action,
            "target": target, "effect": effect, "scope": scope,
            "revision": revision, "expiry": expiry_iso}


# ---------------------------------------------------------------------------
# Sessions: session-lifecycle.md SL-1...SL-27.
# ---------------------------------------------------------------------------

STATES = ("unenrolled", "enrolling", "active", "suspended",
          "revoked", "expired")  # SL-1: exhaustive


class Session:
    def __init__(self, session_id, device_id, state, enrolled_at,
                 expiry, operator, nonce=0):
        self.session_id = session_id
        self.device_id = device_id
        self.state = state
        self.enrolled_at = enrolled_at
        self.expiry = expiry
        self.operator = operator
        self.nonce = nonce


class SessionRegistry:
    """The full device_session_id lifecycle (Q1, SL-1...SL-27)."""

    def __init__(self, clock, session_expiry_seconds=30 * 86400):
        self.clock = clock
        self.session_expiry_seconds = session_expiry_seconds
        self.sessions = {}   # session_id -> Session
        self.tombstones = []  # sealed revocation records, SL-16
        self.security_events = []
        self._counter = 0

    # -- enrollment (SL-6...SL-9) ----------------------------------------
    def enroll(self, device_id, operator="HgX"):
        """Begin the enrollment ceremony. Grants NO authority (SL-4)."""
        self._counter += 1
        sid = f"session-{self._counter:04d}"
        now = self.clock.iso()
        session = Session(sid, device_id, "enrolling", now,
                          (self.clock.now() + timedelta(
                              seconds=self.session_expiry_seconds)).isoformat(),
                          operator)
        self.sessions[sid] = session
        return session

    def complete_enrollment(self, session_id):
        session = self._get_known(session_id)
        if session.state != "enrolling":
            refuse("session-registry", "invalid-transition",
                   f"{session.state} -> active")
        session.state = "active"
        return session

    def cancel_enrollment(self, session_id):
        session = self._get_known(session_id)
        if session.state != "enrolling":
            refuse("session-registry", "invalid-transition",
                   f"{session.state} -> unenrolled")
        session.state = "unenrolled"

    # -- the lookup: SL-3, unknown refused before any other check --------
    def _get_known(self, session_id):
        session = self.sessions.get(session_id)
        if session is None:
            refuse("session-registry", "unknown-session",
                   f"{session_id} never enrolled (SL-3)")
        return session

    def require_active(self, session_id):
        """The single gate every decision point uses (SL-21, SL-22)."""
        session = self._get_known(session_id)
        if session.state == "revoked":
            refuse("session-registry", "revoked-session",
                   f"{session_id} revoked: authority dead (SL-14)")
        if session.state == "expired":
            refuse("session-registry", "expired-session",
                   f"{session_id} expired: authority dead (SL-15)")
        if session.state == "suspended":
            refuse("session-registry", "suspended-session",
                   f"{session_id} suspended: frozen (SL-5)")
        if session.state == "enrolling":
            refuse("session-registry", "enrolling-no-authority",
                   "enrollment ceremony grants no authority (SL-4)")
        if session.state == "unenrolled":
            refuse("session-registry", "unenrolled-device",
                   "no session: all requests refused (SL-3)")
        return session

    # -- expiry (SL-10...SL-13) ------------------------------------------
    def sweep_expiry(self):
        """Expire sessions whose expiry passed. Evaluated at decision
        time (SL-11); terminal, no resurrection (SL-2)."""
        for session in self.sessions.values():
            if session.state == "active" and \
                    self.clock.now() >= datetime.fromisoformat(session.expiry):
                session.state = "expired"

    # -- revocation (SL-14...SL-16): immediate and total ---------------
    def revoke(self, session_id, actor="HgX", reason="operator",
               bindings=None):
        """Revocation kills authority immediately (SL-14): pending
        approvals, in-flight intents, and revision-token validity die
        with it. bindings: an ApprovalStore whose sessions are voided."""
        session = self._get_known(session_id)
        if session.state in ("revoked", "expired"):
            refuse("session-registry", "terminal-session",
                   f"{session_id} already {session.state}: "
                   "no resurrection (SL-2)")
        if session.state == "unenrolled":
            refuse("session-registry", "nothing-to-revoke", session_id)
        session.state = "revoked"
        self.tombstones.append({"session_id": session_id,
                                "revoked_at": self.clock.iso(),
                                "actor": actor, "reason": reason})
        killed = bindings.void_session(session_id) if bindings else 0
        if reason == "device-lost":
            self.security_events.append(
                {"at": self.clock.iso(), "kind": "device-lost-revocation",
                 "session_id": session_id})
        return killed

    # -- suspension (SL-5) -------------------------------------------------
    def suspend(self, session_id, actor):
        session = self.require_active(session_id)
        if actor != "HgX":
            refuse("session-registry", "suspend-not-operator",
                   "only HgX may suspend (SL-5)")
        session.state = "suspended"

    def reactivate(self, session_id, actor):
        session = self._get_known(session_id)
        if session.state != "suspended":
            refuse("session-registry", "invalid-transition",
                   f"{session.state} -> active")
        if actor != "HgX":
            refuse("session-registry", "reactivate-not-operator",
                   "only HgX may reactivate (SL-5)")
        session.state = "active"

    # -- re-enrollment after device replacement (SL-17...SL-20) -----------
    def reenroll_device(self, old_session_id, new_device_id,
                        operator="HgX", lost=False, bindings=None):
        """Revocation-then-enrollment with a fresh ID (SL-17...SL-19).
        The old ID stays dead; the new device inherits no approvals
        (SL-20)."""
        self.revoke(old_session_id, actor=operator,
                    reason="device-lost" if lost else "device-replaced",
                    bindings=bindings)
        new_session = self.enroll(new_device_id, operator=operator)
        return new_session

    def ids_live(self):
        return {s.session_id for s in self.sessions.values()
                if s.state == "active"}


# ---------------------------------------------------------------------------
# Approvals: digest-bound, single-use, session-bound, expiry-bound.
# T-1/T-4, C-1...C-9, CM-3, AT-1/AT-2.
# ---------------------------------------------------------------------------


class ApprovalRecord:
    def __init__(self, approval_id, intent, digest, timestamp,
                 session_id, risk="standard", local_auth=False):
        self.approval_id = approval_id
        self.intent = dict(intent)
        self.digest = digest
        self.timestamp = timestamp
        self.session_id = session_id
        self.risk = risk
        self.local_auth = local_auth
        self.executed = False


class ApprovalStore:
    """The TB-2 decision point: session, then digest, then expiry,
    re-validated at decision time (C-9)."""

    def __init__(self, clock, sessions):
        self.clock = clock
        self.sessions = sessions
        self.records = {}  # approval_id -> ApprovalRecord

    def grant(self, intent, session_id, risk="standard",
              local_auth=False, clock=None):
        """HgX grants an approval for the exact digest-bound intent."""
        clock = clock or self.clock
        self.sessions.require_active(session_id)  # C-1...C-3
        digest = approval_digest(intent)
        approval_id = intent["intent_id"]
        existing = self.records.get(approval_id)
        if existing is not None:
            # C-5: single-use records; duplicate returns the existing
            # record, never a second execution.
            return existing, False
        if risk == "high" and not local_auth:
            refuse("approval-store", "high-risk-requires-local-auth",
                   f"{approval_id} high-risk without local auth (C-19)")
        record = ApprovalRecord(approval_id, intent, digest,
                                clock.iso(), session_id, risk, local_auth)
        self.records[approval_id] = record
        return record, True

    def find_by_digest(self, digest):
        for record in self.records.values():
            if record.digest == digest:
                return record
        refuse("gesture-store", "gesture-no-matching-approval",
               "tap references no live approval")

    def validate(self, approval_id, presented_digest, session_id):
        """Validate an approval at decision time (C-9)."""
        self.sessions.require_active(session_id)  # C-1...C-3 first
        record = self.records.get(approval_id)
        if record is None:
            refuse("approval-store", "fake-approval",
                   f"{approval_id}: invented digest cannot match a live "
                   "intent (AT-1 leaf: C-4)")
        if presented_digest != record.digest:
            refuse("approval-store", "digest-mismatch",
                   f"{approval_id}: intent changed after approval -- "
                   "changed scope voids approval (CM-3, C-4)")
        if self.clock.now() >= datetime.fromisoformat(record.intent["expiry"]):
            refuse("approval-store", "approval-expired",
                   f"{approval_id}: expiry evaluated at decision time "
                   "(C-8)")
        return record

    def execute(self, approval_id, presented_digest, session_id):
        """Single-use execution: the same approval never executes twice."""
        record = self.validate(approval_id, presented_digest, session_id)
        if record.executed:
            refuse("approval-store", "approval-replay",
                   f"{approval_id}: duplicate decision returns the "
                   "existing record, never a second execution (C-5)")
        record.executed = True
        return record

    def void_session(self, session_id):
        """SL-14: revocation voids every approval bound to the session."""
        killed = 0
        for record in self.records.values():
            if record.session_id == session_id and not record.executed:
                record.executed = None  # voided, not executed
                killed += 1
        return killed

    def count_pending(self, session_id):
        return sum(1 for r in self.records.values()
                   if r.session_id == session_id and r.executed is False)


# ---------------------------------------------------------------------------
# Approval cards: C-6 (exact target+effect+scope+expiry from the
# digest-bound intent); C-7 (offline taps are gestures, not consent).
# ---------------------------------------------------------------------------

CARD_FIELDS = ("intent_id", "target", "effect", "scope", "expiry")


def render_approval_card(intent):
    """Cards render ONLY digest-bound fields (C-6). Adjacent content is
    dropped, never rendered."""
    return {k: intent[k] for k in CARD_FIELDS}


class GestureStore:
    """Offline taps are gestures, never consent (C-7): no authoritative
    approval without server validation."""

    def __init__(self, clock, sessions):
        self.clock = clock
        self.sessions = sessions
        self.gestures = []

    def tap(self, intent_digest, session_id, offline=True):
        gesture = {"digest": intent_digest, "session_id": session_id,
                   "at": self.clock.iso(), "offline": offline}
        self.gestures.append(gesture)
        return gesture

    def assert_approval(self, gesture):
        """A client asserting its tap IS an approval: always refused."""
        refuse("gesture-store", "offline-tap-not-approval",
               "an offline tap is a gesture, not consent (C-7): no "
               "authoritative approval without server validation")

    def server_validate(self, gesture, approvals):
        """The only path from tap to authority: full server validation."""
        record = approvals.find_by_digest(gesture["digest"])
        return approvals.validate(record.approval_id, gesture["digest"],
                                  gesture["session_id"])


# ---------------------------------------------------------------------------
# Capabilities: the eight-field format (capability-matrix.md CM-1...CM-4).
# ---------------------------------------------------------------------------


class Capability:
    """(subject, action, object, scope, condition, expiry,
    approval_req, evidence_req) -- CM-10."""

    def __init__(self, subject, action, obj, scope, condition, expiry_iso,
                 approval_req, evidence_req):
        self.subject = subject
        self.action = action
        self.object = obj
        self.scope = scope
        self.condition = condition  # callable -> bool
        self.expiry = expiry_iso
        self.approval_req = approval_req
        self.evidence_req = evidence_req

    def invoke(self, clock, **_kwargs):
        """CM-1/CM-2: conditions, not possessions."""
        if not self.condition():
            refuse("capability", "condition-false",
                   f"{self.subject} {self.action} {self.object}: "
                   "a capability whose condition is false is not a "
                   "capability at all (CM-1)")
        if clock.now() >= datetime.fromisoformat(self.expiry):
            refuse("capability", "capability-expired",
                   "expiry evaluated at decision time (CM-2)")
        return True


# ---------------------------------------------------------------------------
# Artifacts, evidence packets, tamper-evident records, memory.
# C-10 (artifact content digest), C-22 (append-only), C-23 (provenance),
# C-30 (no proof, no done), T-9 (non-repudiable approval objects).
# ---------------------------------------------------------------------------


class ArtifactStore:
    def __init__(self, clock):
        self.clock = clock
        self.artifacts = {}  # id -> {content, digest, revision}

    def seal(self, artifact_id, content, revision):
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        self.artifacts[artifact_id] = {"content": content, "digest": digest,
                                       "revision": revision}
        return digest

    def reference(self, artifact_id):
        artifact = self.artifacts.get(artifact_id)
        if artifact is None:
            refuse("artifact-store", "unknown-artifact", artifact_id)
        return artifact["digest"], artifact["revision"]

    def verify(self, artifact_id, expected_digest):
        """C-10: an artifact altered after production is flagged."""
        artifact = self.artifacts.get(artifact_id)
        if artifact is None:
            refuse("artifact-store", "unknown-artifact", artifact_id)
        current = hashlib.sha256(
            artifact["content"].encode("utf-8")).hexdigest()
        if current != expected_digest:
            refuse("artifact-store", "artifact-digest-mismatch",
                   f"{artifact_id}: content altered after production "
                   "(C-10)")


class EvidencePacket:
    """C-21/C-30: approval objects carry digest + timestamp; a
    consequential action without a sealed evidence packet is refused."""

    def __init__(self, clock, artifact_store, owner):
        self.clock = clock
        self.artifacts = artifact_store
        self.owner = owner  # one accountable owner per handoff (C-21)
        self.packets = {}

    def seal_packet(self, packet_id, approval_record, artifact_refs,
                    observation):
        for artifact_id, digest in artifact_refs:
            self.artifacts.verify(artifact_id, digest)
        packet = {"packet_id": packet_id, "owner": self.owner,
                  "sealed_at": self.clock.iso(),
                  "approval_digest": approval_record.digest,
                  "approval_timestamp": approval_record.timestamp,
                  "artifact_refs": artifact_refs,
                  "observation": observation}
        self.packets[packet_id] = packet
        return packet

    def execute_consequential(self, approval_record, packet_id):
        """T-9/C-30: non-repudiable approval object + sealed packet."""
        packet = self.packets.get(packet_id)
        if packet is None:
            refuse("evidence", "no-proof-no-done",
                   f"{approval_record.approval_id}: consequential action "
                   "without a sealed evidence packet is refused "
                   "(T-3, T-9, C-30)")
        if packet["approval_digest"] != approval_record.digest:
            refuse("evidence", "packet-digest-mismatch",
                   "evidence packet bound to a different intent")
        return packet


class AppendOnlyLog:
    """C-22: append-only, tamper-evident (hash-chained) records."""

    def __init__(self, clock):
        self.clock = clock
        self.records = []
        self._head = "GENESIS"

    def append(self, kind, body, actor):
        entry = {"seq": len(self.records), "at": self.clock.iso(),
                 "kind": kind, "body": body, "actor": actor,
                 "prev": self._head}
        self._head = hashlib.sha256(
            json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()
        entry["seal"] = self._head
        self.records.append(entry)
        return entry

    def alter(self, seq, new_body):
        """Any attempt to alter history: refused (T-6)."""
        refuse("records", "log-alter-refused",
               f"seq {seq}: records are append-only (C-22)")


class MemoryStore:
    """C-23: memory writes require provenance; orchestrator-mediated."""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.entries = []

    def write(self, key, value, provenance, writer="orchestrator"):
        if writer != "orchestrator":
            refuse("memory", "memory-write-not-orchestrator",
                   "no subagent writes direct to memory (C-23)")
        if not provenance or not provenance.get("source"):
            refuse("memory", "memory-write-no-provenance",
                   f"{key}: memory writes require provenance (C-23)")
        self.entries.append({"key": key, "value": value,
                             "provenance": provenance,
                             "writer": "orchestrator"})
        return True


# ---------------------------------------------------------------------------
# Tool plane truthfulness: T-8, C-24 (Q2).
# Two integration classes per the Phase 4 classification:
#   SUPPORTED   -- read-after-write verification is possible.
#   UNSUPPORTED -- no read-back: strongest-approval or manual execution.
# ---------------------------------------------------------------------------

SUPPORTED = "supported"
UNSUPPORTED = "unsupported"


class ToolPlane:
    def __init__(self, clock):
        self.clock = clock
        self.world = {}        # the observable state tools act on
        self.integrations = {}  # name -> SUPPORTED | UNSUPPORTED

    def register(self, name, integration_class):
        self.integrations[name] = integration_class

    def tool_call(self, integration, verb, key, reported_outcome,
                  approval=None, manual=False):
        """A tool reports an outcome; the orchestrator verifies (C-24)."""
        integration_class = self.integrations.get(integration)
        if integration_class is None:
            refuse("tool-plane", "unknown-integration", integration)

        if integration_class == SUPPORTED:
            # Read-after-write: verify the reported outcome against the
            # observable state the tool actually changed.
            actual = self.world.get(key, "absent")
            if reported_outcome == "success" and actual != "present":
                refuse("tool-plane", "false-success-reported",
                       f"{integration}: success reported without executing "
                       "-- read-after-write discrepancy (T-8, C-24)")
            if reported_outcome == "failure" and actual == "present":
                # The tool executed and then reported failure: detected,
                # reconciled as executed, and flagged.
                record_refusal("tool-plane", "false-failure-reported",
                               f"{integration}: failure reported after "
                               "executing -- read-after-write discrepancy "
                               "(T-8, C-24)")
                return "executed-flagged"
            return "verified"

        # UNSUPPORTED: no read-back possible. Strongest approval
        # (digest-bound, high-risk, local auth) or manual execution.
        if manual:
            return "manual-execution"
        if approval is None:
            refuse("tool-plane", "unsupported-no-strong-approval",
                   f"{integration}: no read-back; requires strongest "
                   "approval or manual execution (T-8, C-24)")
        if approval.risk != "high" or not approval.local_auth:
            refuse("tool-plane", "unsupported-approval-too-weak",
                   f"{integration}: strongest approval = high-risk + "
                   "local auth + digest binding (T-8, C-24)")
        return "strongest-approval"


# ---------------------------------------------------------------------------
# Prompt-injection discipline: external content, tool output, subagent
# output are untrusted data, never instructions (C-11, C-12, C-13;
# T-13/T-22; AT-3). Vault: no credentials in prompt context (C-16, TB-7).
# ---------------------------------------------------------------------------

INSTRUCTION_MARKERS = ("run this", "ignore previous", "system:",
                       "you must now", "execute the following")


def scan_untrusted(content, source, actor):
    """External content / tool output / subagent output is data (C-11,
    C-12, C-13). Instructions found in the data path are never
    executed."""
    lowered = content.lower()
    for marker in INSTRUCTION_MARKERS:
        if marker in lowered:
            refuse(actor, "injected-instruction-in-data",
                   f"{source}: '{marker}' treated as untrusted data, "
                   "never an instruction (C-11/C-12/C-13)")
    return "data-only"


def scan_context_no_credentials(context_text, actor="context-scan"):
    """C-16: no credentials in prompt context; vault boundary TB-7."""
    for pattern in ("sk-live-", "AKIA", "xoxb-", "-----BEGIN PRIVATE KEY-----",
                    "ghp_"):
        if pattern in context_text:
            refuse(actor, "credential-in-context",
                   f"pattern '{pattern}': no credential in prompt context "
                   "(C-16, TB-7)")
    return "context-clean"


# ---------------------------------------------------------------------------
# Notifications and shared surfaces: C-14 (hints carry pointer + state
# only), C-15 (states-only on shared surfaces, INV-S5).
# ---------------------------------------------------------------------------


def build_notification(record_id, state):
    """TB-9: a notification is a hint: pointer + state, never the
    record (C-14)."""
    return {"pointer": f"record:{record_id}", "state": state}


def render_shared_surface(view):
    """TB-10 / INV-S5: shared surfaces show states only (C-15)."""
    rendered = {}
    for key, value in view.items():
        if isinstance(value, dict) and "state" in value:
            rendered[key] = {"state": value["state"]}
        else:
            rendered[key] = "state-only"
    return rendered


# ---------------------------------------------------------------------------
# Source validation: C-29 (T-2 fake source): sources validated against
# the allowlist; read-current at decision time.
# ---------------------------------------------------------------------------


class SourceValidator:
    def __init__(self, allowlist):
        self.allowlist = set(allowlist)

    def fetch(self, source):
        if source not in self.allowlist:
            refuse("source-validator", "unallowlisted-source",
                   f"{source}: not the claimed authority (C-29, T-2)")
        return {"source": source, "fetched_at": "now", "current": True}


# ---------------------------------------------------------------------------
# Attention: C-17 (silent-by-default), C-18 (no bulk approval),
# C-19 (risk classes; high-risk needs local auth and exact rendering),
# T-14/T-24 (AT-4). The C-20 review procedure is documented in
# review-procedure.md -- the test asserts the procedure exists and the
# budget log it reviews is exportable.
# ---------------------------------------------------------------------------


class Attention:
    """The estate's attention gate (TB-9)."""

    def __init__(self, clock, budget_per_hour=3):
        self.clock = clock
        self.budget_per_hour = budget_per_hour
        self.requested = []  # (at, intent_id, risk)

    def request_approval(self, intent, risk="standard", card=None):
        """C-19: high-risk requests must carry the card rendered from the
        digest-bound intent -- exact target+effect rendering. Routine
        requests stay silent (C-17). Barrages beyond budget are
        refused/queued (T-24, C-18)."""
        hour = int(self.clock.now().timestamp() // 3600)
        in_window = [r for r in self.requested if
                     int(r[0].timestamp() // 3600) == hour]
        if len(in_window) >= self.budget_per_hour:
            refuse("attention", "attention-budget-exceeded",
                   f"{intent['intent_id']}: barrage beyond budget is "
                   "refused/queued, never bulk-approved (T-24, C-18)")
        if risk != "high":
            # C-17: silent-by-default; routine approvals are not
            # requested.
            record_refusal("attention", "silent-by-default",
                           f"{intent['intent_id']}: routine, not requested "
                           "(C-17)")
            return "silent"
        if card != render_approval_card(intent):
            refuse("attention", "high-risk-not-exact",
                   "high-risk requires local auth and exact target+effect "
                   "rendering from the digest-bound intent (C-19)")
        self.requested.append((self.clock.now(), intent["intent_id"], risk))
        return "requested"

    def bulk_approve(self, intents):
        """C-18: each intent is approved singly. 'Approve all' is refused."""
        refuse("attention", "bulk-approval-refused",
               f"{len(intents)} intents: no bulk approval (C-18)")

    def export_budget_log(self):
        return [{"at": t.isoformat(), "intent_id": i, "risk": r}
                for t, i, r in self.requested]


# ---------------------------------------------------------------------------
# Router: TB-8 -- recommends only, never approves (C-27/T-20);
# denies repeated no-progress loops, budgets, no retry on unknown
# (C-25: T-15/T-16).
# ---------------------------------------------------------------------------


class Router:
    def __init__(self, clock, call_budget=10):
        self.clock = clock
        self.call_budget = call_budget
        self.calls = 0
        self.history = []

    def recommend(self, options):
        """The router recommends a path only (T-20, C-27)."""
        self._charge()
        choice = options[0] if options else None
        self.history.append(("recommend", choice))
        return choice

    def issue_approval(self, intent):
        refuse("router", "router-cannot-approve",
               "the router recommends only; it never approves (T-20, C-27)")

    def authorize_spend(self, amount):
        refuse("router", "router-cannot-spend",
               "the router never authorizes spending (T-20, C-27)")

    def action(self, name, progress_made, known):
        """C-25: loop waste and cost explosion."""
        self._charge()
        if not known:
            # No retry on unknown.
            refuse("router", "no-retry-on-unknown",
                   f"{name}: unknown outcome is not retried (C-25)")
        recent = [h for h in self.history if h[0] == "action"]
        if len(recent) >= 2 and not progress_made and \
                all(h[1] == name and not h[2] for h in recent[-2:]):
            refuse("router", "router-denies-loop",
                   f"{name}: repeated no-progress action denied (C-25)")
        self.history.append(("action", name, progress_made))
        return "ran"

    def _charge(self):
        self.calls += 1
        if self.calls > self.call_budget:
            refuse("router", "call-budget-exceeded",
                   "unbounded compute is refused (C-25)")


# ---------------------------------------------------------------------------
# Connectors and custody boundaries: least privilege (C-27/T-19),
# money custody exact-approval (C-31/TB-11), sealed boundaries (TB-13,
# TB-15), location boundary named not named-custodian (TB-14, Q6).
# ---------------------------------------------------------------------------


class ConnectorRegistry:
    """A connector capability cannot exceed its granted scope (C-27)."""

    def __init__(self):
        self.grants = {}  # connector -> set of (action, asset) pairs

    def grant(self, connector, actions_assets):
        self.grants[connector] = set(actions_assets)

    def use(self, connector, action, asset):
        if (action, asset) not in self.grants.get(connector, set()):
            refuse("connector-registry", "connector-overreach",
                   f"{connector}: {action} on {asset} outside its grant "
                   "(T-19, C-27)")
        return True


class MoneyCustody:
    """TB-11: one custodian holds money access. Any money need
    elsewhere: HgX's explicit approval of the exact amount, account,
    and date -- one approval = one action (C-31)."""

    def __init__(self, clock):
        self.clock = clock
        self.spent = []

    def execute_money(self, subject, approval_record, amount, account, date):
        if subject != "money-custodian":
            refuse("money-custody", "custody-crossing-refused",
                   f"{subject}: money access is the sole custodian's; "
                   "crossing rules hold (TB-11, C-31)")
        intent = approval_record.intent
        scope = intent.get("scope", {})
        if not (scope.get("amount") == amount and
                scope.get("account") == account and
                scope.get("date") == date):
            refuse("money-custody", "money-approval-not-exact",
                   "one approval = one exact amount, account, date "
                   "(TB-11, C-31)")
        if approval_record.executed:
            refuse("money-custody", "money-approval-replay",
                   "one approval = one action; already executed (C-31)")
        approval_record.executed = True
        self.spent.append({"at": self.clock.iso(), "amount": amount,
                           "account": account, "date": date,
                           "digest": approval_record.digest})
        return True


def health_crossing(subject, action):
    """TB-13: sealed -- health contents never cross any boundary."""
    refuse("health-boundary", "health-sealed",
           f"{subject}: health data is sealed in its own service; it never "
           "crosses to another chat, summary, or report (TB-13)")


def research_crossing(item):
    """TB-15: sealed -- findings never route back to the working room."""
    refuse("research-boundary", "research-sealed",
           f"{item}: findings stay in the research section; publication "
           "only on HgX's explicit per-item command, never through the "
           "working room (TB-15)")


def location_access(subject):
    """TB-14: the boundary is named; the custodian is never named outside
    its own chat. No other bot, chat, worker, or system reads, requests,
    stores, or uses live location."""
    refuse("location-boundary", "location-not-custodian",
           f"{subject}: every location-dependent need routes to HgX "
           "personally (TB-14, Q6 secrecy)")


# ---------------------------------------------------------------------------
# Client as orchestrator: T-21 -- clients render contracts only (C-27's
# "clients render contracts only" reading).
# ---------------------------------------------------------------------------


def render_contract(capability):
    """A client receives a contract: what it may request, never the
    authority to execute or approve."""
    return {"contract": True,
            "subject": capability.subject,
            "action": capability.action,
            "object": capability.object,
            "scope": capability.scope,
            "condition": "evaluated-at-decision-time",
            "expiry": capability.expiry}


def client_orchestrate(request):
    refuse("client-plane", "client-cannot-orchestrate",
           f"{request}: clients render contracts only; no local "
           "approval, no inferred state (T-21)")


# ---------------------------------------------------------------------------
# L0 compensations (control-matrix.md section 5): three-plane
# enforcement, key custody asserted, sealed logged denials.
# ---------------------------------------------------------------------------

PLANES = ("orchestrator", "tool", "subagent")


class PlaneViolation(Refusal):
    pass


def cross_plane(caller_plane, callee_plane, call):
    """Compensation 2: direct cross-plane calls raise PlaneViolation --
    the one mechanical enforcement L0 has."""
    if caller_plane != callee_plane and caller_plane in PLANES and \
            callee_plane in PLANES:
        record_refusal("planes", "plane-violation",
                       f"{caller_plane} -> {callee_plane}: {call}")
        raise PlaneViolation("plane-violation",
                             f"direct cross-plane call refused: "
                             f"{caller_plane} -> {callee_plane}")
    return "same-plane-ok"


# Components assert they hold no ceremony key bytes (compensation 3).
KEY_CUSTODY_ASSERTIONS = {
    "orchestrator": "holds no ceremony key bytes",
    "tool-plane": "holds no ceremony key bytes",
    "subagent-plane": "holds no ceremony key bytes",
    "approval-store": "holds no ceremony key bytes",
    "session-registry": "holds no ceremony key bytes",
    "evidence": "holds no ceremony key bytes",
}


def assert_key_custody(component):
    assertion = KEY_CUSTODY_ASSERTIONS.get(component)
    if assertion is None:
        refuse("key-custody", "component-not-asserted",
               f"{component}: no key-custody assertion on file")
    return assertion


# ---------------------------------------------------------------------------
# Honest limitation T-26/C-28: no privacy property is asserted in
# evidence. The vocabulary of privacy guarantees must be absent from
# every evidence output.
# ---------------------------------------------------------------------------

PRIVACY_VOCABULARY = ("zero-knowledge", "zk-proof", "end-to-end encrypted",
                      "e2ee", "anonymized", "untraceable", "private by design")


def scan_no_privacy_claim(evidence_text, origin):
    """T-26 (L), C-28: protocol-shape ZK is not a control, and no
    evidence packet, log, or report may claim a privacy guarantee the
    build does not provide."""
    lowered = evidence_text.lower()
    for term in PRIVACY_VOCABULARY:
        if term in lowered:
            refuse("privacy-honesty", "privacy-property-asserted",
                   f"{origin}: '{term}' -- no privacy property is "
                   "asserted in evidence (T-26, C-28)")
    return "no-privacy-claim"


# ---------------------------------------------------------------------------
# Freshness: C-26 -- live re-read before consequence; unknown on
# observation failure; no stale substitution (T-17/T-23).
# ---------------------------------------------------------------------------


class LiveSource:
    def __init__(self, validator, clock):
        self.validator = validator
        self.clock = clock

    def read(self, source):
        info = self.validator.fetch(source)
        return {"source": source, "at": self.clock.iso(),
                "fresh": True, "current": True}

    def read_or_unknown(self, source, alive):
        """T-17: a dead source renders as unknown -- never a stale
        substitution."""
        if not alive:
            return {"source": source, "state": "unknown",
                    "reason": "observation failure (C-26)"}
        return self.read(source)


def consequential_on_reading(reading, execute):
    """T-23: a stale or unknown reading cannot become a consequence."""
    if reading.get("state") == "unknown":
        refuse("freshness", "stale-state-cannot-consequence",
               "unknown on observation failure (T-23, C-26)")
    if not reading.get("fresh"):
        refuse("freshness", "stale-state-cannot-consequence",
               "live re-read required before consequence (T-23, C-26)")
    return execute()
