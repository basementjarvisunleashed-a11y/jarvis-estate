"""Phase 1 — Pull protocol (paper section 2.2).

Five pull-discipline rules, enforced in code:
  (1) every interaction begins with a client pull;
  (2) every response is sealed;
  (3) nothing renders/executes before its seal verifies;
  (4) denials are sealed and auditable — a refused pull is information;
  (5) timeouts/retries are the client's business; the server never chases.

There is NO push path. Anything push-like is a long-poll (a client pull
with a wait_deadline) or a routine client pull.

Components (each in exactly one plane):
  PullServer        control plane — answers pulls. Reaches the data plane
                    ONLY through PlaneGateway.pull(). Holds NO key material.
  PullClient        data plane    — a surface. Signs requests with its own
                    enrollment key (the one key a surface holds, issued by
                    the Phase-0 ceremony). Verifies every seal before render.
  GovernanceServer  governance    — holds ALL ceremony keys. The only
                    component that seals or verifies with them.
  DataServer        data plane    — serves sealed state. Blobs are sealed by
                    governance at rest; the data plane never seals itself.
  Phase1Gateway     PlaneGateway + gateway-bypass enforcement + partition
                    fault injection (chaos testing).

Authority model (keys stay in governance):
  * Request / response / denial envelopes are sealed INSIDE governance with
    the surface's enrollment key (the "verify-request" and "seal" ops take
    key NAMES — key bytes never cross a plane boundary).
  * The gateway's own transport envelope on server-initiated pulls is sealed
    with TRANSPORT_KEY, a PUBLIC framing constant, not a credential: it
    carries no authority. Authority lives only in the inner envelopes that
    governance sealed. Control/data components never receive ceremony keys.
  * A client verifies with the keys it legitimately holds (its own
    enrollment key); proof verification against the master key runs inside
    governance via the "verify" op.

Python 3 stdlib only. No network, no git, no publishing.
"""
import os
import sys
import time
from contextvars import ContextVar

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import seal
from common.log import IntentLog, ENTRY_TYPES
from common.planes import Plane, PlaneViolation, Component, PlaneGateway
from common.seal import SealError

# Requests older/newer than this vs. the server clock are refused (chaos:
# clock-skew case uses +/-300s against this bound).
MAX_SKEW = 300

# Public framing constant for gateway transport envelopes on
# server-initiated pulls. NOT a credential — carries no authority.
TRANSPORT_KEY = b"phase1-test-transport-framing-only"

_gateway_in_ctx = ContextVar("phase1_gateway_ctx", default=False)


class PartitionError(Exception):
    """The gateway dropped a pull (simulated partition, chaos testing)."""


class Phase1Gateway(PlaneGateway):
    """PlaneGateway with (a) bypass enforcement and (b) partition injection.

    (a) serve_pull on any Phase-1 server raises PlaneViolation unless the
        call arrived through this gateway (context flag).
    (b) when .partition is True, pulls are dropped with PartitionError
        before they are audited or served — the client retries (rule 5)
        and the server never chases (there is no code path for it).
    """

    def __init__(self, clock):
        super().__init__(clock)
        self.partition = False

    def pull(self, requester, to_plane, query, key):
        if self.partition:
            raise PartitionError(
                "partition: pull %r (%s -> %s) dropped"
                % (query.get("req_id"), requester.plane, to_plane))
        token = _gateway_in_ctx.set(True)
        try:
            return super().pull(requester, to_plane, query, key)
        finally:
            _gateway_in_ctx.reset(token)


def _require_gateway():
    if not _gateway_in_ctx.get():
        raise PlaneViolation(
            "serve_pull called outside a gateway pull — cross-plane "
            "traffic must go through the gateway")


