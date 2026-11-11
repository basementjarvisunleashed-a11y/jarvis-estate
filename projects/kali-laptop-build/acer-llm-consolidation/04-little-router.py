#!/usr/bin/env python3
"""The Little Router — one door for everything on the Acer.

Listens on 127.0.0.1:11435 and exposes an OpenAI-compatible
/v1/chat/completions endpoint. It picks the brain:
  - default (easy work) -> RESIDENT_MODEL: the 9B abliterated on VRAM
  - hard work           -> HEAVY_MODEL: the 27B on system RAM
  - "model": "cloud"    -> CLOUD_JARVIS: Cloud Jarvis, the Grokbot
                           (remote, Grok-powered)
  - "model": "free"     -> FREELLM: the free LLM (FreeLLMAPI, the local
                           Docker service on :3001)

Hard is chosen when the caller asks for it ("model": "hard" in the
request) or the prompt is long (over HARD_CHAR_THRESHOLD characters).
Cloud and free are chosen only when the caller asks for them by name —
they are explicit routes, not fallbacks. Every routing decision is
logged to router.log.

Ollama routes are translated to Ollama's native /api/chat before
forwarding, because the native door is the one that obeys "think" and
"keep_alive": a request that does not set "think" lets the model think
(Qwen3.5 default); "think": false answers at once. The router also
pins the resident model by setting keep_alive on every Ollama call
(easy: 24h, hard: 1h), so a plain call can never reset the clock back
to Ollama's 5-minute default. Cloud and free stay OpenAI-shaped — they
are OpenAI-compatible upstreams. Responses are translated back to
OpenAI shape, so callers always see the same door.

Cloud Jarvis needs CLOUD_JARVIS_URL + CLOUD_JARVIS_KEY (Grok tokens);
if the key is missing, the cloud route answers 503 "not configured"
instead of breaking. The default URL is xAI's API base; confirm the
model name and the key at home. FreeLLMAPI needs FREELLM_URL (default
http://127.0.0.1:3001); if it is down, the free route answers 502.
Confirm the free model name at home.

GPU orchestrator (2026-11-06): before an easy (9B) call the router
asks the GPU orchestrator on 127.0.0.1:11436 to make sure the 9B is
resident. If the orchestrator is down, the call routes as today (fail
open). If a render is running or the swap fails, the call answers 503
(fail closed) instead of killing the render. The hard (27B) route never
asks: the 27B uses no VRAM.

Response capture (2026-11-07): every call — the full prompt (messages)
and the full reply — is appended to router-responses.jsonl, next to
router.log, one JSON object per line. The capture is fail-open: if
logging fails, the call still succeeds and the caller still gets its
reply. The publishing house scrubs each batch before it reaches
GitHub; raw logs never go to GitHub.

Stdlib only — no dependencies. Run:  python3 04-little-router.py
Config via environment: ROUTER_PORT, OLLAMA_URL, RESIDENT_MODEL,
HEAVY_MODEL, HARD_CHAR_THRESHOLD, ROUTER_LOG, ROUTER_RESPONSES_LOG,
KEEP_ALIVE_EASY, KEEP_ALIVE_HARD, CLOUD_JARVIS_URL, CLOUD_JARVIS_KEY,
CLOUD_JARVIS_MODEL, FREELLM_URL, FREELLM_MODEL.
"""
import json
import os
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    from router_integration import ensure_gpu_llm
except Exception:
    ensure_gpu_llm = None

PORT = int(os.environ.get("ROUTER_PORT", "11435"))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
RESIDENT_MODEL = os.environ.get("RESIDENT_MODEL", "qwen9b-abliterated")
HEAVY_MODEL = os.environ.get("HEAVY_MODEL", "huihui_ai/Qwen3.8-abliterated:27b")
HARD_CHAR_THRESHOLD = int(os.environ.get("HARD_CHAR_THRESHOLD", "8000"))
LOG_PATH = os.environ.get(
    "ROUTER_LOG",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "router.log"),
)
RESPONSE_LOG_PATH = os.environ.get(
    "ROUTER_RESPONSES_LOG",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "router-responses.jsonl"),
)
KEEP_ALIVE_EASY = os.environ.get("KEEP_ALIVE_EASY", "24h")
KEEP_ALIVE_HARD = os.environ.get("KEEP_ALIVE_HARD", "1h")

