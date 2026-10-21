"""Phase 2 — Orchestral layers: per-surface pull contracts + the pull server.

Normative source: the Phase 2 spec — per-surface PULLS / NEVER-PULLS lists,
the enrollment ceremony, and the attention budgets.

The contract is bilateral and enforced AT THE PULL: the pull server (a
control-plane Component) refuses what the surface may not pull — with a
SEALED denial. The denial body is sealed by the governance plane (the only
plane that holds ceremony keys) and the refusal is appended to the intent
log as DENIAL. Deploy the refusal, not just the service.

Sealing model (test build):
  * Every pull response — allowed content, denial, or queued notice — is a
    sealed envelope produced by the governance KeyService with the ceremony
    master key (inner seal). The client verifies this seal: it is the proof
    the response is authentic.
  * The PlaneGateway wraps each hop in an outer envelope sealed with a
    transport credential supplied by the harness (outer seal). The pull
    server holds the transport credential; it NEVER holds ceremony keys.
    Deployment note: the transport credential is a governance-issued,
    short-lived key, distinct from the ceremony master/surface keys, which
    never leave governance.

Spec note (flagged, not invented): the enrollment handshake's first pull —
Watchtower status rendered as state — is a ceremony-scoped pull, not a
member of any surface's operational PULLS list. The pull server accepts
category 'watchtower_status' only with handshake=True and a pending,
accepted enrollment for that exact device+surface.
"""

from common import planes
from common import seal
from common.planes import Plane

from budget import BUDGETS


SURFACES = ("phone", "watch", "tablet", "tv", "headset")

# Normative per-surface contracts (Phase 2 spec). pulls = may pull;
# never = refused at the pull with a sealed denial.
CONTRACTS = {
    "phone": {
        "pulls": ("briefs", "decisions", "blocks", "packets"),
        "never": ("engine_internals", "other_roles_private_state"),
    },
    "watch": {
        "pulls": ("approvals_5s", "critical_alerts"),
        "never": ("evidence_bodies", "configuration"),
    },
    "tablet": {
        "pulls": ("full_evidence_packets",),
        "never": ("credentials", "sealed_private_memory"),
    },
    "tv": {
        "pulls": ("state",),
        "never": ("contents", "approvals"),
    },
    "headset": {
        "pulls": ("role_artifact_evidence_relationships",),
        "never": ("outside_private_session",),
    },
}

VALID_STATES = ("operational", "paused", "degraded", "unknown")

WATCHTOWER_STATE = "operational"


def terms(surface: str) -> dict:
    """The exact terms a surface is enrolled into (pulls, never, budget).

    The principal enrolls the surface into a contract, not vaguely:
    enrollment acceptance requires byte-exact equality with this dict.
    """
    if surface not in CONTRACTS:
        raise KeyError("unknown surface %r" % (surface,))
    c = CONTRACTS[surface]
    b = BUDGETS[surface]
    return {
        "surface": surface,
        "pulls": list(c["pulls"]),
        "never": list(c["never"]),
        "attention_budget_per_day": ("unbounded, principal-initiated only"
                                     if b is None else b),
    }


def check_contract(surface: str, category: str):
    """(allowed, reason) for a surface pulling a category. Fail closed."""
    c = CONTRACTS.get(surface)
    if c is None:
        return False, "unknown surface %r" % (surface,)
    if category in c["never"]:
        return False, ("contract: %s never pulls '%s'"
                       % (surface, category))
    if category in c["pulls"]:
        return True, ("contract: %s may pull '%s'" % (surface, category))
    return False, ("contract: '%s' is not in %s's pull set (fail closed)"
                   % (category, surface))


def denial_body(surface=None, device=None, category=None,
                reason="", rule=""):
    """The refusal payload. Sealed by governance before it leaves."""
    return {"denial": True, "surface": surface, "device": device,
            "category": category, "reason": reason, "rule": rule}


# ---------------------------------------------------------------------------
# Data plane: the content behind the contracts. Never decides; never pushes.


