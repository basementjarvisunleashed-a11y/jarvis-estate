"""Drop-in helper for the router (04-little-router.py, port 11435).

The router asks the GPU orchestrator before it routes an easy (9B) call.
The hard (27B) route never calls this: the 27B uses no VRAM.

Call it at the top of the easy-route handler, before the Ollama call:

    from router_integration import ensure_gpu_llm

    gpu = ensure_gpu_llm(timeout=180)
    if not gpu["ok"]:
        return 503, {"error": gpu["error"]}
    # ... route the easy call to the 9B as today ...

Behaviour:
  - {"ok": True, "mode": "llm"}: the 9B is resident. Route as normal.
  - {"ok": True, "mode": "llm", "orchestrator": "unreachable"}: the
    orchestrator is down. FAIL OPEN: route as today and log a warning.
    The 9B is usually resident, so the call usually works. The
    orchestrator being down must never take the LLM down with it.
  - {"ok": False, "error": ...}: the swap failed or the GPU is busy
    (a render is running). FAIL CLOSED: return 503 with that message.
    Killing a render to answer a chat call would be worse than asking
    the caller to wait a moment.

Stdlib only. No credentials.
"""

import json
import urllib.error
import urllib.request

ORCHESTRATOR_URL = "http://127.0.0.1:11436"


def _post(path, payload, timeout):
    url = ORCHESTRATOR_URL + path
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", "replace")
        return resp.status, json.loads(body) if body else {}


def ensure_gpu_llm(timeout=180, orchestrator_url=None):
    """Make sure the 9B is resident on the GPU. See the module docstring
    for the fail-open / fail-closed contract."""
    base = orchestrator_url or ORCHESTRATOR_URL
    url = base + "/acquire"
    data = json.dumps(
        {"purpose": "llm", "holder": "router", "wait": True}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            result = json.loads(body) if body else {}
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        # Orchestrator unreachable: fail open, route as today.
        return {
            "ok": True,
            "mode": "llm",
            "orchestrator": "unreachable",
            "note": "proceeding anyway: %s" % exc,
        }
    if result.get("ok"):
        return {"ok": True, "mode": result.get("mode", "llm")}
    return {
        "ok": False,
        "mode": result.get("mode"),
        "error": result.get("error") or "GPU orchestrator could not ready the LLM",
        "state": result.get("state"),
    }


def ensure_gpu_comfy(timeout=180, orchestrator_url=None):
    """Hand the GPU to ComfyUI (park the 9B, start ComfyUI). Used by the
    dashboard before it queues a render. Unlike the LLM helper this
    FAILS CLOSED when the orchestrator is unreachable: a render without
    the GPU swap is guaranteed to fail with an out-of-memory error, so a
    clear error is better than a confusing one."""
    base = orchestrator_url or ORCHESTRATOR_URL
    url = base + "/acquire"
    data = json.dumps(
        {"purpose": "comfy", "holder": "dashboard", "wait": True}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            result = json.loads(body) if body else {}
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return {
            "ok": False,
            "mode": None,
            "error": "GPU orchestrator unreachable, cannot start the picture brain: %s" % exc,
        }
    if result.get("ok"):
        return {"ok": True, "mode": result.get("mode", "comfy")}
    return {
        "ok": False,
        "mode": result.get("mode"),
        "error": result.get("error") or "GPU orchestrator could not ready ComfyUI",
        "state": result.get("state"),
    }


def gpu_state(timeout=10, orchestrator_url=None):
    """Return the orchestrator's state dict, or None if unreachable."""
    base = orchestrator_url or ORCHESTRATOR_URL
    try:
        with urllib.request.urlopen(base + "/state", timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            return json.loads(body) if body else None
    except (urllib.error.URLError, OSError, TimeoutError, ValueError):
        return None
