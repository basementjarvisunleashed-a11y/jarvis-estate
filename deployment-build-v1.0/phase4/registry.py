"""Phase 4 — versioned statement registry (paper §4).

Each statement id is bound to a circuit version. Verifiers REJECT proofs
for superseded circuits: a proof is accepted only when its
circuit_version equals the registry's current version for that
statement id. Old versions are kept in history (audit trail) but never
accepted again.

REFERENCE component of the Phase 4 reference build — see proofs.py for
the honesty notice.
"""

from .proofs import RegistryError  # noqa: F401  (single error taxonomy)


class StatementRegistry:
    """register(statement_id, version, descriptor);
    supersede(statement_id, new_version)."""

    def __init__(self):
        self._entries = {}  # statement_id -> {"version", "descriptor", "history"}

    def register(self, statement_id: str, version: int, descriptor: str):
        """Bind a statement id to its first circuit version."""
        sid = str(statement_id)
        if sid in self._entries:
            raise RegistryError("statement %r already registered" % sid)
        self._entries[sid] = {
            "version": int(version),
            "descriptor": str(descriptor),
            "history": [int(version)],
        }

    def supersede(self, statement_id: str, new_version: int):
        """Move a statement to a new circuit version. Versions only move
        forward; the old version is recorded in history and rejected by
        verifiers from here on."""
        sid = str(statement_id)
        entry = self._entries.get(sid)
        if entry is None:
            raise RegistryError("unknown statement %r" % sid)
        new_version = int(new_version)
        if new_version <= entry["version"]:
            raise RegistryError(
                "supersede requires a strictly greater version "
                "(current v%s, got v%s)" % (entry["version"], new_version))
        entry["history"].append(entry["version"])
        entry["version"] = new_version

    def current_version(self, statement_id: str) -> int:
        entry = self._entries.get(str(statement_id))
        if entry is None:
            raise RegistryError("unknown statement %r" % (statement_id,))
        return entry["version"]

    def descriptor(self, statement_id: str) -> str:
        entry = self._entries.get(str(statement_id))
        if entry is None:
            raise RegistryError("unknown statement %r" % (statement_id,))
        return entry["descriptor"]

    def history(self, statement_id: str) -> list:
        entry = self._entries.get(str(statement_id))
        if entry is None:
            raise RegistryError("unknown statement %r" % (statement_id,))
        return list(entry["history"])

    def is_current(self, statement_id: str, version: int) -> bool:
        """The check every verifier applies: accept only the current
        circuit version. Unknown ids and superseded versions -> False."""
        try:
            return self.current_version(statement_id) == int(version)
        except (RegistryError, TypeError, ValueError):
            return False

    def statement_ids(self):
        return sorted(self._entries)