CONTENT = {
    "briefs": {"briefs": [
        {"id": "brief-001", "title": "Morning brief",
         "summary": "Overnight estate status in three lines."}]},
    "decisions": {"decisions": [
        {"id": "dec-001", "summary": "Approve nightly release publish",
         "status": "pending-principal"}]},
    "blocks": {"blocks": [
        {"id": "block-001", "title": "Deep-work block",
         "window": "09:00-11:00"}]},
    "packets": {"packets": [
        {"id": "pkt-001", "kind": "brief-packet", "items": 3}]},
    "approvals_5s": {"approvals": [
        {"id": "appr-001", "summary": "Release publish: approve?",
         "fits_5s": True}]},
    "critical_alerts": {"alerts": [
        {"id": "alert-001", "severity": "critical",
         "summary": "Watchtower state changed"}]},
    "full_evidence_packets": {"evidence_packets": [
        {"id": "ev-001", "title": "Nightly release evidence",
         "body": "Full evidence body: build log, digests, receipts."}]},
    "state": {"state": WATCHTOWER_STATE},
    "role_artifact_evidence_relationships": {"relationships": [
        {"role": "principal", "artifact": "release",
         "evidence": "ev-001"}]},
    "watchtower_status": {},  # filled per-pull below (handshake only)
}


class DataStore(planes.Component):
    """Data plane: owns sealed state, evidence, baselines. Never decides.

    Serves ONLY through the pull server: a fetch without the pull server's
    authorization is refused. This keeps the contract enforced at the pull —
    there is no side door around the pull server.
    """

    plane = Plane.DATA

    def __init__(self, name: str, clock):
        super().__init__(name)
        self.clock = clock

    def serve_pull(self, query: dict) -> dict:
        if (query.get("query") != "fetch"
                or query.get("authorized_by") != "pull-server"):
            return {"denial": True,
                    "reason": "data plane serves only via the pull server"}
        category = query.get("category")
        if category == "watchtower_status":
            return {"watchtower": {"state": WATCHTOWER_STATE,
                                   "ts": self.clock.now()}}
        if category not in CONTENT:
            raise ValueError("unknown data category %r" % (category,))
        return dict(CONTENT[category])


# ---------------------------------------------------------------------------
# Governance plane: the only component that holds ceremony key material.


class KeyService(planes.Component):
    """Governance plane: holds the ceremony keys; seals on request.

    The master key seals every pull response/denial (inner seal). Per-surface
    enrollment keys are held here and never leave governance.
    """

    plane = Plane.GOVERNANCE

    def __init__(self, name: str, keyset: dict, clock):
        super().__init__(name)
        self._master = keyset["master"]
        self._surface_keys = {k: v for k, v in keyset.items()
                              if k.startswith("surface:")}
        self.clock = clock

    def serve_pull(self, query: dict) -> dict:
        if query.get("query") != "seal":
            return {"denial": True, "reason": "key service seals only"}
        body = query["content"]
        origin = str(query.get("origin", self.name))
        return {"envelope": seal.make_envelope(self._master, body, origin,
                                               self.clock.now())}


# ---------------------------------------------------------------------------
# Control plane: the pull server. The contract is enforced here, at the pull.


