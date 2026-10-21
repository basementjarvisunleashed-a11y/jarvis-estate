"""Phase 2, Layer 1 — reference renderer for rendering-side invariant tests.

A tiny, stdlib-only model of how estate state is RENDERED on a surface
(Watchtower-style service status). It exists so the rendering-side
invariants — INV-E3 (missing evidence renders as missing), INV-S1 (unknown
never renders as operational), INV-S2 (paused never renders as failed),
INV-S3 (degraded requires observed impairment), INV-S4 (stale data shows
reduced confidence or unknown), INV-S5 (shared surfaces never render
restricted content) — can be asserted fail-closed against real code,
not just prose.

Status vocabulary is loaded from contracts/watchtower.schema.json's
closed state enum (operational|paused|degraded|unknown).

Render rules (all fail closed):
  1. An observed state outside the closed enum renders as "unknown".
  2. Missing evidence (None or {}) renders evidence_ref="missing" and
     forces status "unknown" at confidence 0.0 — no evidence, no assertion.
  3. Claimed "degraded" WITHOUT an impairment observation renders as
     "unknown" (INV-S3: degraded requires observed impairment).
  4. An impairment observation present while "operational" is claimed
     renders as "degraded" (an observed impairment contradicts
     "operational"; fail toward caution).
  5. "paused" renders as "paused" — the word "failed" never appears
     in a render (INV-S2).
  6. Stale readings (now > fresh_until) render at reduced confidence
     (capped at 0.4); readings with no freshness information at all
     render at confidence 0.0 (INV-S4).
  7. Restricted fields are stripped from the render; `redacted` reports
     whether anything was stripped (INV-S5).

Input service dict:
  {
    "service_id": str, "name": str,
    "observed_state": "operational"|"paused"|"degraded"|"unknown"|None,
    "impairment": None | {"observed_at": str, "detail": str},
    "evidence": None | {} | {"packet_id": str, "ref": str},
    "fresh_until": int (epoch seconds) | None,
    "now": int (epoch seconds),
    "restricted": dict  # fields that must never reach a shared surface
  }
"""

import json
import os

_SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "contracts",
    "watchtower.schema.json")


def _load_status_enum():
    try:
        with open(_SCHEMA_PATH, encoding="utf-8") as fh:
            schema = json.load(fh)
        props = schema["properties"]["services"]["items"]["properties"]
        return tuple(props["state"]["enum"])
    except (OSError, KeyError, ValueError):
        # Fallback keeps the renderer fail-closed even if the schema
        # file is absent; the enum is asserted in the test suite.
        return ("operational", "paused", "degraded", "unknown")


STATUSES = _load_status_enum()

# Fields that must never appear on a shared surface (INV-S5).
# Trust boundary 10 (Paper IV §5.6): operator identity, session secrets,
# and private operator notes are never renderable.
RESTRICTED_FIELDS = frozenset({
    "owner_token",
    "device_session_id",
    "auth_secret",
    "private_note",
    "operator_identity",
})

STALE_CONFIDENCE_CAP = 0.4


def render(service):
    """Render a service state for a shared surface. Returns a dict."""
    observed = service.get("observed_state")
    impairment = service.get("impairment")
    evidence = service.get("evidence")
    fresh_until = service.get("fresh_until")
    now = service.get("now", 0)

    render_out = {}

    # Rule 7 first: redaction. The render dict never carries restricted
    # fields, whatever the input contains.
    restricted = service.get("restricted") or {}
    stripped = [k for k in restricted if k in RESTRICTED_FIELDS]
    render_out["redacted"] = bool(stripped)

    # Rule 2: no evidence -> no assertion. (INV-E3)
    if not evidence:
        render_out["evidence_ref"] = "missing"
        render_out["status"] = "unknown"
        render_out["confidence"] = 0.0
        return render_out

    render_out["evidence_ref"] = (
        evidence.get("ref") or evidence.get("packet_id") or "missing")

    # Rule 1: closed enum; anything else is unknown. (INV-S1)
    if observed not in STATUSES:
        status = "unknown"
    elif observed == "degraded" and not impairment:
        # Rule 3: degraded requires observed impairment. (INV-S3)
        status = "unknown"
    elif observed == "operational" and impairment:
        # Rule 4: an observed impairment contradicts "operational".
        status = "degraded"
    else:
        status = observed
    # Rule 5: "paused" renders as "paused"; "failed" never appears. (INV-S2)
    render_out["status"] = status

    # Rule 6: freshness discipline. (INV-S4)
    confidence = 1.0
    if fresh_until is None:
        confidence = 0.0
    elif now > fresh_until:
        confidence = min(confidence, STALE_CONFIDENCE_CAP)
    render_out["confidence"] = confidence

    return render_out
