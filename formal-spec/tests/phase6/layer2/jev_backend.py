"""Jev backend interface — Jev-ready, never called without his approval.

Q2 (2026-10-22 ~12:48 ET): evaluate Jev only on HgX's explicit approval.
This module defines the pluggable interface the harness is built against.
No endpoint is called, no key is read, nothing is sent off-estate.
"""
from __future__ import annotations


class JevNotApproved(Exception):
    """Raised whenever the Jev backend is invoked without his approval."""


class Backend:
    """Pluggable router backend interface."""

    name = "base"

    def decide(self, decision_state: dict) -> str:
        raise NotImplementedError


class LocalBackend(Backend):
    """The local seven-rule policy, as the backend interface sees it."""

    name = "local"

    def decide(self, decision_state: dict) -> str:
        from policies import local_policy
        return local_policy(decision_state)


class JevBackend(Backend):
    """TypeSafe Jev backend — interface only.

    Per Q2 and the skill doc: only on HgX's explicit ask; he creates the
    key himself via the Secure Vault flow (never in chat, never in a
    file); only the compact decision state is sent; any failure falls
    back to local immediately, logged. Until then this class refuses.
    """

    name = "jev"

    def __init__(self) -> None:
        raise JevNotApproved(
            "Jev backend not approved: HgX's explicit word and his key "
            "are required (Q2, 2026-10-22). No call made, nothing sent."
        )

    def decide(self, decision_state: dict) -> str:  # pragma: no cover
        raise JevNotApproved("Jev backend not approved.")


class FailingBackend(Backend):
    """Test double: simulates a backend failure for the INV-R5 check."""

    name = "failing-test-double"

    def decide(self, decision_state: dict) -> str:
        raise ConnectionError("simulated backend outage")


def decide_with_fallback(state: dict, backend: Backend) -> tuple[str, str]:
    """Route through backend; on ANY failure fall back to local, logged.

    Returns (recommendation, backend_used). INV-R5: fallback preserves
    safety — the local policy never approves consequences (rule 1).
    """
    try:
        result = backend.decide(state)
        rec = result[0] if isinstance(result, tuple) else result
        return rec, backend.name
    except Exception as exc:  # noqa: BLE001 - any backend failure
        from policies import local_policy
        rec = local_policy(state)[0]
        return rec, "local-fallback-after:%s" % type(exc).__name__
