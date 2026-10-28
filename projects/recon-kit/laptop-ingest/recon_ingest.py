#!/usr/bin/env python3
"""
recon_ingest.py - Jarvis Recon Kit vision service (brain side, LOCAL ONLY).

Mentra Live --direct RTMP/SRT/WHIP (auth)--> MediaMTX path "glasses"
  -> this service grabs 1 frame (ffmpeg, rtsp://127.0.0.1:8554, auth; memory only)
  -> Ollama PINNED vision model @ 127.0.0.1:11434   (no cloud fallback - SAF)
  -> reply envelope to caller + push to watch via LoRa bridge 127.0.0.1:8766/push

Design rules (Plugin Armoury + SAF):
  * Envelope v1 (shared/schema.json) validated in and out; fail closed.
  * Vision text is UNTRUSTED: it is never sent to the agentic orchestrator
    /jarvis route (which can run tools). It is only displayed/spoken.
  * Frames are never written to disk or logged; logs are JSON lines, metadata only.
  * Throttle: at most one frame per MIN_FRAME_GAP seconds.
  * Ollama down -> retry with backoff, then queue (no hard fail); queued results
    are pushed to the watch when ready.
  * Bind 127.0.0.1 by default; LAN bind only if JV_INGEST_BIND is set (approval).

HTTP (default 127.0.0.1:8767 - 8765 avoided per Cartographer port-clash note):
  POST /look   body = envelope {v,id,ts,src,kind:"cmd",payload:{prompt}}
               -> envelope {kind:"reply", ack_of:id, payload:{text,short,ms,status}}
  GET  /health -> {"ok":true,"stream":bool,"queued":n}
Not run by this build - see BUILD-STATUS.md.
"""
import base64, json, os, queue, subprocess, sys, threading, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
from jv_envelope import validate, make  # noqa: E402

# ---- CONFIG (env overrides; secrets ONLY from env / .env, never in code) ----
BIND_HOST     = os.environ.get("JV_INGEST_BIND", "127.0.0.1")
BIND_PORT     = int(os.environ.get("JV_INGEST_PORT", "8767"))
RTSP_USER     = os.environ.get("JV_MTX_READ_USER", "")
RTSP_PASS     = os.environ.get("JV_MTX_READ_PASS", "")
RTSP_URL      = "rtsp://%s127.0.0.1:8554/glasses" % (
    ("%s:%s@" % (RTSP_USER, RTSP_PASS)) if RTSP_USER else "")
FFMPEG        = os.environ.get("JV_FFMPEG", "ffmpeg")
OLLAMA_URL    = "http://127.0.0.1:11434/api/generate"
VISION_MODEL  = os.environ.get("JV_VISION_MODEL", "moondream:1.8b")  # PINNED, never "auto"
LORA_PUSH_URL = "http://127.0.0.1:8766/push"
# Per-device bearer tokens (comma list) from env only, e.g. iphone/ipad/watch-relay.
TOKENS = {t.strip() for t in os.environ.get("JV_INGEST_TOKENS", "").split(",") if t.strip()}
# Nested timeouts (SAF): ingest HARD CAP 30 s < orchestrator 40 s < caller 45 s < voice 50 s.
REPLY_BUDGET_S = 30           # /look always answers (ok / queued / error) within this
VISION_TIMEOUT = 20           # per Ollama attempt, further clipped to the remaining budget
RETRY_BACKOFF  = [2, 5]       # in-request retries (only while budget remains)
QUEUE_MAX_TRIES = 3           # background retries per queued look, then dead-letter
QUEUE_BACKOFF   = [10, 30, 60]
QUEUE_TTL_S     = 600         # queued looks older than this are dead-lettered
DEAD_LETTER     = os.environ.get("JV_DEADLETTER", r"C:\JarvisData\recon\deadletter.jsonl")  # metadata only, not synced
PUSH_TOKEN      = os.environ.get("JV_PUSH_TOKEN", "")   # shared secret for 127.0.0.1:8766/push
MIN_FRAME_GAP  = 2.0          # seconds (1 frame / 2-5 s)
MAX_JPEG_BYTES = 1_000_000
MAX_WATCH      = 160
DEFAULT_PROMPT = ("In one or two short sentences, identify the main object or device "
                  "in view, including brand, model, or label text. Describe only; "
                  "do not give instructions.")