class GovernanceServer(Component):
    """Governance plane. Holds ALL ceremony keys; the only component that
    seals or verifies with them. Never executes work, never pushes."""

    plane = Plane.GOVERNANCE

    def __init__(self, name, keyset):
        super().__init__(name)
        self.keyset = dict(keyset)

    def serve_pull(self, query):
        _require_gateway()
        op = query.get("op")
        if op == "verify-request":
            return self._verify_request(query.get("envelope") or {})
        if op == "seal":
            key = self.keyset.get(query.get("key_name"))
            if key is None:
                raise SealError("unknown key_name %r" % query.get("key_name"))
            return {"envelope": seal.make_envelope(
                key, query.get("content"), query.get("origin"),
                query.get("ts"))}
        if op == "verify":
            key = self.keyset.get(query.get("key_name"))
            if key is None:
                raise SealError("unknown key_name %r" % query.get("key_name"))
            return {"ok": seal.verify_envelope(
                key, query.get("envelope") or {})}
        raise ValueError("unknown governance op %r" % op)

    def _verify_request(self, env):
        content = env.get("content") or {}
        surface_id = content.get("surface_id")
        key = self.keyset.get("surface:%s" % surface_id)
        if key is None:
            return {"ok": False, "surface_id": None,
                    "reason": "unknown-surface"}
        if seal.verify_envelope(key, env):
            return {"ok": True, "surface_id": surface_id, "reason": None}
        return {"ok": False, "surface_id": None, "reason": "bad-signature"}


class DataServer(Component):
    """Data plane. Serves sealed state, evidence, baselines. Never decides,
    never pushes. Blobs arrive already sealed by governance."""

    plane = Plane.DATA

    def __init__(self, name):
        super().__init__(name)
        self.blobs = {}        # key -> {"data": ..., "sealed": envelope}
        self.samples = []      # sense feed: [{"data": ..., "sealed": ...}]
        self.read_counts = {}  # key -> reads served (idempotency evidence)

    def store(self, key, data, sealed_envelope):
        self.blobs[key] = {"data": data, "sealed": sealed_envelope}

    def push_sample(self, data, sealed_envelope):
        self.samples.append({"data": data, "sealed": sealed_envelope})

    def serve_pull(self, query):
        _require_gateway()
        op = query.get("op")
        if op in ("read", "deep-read"):
            key = query.get("key")
            self.read_counts[key] = self.read_counts.get(key, 0) + 1
            blob = self.blobs.get(key)
            if blob is None:
                return {"ok": False, "reason": "no-data", "key": key}
            return {"ok": True, "key": key, "data": blob["data"],
                    "sealed": blob["sealed"], "deep": op == "deep-read"}
        if op == "sample":
            if not self.samples:
                return {"ok": False, "reason": "no-samples"}
            item = self.samples.pop(0)
            return {"ok": True, "data": item["data"],
                    "sealed": item["sealed"]}
        raise ValueError("unknown data op %r" % op)


