"""Phase 4 Layer 2 — idempotency orchestrator reference model.

Implements the v0.1 drafts in ~/workspace/jarvis-formal-spec/tests/phase4/:
- idempotency-key-spec.md: K1-K6 — eight-field key, revision frozen at
  BIND (Q2), device_session_id excluded (Q3), canonical-JSON procedure
  (Phase 2 Q4), the effect/request asymmetry.
- execution-record-spec.md: ten-field record, ER1-ER6, the state machine
  prepared -> approved -> execution_requested -> execution_started ->
  execution_observed / execution_failed / execution_unknown ->
  completed / cancelled.
- saga-spec.md: S1-S8 — the governed saga over the six-step ceremony;
  Q1 (orchestrator signs worker-prepared digests after recompute);
  Q5 (fresh ceremony for consequential compensation); no silent rollback.
- retry-policy-matrix.md: RF1-RF9 — the safe_to_retry flag as the single
  gate on retries.
- ambiguity-protocol.md: AP1-AP6 — no silent completion, no auto-retry,
  verify-externally-per-class, execution_unknown surfaced on next pull
  plus an escalated notification hint (Q4).

Reuses the Phase 3 harness: approval_digest (the ratified eight-field
procedure) from tests/phase3/layer2/digest.py — extended, not duplicated.

NOT production code: a minimal model enforcing the draft rules so the
Layer 2 tests can assert them. Python 3 standard library only. No
network, no git, no publishing. Virtual clock, integer epoch seconds.
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "phase3", "layer2"))
from digest import approval_digest  # ratified eight-field procedure

# ----------------------------------------------------------------------
# canonical JSON (Phase 2 Q4 procedure, shared with digest.py)
# ----------------------------------------------------------------------

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256hex(b):
    return hashlib.sha256(b).hexdigest()


# The eight key fields, in binding order (idempotency-key-spec.md K1).
KEY_FIELDS = ("work_id", "intent_id", "intent_digest", "action", "target",
              "scope", "revision", "operation_class")


def compute_key(work_id, intent_id, intent_digest, action, target, scope,
                revision_at_approval, operation_class):
    """K1-K5: the idempotency key. revision is frozen at BIND (K2/Q2);
    device_session_id is excluded (K3/Q3)."""
    bound = {"work_id": work_id, "intent_id": intent_id,
             "intent_digest": intent_digest, "action": action,
             "target": target, "scope": scope,
             "revision": revision_at_approval,
             "operation_class": operation_class}
    return sha256hex(canonical({k: bound[k] for k in KEY_FIELDS}))


# Every orchestrator ever constructed registers here so run.sh can dump
# one combined rejection ledger at teardown (Phase 3 convention).
_ALL = []


def dump_all_refusals(path):
    with open(path, "a", encoding="utf-8") as f:
        for oi, orch in enumerate(_ALL):
            start = getattr(orch, "_dumped", 0)
            for si, (reason, kind, ref, detail) in enumerate(orch.refusals[start:], start):
                f.write("%d:%d\t%s\t%s\t%s\t%s\n" % (oi, si, reason, kind, ref, detail))
            orch._dumped = len(orch.refusals)


# ----------------------------------------------------------------------
# tool plane — deterministic, test-configured
# ----------------------------------------------------------------------
# Outcomes per fire: "receipt" (effect + receipt), "dropped" (effect,
# no receipt — ambiguous), "lost" (no effect, no receipt — ambiguous),
# "failed" (definitive failure, no effect). The orchestrator cannot
# distinguish "dropped" from "lost": that is the point of ambiguity.

class ToolPlane:
    def __init__(self):
        self.plan = {}      # key -> list of outcomes, consumed in order
        self.effects = {}   # key -> times the consequential effect fired

    def set(self, key, outcomes):
        self.plan[key] = list(outcomes)

    def fire(self, key):
        outcomes = self.plan.get(key, ["receipt"])
        outcome = outcomes.pop(0) if outcomes else "receipt"
        self.plan[key] = outcomes
        if outcome in ("receipt", "dropped"):
            self.effects[key] = self.effects.get(key, 0) + 1
        return outcome

    def effect_count(self, key):
        return self.effects.get(key, 0)


# ----------------------------------------------------------------------
# the idempotency orchestrator
# ----------------------------------------------------------------------

TERMINAL = ("completed", "cancelled")


class IdemOrchestrator:
    """Single authoritative writer of execution records."""

    def __init__(self, now):
        self.now = int(now)
        self.records = {}       # key -> execution record
        self.tool = ToolPlane()
        self.hints = []         # escalated notification hints (Q4/AP5)
        self.refusals = []      # the sealed refusal ledger
        self.sealed_log = []    # every transition + refusal, in order
        _ALL.append(self)

    # -- internal ------------------------------------------------------
    def _refuse(self, reason, key, detail):
        self.refusals.append((reason, "idempotency", key[:12], detail))
        self.sealed_log.append(("refused", reason, key[:12], self.now))
        return {"ok": False, "reason": reason, "detail": detail}

    def _transition(self, rec, state):
        rec["execution_state"] = state
        rec["updated_at"] = self.now
        rec["status"] = ("completed" if state == "completed"
                         else "cancelled" if state == "cancelled"
                         else "active")
        self.sealed_log.append(("transition", rec["key"][:12], state, self.now))

    def _public(self, rec):
        # The pull view of a record (ambiguity-protocol.md section 4).
        view = dict(rec)
        if rec["execution_state"] == "execution_unknown":
            view["safe_options"] = ["cancel", "verify-manually", "re-approve-afresh"]
        return view

    # -- saga surface (saga-spec.md S1-S8) -------------------------------
    def prepare(self, key, operation_class):
        rec = self.records.get(key)
        if rec is not None:
            return {"ok": True, "duplicate": True, "record": self._public(rec)}
        rec = {"key": key, "status": "active",
               "created_at": self.now, "updated_at": self.now,
               "approval_ref": None, "execution_state": "prepared",
               "observed_result": None, "attempt_count": 0,
               "last_error": None, "safe_to_retry": False,
               "operation_class": operation_class}
        self.records[key] = rec
        self.sealed_log.append(("prepared", key[:12], self.now))
        return {"ok": True, "record": self._public(rec)}

    def approve(self, key, approval_ref):
        rec = self.records.get(key)
        if rec is None:
            return self._refuse("no-such-record", key, "approve before prepare")
        if rec["execution_state"] != "prepared":
            # RF3: approvals recorded once — duplicates return the existing
            # decision, never a second decision.
            return {"ok": True, "duplicate": True, "record": self._public(rec)}
        rec["approval_ref"] = approval_ref
        self._transition(rec, "approved")
        return {"ok": True, "record": self._public(rec)}

    def request_execution(self, key):
        """S4/ER2: the at-most-once point. Duplicates return the existing
        record — never a second execution."""
        rec = self.records.get(key)
        if rec is None:
            return self._refuse("no-such-record", key, "execute before prepare")
        if rec["execution_state"] != "approved":
            # Duplicate tap / replay against any non-approved state:
            # return the existing record (DT family).
            return {"ok": True, "duplicate": True, "record": self._public(rec)}
        self._transition(rec, "execution_requested")
        return self._fire(rec)

    def _fire(self, rec):
        key = rec["key"]
        self._transition(rec, "execution_started")
        rec["attempt_count"] += 1
        outcome = self.tool.fire(key)
        if outcome == "receipt":
            rec["observed_result"] = {"receipt": "tool-receipt:%s" % key[:12]}
            self._transition(rec, "execution_observed")
            self._transition(rec, "completed")
            return {"ok": True, "record": self._public(rec)}
        if outcome == "failed":
            rec["last_error"] = "tool-failed"
            # RF7: the tool plane observed non-occurrence — a retry is
            # safe (this is a definitive observation, not ambiguity).
            # Trust boundary note: the tool is trusted to report its own
            # outcomes truthfully; Byzantine tools are Phase 5 scope
            # (P4-OP-5).
            rec["safe_to_retry"] = True
            self._transition(rec, "execution_failed")
            return {"ok": False, "reason": "execution-failed",
                    "record": self._public(rec)}
        # "dropped" or "lost": ambiguous. AP1/AP2 — do not mark
        # completed, do not auto-retry. The orchestrator cannot tell
        # which happened; that is the point.
        rec["last_error"] = "no-receipt"
        rec["safe_to_retry"] = False          # RF8
        self._transition(rec, "execution_unknown")
        return {"ok": False, "reason": "execution-unknown",
                "record": self._public(rec)}

    def retry(self, key):
        """RF4: retries proceed only when safe_to_retry holds."""
        rec = self.records.get(key)
        if rec is None:
            return self._refuse("no-such-record", key, "retry of nothing")
        if rec["execution_state"] in TERMINAL:
            return {"ok": True, "duplicate": True, "record": self._public(rec)}
        if not rec["safe_to_retry"]:
            # RF9: a refused retry changes nothing — attempt_count does
            # not advance.
            return self._refuse("unsafe-retry", key,
                                "safe_to_retry=false (RF4/RF8): refusing")
        # Verified safe: the earlier effect was observed absent (RF7), so
        # this fire is still the first actual effect. Reset to approved
        # and fire once.
        rec["safe_to_retry"] = False  # one-shot: re-verify after each fire
        self._transition(rec, "approved")
        self._transition(rec, "execution_requested")
        return self._fire(rec)

    def verify_external(self, key, observed):
        """AP3: external verification resolves the unknown. observed is
        "present" (the effect happened) or "absent" (it did not)."""
        rec = self.records.get(key)
        if rec is None:
            return self._refuse("no-such-record", key, "verify of nothing")
        if rec["execution_state"] != "execution_unknown":
            return self._refuse("not-unknown", key,
                                "nothing ambiguous to resolve")
        if observed == "present":
            rec["observed_result"] = {"receipt": "external-verification:%s" % key[:12]}
            rec["last_error"] = None
            self._transition(rec, "execution_observed")
            self._transition(rec, "completed")
            return {"ok": True, "record": self._public(rec)}
        if observed == "absent":
            # RF7: the effect is verified absent — a retry is now safe.
            rec["safe_to_retry"] = True
            rec["last_error"] = "verified-absent"
            self._transition(rec, "execution_unknown")  # re-log the state
            return {"ok": True, "record": self._public(rec)}
        return self._refuse("bad-observation", key, "observed must be present|absent")

    def pull(self, key):
        """The record is the truth (Q4/AP5). An unknown record surfaces
        with its safe options and emits an escalated hint — a pointer,
        never the record itself (AP6)."""
        rec = self.records.get(key)
        if rec is None:
            return {"ok": False, "reason": "no-such-record"}
        view = self._public(rec)
        if rec["execution_state"] == "execution_unknown":
            self.hints.append({"key": key[:12],
                               "state": "execution_unknown",
                               "at": self.now,
                               "pointer": "record"})
            view["hint_emitted"] = True
        return {"ok": True, "record": view}

    def cancel(self, key):
        rec = self.records.get(key)
        if rec is None:
            return self._refuse("no-such-record", key, "cancel of nothing")
        if rec["execution_state"] in TERMINAL:
            return {"ok": True, "duplicate": True, "record": self._public(rec)}
        self._transition(rec, "cancelled")
        return {"ok": True, "record": self._public(rec)}

    # -- worker-prepared intents (Q1 / saga-spec.md S7) -------------------
    def propose_worker_intent(self, worker_id, record):
        """The orchestrator recomputes the digest and signs; authorship
        goes in provenance. A digest the worker tampered with is refused."""
        claimed = record.get("digest")
        bare = {k: v for k, v in record.items() if k != "digest"}
        recomputed = approval_digest(bare)
        if claimed != recomputed:
            return self._refuse("digest-mismatch", record.get("intent_id", "?"),
                                "worker digest != recomputed digest")
        signed = dict(record)
        signed["signature"] = {"by": "orchestrator", "digest": recomputed,
                               "at": self.now}
        signed["provenance"] = {"prepared_by": worker_id}
        self.sealed_log.append(("worker-intent-signed", record.get("intent_id"),
                                worker_id, self.now))
        return {"ok": True, "intent": signed}

    # -- compensation (Q5 / saga-spec.md S6) -------------------------------
    def request_compensation(self, original_key, comp_key, comp_approval_ref):
        """A consequential compensation needs its own fresh ceremony: its
        own key and its own approval. Riding the original key/approval is
        refused — no silent rollback (S8)."""
        if comp_key == original_key or not comp_approval_ref:
            return self._refuse("needs-fresh-ceremony", comp_key,
                                "compensation requires its own key and approval (S6)")
        r = self.prepare(comp_key, "compensate")
        if not r["ok"]:
            return r
        r = self.approve(comp_key, comp_approval_ref)
        if not r["ok"]:
            return r
        return self.request_execution(comp_key)
