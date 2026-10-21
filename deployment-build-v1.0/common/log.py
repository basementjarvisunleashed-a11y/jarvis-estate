"""Append-only intent log (Phase 0; control plane owns it — paper §2.1).

Every entry is a sealed envelope chained to its predecessor:
    entry = {seq, ts, type, content, prev}
    seal  = HMAC(key, canonical(sha256(entry-without-seal), origin, ts))

verify_chain() walks the whole log: every seal must verify and every
prev must equal the previous entry's seal. Done when the chain verifies
end-to-end (§6.1 Phase 0).

Rollback (§6.3): every phase is reversible. The previous phase's state is
sealed before the next begins (checkpoint()), and rollback is a return to
the last sealed phase — itself a sealed log entry (rollback() appends a
ROLLBACK entry; the log is never truncated).
"""
import json
import os
from . import seal as _seal
from .seal import SealError

ENTRY_TYPES = ("INTENT", "DECISION", "EVIDENCE", "CHECKPOINT", "ROLLBACK",
               "DENIAL", "PROOF")


class IntentLog:
    def __init__(self, path: str, key: bytes, origin: str = "intent-log",
                 clock=None):
        self.path = path
        self.key = key
        self.origin = origin
        self.clock = clock
        self.entries = []
        if os.path.isfile(path):
            self._load()

    def _load(self):
        with open(self.path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    env = json.loads(line)
                    _seal.open_envelope(self.key, env)  # raises on bad seal
                    self.entries.append(env)

    def _persist(self, env: dict):
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(env, sort_keys=True) + "\n")

    def append(self, entry_type: str, content: dict, ts: int = None) -> dict:
        if entry_type not in ENTRY_TYPES:
            raise ValueError("unknown entry type %r" % entry_type)
        ts = self.clock.now() if (ts is None and self.clock) else int(ts or 0)
        prev = self.entries[-1]["seal"] if self.entries else "GENESIS"
        body = {"seq": len(self.entries), "ts": ts, "type": entry_type,
                "content": content, "prev": prev}
        env = _seal.make_envelope(self.key, body, self.origin, ts)
        self._persist(env)
        self.entries.append(env)
        return env

    def verify_chain(self) -> bool:
        """Every seal verifies; every prev links. Returns bool."""
        prev = "GENESIS"
        for env in self.entries:
            if not _seal.verify_envelope(self.key, env):
                return False
            body = env["content"]
            if body.get("prev") != prev:
                return False
            prev = env["seal"]
        return True

    def checkpoint(self, label: str) -> dict:
        """Seal the current state before the next phase begins (§6.3)."""
        return self.append("CHECKPOINT", {"label": label,
                                          "seq": len(self.entries)})

    def rollback(self, label: str) -> dict:
        """Return to the last sealed phase — itself a sealed log entry."""
        marks = [e for e in self.entries
                 if e["content"]["type"] == "CHECKPOINT"
                 and e["content"]["content"]["label"] == label]
        if not marks:
            raise SealError("no checkpoint labelled %r" % label)
        return self.append("ROLLBACK", {"label": label,
                                       "to_seq": marks[-1]["content"]["seq"]})

    def __len__(self):
        return len(self.entries)