class PullServer(Component):
    """Control plane. Answers pulls. Reaches data/governance ONLY through
    PlaneGateway.pull(). Holds no key material: every seal/verify runs
    inside governance.

    Order of checks per pull (rule 3): replay -> freshness -> signature ->
    work. Nothing is fetched or executed before the seal verifies.
    """

    plane = Plane.CONTROL

    def __init__(self, name, clock):
        super().__init__(name)
        self.clock = clock
        self.seen = {}            # req_id -> (request bytes, sealed response)
        self.served_journal = []  # drained by the orchestrator SERVE phase
        self.log = None           # GovernedLog, wired by the harness

    # -- gateway entry point -------------------------------------------
    def serve_pull(self, query):
        _require_gateway()
        req_env = query.get("request") or {}
        content = req_env.get("content") or {}
        req_id = content.get("req_id", "req-?")
        surface_id = content.get("surface_id")
        wait_deadline = query.get("wait_deadline")

        # Replay: identical request -> identical sealed response, no new
        # effect. Same req_id with DIFFERENT bytes -> sealed denial.
        if req_id in self.seen:
            seen_bytes, seen_resp = self.seen[req_id]
            if seen_bytes == seal.canonical(req_env):
                return {"response": seen_resp, "duplicate": True}
            return self._deny(req_id, surface_id, "req-id-reuse")

        # Freshness before crypto before work.
        ts = content.get("ts")
        if not isinstance(ts, int) or abs(self.clock.now() - ts) > MAX_SKEW:
            return self._deny(req_id, surface_id, "stale-request")

        # Signature verification, inside governance.
        verdict = self._gov({"op": "verify-request", "envelope": req_env,
                             "req_id": req_id})
        if not verdict.get("ok"):
            return self._deny(req_id, surface_id,
                              verdict.get("reason") or "bad-signature")

        data_key = (content.get("query") or {}).get("key")
        revision = content.get("revision")

        if wait_deadline is not None:
            # Long-poll: a client pull the server holds until data arrives
            # or the deadline passes. Still client-initiated.
            return self._long_poll(req_env, req_id, surface_id, revision,
                                   data_key, wait_deadline)
        res = self._data({"op": "read", "key": data_key, "req_id": req_id})
        if not res.get("ok"):
            return self._deny(req_id, surface_id,
                              res.get("reason") or "no-data")
        return self._respond(req_env, req_id, surface_id, revision,
                             data_key, res)

    # -- long-poll ------------------------------------------------------
    def _wait_tick(self, n):
        """Hold a long-poll one step. Test seam: override to inject data."""
        if hasattr(self.clock, "advance"):
            self.clock.advance(1)
        else:
            time.sleep(0.01)

    def _long_poll(self, req_env, req_id, surface_id, revision, data_key,
                   deadline):
        for n in range(10000):  # bounded; the deadline always terminates it
            res = self._data({"op": "read", "key": data_key,
                              "req_id": req_id})
            if res.get("ok"):
                return self._respond(req_env, req_id, surface_id, revision,
                                     data_key, res)
            if self.clock.now() >= deadline:
                return self._respond_timeout(req_env, req_id, surface_id,
                                             revision)
            self._wait_tick(n)
        return self._respond_timeout(req_env, req_id, surface_id, revision)

    # -- responses (every one sealed — rule 2) --------------------------
    def _respond(self, req_env, req_id, surface_id, revision, data_key,
                 res):
        ts = self.clock.now()
        content = {"req_id": req_id, "revision": revision,
                   "body": res["data"], "proof": res["sealed"]}
        envelope = self._gov({
            "op": "seal", "key_name": "surface:%s" % surface_id,
            "content": content, "origin": self.name, "ts": ts,
            "req_id": req_id})["envelope"]
        return self._record(req_env, req_id, surface_id, "served",
                            data_key, envelope, ts)

    def _respond_timeout(self, req_env, req_id, surface_id, revision):
        ts = self.clock.now()
        content = {"req_id": req_id, "revision": revision,
                   "body": None, "timeout": True}
        envelope = self._gov({
            "op": "seal", "key_name": "surface:%s" % surface_id,
            "content": content, "origin": self.name, "ts": ts,
            "req_id": req_id})["envelope"]
        return self._record(req_env, req_id, surface_id, "timeout",
                            None, envelope, ts)

    def _deny(self, req_id, surface_id, reason):
        """Sealed denial (rule 4). The refused pull is logged as DENIAL —
        a refused pull is information."""
        ts = self.clock.now()
        key_name = ("surface:%s" % surface_id) if surface_id else "master"
        try:
            envelope = self._gov({
                "op": "seal", "key_name": key_name,
                "content": {"req_id": req_id, "reason": reason, "ts": ts},
                "origin": self.name, "ts": ts,
                "req_id": req_id})["envelope"]
        except SealError:
            # Unknown/forged surface: seal with master; still auditable.
            envelope = self._gov({
                "op": "seal", "key_name": "master",
                "content": {"req_id": req_id, "reason": reason, "ts": ts},
                "origin": self.name, "ts": ts,
                "req_id": req_id})["envelope"]
        if self.log is not None:
            self.log.append("DENIAL", {"req_id": req_id,
                                       "surface_id": surface_id,
                                       "reason": reason, "ts": ts})
        self.served_journal.append({"req_id": req_id,
                                    "surface_id": surface_id,
                                    "outcome": "denied:" + reason,
                                    "sealed": envelope, "ts": ts})
        return {"response": envelope}

    def _record(self, req_env, req_id, surface_id, outcome, data_key,
                envelope, ts):
        self.seen[req_id] = (seal.canonical(req_env), envelope)
        if self.log is not None:
            self.log.append("EVIDENCE", {"req_id": req_id,
                                         "surface_id": surface_id,
                                         "outcome": outcome,
                                         "data_key": data_key, "ts": ts})
        self.served_journal.append({"req_id": req_id,
                                    "surface_id": surface_id,
                                    "outcome": outcome,
                                    "sealed": envelope, "ts": ts})
        return {"response": envelope}

    # -- plane-crossing helpers (the ONLY cross-plane paths) -------------
    def _gov(self, query):
        env = self.gateway.pull(self, Plane.GOVERNANCE, query,
                                key=TRANSPORT_KEY)
        return env["content"]

    def _data(self, query):
        env = self.gateway.pull(self, Plane.DATA, query, key=TRANSPORT_KEY)
        return env["content"]


