"""Three planes (paper §2.1) with the pull-only cross-plane rule enforced in code.

| PLANE      | OWNS                                        | NEVER                          |
|------------|---------------------------------------------|--------------------------------|
| control    | pull protocol, intent log, ceremony, sched. | touches the filesystem directly; holds credentials |
| data       | sealed state, evidence, baselines           | decides; pushes                |
| governance | keys, approvals, policies                   | executes work                  |

Every component lives in exactly one plane. A component that needs
something from another plane pulls it through the PlaneGateway — a direct
cross-plane call raises PlaneViolation, and the test suite asserts this.

The PlaneGateway is the ONLY sanctioned cross-plane path. It logs every
pull (auditable, per §2.2 rule 4's spirit) and serves only sealed envelopes.
"""
from . import seal as _seal


class PlaneViolation(Exception):
    """A component reached across planes except by pull. Fail closed."""


class Plane:
    CONTROL = "control"
    DATA = "data"
    GOVERNANCE = "governance"
    ALL = (CONTROL, DATA, GOVERNANCE)


# What each plane is forbidden to do (§2.1 NEVER column), checked by tests.
FORBIDDEN = {
    Plane.CONTROL: ("fs_write", "hold_credential"),
    Plane.DATA: ("decide", "push"),
    Plane.GOVERNANCE: ("execute",),
}


class Component:
    """Base class: every component declares exactly one plane."""

    plane = None  # subclasses must set

    def __init__(self, name: str):
        if self.plane not in Plane.ALL:
            raise PlaneViolation(
                "%s must declare exactly one plane" % type(self).__name__)
        self.name = name
        self.gateway = None  # wired by the harness, never peer-to-peer

    def wire(self, gateway: "PlaneGateway"):
        self.gateway = gateway

    def call(self, other: "Component", method: str, *args, **kwargs):
        """Direct call to another component. Cross-plane -> violation.

        Same-plane collaboration is allowed; cross-plane MUST go through
        gateway.pull(). This is the enforcement point the tests exercise.
        """
        if other.plane != self.plane:
            raise PlaneViolation(
                "%s(%s) -> %s(%s): cross-plane call forbidden; use pull"
                % (self.name, self.plane, other.name, other.plane))
        return getattr(other, method)(*args, **kwargs)


class PullRecord:
    """One audited cross-plane pull."""

    def __init__(self, req_id, from_plane, to_plane, query, ts):
        self.req_id = req_id
        self.from_plane = from_plane
        self.to_plane = to_plane
        self.query = query
        self.ts = ts


class PlaneGateway:
    """The only sanctioned cross-plane path. Serves sealed envelopes only."""

    def __init__(self, clock):
        self.clock = clock
        self.servers = {}   # plane -> component that serves pulls for it
        self.audit = []     # every pull, in order (auditable)

    def serve(self, plane: str, component: Component):
        if component.plane != plane:
            raise PlaneViolation("server plane mismatch")
        self.servers[plane] = component

    def pull(self, requester: Component, to_plane: str, query: dict,
             key: bytes) -> dict:
        """Cross-plane pull. Returns a sealed envelope. Always initiated by
        the client side (requester); the server never pushes (§2.2)."""
        if requester.plane == to_plane:
            raise PlaneViolation("same-plane traffic must not use the gateway")
        server = self.servers.get(to_plane)
        if server is None:
            raise PlaneViolation("no server for plane %r" % to_plane)
        req_id = query.get("req_id", "req-?")
        rec = PullRecord(req_id, requester.plane, to_plane,
                         query.get("query"), self.clock.now())
        self.audit.append(rec)
        body = server.serve_pull(query)  # the server only responds
        return _seal.make_envelope(key, body, origin=server.name,
                                   ts=self.clock.now())

    def audit_log(self):
        return list(self.audit)