_last_grab = 0.0
_grab_lock = threading.Lock()
PENDING = queue.Queue(maxsize=5)   # small: each item holds one JPEG in RAM


def jlog(event, **kw):
    """JSON-line log, metadata only (never image bytes, never full prompts)."""
    kw.update(ts=round(time.time(), 3), svc="recon-ingest", event=event)
    print(json.dumps(kw), flush=True)


def grab_frame(timeout=8.0) -> bytes:
    global _last_grab
    with _grab_lock:
        wait = MIN_FRAME_GAP - (time.time() - _last_grab)
        if wait > 0:
            time.sleep(wait)
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-rtsp_transport", "tcp",
               "-i", RTSP_URL, "-frames:v", "1", "-q:v", "5",
               "-vf", "scale=w=1024:h=1024:force_original_aspect_ratio=decrease",
               "-f", "image2pipe", "-vcodec", "mjpeg", "pipe:1"]
        out = subprocess.run(cmd, capture_output=True, timeout=timeout, check=True).stdout
        _last_grab = time.time()
    if not out:
        raise RuntimeError("no frame")
    if len(out) > MAX_JPEG_BYTES:
        raise ValueError("frame over 1MB")
    return out


def post_json(url, obj, timeout, headers=None):
    h = {"Content-Type": "application/json"}
    h.update(headers or {})
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace") or "{}")


def ask_ollama(jpeg, prompt, timeout=VISION_TIMEOUT):
    data = post_json(OLLAMA_URL, {
        "model": VISION_MODEL, "prompt": prompt or DEFAULT_PROMPT,
        "images": [base64.b64encode(jpeg).decode()], "stream": False,
        "keep_alive": "2m",            # free VRAM soon after (qwen3:8b ~5.2 GB)
        "options": {"temperature": 0.2, "num_predict": 120}}, timeout=timeout)
    return " ".join(str(data.get("response", "")).split()) or "Nothing recognized."


def ask_vision(jpeg, prompt, deadline):
    """Retry Ollama only while the 30 s reply budget lasts; then ConnectionError -> queued."""
    for i, wait in enumerate([0] + RETRY_BACKOFF):
        if time.time() + wait + 3 >= deadline:
            break
        time.sleep(wait)
        left = deadline - time.time() - 1
        if left < 2:
            break
        try:
            return ask_ollama(jpeg, prompt, timeout=min(VISION_TIMEOUT, left))
        except Exception as e:
            jlog("ollama_retry", attempt=i + 1, err=type(e).__name__)
    raise ConnectionError("vision offline")
    # Cloud fallback (FreeLLMAPI :3001) intentionally NOT implemented - SAF:
    # local-only unless HgX explicitly approves later.


def sanitize(text):
    """Vision text is untrusted: printable, single line, capped."""
    t = "".join(c for c in text if c.isprintable()).replace("|", "/")
    return t[:400]


def short(text):
    return text if len(text) <= MAX_WATCH else text[:MAX_WATCH - 1] + "\u2026"


def push_watch(mid, text):
    try:
        post_json(LORA_PUSH_URL, {"msgid": mid[:4], "text": "RC:" + short(text)}, 5,
                  headers={"X-JV-Push-Token": PUSH_TOKEN})
        jlog("push_ok", id=mid)
    except Exception as e:
        jlog("push_failed", id=mid, err=type(e).__name__)   # loud, not silent