class PullClient(Component):
    """A surface (data plane). Signs requests with its own enrollment key —
    the one key a surface holds, per the Phase-0 ceremony. Verifies every
    seal before render (rule 3). Retries are the client's business
    (rule 5): pull_with_retry lives here, not on the server."""

    plane = Plane.DATA

    def __init__(self, name, surface_id, key, clock):
        super().__init__(name)
        self.surface_id = surface_id
        self.key = key  # the surface's OWN enrollment key (ceremony-issued)
        self.clock = clock
        self.counter = 0
        self.attempts = 0
        self.received = []  # envelopes received ONLY as pull returns (rule 1)

    def _request_envelope(self, query, revision):
        self.counter += 1
        content = {"req_id": "%s-%d" % (self.surface_id, self.counter),
                   "surface_id": self.surface_id, "query": query,
                   "revision": revision, "ts": self.clock.now()}
        return seal.make_envelope(self.key, content,
                                  "surface:%s" % self.surface_id,
                                  content["ts"])

    def pull(self, query, revision="r1", wait_deadline=None):
        """A client pull: {req_id, surface_id, query, revision, ts},
        signed with the surface's enrollment key."""
        req_env = self._request_envelope(query, revision)
        q = {"request": req_env, "req_id": req_env["content"]["req_id"]}
        if wait_deadline is not None:
            q["wait_deadline"] = wait_deadline
        resp_env = self.gateway.pull(self, Plane.CONTROL, q, key=self.key)
        # Rule 3: the transport seal verifies before we touch the payload.
        content = seal.open_envelope(self.key, resp_env)[0]
        inner = content["response"]
        self.received.append(inner)
        return inner

    def render(self, response_envelope):
        """Verify the seal BEFORE render. Raises SealError on mismatch."""
        return seal.open_envelope(self.key, response_envelope)[0]

    def trust(self, response_envelope):
        """Proof verified before trust. The client holds no master key, so
        proof verification runs inside governance (key by name)."""
        content = seal.open_envelope(self.key, response_envelope)[0]
        proof = content.get("proof")
        if proof is None:
            return content.get("body") is None
        env = self.gateway.pull(
            self, Plane.GOVERNANCE,
            {"op": "verify", "key_name": "master", "envelope": proof,
             "req_id": "trust-%s" % content["req_id"]}, key=self.key)
        return bool(env["content"].get("ok"))

    def pull_with_retry(self, query, revision="r1", max_attempts=3,
                        backoff=1):
        """Rule 5: timeouts and retries are the client's business."""
        self.attempts = 0
        last = None
        for _ in range(max_attempts):
            self.attempts += 1
            try:
                return self.pull(query, revision)
            except PartitionError as exc:
                last = exc
                if hasattr(self.clock, "advance"):
                    self.clock.advance(backoff)
        raise last


class GovernedLog(IntentLog):
    """Intent log whose seals are applied and verified INSIDE governance.

    The control plane owns the log (paper section 2.1) but never holds the
    seal key: every append pulls governance for the seal, every chain check
    pulls governance for verification. self.key is never used.
    """

    def __init__(self, path, gateway, actor, clock, origin="intent-log"):
        IntentLog.__init__(self, path, key=None, origin=origin, clock=clock)
        self.gateway = gateway
        self.actor = actor

    def _seal_via_governance(self, body):
        env = self.gateway.pull(
            self.actor, Plane.GOVERNANCE,
            {"op": "seal", "key_name": "master", "content": body,
             "origin": self.origin, "ts": body["ts"],
             "req_id": "log-%d" % body["seq"]}, key=TRANSPORT_KEY)
        return env["content"]["envelope"]

    def append(self, entry_type, content, ts=None):
        if entry_type not in ENTRY_TYPES:
            raise ValueError("unknown entry type %r" % entry_type)
        ts = self.clock.now() if (ts is None and self.clock) else int(ts or 0)
        prev = self.entries[-1]["seal"] if self.entries else "GENESIS"
        body = {"seq": len(self.entries), "ts": ts, "type": entry_type,
                "content": content, "prev": prev}
        env = self._seal_via_governance(body)
        self._persist(env)
        self.entries.append(env)
        return env

    def verify_chain(self):
        prev = "GENESIS"
        for env in self.entries:
            resp = self.gateway.pull(
                self.actor, Plane.GOVERNANCE,
                {"op": "verify", "key_name": "master", "envelope": env,
                 "req_id": "verify-chain"}, key=TRANSPORT_KEY)["content"]
            if not resp.get("ok"):
                return False
            if env["content"].get("prev") != prev:
                return False
            prev = env["seal"]
        return True
