"""Phase 1 — Orchestrator main loop (control plane).

tick() runs SERVE -> SENSE -> QUEUE -> REVIEW -> MAINTAIN, in that order.

  SERVE:    answer pulls — pulls are answered synchronously when the
            gateway calls PullServer.serve_pull; this phase drains the
            server's served journal into the review pipeline.
  SENSE:    ingest samples via a data-plane pull, update baselines, fire a
            deep pull on surprise.
  QUEUE:    brief engines for pulled work.
  REVIEW:    check returns — provenance (response seal via the surface key
            AND data proof via the master key, both verified inside
            governance before trust), contract (well-formed outcome),
            boundary (no push path exists).
  MAINTAIN: renew leases, update scorecards, queue health.

The loop never pushes: every cross-plane contact is a client-initiated
pull through the gateway. There is no send/push/notify/chase method
anywhere in this file — that absence is asserted by the test suite.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.planes import Plane, Component
from pull import TRANSPORT_KEY


class Orchestrator(Component):
    """Control-plane orchestrator. Same-plane delegate of the PullServer."""

    plane = Plane.CONTROL

    def __init__(self, name, server, log, clock, surprise_threshold=10.0):
        super().__init__(name)
        self.server = server
        self.log = log
        self.clock = clock
        self.surprise_threshold = surprise_threshold
        self.review_queue = []
        self.verdicts = []
        self.engine_briefs = []
        self.baseline = {"count": 0, "mean": 0.0}
        self.leases = {}
        self.scorecards = {}
        self.phases_run = []

    def _pull(self, to_plane, query):
        env = self.gateway.pull(self, to_plane, query, key=TRANSPORT_KEY)
        return env["content"]

    def tick(self):
        self.serve()
        self.sense()
        self.queue()
        self.review()
        self.maintain()

    # -- SERVE ----------------------------------------------------------
    def serve(self):
        """Answer pulls: drain the pull server's journal into review."""
        self.phases_run.append("serve")
        for item in self.server.served_journal:
            self.review_queue.append(dict(item))
        self.server.served_journal[:] = []

    # -- SENSE ----------------------------------------------------------
    def sense(self):
        """Ingest samples, update baselines, deep-pull on surprise."""
        self.phases_run.append("sense")
        res = self._pull(Plane.DATA, {"op": "sample",
                                      "req_id": "sense-%d" % self.clock.now()})
        if not res.get("ok"):
            return
        sample = res["data"] or {}
        try:
            x = float(sample["value"])
        except (KeyError, TypeError, ValueError):
            return
        base = self.baseline
        if base["count"] >= 3 and abs(x - base["mean"]) > self.surprise_threshold:
            deep = self._pull(Plane.DATA, {
                "op": "deep-read", "key": sample.get("key"),
                "req_id": "sense-deep-%d" % self.clock.now()})
            self.log.append("EVIDENCE", {"surprise": True, "value": x,
                                         "baseline_mean": base["mean"],
                                         "deep_ok": bool(deep.get("ok")),
                                         "ts": self.clock.now()})
        base["count"] += 1
        base["mean"] += (x - base["mean"]) / base["count"]

    # -- QUEUE ----------------------------------------------------------
    def queue(self):
        """Brief engines for pulled work."""
        self.phases_run.append("queue")
        for item in self.review_queue:
            if item["outcome"] == "served":
                self.engine_briefs.append(
                    {"req_id": item["req_id"],
                     "surface_id": item["surface_id"],
                     "brief": "engine: handle pulled work for %s"
                              % item["req_id"],
                     "ts": self.clock.now()})

    # -- REVIEW ---------------------------------------------------------
    def review(self):
        """Check returns: provenance, contract, boundary."""
        self.phases_run.append("review")
        trusted = 0
        while self.review_queue:
            item = self.review_queue.pop(0)
            verdict = self._review_item(item)
            self.verdicts.append(verdict)
            if verdict["trusted"]:
                trusted += 1
            sid = item.get("surface_id") or "unknown"
            score = self.scorecards.setdefault(
                sid, {"served": 0, "denied": 0, "timeout": 0})
            if item["outcome"] == "served":
                score["served"] += 1
            elif item["outcome"] == "timeout":
                score["timeout"] += 1
            elif item["outcome"].startswith("denied"):
                score["denied"] += 1
        self.log.append("DECISION", {"reviewed": len(self.verdicts),
                                     "trusted": trusted,
                                     "ts": self.clock.now()})

    def _review_item(self, item):
        sealed = item.get("sealed") or {}
        sid = item.get("surface_id")
        key_name = "surface:%s" % sid if sid else "master"
        # Provenance, part 1: the response/denial seal verifies (surface key).
        prov_resp = self._pull(Plane.GOVERNANCE, {
            "op": "verify", "key_name": key_name, "envelope": sealed,
            "req_id": "review-%s" % item["req_id"]}).get("ok", False)
        # Provenance, part 2: the data proof verifies (master key) before
        # the body is trusted.
        content = sealed.get("content") or {}
        proof = content.get("proof")
        prov_proof = True
        if proof is not None:
            prov_proof = self._pull(Plane.GOVERNANCE, {
                "op": "verify", "key_name": "master", "envelope": proof,
                "req_id": "review-proof-%s" % item["req_id"]}).get("ok", False)
        # Contract: well-formed outcome.
        contract = (item["outcome"] in ("served", "timeout")
                    or item["outcome"].startswith("denied"))
        # Boundary: no push path exists on this loop or its server.
        boundary = not any(hasattr(o, n) for o in (self, self.server)
                           for n in ("push", "send", "notify", "chase"))
        trusted = bool(prov_resp and prov_proof and contract and boundary)
        return {"req_id": item["req_id"], "outcome": item["outcome"],
                "provenance": bool(prov_resp and prov_proof),
                "contract": bool(contract), "boundary": bool(boundary),
                "trusted": trusted}

    # -- MAINTAIN -------------------------------------------------------
    def maintain(self):
        """Renew leases, update scorecards (done in review), queue health."""
        self.phases_run.append("maintain")
        now = self.clock.now()
        for name, expiry in list(self.leases.items()):
            if now >= expiry - 60:
                self.leases[name] = now + 600
        # Queue health: briefs stay bounded; drop anything ancient.
        self.engine_briefs[:] = [b for b in self.engine_briefs
                                 if now - b["ts"] < 3600]