def dead_letter(mid, src, reason, tries):
    """Append METADATA ONLY (never the frame) to the local dead-letter JSONL, log, and tell the watch."""
    rec = {"ts": round(time.time(), 3), "id": mid, "src": src, "reason": reason, "tries": tries}
    try:
        os.makedirs(os.path.dirname(DEAD_LETTER), exist_ok=True)
        with open(DEAD_LETTER, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    except Exception as e:
        jlog("deadletter_write_failed", id=mid, err=type(e).__name__)
    jlog("dead_letter", **{k: v for k, v in rec.items() if k != "ts"})
    push_watch(mid, "Recon failed - vision offline.")


def _drain():
    while True:
        mid, src, prompt, jpeg, queued_at = PENDING.get()
        tries = 0
        while True:
            if time.time() - queued_at > QUEUE_TTL_S:
                dead_letter(mid, src, "expired", tries); break
            if tries >= QUEUE_MAX_TRIES:
                dead_letter(mid, src, "max_tries", tries); break
            time.sleep(QUEUE_BACKOFF[min(tries, len(QUEUE_BACKOFF) - 1)])
            tries += 1
            try:
                txt = sanitize(ask_ollama(jpeg, prompt))
                jlog("queued_done", id=mid, tries=tries)
                push_watch(mid, txt)
                break
            except Exception as e:
                jlog("queued_retry", id=mid, tries=tries, err=type(e).__name__)
        jpeg = None   # drop frame from RAM


def run_look(env):
    mid, src = env["id"], env["src"]
    prompt = str(env["payload"].get("prompt", ""))[:300]
    t0 = time.time(); status = "ok"; jpeg = None
    deadline = t0 + REPLY_BUDGET_S
    try:
        jpeg = grab_frame(timeout=min(8.0, REPLY_BUDGET_S / 3))
        text = sanitize(ask_vision(jpeg, prompt, deadline))
    except ConnectionError:
        try:
            PENDING.put_nowait((mid, src, prompt, jpeg, time.time()))
            text, status = "Vision busy - queued; result will buzz when ready.", "queued"
        except queue.Full:
            text, status = "Vision offline - queue full.", "error"
    except Exception as e:
        text, status = "Recon failed: %s" % type(e).__name__, "error"
    ms = int((time.time() - t0) * 1000)
    jlog("look", id=mid, src=src, status=status, ms=ms, chars=len(text))
    if src == "glasses" and status == "ok":
        push_watch(mid, text)      # watch-originated looks get it in the reply
    return make(mid, "brain", "reply",
                {"text": text, "short": short(text), "ms": ms, "status": status}, ack_of=mid)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def _authed(self):
        if not TOKENS:                      # no tokens -> loopback callers only
            return self.client_address[0] == "127.0.0.1"
        import hmac
        h = self.headers.get("Authorization", "")
        tok = h[7:] if h.startswith("Bearer ") else ""
        return any(hmac.compare_digest(tok, t) for t in TOKENS)

    def do_GET(self):
        if not self._authed():
            return self._send(401, {"error": "auth"})
        if self.path == "/health":
            try:
                grab_frame(timeout=4); live = True
            except Exception:
                live = False
            return self._send(200, {"ok": True, "stream": live, "queued": PENDING.qsize()})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self._authed():
            jlog("reject", err="auth")
            return self._send(401, {"error": "auth"})            # fail closed
        if self.path != "/look":
            return self._send(404, {"error": "not found"})
        n = min(int(self.headers.get("Content-Length", 0)), 4096)
        try:
            env = validate(json.loads(self.rfile.read(n) or b"{}"))
            if env["kind"] != "cmd" or env["src"] not in ("glasses", "watch"):
                raise ValueError("look needs kind=cmd from glasses/watch")
        except Exception as e:
            jlog("reject", err=str(e)[:80])
            return self._send(400, {"error": "schema"})          # fail closed
        self._send(200, run_look(env))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    if BIND_HOST != "127.0.0.1" and not TOKENS:
        sys.exit("Refusing non-loopback bind without JV_INGEST_TOKENS")
    if len(PUSH_TOKEN) < 24:
        sys.exit("Refusing to start: JV_PUSH_TOKEN missing or < 24 chars (shared with the LoRa bridge)")
    jlog("start", bind=BIND_HOST, port=BIND_PORT, model=VISION_MODEL, auth=bool(TOKENS))
    threading.Thread(target=_drain, daemon=True).start()
    ThreadingHTTPServer((BIND_HOST, BIND_PORT), Handler).serve_forever()
