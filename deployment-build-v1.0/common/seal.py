"""Sealed envelopes — the integrity-and-origin primitive (paper Appendix A).

Sealed envelope (every stored/transmitted object):
    {content, origin, ts, seal}
where
    seal = HMAC(key, canonical(sha256(content), origin, ts))

canonical() is the JSON canonicalisation: code-point key order,
(',', ':') separators, UTF-8, ensure_ascii=False — the same procedure
the estate uses for approval digests (spec/approval-digest.md).

Nothing renders or executes before its seal verifies (paper §2.2 rule 3).
"""
import hashlib
import hmac
import json


class SealError(Exception):
    """Raised when a seal does not verify. Fail closed."""


def canonical(obj) -> bytes:
    """Canonical JSON bytes for hashing/signing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_seal(key: bytes, content, origin: str, ts: int) -> str:
    """seal = HMAC(key, canonical(sha256(content), origin, ts))."""
    inner = sha256_hex(canonical(content))
    msg = canonical([inner, str(origin), int(ts)])
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def verify_seal(key: bytes, seal: str, content, origin: str, ts: int) -> bool:
    """Constant-time seal check. Returns bool; never raises on mismatch."""
    expected = make_seal(key, content, origin, ts)
    return hmac.compare_digest(expected, str(seal))


def make_envelope(key: bytes, content, origin: str, ts: int) -> dict:
    """Build a sealed envelope."""
    return {
        "content": content,
        "origin": str(origin),
        "ts": int(ts),
        "seal": make_seal(key, content, origin, ts),
    }


def verify_envelope(key: bytes, env: dict) -> bool:
    """Check an envelope's seal. Missing fields -> False (fail closed)."""
    try:
        return verify_seal(key, env["seal"], env["content"],
                           env["origin"], env["ts"])
    except (KeyError, TypeError, ValueError):
        return False


def open_envelope(key: bytes, env: dict):
    """Verify, then return (content, origin, ts). Raises SealError."""
    if not verify_envelope(key, env):
        raise SealError("seal does not verify for origin=%r ts=%r"
                        % (env.get("origin"), env.get("ts")))
    return env["content"], env["origin"], env["ts"]


def intent_digest(intent: dict) -> str:
    """Intent digest D: SHA-256 over the canonical intent (paper §5.2).

    The principal approves the digest D, not the description: any mutation
    of target, effect, or content changes D, and the approval no longer binds.
    """
    return sha256_hex(canonical(intent))
