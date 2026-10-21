"""Phase 2 — enrollment ceremony (control-plane Component).

In-person, phone-initiated:
  1. begins on the trusted surface (the phone) — the new device NEVER
     enrolls itself;
  2. both screens show a pairing code; the principal confirms they match;
  3. the phone displays the new surface's pull contract — the principal
     enrolls the surface into the contract's exact terms, not vaguely;
  4. the surface's first pull is the Watchtower status — the handshake
     rendered as state.

The ceremony is driven over the pull protocol: the phone pulls the control
plane with {"query": "enroll", "step": ...} and the pull server dispatches
same-plane into handle_step(). Every refusal is returned as a denial body;
the pull server seals it (governance) and logs DENIAL. Pairing codes are
short-lived screen secrets and are never written to the log.
"""

import secrets

from common import planes
from common.planes import Plane

from contracts import SURFACES, terms


class EnrollmentCeremony(planes.Component):
    """Control plane: runs the in-person enrollment ceremony."""

    plane = Plane.CONTROL

    TRUSTED_SURFACE = "phone"

    def __init__(self, name: str, log, clock):
        super().__init__(name)
        self.log = log      # harness-supplied handle (phase-0 precedent)
        self.clock = clock
        self.enrolled = {}  # device -> {"surface":..., "enrolled_ts":...}
        self.pending = {}   # enrollment_id -> pending record
        self._next_id = 0

    # -- harness ---------------------------------------------------------
    def bootstrap(self, devices):
        """Pre-enroll trusted devices (test harness; production enrolls each
        device through this ceremony)."""
        for device, surface in devices:
            self.enrolled[device] = {"surface": surface,
                                     "enrolled_ts": self.clock.now()}
        self.log.append("DECISION", {"bootstrap_trusted_devices":
                                     [{"device": d, "surface": s}
                                      for d, s in devices]})

    def is_enrolled(self, device) -> bool:
        return device in self.enrolled

    def get_pending(self, enrollment_id):
        return self.pending.get(enrollment_id)

    # -- pull protocol (dispatched by the pull server, same plane) --------
    def handle_step(self, query: dict) -> dict:
        handler = {"begin": self._begin,
                   "confirm": self._confirm,
                   "contract": self._contract,
                   "accept": self._accept}.get(query.get("step"))
        if handler is None:
            return self._deny("unknown enrollment step", "fail-closed")
        return handler(query)

    def _deny(self, reason: str, rule: str) -> dict:
        return {"denial": True, "reason": reason, "rule": rule}

    def _begin(self, q: dict) -> dict:
        initiator = q.get("initiator")
        initiator_device = q.get("initiator_device")
        new_device = q.get("new_device")
        surface = q.get("surface")
        if initiator != self.TRUSTED_SURFACE:
            return self._deny(
                "enrollment begins on the trusted surface (the phone); "
                "initiator %r refused" % (initiator,), "trusted-surface")
        if initiator_device == new_device:
            return self._deny(
                "a device cannot enroll itself; enrollment begins on "
                "the phone", "no-self-enrollment")
        anchor = self.enrolled.get(initiator_device)
        if not anchor or anchor["surface"] != self.TRUSTED_SURFACE:
            return self._deny(
                "initiator device is not the trusted phone",
                "trusted-surface")
        if surface not in SURFACES:
            return self._deny("unknown surface %r" % (surface,),
                              "fail-closed")
        if new_device in self.enrolled:
            return self._deny("device %r is already enrolled" % (new_device,),
                              "already-enrolled")
        if any(p["device"] == new_device for p in self.pending.values()):
            return self._deny(
                "device %r already has a pending enrollment" % (new_device,),
                "already-pending")
        self._next_id += 1
        eid = "enr-%04d" % self._next_id
        code = "%06d" % secrets.randbelow(1000000)
        self.pending[eid] = {"id": eid, "device": new_device,
                             "surface": surface, "code": code,
                             "state": "pairing",
                             "began_ts": self.clock.now()}
        # The code is shown on both screens; it is never logged.
        return {"enrollment_id": eid, "device": new_device,
                "surface": surface, "pairing_code": code,
                "state": "pairing"}

    def _confirm(self, q: dict) -> dict:
        p = self.pending.get(q.get("enrollment_id"))
        if p is None or p["state"] != "pairing":
            return self._deny("no pairing-pending enrollment", "fail-closed")
        if q.get("surface_code") != p["code"]:
            # The principal did not confirm a match: abort the enrollment.
            del self.pending[p["id"]]
            return self._deny("pairing codes do not match; enrollment "
                              "aborted", "pairing-mismatch")
        p["state"] = "contract"
        return {"enrollment_id": p["id"], "pairing": "matched",
                "state": "contract"}

    def _contract(self, q: dict) -> dict:
        p = self.pending.get(q.get("enrollment_id"))
        if p is None or p["state"] != "contract":
            return self._deny("no contract-pending enrollment", "fail-closed")
        return {"enrollment_id": p["id"], "surface": p["surface"],
                "terms": terms(p["surface"]),
                "note": "the principal enrolls the surface into these "
                        "exact terms"}

    def _accept(self, q: dict) -> dict:
        p = self.pending.get(q.get("enrollment_id"))
        if p is None or p["state"] != "contract":
            return self._deny("no contract-pending enrollment", "fail-closed")
        if q.get("terms") != terms(p["surface"]):
            del self.pending[p["id"]]
            return self._deny("enrollment is into the contract's exact "
                              "terms; modified terms rejected, enrollment "
                              "aborted", "exact-terms")
        p["state"] = "accepted"
        return {"enrollment_id": p["id"], "enrolled_into_contract": True,
                "state": "accepted",
                "next": "the surface's first pull is the Watchtower status"}

    def complete_enrollment(self, enrollment_id: str) -> dict:
        """Called by the pull server after the handshake first pull."""
        p = self.pending.pop(enrollment_id, None)
        if p is None or p["state"] != "accepted":
            raise ValueError("no accepted pending enrollment %r"
                             % (enrollment_id,))
        self.enrolled[p["device"]] = {"surface": p["surface"],
                                      "enrolled_ts": self.clock.now()}
        self.log.append("DECISION", {"enrollment": {
            "device": p["device"], "surface": p["surface"],
            "contract": terms(p["surface"]),
            "first_pull": "watchtower_status",
            "began_ts": p["began_ts"],
            "completed_ts": self.clock.now()}})
        return self.enrolled[p["device"]]