class PullServer(planes.Component):
    """Control plane: enforces surface contracts at the pull.

    Holds no ceremony keys — only the pull-protocol transport credential for
    the gateway's outer envelopes. Every response body (allowed content,
    denial, or queued notice) is sealed by the governance KeyService via a
    pull, never by direct call. Every denial is appended to the intent log.
    """

    plane = Plane.CONTROL

    def __init__(self, name: str, ceremony, budget, log, transport_key: bytes):
        super().__init__(name)
        self.ceremony = ceremony    # same plane: direct reference is legal
        self.budget = budget        # same plane: direct reference is legal
        self.log = log              # harness-supplied handle (phase-0
                                    # precedent; control owns the log protocol)
        self.transport_key = transport_key

    # -- gateway entry ---------------------------------------------------
    def serve_pull(self, query: dict) -> dict:
        q = query.get("query")
        if q == "pull":
            return self._serve_pull(query)
        if q == "enroll":
            # Same-plane dispatch into the ceremony; the pull itself arrived
            # over the gateway from the surface.
            body = self.ceremony.handle_step(query)
            return self._seal_response(body, query)
        return self._seal_response(
            denial_body(reason="unknown query %r" % (q,),
                        rule="fail-closed"), query)

    # -- data pulls ------------------------------------------------------
    def _serve_pull(self, query: dict) -> dict:
        surface = query.get("surface")
        device = query.get("device")
        category = query.get("category")
        initiated = query.get("initiated", "principal")

        if query.get("handshake"):
            return self._handshake_pull(query)

        if not self.ceremony.is_enrolled(device):
            return self._seal_response(denial_body(
                surface, device, category,
                reason=("device %r is not enrolled; "
                        "enroll via the ceremony first" % (device,)),
                rule="enrollment"), query)

        if initiated == "system":
            verdict = self.budget.request(surface, initiated="system")
            if verdict["verdict"] == "queued":
                return self._seal_response({
                    "queued": True, "surface": surface, "device": device,
                    "category": category,
                    "reason": "attention budget exhausted; pull queued, "
                              "not spent",
                    "spent": verdict["spent"], "budget": verdict["budget"],
                }, query)
            if verdict["verdict"] != "allowed":
                return self._seal_response(denial_body(
                    surface, device, category,
                    reason=verdict["reason"],
                    rule="attention-budget"), query)

        ok, reason = check_contract(surface, category)
        if not ok:
            return self._seal_response(denial_body(
                surface, device, category, reason=reason,
                rule="surface-contract"), query)

        data = self._fetch_from_data_plane(category,
                                           query.get("req_id", "req-?"))
        return self._seal_response(data, query)

    def _handshake_pull(self, query: dict) -> dict:
        # Ceremony-scoped first pull (see module docstring): accepted only
        # with a pending, accepted enrollment for this exact device+surface.
        eid = query.get("enrollment_id")
        pending = self.ceremony.get_pending(eid)
        if (not pending or pending["state"] != "accepted"
                or pending["device"] != query.get("device")
                or pending["surface"] != query.get("surface")):
            return self._seal_response(denial_body(
                query.get("surface"), query.get("device"), "watchtower_status",
                reason="no accepted pending enrollment for this handshake",
                rule="enrollment-handshake"), query)
        data = self._fetch_from_data_plane("watchtower_status",
                                           query.get("req_id", "req-?"))
        self.ceremony.complete_enrollment(eid)  # same plane: direct call
        return self._seal_response(data, query)

    # -- plumbing --------------------------------------------------------
    def _fetch_from_data_plane(self, category: str, req_id: str) -> dict:
        # Cross-plane ONLY by pull — a direct call would raise PlaneViolation.
        outer = self.gateway.pull(
            self, Plane.DATA,
            {"query": "fetch", "category": category,
             "authorized_by": "pull-server", "req_id": req_id},
            self.transport_key)
        content, _origin, _ts = seal.open_envelope(self.transport_key, outer)
        return content

    def _seal_response(self, body: dict, query: dict) -> dict:
        if body.get("denial"):
            self.log.append("DENIAL", {
                "at": "pull",
                "surface": query.get("surface"),
                "device": query.get("device"),
                "category": query.get("category"),
                "step": query.get("step"),
                "reason": body.get("reason"),
                "rule": body.get("rule"),
            })
        # Sealed by governance via pull — the server never touches the key.
        outer = self.gateway.pull(
            self, Plane.GOVERNANCE,
            {"query": "seal", "content": body, "origin": "pull-server"},
            self.transport_key)
        content, _origin, _ts = seal.open_envelope(self.transport_key, outer)
        return {"sealed": content["envelope"]}


# ---------------------------------------------------------------------------
# Surfaces: data-plane clients. They pull; they never decide or hold keys.


class SurfaceClient(planes.Component):
    """A surface device. Receives sealed state; never decides, never holds
    ceremony keys."""

    plane = Plane.DATA

    def __init__(self, name: str, surface: str, device: str):
        super().__init__(name)
        self.surface = surface
        self.device = device

    def pull(self, query: dict, transport_key: bytes) -> dict:
        return self.gateway.pull(self, Plane.CONTROL, query, transport_key)
