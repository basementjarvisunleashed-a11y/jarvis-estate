"""The three evaluated policies, implemented exactly as specified.

- unconstrained: RP-8a — every consultation answers proceed.
- cache_only:  RP-8b — use-cache when a fresh cached artifact/note answers
  the goal; every other decision answers proceed directly.
- local:       RP-8c — the seven rules of RP-6, first match wins.

Jev (RP-8d) and hybrid (RP-8e) are NOT evaluated without his approval;
learned (RP-8f) is later. See jev_backend.py.
"""
from __future__ import annotations

ACTIONS = ("proceed", "use-cache", "defer", "escalate", "deny")


def unconstrained_policy(state: dict) -> tuple[str, str]:
    """RP-8a: the no-gate baseline."""
    return "proceed", "RP-8a/unconstrained"


def cache_only_policy(state: dict) -> tuple[str, str]:
    """RP-8b: cache preference only; everything else proceeds directly."""
    if state.get("cached_artifact") and state.get("cached_fresh"):
        return "use-cache", "RP-8b/cache-hit"
    return "proceed", "RP-8b/no-cache"


def local_policy(state: dict) -> tuple[str, str]:
    """RP-8c: the seven rules, in order, first match wins. Returns
    (action, rule_id)."""
    # Rule 1 — irreversible actions escalate, always.
    if state.get("irreversible"):
        return "escalate", "RP-6.1/irreversible"
    # Rule 2 — retry budget: same error twice, then escalate.
    if state.get("prior_error") and state.get("same_error_count", 0) >= 2:
        return "escalate", "RP-6.2/retry-budget"
    # Rule 3 — loop detection: 3rd no-progress proposal denied.
    if state.get("action_repeat_count", 0) >= 3 and not state.get("measurable_progress"):
        return "deny", "RP-6.3/loop"
    # Rule 4 — cache preference.
    if state.get("cached_artifact") and state.get("cached_fresh"):
        return "use-cache", "RP-6.4/cache"
    # Rule 5 — subagent gating.
    if state.get("proposed_action") == "spawn":
        if state.get("multi_step") and state.get("independent") and state.get("long_running"):
            return "proceed", "RP-6.5/spawn-warranted"
        return "deny", "RP-6.5/spawn-denied"
    # Rule 6 — browser gating.
    if state.get("proposed_action") == "browser_search":
        return "proceed", "RP-6.6/search-cheap"
    if state.get("proposed_action") == "live_browser":
        if state.get("needs_current_state"):
            return "proceed", "RP-6.6/live-needed"
        return "deny", "RP-6.6/curiosity"
    # Rule 7 — deferral: vague goal plus high cost.
    if state.get("goal_vague") and state.get("cost_high"):
        return "defer", "RP-6.7/defer"
    return "proceed", "RP-6.6/default"  # default falls through rule 6's cheap path