CLOUD_JARVIS_URL = os.environ.get("CLOUD_JARVIS_URL", "https://api.x.ai/v1").rstrip("/")
CLOUD_JARVIS_KEY = os.environ.get("CLOUD_JARVIS_KEY", "")
CLOUD_JARVIS_MODEL = os.environ.get("CLOUD_JARVIS_MODEL", "grok-4")
FREELLM_URL = os.environ.get("FREELLM_URL", "http://127.0.0.1:3001").rstrip("/")
FREELLM_MODEL = os.environ.get("FREELLM_MODEL", "free")


def log_decision(route, model, prompt_chars, stream):
    line = json.dumps({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "route": route,
        "model": model,
        "prompt_chars": prompt_chars,
        "stream": stream,
    })
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


def log_response(route, model, stream, messages, response,
                 thinking=None, error=None):
    """Append one response-capture entry (JSONL) to RESPONSE_LOG_PATH.

    One entry per call: time, route, model, the full prompt (messages),
    and the FULL reply text (whole, not summarized). Fail open: a
    logging failure must never break a call, so every failure path
    here is swallowed. The entry is written best-effort; if the
    primary encoding fails, retry with ASCII escapes.
    """
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "route": route,
        "model": model,
        "stream": stream,
        "prompt_chars": prompt_chars({"messages": messages}),
        "messages": messages,
        "response": response,
        "thinking": thinking or "",
        "error": error or "",
    }
    try:
        line = json.dumps(entry, ensure_ascii=False)
    except Exception:
        try:
            line = json.dumps(entry, ensure_ascii=True)
        except Exception:
            return
    try:
        with open(RESPONSE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
    except Exception:
        pass


def prompt_chars(body):
    total = 0
    for m in body.get("messages", []):
        c = m.get("content", "")
        if isinstance(c, str):
            total += len(c)
    return total


def _openai_content(data):
    """Best-effort: pull the assistant message text out of an
    OpenAI-shaped chat.completion body (a dict). Returns "" when the
    body is not that shape."""
    try:
        choices = data.get("choices") or []
        if choices:
            msg = choices[0].get("message") or {}
            return msg.get("content", "") or ""
    except Exception:
        pass
    return ""


def _extract_sse_content(text):
    """Best-effort: pull the joined delta content out of an OpenAI SSE
    stream body (text). Returns "" when nothing is found."""
    parts = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            continue
        try:
            item = json.loads(payload)
        except Exception:
            continue
        try:
            choices = item.get("choices") or [{}]
            delta = choices[0].get("delta") or {}
            c = delta.get("content", "")
        except Exception:
            continue
        if c:
            parts.append(c)
    return "".join(parts)


def decide(body):
    """Returns (route, model, base_url, needs_cloud_key, native, keep_alive)."""
    m = body.get("model")
    if m in ("cloud", "grok", "cloud-jarvis"):
        return "cloud", CLOUD_JARVIS_MODEL, CLOUD_JARVIS_URL, True, False, None
    if m in ("free", "freellm", "free-llm"):
        return "free", FREELLM_MODEL, FREELLM_URL, False, False, None
    if m in ("hard", "heavy", "27b"):
        return "hard", HEAVY_MODEL, OLLAMA_URL, False, True, KEEP_ALIVE_HARD
    if prompt_chars(body) > HARD_CHAR_THRESHOLD:
        return "hard", HEAVY_MODEL, OLLAMA_URL, False, True, KEEP_ALIVE_HARD
    return "easy", RESIDENT_MODEL, OLLAMA_URL, False, True, KEEP_ALIVE_EASY


def to_native(body, model, keep_alive, stream):
    """Translate an OpenAI-shaped body to Ollama's native /api/chat body."""
    native = {
        "model": model,
        "messages": body.get("messages", []),
        "stream": stream,
        "keep_alive": keep_alive,
    }
    if "think" in body:
        native["think"] = body["think"]
    options = {}
    if isinstance(body.get("options"), dict):
        options.update(body["options"])
    if "temperature" in body:
        options["temperature"] = body["temperature"]
    if "top_p" in body:
        options["top_p"] = body["top_p"]
    if "max_tokens" in body:
        options["num_predict"] = body["max_tokens"]
    if model == HEAVY_MODEL:
        options["num_gpu"] = 0
    if options:
        native["options"] = options
    return native


def native_to_openai(native, model):
    """Translate a native /api/chat reply to OpenAI chat.completion shape."""
    msg = native.get("message", {})
    out_msg = {"role": msg.get("role", "assistant"),
               "content": msg.get("content", "")}
    if native.get("thinking"):
        out_msg["reasoning"] = native["thinking"]
    return {
        "id": "chatcmpl-router",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": out_msg,
                     "finish_reason": "stop"}],
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep stdout quiet
        pass

    def _forward(self, base, path, body_bytes, extra_headers=None):
        headers = {"Content-Type": "application/json"}
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(
            base + path, data=body_bytes, headers=headers, method="POST",
        )
        return urllib.request.urlopen(req, timeout=600)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {
                "ok": True,
                "routes": {
                    "easy": RESIDENT_MODEL,
                    "hard": HEAVY_MODEL,
                    "cloud": {"model": CLOUD_JARVIS_MODEL,
                              "url": CLOUD_JARVIS_URL,
                              "configured": bool(CLOUD_JARVIS_KEY)},
                    "free": {"model": FREELLM_MODEL, "url": FREELLM_URL},
                },
            })
        elif self.path == "/v1/models":
            try:
                with urllib.request.urlopen(
                        OLLAMA_URL + "/api/tags", timeout=10) as r:
                    self._send_raw(r.status, r.read(),
                                   r.headers.get("Content-Type", "application/json"))
            except Exception as e:
                self._send_json(502, {"error": str(e)})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self._send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_json(400, {"error": "invalid JSON"})
            return
        route, model, base, needs_key, native, keep_alive = decide(body)
        stream = bool(body.get("stream"))
        messages = body.get("messages", [])
        log_decision(route, model, prompt_chars(body), stream)
        if route == "easy" and ensure_gpu_llm is not None:
            gpu = ensure_gpu_llm(timeout=180)
            if not gpu["ok"]:
                log_response(route, model, stream, messages, "",
                             error=gpu.get("error", "GPU orchestrator could not ready the LLM"))
                self._send_json(503, {"error": gpu["error"]})
                return
        if needs_key and not CLOUD_JARVIS_KEY:
            log_response(route, model, stream, messages, "",
                         error="cloud Jarvis not configured: set CLOUD_JARVIS_URL and CLOUD_JARVIS_KEY")
            self._send_json(503, {"error": "cloud Jarvis not configured: "
                                  "set CLOUD_JARVIS_URL and CLOUD_JARVIS_KEY"})
            return
        extra = ({"Authorization": "Bearer " + CLOUD_JARVIS_KEY}
                 if needs_key else None)
        if native:
            path = "/api/chat"
            fwd_body = to_native(body, model, keep_alive, stream)
        else:
            path = "/v1/chat/completions"
            fwd_body = dict(body)
            fwd_body["model"] = model
        try:
            resp = self._forward(base, path,
                                 json.dumps(fwd_body).encode("utf-8"), extra)
        except urllib.error.HTTPError as e:
            err_body = e.read()
            err_text = err_body.decode("utf-8", "replace")
            log_response(route, model, stream, messages, err_text,
                         error="upstream HTTP %s" % e.code)
            self._send_raw(e.code, err_body, "application/json")
            return
        except Exception as e:
            log_response(route, model, stream, messages, "",
                         error=str(e))
            self._send_json(502, {"error": str(e)})
            return
        if stream:
            self.send_response(resp.status)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if native:
                self._relay_native_stream(resp, model, route, messages)
            else:
                self._relay_openai_stream(resp, model, route, messages)
            resp.close()
        else:
            if native:
                try:
                    native_resp = json.loads(resp.read())
                except Exception as e:
                    log_response(route, model, stream, messages, "",
                                 error=str(e))
                    self._send_json(502, {"error": str(e)})
                    return
                msg = native_resp.get("message", {}) or {}
                log_response(route, model, stream, messages,
                             msg.get("content", "") or "",
                             thinking=native_resp.get("thinking", "") or None)
                self._send_json(resp.status,
                                native_to_openai(native_resp, model))
            else:
                raw_body = resp.read()
                content = ""
                try:
                    content = _openai_content(json.loads(raw_body.decode("utf-8")))
                except Exception:
                    content = ""
                log_response(route, model, stream, messages,
                             content if content else raw_body.decode("utf-8", "replace"))
                self._send_raw(resp.status, raw_body, "application/json")

    def _relay_native_stream(self, resp, model, route, messages):
        """Translate a native NDJSON stream into OpenAI SSE chunks.
        Accumulates the full reply and logs it (response capture) when
        the stream ends, even if the client disconnects mid-stream."""
        buf = b""
        parts = []
        thinking_parts = []
        try:
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                    except Exception:
                        continue
                    content = item.get("message", {}).get("content", "")
                    if content:
                        parts.append(content)
                    thinking = item.get("thinking", "")
                    if thinking:
                        thinking_parts.append(thinking)
                    done = item.get("done", False)
                    sse = {"id": "chatcmpl-router",
                           "object": "chat.completion.chunk",
                           "created": int(time.time()),
                           "model": model,
                           "choices": [{"index": 0,
                                        "delta": {"content": content} if content else {},
                                        "finish_reason": "stop" if done else None}]}
                    self.wfile.write(("data: " + json.dumps(sse) + "\n\n").encode())
                    if done:
                        self.wfile.write(b"data: [DONE]\n\n")
                        return
            self.wfile.write(b"data: [DONE]\n\n")
        finally:
            log_response(route, model, True, messages, "".join(parts),
                         thinking="".join(thinking_parts) or None)

    def _relay_openai_stream(self, resp, model, route, messages):
        """Pass an OpenAI SSE stream through unchanged, and log the full
        reply (response capture) when it ends, even if the client
        disconnects mid-stream."""
        raw = bytearray()
        try:
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                raw += chunk
                self.wfile.write(chunk)
        finally:
            text = bytes(raw).decode("utf-8", "replace")
            content = _extract_sse_content(text)
            log_response(route, model, True, messages,
                         content if content else text)

    def _send_json(self, code, obj):
        data = json.dumps(obj).encode("utf-8")
        self._send_raw(code, data, "application/json")

    def _send_raw(self, code, data, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print(f"Little Router on 127.0.0.1:{PORT} -> {OLLAMA_URL}")
    print(f"  easy  -> {RESIDENT_MODEL} (VRAM resident, keep_alive {KEEP_ALIVE_EASY})")
    print(f"  hard  -> {HEAVY_MODEL} (system RAM, on demand, keep_alive {KEEP_ALIVE_HARD})")
    print(f"  cloud -> {CLOUD_JARVIS_MODEL} (Cloud Jarvis / Grokbot) "
          f"[{'configured' if CLOUD_JARVIS_KEY else 'NOT CONFIGURED'}]")
    print(f"  free  -> {FREELLM_MODEL} (FreeLLMAPI {FREELLM_URL})")
    print(f"  log   -> {LOG_PATH}")
    print(f"  responses -> {RESPONSE_LOG_PATH}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
