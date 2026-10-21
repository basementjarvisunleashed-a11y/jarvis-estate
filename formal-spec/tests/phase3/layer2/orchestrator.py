"""Phase 3 Layer 2 — orchestrator reference model for the protocol tests.

Implements the v0.1 drafts in ~/workspace/jarvis-formal-spec/tests/phase3/:
- revision-protocol.md: six-field revision token, monotonicity R1-R5,
  the five-step rejection order (session -> freshness -> intent liveness
  -> revision currency -> digest binding), fail-closed, every refusal a
  logged event. For decide requests the digest binding is evaluated
  BEFORE revision currency (5-before-4): sequence-diagrams.md (b)
  requires a digest mismatch to lapse the ceremony even when the
  revision is also stale — "the stricter of the two failures governs"
  (Layer 3 chaos finding, 2026-10-21).
- conflict-resolution.md: CR-1..CR-8 deterministic resolutions.
- consistency-model.md: the orchestrator as single authoritative writer
  (NT-1); event-sourced work state; the tap is a gesture, the record is
  the decision (NT-5).
- sequence-diagrams.md: the (a)-(d) paths, including the loser's
  refuse/name-current/re-pull path in (b).

NOT the deployment substrate and NOT production code: a minimal model
that enforces the draft rules so the Layer 2 tests can assert them.
Python 3 standard library only. No network, no git, no publishing.

Clock bounds (OP-1, resolved on HgX's word 2026-10-21 ~17:49 ET):
  REQUEST_SKEW = 300 s — request freshness (five-step check #2).
  EVENT_SKEW   =  60 s — state/event freshness (Phase 0 U-5/D7, ratified).
"""

import os

from digest import approval_digest

# OP-1 ruling: keep both bounds.
REQUEST_SKEW = 300  # seconds — request freshness (substrate reference)
EVENT_SKEW = 60     # seconds — state/event freshness (Phase 0 U-5/D7, ratified)

# Draft horizons from freshness-policy.md section 4 / cache-policy.md
# section 3 (draft numbers — the rules, not the numbers, are the policy).
STATUS_HORIZON_WATCH = 30
STATUS_HORIZON_IPHONE = 60


class Refusal(Exception):
    """Raised internally; the model returns refusal dicts, not exceptions."""

    def __init__(self, reason, detail=""):
        self.reason = reason
        self.detail = detail
        super().__init__("%s: %s" % (reason, detail))


# Every orchestrator ever constructed registers here so run.sh can dump
# one combined rejection ledger at teardown.
_ALL = []


def dump_all_refusals(path):
    """Append every recorded refusal (seq, reason, kind, ref, detail) —
    each exactly once, even when called from several modules'
    tearDownModule. The per-orchestrator sequence number proves
    exactly-once: no two rows share an (orchestrator, seq)."""
    with open(path, "a", encoding="utf-8") as f:
        for oi, orch in enumerate(_ALL):
            start = getattr(orch, "_dumped", 0)
            for si, (reason, kind, ref, detail) in enumerate(orch.refusals[start:], start):
                f.write("%d:%d\t%s\t%s\t%s\t%s\n" % (oi, si, reason, kind, ref, detail))
            orch._dumped = len(orch.refusals)


