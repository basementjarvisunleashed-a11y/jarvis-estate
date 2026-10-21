"""Phase 3 Layer 2 — surface client models for the protocol tests.

Implements the surface-side rules from the v0.1 drafts:
- cache-policy.md sections 2-4: what each surface may cache; a cached
  entry is renderable only while fresh (now <= fresh_until); past that,
  the surface renders unknown — never the expired value as current; an
  approval action on an unknown card is disabled.
- sequence-diagrams.md (d): the offline tap records a LOCAL pending
  gesture only — not consent, not a decision, never transmitted as one.
  On reconnect the gesture is discarded; re-approval needs a fresh tap
  on a fresh card.
- consistency-model.md NT-2: every render carries provenance (the
  revision and age it was rendered from).

Python 3 standard library only.
"""


class Surface:
    def __init__(self, orch, session_id, device):
        self.orch = orch
        self.session_id = session_id
        self.device = device          # "iphone" or "watch"
        self.offline = False
        self.cached = None            # (payload, stamp) of the current render
        self.gesture_log = []         # device-local only; never a decision

    # -- pulls ----------------------------------------------------------
    def pull_card(self, intent_id, work_id, revision, timestamp):
        """Pull the approval card (the sealed card the principal taps)."""
        if self.offline:
            return {"ok": False, "reason": "offline"}
        it = self.orch.intents[intent_id]
        stamp = self.orch._stamp(work_id, "approval-card",
                                 fresh_until=it["record"]["expiry"])
        card = {"intent_id": intent_id, "work_id": work_id,
                "digest": it["digest"], "revision": revision,
                "expires_at": it["record"]["expiry"]}
        self.cached = (card, stamp)
        return {"ok": True, "card": card, "stamp": stamp}

    def pull_status(self, work_id, revision, timestamp):
        """Pull current status (a pinned read)."""
        if self.offline:
            return {"ok": False, "reason": "offline"}
        resp = self.orch.submit({"kind": "read", "work_id": work_id,
                                 "revision": revision,
                                 "device_session_id": self.session_id,
                                 "device": self.device, "timestamp": timestamp})
        if resp["ok"]:
            self.cached = (resp, resp["stamp"])
        return resp

    # -- rendering ------------------------------------------------------
    def render_cached(self, now):
        """Render the cached entry with age honesty (cache-policy.md section 4).

        Returns (render, provenance): render is "current" or "unknown";
        an unknown card carries a disabled tap target.
        """
        if self.cached is None:
            return ("unknown", {"reason": "no-cache"})
        payload, stamp = self.cached
        age = now - stamp["observed_at"]
        provenance = {"revision": stamp["revision"], "age": age,
                      "observed_at": stamp["observed_at"]}
        if now <= stamp["fresh_until"]:
            return ("current", dict(provenance, payload=payload))
        return ("unknown", dict(provenance, last_seen_age=age,
                                tap_disabled=True))

    # -- tapping --------------------------------------------------------
    def tap(self, card, timestamp):
        """The principal taps Approve on a card.

        Offline: records a local pending gesture ONLY (sequence (d)) —
        the orchestrator is never contacted, nothing is transmitted.
        On an unknown/stale card: the tap target is disabled — the tap
        cannot become consent.
        """
        if self.offline:
            self.gesture_log.append({"type": "pending-gesture",
                                     "intent_id": card["intent_id"],
                                     "at": timestamp})
            return {"ok": False, "reason": "offline-gesture-recorded-locally"}
        render, _prov = self.render_cached(timestamp)
        if render == "unknown":
            return {"ok": False, "reason": "tap-disabled-unknown-card"}
        return self.orch.submit({"kind": "decide",
                                 "intent_id": card["intent_id"],
                                 "work_id": card["work_id"],
                                 "revision": card["revision"],
                                 "digest_seen": card["digest"],
                                 "device_session_id": self.session_id,
                                 "timestamp": timestamp})

    # -- reconnect (sequence (d)) ---------------------------------------
    def reconnect(self, timestamp):
        """Reconnect: discard pending gestures (never transmitted),
        re-pull the current card; re-approval needs a fresh tap."""
        self.offline = False
        discarded = len(self.gesture_log)
        self.gesture_log = []
        return {"ok": True, "discarded_gestures": discarded}

    # -- hints (CR-6) ---------------------------------------------------
    def receive_hint(self, hint):
        self._hint = hint

    def pull_after_hint(self, work_id, revision, timestamp):
        """The hint is discarded; the surface pulls current state."""
        self._hint = None
        return self.pull_status(work_id, revision, timestamp)
