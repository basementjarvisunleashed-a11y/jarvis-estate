"""Stdlib validator for shared/schema.json (v1). Fail closed: raises ValueError."""
import base64
import time

SRC = {"glasses", "watch", "flipper", "brain"}
KIND = {"frame", "audio", "scan", "cmd", "reply", "snapshot", "escalate"}  # unknown kinds rejected
SNAP_MAX_PX = 640
SNAP_MAX_Q = 70
SNAP_MAX_BYTES = 150 * 1024
KEYS = {"v", "id", "ts", "src", "kind", "payload", "ack_of"}


def _id_ok(s):
    return isinstance(s, str) and 1 <= len(s) <= 8 and all(c in "0123456789abcdefghijklmnopqrstuvwxyz" for c in s)


def validate(env: dict) -> dict:
    if not isinstance(env, dict):
        raise ValueError("envelope must be an object")
    extra = set(env) - KEYS
    if extra:
        raise ValueError("unknown fields: %s" % sorted(extra))
    if env.get("v") != 1:
        raise ValueError("v must be 1")
    if not _id_ok(env.get("id")):
        raise ValueError("bad id")
    if not isinstance(env.get("ts"), (int, float)):
        raise ValueError("bad ts")
    if env.get("src") not in SRC or env.get("kind") not in KIND:
        raise ValueError("bad src/kind")
    if not isinstance(env.get("payload"), dict):
        raise ValueError("payload must be an object")
    if "ack_of" in env and not _id_ok(env["ack_of"]):
        raise ValueError("bad ack_of")
    p = env["payload"]
    if env["kind"] == "snapshot":
        # ONE still for escalation - never a stream. JPEG <=640 px, q<=70, <=150 KB + local_summary.
        if set(p) - {"jpeg_b64", "w", "h", "q", "local_summary"}:
            raise ValueError("snapshot: unknown payload fields")
        for k in ("w", "h", "q"):
            if not isinstance(p.get(k), int) or p[k] < 1:
                raise ValueError("snapshot: bad %s" % k)
        if p["w"] > SNAP_MAX_PX or p["h"] > SNAP_MAX_PX or p["q"] > SNAP_MAX_Q:
            raise ValueError("snapshot: over 640 px or q70")
        b = p.get("jpeg_b64")
        if not isinstance(b, str):
            raise ValueError("snapshot: jpeg_b64 missing")
        raw = base64.b64decode(b, validate=True)
        if len(raw) > SNAP_MAX_BYTES or not raw.startswith(b"\xff\xd8"):
            raise ValueError("snapshot: not a JPEG or over 150 KB")
        if not isinstance(p.get("local_summary"), dict):
            raise ValueError("snapshot: local_summary required")
    elif env["kind"] == "escalate":
        q = p.get("question")
        if not isinstance(q, str) or not q or len(q) > 2000 or not isinstance(p.get("local_summary"), dict):
            raise ValueError("escalate: question (<=2000 chars) + local_summary required")
        if "snapshot_id" in p and not _id_ok(p["snapshot_id"]):
            raise ValueError("escalate: bad snapshot_id")
    return env


def make(id, src, kind, payload, ack_of=None):
    e = {"v": 1, "id": id, "ts": time.time(), "src": src, "kind": kind, "payload": payload}
    if ack_of:
        e["ack_of"] = ack_of
    return validate(e)