class Orchestrator:
    """The estate's single authoritative writer (consistency-model.md section 4)."""

    def __init__(self, now):
        self.now = int(now)          # virtual server clock, integer epoch seconds
        self.sessions = {}           # device_session_id -> {"device", "revoked"}
        self.works = {}              # work_id -> {"revision", "state", "history", "events"}
        self.intents = {}            # intent_id -> {"record", "digest", "superseded", "live_predicate"}
        self.decisions = {}          # intent_id -> recorded decision (exactly one per intent)
        self.lapses = []             # attested lapses (digest mismatch)
        self.memory = {}             # durable memory facts (CR-4: superseded history)
        self.live_source = {}        # work_id -> current live fact (CR-4)
        self.evidence = {}           # work_id -> [sealed packet revisions] (CR-7)
        self.artifacts = {}          # artifact_id -> {"digest"} (CR-8)
        self.hints = []              # emitted notification hints (CR-6)
        self.refusals = []           # the sealed refusal ledger
        self.sealed_log = []         # every accepted transition + refusal, in order
        _ALL.append(self)

    # ------------------------------------------------------------------
    # setup (test fixture helpers, not protocol surface)
    # ------------------------------------------------------------------
    def enroll(self, session_id, device):
        self.sessions[session_id] = {"device": device, "revoked": False}

    def revoke(self, session_id):
        self.sessions[session_id]["revoked"] = True

    def mint_work(self, work_id, state):
        self.works[work_id] = {"revision": 0, "state": state,
                               "history": {0: state},
                               "events": [("minted", 0, self.now)]}

    def propose_intent(self, intent_id, work_id, action, target, effect,
                       scope, revision, expiry, live_predicate=None):
        record = {"intent_id": intent_id, "work_id": work_id, "action": action,
                  "target": target, "effect": effect, "scope": scope,
                  "revision": revision, "expiry": expiry}
        self.intents[intent_id] = {"record": record,
                                   "digest": approval_digest(record),
                                   "superseded": False,
                                   "live_predicate": live_predicate}

    def set_live_fact(self, work_id, fact):
        old = self.live_source.get(work_id)
        if old is not None and old != fact:
            self.memory[work_id] = old  # superseded, retained, flagged
        self.live_source[work_id] = fact

    def seal_evidence(self, work_id, packet):
        revs = self.evidence.setdefault(work_id, [])
        revs.append({"artifact_revision": len(revs), "packet": packet,
                     "sealed_at": self.now})
        return len(revs) - 1

    def record_artifact(self, artifact_id, digest):
        self.artifacts[artifact_id] = {"digest": digest}

    # ------------------------------------------------------------------
    # the five-step gate — revision-protocol.md section 5, in order,
    # fail closed at the first failure.
    # ------------------------------------------------------------------
    def _refuse(self, reason, req, detail):
        kind = req.get("kind", "?")
        ref = req.get("intent_id") or req.get("work_id") or "?"
        self.refusals.append((reason, kind, ref, detail))
        self.sealed_log.append(("refused", reason, kind, ref, self.now))
        resp = {"ok": False, "reason": reason, "detail": detail}
        wid = req.get("work_id")
        if wid in self.works:
            resp["current_revision"] = self.works[wid]["revision"]
        return resp

    def _gate(self, req):
        # 1. session
        sess = self.sessions.get(req.get("device_session_id"))
        if not sess or sess["revoked"]:
            return self._refuse("unknown-session", req,
                                "session not enrolled or revoked")
        # 2. freshness — request bound (300 s), then event bound (60 s)
        ts = req.get("timestamp")
        if ts is None:
            return self._refuse("stale-request", req, "missing timestamp")
        if abs(self.now - int(ts)) > REQUEST_SKEW:
            return self._refuse(
                "stale-request", req,
                "|now-ts|=%d > %d (request bound)" % (abs(self.now - int(ts)), REQUEST_SKEW))
        oa = req.get("observed_at")
        if oa is not None and self.now - int(oa) > EVENT_SKEW:
            return self._refuse(
                "stale-event", req,
                "event age %d s > %d s (state/event bound)" % (self.now - int(oa), EVENT_SKEW))
        # 3. intent liveness
        iid = req.get("intent_id")
        if iid is not None:
            it = self.intents.get(iid)
            if it is None:
                return self._refuse("intent-invalid", req, "intent unknown")
            if it["superseded"]:
                return self._refuse("intent-invalid", req, "intent superseded")
            if self.now >= it["record"]["expiry"]:
                return self._refuse("intent-invalid", req, "intent expired")
            if approval_digest(it["record"]) != it["digest"]:
                # Changed intent is never updated in place.
                return self._refuse("intent-invalid", req,
                                    "intent mutated since proposal; propose a new intent")
            lp = it.get("live_predicate")
            if lp is not None:
                live = self.live_source.get(lp["work_id"])
                if live != lp["expected"]:
                    return self._refuse(
                        "intent-invalid", req,
                        "live source moved (CR-4): expected %r, live is %r"
                        % (lp["expected"], live))
        # 5-before-4 for decisions (Layer 3 chaos finding, 2026-10-21):
        # sequence-diagrams.md (b) requires that a digest mismatch lapses
        # the ceremony even when the revision is also stale — "the
        # stricter of the two failures governs". A stale-revision refusal
        # must not mask a digest mismatch: the attested lapse is the audit
        # trail for approving something that is not the current intent.
        if req.get("kind") == "decide" and iid is not None:
            it2 = self.intents.get(iid)
            if it2 is not None and req.get("digest_seen") != it2["digest"]:
                self.lapses.append({"intent_id": iid, "at": self.now,
                                    "seen": req.get("digest_seen"),
                                    "digest": it2["digest"]})
                self.sealed_log.append(("lapsed", iid, self.now))
                return self._refuse("digest-lapse", req,
                                    "D_seen != D: ceremony lapsed, no execution, attested lapse")
        # 4. revision currency — accepted iff held == current (R2)
        wid = req.get("work_id")
        if wid is not None:
            cur = self.works[wid]["revision"]
            if req.get("revision") != cur:
                return self._refuse(
                    "stale-revision", req,
                    "held=%r current=%d (R2: no older, no newer, no missing)"
                    % (req.get("revision"), cur))
        return None

    # ------------------------------------------------------------------
    # protocol surface
    # ------------------------------------------------------------------
    def submit(self, req):
        refused = self._gate(req)
        if refused:
            return refused
        kind = req.get("kind")
        if kind == "mutate":
            return self._mutate(req)
        if kind == "decide":
            return self._decide(req)
        if kind == "read":
            return self._read(req)
        if kind == "reconcile":
            return self._reconcile(req)
        return self._refuse("unknown-kind", req, "no such request kind")

    def _mutate(self, req):
        w = self.works[req["work_id"]]
        w["state"] = req["new_state"]
        w["revision"] += 1                      # R3: revision becomes revision + 1
        w["history"][w["revision"]] = req["new_state"]
        w["events"].append(("mutated", w["revision"], req["device_session_id"], self.now))
        self.sealed_log.append(("mutated", req["work_id"], w["revision"], self.now))
        return {"ok": True, "revision": w["revision"]}   # R3: response carries the new revision

    def _decide(self, req):
        iid = req["intent_id"]
        it = self.intents[iid]
        # 5. digest binding — D_seen must equal the intent's current digest D.
        if req.get("digest_seen") != it["digest"]:
            self.lapses.append({"intent_id": iid, "at": self.now,
                                "seen": req.get("digest_seen"), "digest": it["digest"]})
            self.sealed_log.append(("lapsed", iid, self.now))
            return self._refuse("digest-lapse", req,
                                "D_seen != D: ceremony lapsed, no execution, attested lapse")
        if iid in self.decisions:
            d = self.decisions[iid]
            if d.get("superseded_by_artifact_change"):
                # CR-8: the approval is invalid; there is no "re-confirm
                # the same approval" — the changed artifact is a new
                # intent, proposed and approved afresh.
                return self._refuse(
                    "intent-invalid", req,
                    "approval invalidated by artifact change; propose a new intent")
            # First valid decision recorded wins (CR-2): the loser's
            # request is a read of the existing decision — not recorded,
            # not executed, not an error the principal must resolve.
            return {"ok": True, "status": "already-recorded", "decision": d}
        w = self.works[it["record"]["work_id"]]
        w["revision"] += 1
        w["history"][w["revision"]] = w["state"]
        decision = {"intent_id": iid, "digest": it["digest"],
                    "recorded_at": self.now, "revision": w["revision"],
                    "executed": True, "by": req["device_session_id"]}
        self.decisions[iid] = decision
        w["events"].append(("decision-recorded", w["revision"], iid, self.now))
        self.sealed_log.append(("decision-recorded", iid, w["revision"], self.now))
        return {"ok": True, "status": "recorded", "decision": decision}

    def _read(self, req):
        # R5: reads carry the token's work_id/revision as a pin — the
        # server serves the pinned revision or refuses, never a silently
        # newer one.
        w = self.works[req["work_id"]]
        pin = req.get("revision")
        if pin not in w["history"]:
            return self._refuse("stale-revision", req,
                                "pinned read: revision %r not held; refusing rather "
                                "than serving newer silently" % (pin,))
        return {"ok": True, "state": w["history"][pin], "revision": pin,
                "stamp": self._stamp(req["work_id"], "status", req.get("device"))}

    def _reconcile(self, req):
        # CR-5: the orchestrator reconciles durable contradictions as a
        # proposed correction citing both antecedents — append-only.
        w = self.works[req["work_id"]]
        w["revision"] += 1
        w["history"][w["revision"]] = req["correction"]
        w["events"].append(("correction", w["revision"], req["antecedents"], self.now))
        self.sealed_log.append(("correction", req["work_id"], w["revision"], self.now))
        return {"ok": True, "revision": w["revision"],
                "antecedents": req["antecedents"]}

    # ------------------------------------------------------------------
    # CR-6 / CR-7 / CR-8 helpers
    # ------------------------------------------------------------------
    def emit_hint(self, work_id):
        hint = {"work_id": work_id, "state": self.works[work_id]["state"],
                "revision": self.works[work_id]["revision"], "at": self.now}
        self.hints.append(hint)
        return hint

    def read_evidence(self, work_id, artifact_revision):
        revs = self.evidence.get(work_id, [])
        if 0 <= artifact_revision < len(revs):
            return {"ok": True, "packet": revs[artifact_revision]}
        return {"ok": False, "reason": "no-such-revision"}

    def change_artifact(self, artifact_id, new_digest):
        # CR-8: the artifact changed after approval — the old approval is
        # invalid; a new approval requires a fresh intent.
        self.artifacts[artifact_id]["digest"] = new_digest
        for iid, d in self.decisions.items():
            if d.get("artifact_id") == artifact_id:
                d["superseded_by_artifact_change"] = True
        for iid, it in self.intents.items():
            if it["record"].get("target") == artifact_id and iid not in self.decisions:
                it["superseded"] = True

    # ------------------------------------------------------------------
    # stamps (freshness-policy.md)
    # ------------------------------------------------------------------
    def _stamp(self, work_id, payload_class, device=None, fresh_until=None):
        if payload_class == "approval-card":
            # The card lives until the intent's expiry (freshness-policy.md
            # section 4: approval card horizon is expires_at, binding).
            fresh_until = fresh_until if fresh_until is not None else self.now
        elif payload_class == "status":
            horizon = STATUS_HORIZON_WATCH if device == "watch" else STATUS_HORIZON_IPHONE
            fresh_until = self.now + horizon
        else:
            fresh_until = self.now + EVENT_SKEW
        return {"observed_at": self.now, "fresh_until": fresh_until,
                "revision": self.works[work_id]["revision"]}
