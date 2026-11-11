#!/usr/bin/env python3
"""GPU orchestrator for the Acer (RTX 2060, 6 GB VRAM).

Makes VRAM swaps automatic so no one has to say "swap" or run a manual
park/resume. The router asks this service before it routes a call that
needs the GPU; the orchestrator parks or loads the right tenant and
reports the state. It also keeps a state file the keep-alive cron reads
so a parked model is never reloaded mid-render.

Tenants (only one owns the GPU at a time):
  - LLM mode (default): qwen9b-abliterated resident on VRAM, the 27B
    resident on CPU/RAM, ComfyUI stopped.
  - COMFY mode: the 9B parked, ComfyUI running (holds about 2 GB VRAM),
    the 27B resident on CPU/RAM (unaffected).

Safe rules (learned the hard way, do not break them):
  1. Load order: 9B first, then 27B. Reloading the 9B while the 27B is
     resident can evict the 27B.
  2. The 27B must always be loaded with num_gpu 0. It is 18 GB; it can
     never live on a 6 GB card, and trying evicts the 9B.
  3. The keep-alive must skip the 9B while it is parked (see the state
     file and keep-brains-alive-v2.sh).
  4. Never stop ComfyUI while a render is running. Wait for the queue
     to drain (grace period), then report busy rather than kill it.
  5. If a swap fails, restore the previous tenant and report the error.
     Never leave the GPU in a half state.
  6. If this service is unreachable, the router proceeds as it does
     today (fail open for LLM calls). A ComfyUI start without this
     service is refused with a clear error (fail closed), because a
     render without the GPU swap is guaranteed to fail.

Stdlib only. No credentials. Nothing here talks to the network except
localhost (Ollama, ComfyUI, and this service's own port).

Usage:
  python3 gpu_orchestrator.py --serve            run the daemon (default)
  python3 gpu_orchestrator.py --state            print the GPU state
  python3 gpu_orchestrator.py --ensure-llm      park ComfyUI, load the 9B
  python3 gpu_orchestrator.py --ensure-comfy    park the 9B, start ComfyUI
  python3 gpu_orchestrator.py --serve --dry-run log what it would do only

Environment (all optional, defaults match the Acer):
  GPU_ORCH_PORT, GPU_ORCH_STATE_FILE, GPU_ORCH_LOG_FILE,
  GPU_ORCH_OLLAMA_URL, GPU_ORCH_COMFY_URL, GPU_ORCH_COMFY_PORT,
  GPU_ORCH_COMFY_DIR, GPU_ORCH_COMFY_PYTHON, GPU_ORCH_COMFY_MAIN,
  GPU_ORCH_COMFY_LOG, GPU_ORCH_COMFY_PID_FILE, GPU_ORCH_IDLE_RESTORE_MIN,
  GPU_ORCH_COMFY_GRACE_S, GPU_ORCH_VRAM_FREE_MIB
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------- config

HOME = os.path.expanduser("~")

NINE_B = "qwen9b-abliterated"
TWENTY_SEVEN_B = "huihui_ai/Qwen3.8-abliterated:27b"

# VRAM (MiB) the RTX 2060 reports. The 9B needs about 4830 MiB; ComfyUI
# (SD 1.5) needs about 2000 MiB; the desktop alone uses about 130 MiB.
VRAM_TOTAL_MIB = 6144
VRAM_FREE_MIB = int(os.environ.get("GPU_ORCH_VRAM_FREE_MIB", "500"))

CFG = {
    "port": int(os.environ.get("GPU_ORCH_PORT", "11436")),
    "ollama_url": os.environ.get("GPU_ORCH_OLLAMA_URL", "http://127.0.0.1:11434"),
    "comfy_url": os.environ.get("GPU_ORCH_COMFY_URL", "http://127.0.0.1:8188"),
    "comfy_port": int(os.environ.get("GPU_ORCH_COMFY_PORT", "8188")),
    "comfy_dir": os.environ.get("GPU_ORCH_COMFY_DIR", os.path.join(HOME, "ComfyUI")),
    "comfy_python": os.environ.get(
        "GPU_ORCH_COMFY_PYTHON", os.path.join(HOME, "ComfyUI", "venv313", "bin", "python")
    ),
    "comfy_main": os.environ.get("GPU_ORCH_COMFY_MAIN", "main.py"),
    "comfy_log": os.environ.get(
        "GPU_ORCH_COMFY_LOG", os.path.join(HOME, "ComfyUI", "comfyui.log")
    ),
    "comfy_pid_file": os.environ.get(
        "GPU_ORCH_COMFY_PID_FILE", os.path.join(HOME, "ComfyUI", "comfyui.pid")
    ),
    "state_file": os.environ.get(
        "GPU_ORCH_STATE_FILE", os.path.join(HOME, "Jarvis", "gpu-state.json")
    ),
    "log_file": os.environ.get(
        "GPU_ORCH_LOG_FILE", os.path.join(HOME, "Jarvis", "gpu-orchestrator.log")
    ),
    # Minutes of ComfyUI inactivity before the GPU is handed back to the
    # LLM on its own. 0 disables the idle restore.
    "idle_restore_min": int(os.environ.get("GPU_ORCH_IDLE_RESTORE_MIN", "30")),
    # Seconds to wait for a running ComfyUI render to finish before
    # reporting busy instead of killing it.
    "comfy_grace_s": int(os.environ.get("GPU_ORCH_COMFY_GRACE_S", "120")),
    "http_timeout_s": 30,
    "load_timeout_s": 300,
}

DRY_RUN = False
LOCK = threading.RLock()
LOG_LOCK = threading.Lock()

# In-memory desired mode. The state file and the /state endpoint always
# report this alongside the observed facts, so a mismatch is visible.
MODE = {"mode": "llm", "last_swap": None, "last_error": None}
LAST_COMFY_ACTIVITY = {"at": 0.0}  # epoch seconds; 0 means never observed


# ---------------------------------------------------------------- helpers

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(msg):
    line = "%s [gpu-orchestrator] %s" % (now_iso(), msg)
    with LOG_LOCK:
        try:
            os.makedirs(os.path.dirname(CFG["log_file"]), exist_ok=True)
            with open(CFG["log_file"], "a") as fh:
                fh.write(line + "\n")
        except OSError:
            pass
    print(line, flush=True)


def run(cmd, timeout=30):
    """Run a command. Returns (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, proc.stdout, proc.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -1, "", str(exc)


def http_get(url, timeout=30):
    """GET a URL. Returns (status, parsed_json_or_None)."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            try:
                return resp.status, json.loads(body) if body else None
            except ValueError:
                return resp.status, None
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except (urllib.error.URLError, OSError, TimeoutError):
        return None, None


def http_post_json(url, payload, timeout=300):
    """POST JSON. Returns (status, parsed_json_or_None)."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            try:
                return resp.status, json.loads(body) if body else None
            except ValueError:
                return resp.status, None
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except (urllib.error.URLError, OSError, TimeoutError):
        return None, None


# ---------------------------------------------------------------- observers

def read_vram():
    """Return (used_mib, total_mib) from nvidia-smi, or (None, None)."""
    rc, out, _err = run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used,memory.total",
            "--format=csv,noheader,nounits",
        ],
        timeout=15,
    )
    if rc != 0 or not out.strip():
        return None, None
    try:
        used_s, total_s = out.strip().split(",")
        return int(used_s.strip()), int(total_s.strip())
    except ValueError:
        return None, None


def read_ollama_models():
    """Return a dict {model_name: model_info} for loaded models, or None
    if Ollama cannot be reached. Names are normalised (no :latest)."""
    status, data = http_get(CFG["ollama_url"] + "/api/ps", timeout=15)
    if status is None or not isinstance(data, dict):
        return None
    models = {}
    for entry in data.get("models", []):
        name = entry.get("name", "")
        if name.endswith(":latest"):
            name = name[: -len(":latest")]
        models[name] = entry
    return models


def comfy_is_up():
    status, _data = http_get(CFG["comfy_url"] + "/", timeout=10)
    return status == 200


def comfy_queue_busy():
    """True if ComfyUI has a prompt running or queued. False if it is
    idle or unreachable. Also refreshes the last-activity timestamp."""
    status, data = http_get(CFG["comfy_url"] + "/queue", timeout=10)
    if status is None or not isinstance(data, dict):
        return False
    running = data.get("queue_running") or []
    pending = data.get("queue_pending") or []
    if running or pending:
        LAST_COMFY_ACTIVITY["at"] = time.time()
        return True
    return False


def current_state():
    """Gather the observed facts and the desired mode. Writes the state
    file atomically. Returns the state dict."""
    used, total = read_vram()
    models = read_ollama_models()
    comfy_up = comfy_is_up()
    if comfy_up:
        comfy_queue_busy()  # refreshes the activity timestamp if busy

    if models is None:
        nine_b = "unknown"
        twenty_seven_b = "unknown"
    else:
        nine_b = "resident" if NINE_B in models else "parked"
        twenty_seven_b = "resident" if TWENTY_SEVEN_B in models else "absent"

    state = {
        "mode": MODE["mode"],
        "nine_b": nine_b,
        "twenty_seven_b": twenty_seven_b,
        "comfy": "running" if comfy_up else "stopped",
        "vram_used_mib": used,
        "vram_total_mib": total if total is not None else VRAM_TOTAL_MIB,
        "updated": now_iso(),
        "last_swap": MODE["last_swap"],
        "last_error": MODE["last_error"],
    }
    write_state_file(state)
    return state


def write_state_file(state):
    if DRY_RUN:
        log("[dry-run] would write state file: mode=%s" % state.get("mode"))
        return
    try:
        os.makedirs(os.path.dirname(CFG["state_file"]), exist_ok=True)
        tmp = CFG["state_file"] + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(state, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(tmp, CFG["state_file"])
    except OSError as exc:
        log("could not write state file %s: %s" % (CFG["state_file"], exc))


def set_mode(mode, swap_from=None, reason=None):
    MODE["mode"] = mode
    MODE["last_error"] = None
    if swap_from is not None and swap_from != mode:
        MODE["last_swap"] = {
            "from": swap_from,
            "to": mode,
            "at": now_iso(),
            "reason": reason,
        }
        log("mode %s -> %s (%s)" % (swap_from, mode, reason or ""))


# ---------------------------------------------------------------- actors

def ollama_load(model, num_gpu=None, keep_alive="24h"):
    """Load a model by making a tiny chat call. num_gpu None means the
    Ollama default (GPU); num_gpu 0 forces CPU. Returns True on success.
    The 27B must always be loaded with num_gpu 0 (rule 2)."""
    if DRY_RUN:
        log("[dry-run] would load %s (num_gpu=%s)" % (model, num_gpu))
        return True
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Pong"}],
        "stream": False,
        "keep_alive": keep_alive,
        "think": False,
    }
    if num_gpu is not None:
        payload["options"] = {"num_gpu": num_gpu}
    status, _data = http_post_json(
        CFG["ollama_url"] + "/api/chat", payload, timeout=CFG["load_timeout_s"]
    )
    if status == 200:
        log("loaded %s (num_gpu=%s)" % (model, num_gpu))
        return True
    log("failed to load %s (HTTP %s)" % (model, status))
    return False


def ollama_stop(model):
    """Unload a model (the proven `ollama stop`). Returns True on success."""
    if DRY_RUN:
        log("[dry-run] would stop %s" % model)
        return True
    rc, _out, err = run(["ollama", "stop", model], timeout=60)
    if rc == 0:
        log("stopped %s" % model)
        return True
    log("failed to stop %s (rc=%s err=%s)" % (model, rc, err.strip()))
    return False


def wait_for_model(name, want_present, timeout_s):
    """Poll /api/ps until the model is present (or absent)."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        models = read_ollama_models()
        if models is not None:
            present = name in models
            if present == want_present:
                return True
        time.sleep(5)
    return False


def wait_for_vram_below(threshold_mib, timeout_s):
    """Poll nvidia-smi until VRAM used drops below the threshold."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        used, _total = read_vram()
        if used is not None and used < threshold_mib:
            return True
        time.sleep(2)
    return False


def start_comfy():
    """Start ComfyUI as a detached process and wait for it to answer.
    Returns True when it is up. Records the PID so stop is precise."""
    if DRY_RUN:
        log("[dry-run] would start ComfyUI")
        return True
    if comfy_is_up():
        log("ComfyUI is already up")
        return True
    try:
        os.makedirs(CFG["comfy_dir"], exist_ok=True)
        log_fh = open(CFG["comfy_log"], "a")
    except OSError as exc:
        log("cannot open ComfyUI log %s: %s" % (CFG["comfy_log"], exc))
        return False
    cmd = [
        CFG["comfy_python"],
        CFG["comfy_main"],
        "--listen",
        "127.0.0.1",
        "--port",
        str(CFG["comfy_port"]),
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=CFG["comfy_dir"],
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except OSError as exc:
        log("cannot start ComfyUI: %s" % exc)
        log_fh.close()
        return False
    # The child has its own copy of the log fd; close the parent's.
    log_fh.close()
    try:
        with open(CFG["comfy_pid_file"], "w") as fh:
            fh.write(str(proc.pid))
    except OSError as exc:
        log("cannot write ComfyUI PID file: %s" % exc)
    log("ComfyUI starting (pid %s)" % proc.pid)
    deadline = time.time() + 90
    while time.time() < deadline:
        if comfy_is_up():
            LAST_COMFY_ACTIVITY["at"] = time.time()
            log("ComfyUI is up")
            return True
        if proc.poll() is not None:
            log("ComfyUI exited early (rc=%s); see %s" % (proc.returncode, CFG["comfy_log"]))
            return False
        time.sleep(5)
    log("ComfyUI did not answer within 90s; see %s" % CFG["comfy_log"])
    return False


def stop_comfy():
    """Stop ComfyUI by its PID file (fall back to a pattern kill).
    Returns True when it is gone."""
    if DRY_RUN:
        log("[dry-run] would stop ComfyUI")
        return True
    pid = None
    try:
        with open(CFG["comfy_pid_file"]) as fh:
            pid = int(fh.read().strip())
    except (OSError, ValueError):
        pid = None
    stopped = False
    if pid:
        try:
            os.killpg(pid, signal.SIGTERM)
        except (OSError, ProcessLookupError):
            try:
                os.kill(pid, signal.SIGTERM)
            except (OSError, ProcessLookupError):
                stopped = True
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                os.kill(pid, 0)
            except (OSError, ProcessLookupError):
                stopped = True
                break
            time.sleep(1)
        if not stopped:
            try:
                os.killpg(pid, signal.SIGKILL)
            except (OSError, ProcessLookupError):
                try:
                    os.kill(pid, signal.SIGKILL)
                except (OSError, ProcessLookupError):
                    pass
            time.sleep(2)
            try:
                os.kill(pid, 0)
            except (OSError, ProcessLookupError):
                stopped = True
    if not stopped:
        rc, _out, _err = run(
            ["pkill", "-f", "main.py --listen 127.0.0.1 --port 8188"], timeout=15
        )
        stopped = rc in (0, 1)  # 1 means no process matched (already gone)
    try:
        os.remove(CFG["comfy_pid_file"])
    except OSError:
        pass
    deadline = time.time() + 10
    while time.time() < deadline:
        if not comfy_is_up():
            log("ComfyUI stopped")
            return True
        time.sleep(1)
    log("ComfyUI still answering after stop")
    return False


def wait_for_comfy_idle(grace_s):
    """Wait for a running ComfyUI render to finish. Returns True when
    the queue is empty, False when the grace period runs out."""
    deadline = time.time() + grace_s
    while time.time() < deadline:
        if not comfy_queue_busy():
            return True
        time.sleep(5)
    return not comfy_queue_busy()


# ---------------------------------------------------------------- operations

def ensure_llm(holder, reason):
    """Bring the GPU back to LLM mode: stop ComfyUI, load the 9B, then
    the 27B (safe order, rule 1). Returns (ok, state, error)."""
    with LOCK:
        log("ensure_llm holder=%s reason=%s" % (holder, reason))
        previous = MODE["mode"]
        st = current_state()
        if (
            st["mode"] == "llm"
            and st["nine_b"] == "resident"
            and st["comfy"] == "stopped"
        ):
            return True, st, None
        set_mode("transition", swap_from=previous, reason=reason)

        if comfy_is_up():
            if not wait_for_comfy_idle(CFG["comfy_grace_s"]):
                MODE["mode"] = previous
                MODE["last_error"] = "ComfyUI is busy rendering"
                log("refusing to stop ComfyUI: a render is running")
                return False, current_state(), "ComfyUI is busy rendering; try again in a moment"
            if not stop_comfy():
                MODE["mode"] = previous
                MODE["last_error"] = "could not stop ComfyUI"
                return False, current_state(), "could not stop ComfyUI"
            if not wait_for_vram_below(VRAM_FREE_MIB, 30):
                MODE["mode"] = previous
                MODE["last_error"] = "VRAM did not free after stopping ComfyUI"
                return False, current_state(), "VRAM did not free after stopping ComfyUI"

        st = current_state()
        if st["nine_b"] != "resident":
            if not ollama_load(NINE_B):
                MODE["mode"] = previous
                MODE["last_error"] = "could not load the 9B"
                return False, current_state(), "could not load the 9B on the GPU"
            if not wait_for_model(NINE_B, True, 120):
                MODE["mode"] = previous
                MODE["last_error"] = "9B did not appear after load"
                return False, current_state(), "the 9B did not appear after loading"

        # Safe order (rule 1): the 9B is loaded first, so restoring the
        # 27B now cannot evict it. The 27B always loads with num_gpu 0
        # (rule 2) because it lives in system RAM, never on the card.
        st = current_state()
        if st["twenty_seven_b"] != "resident":
            if not ollama_load(TWENTY_SEVEN_B, num_gpu=0):
                MODE["mode"] = previous
                MODE["last_error"] = "could not load the 27B"
                return False, current_state(), "could not load the 27B on CPU"
            if not wait_for_model(TWENTY_SEVEN_B, True, 180):
                MODE["mode"] = previous
                MODE["last_error"] = "27B did not appear after load"
                return False, current_state(), "the 27B did not appear after loading"

        set_mode("llm", swap_from=previous, reason=reason)
        return True, current_state(), None


def ensure_comfy(holder, reason):
    """Bring the GPU to COMFY mode: park the 9B, start ComfyUI.
    Returns (ok, state, error). If ComfyUI fails to start, the LLM is
    restored so the 9B is not left down (rule 5)."""
    with LOCK:
        log("ensure_comfy holder=%s reason=%s" % (holder, reason))
        previous = MODE["mode"]
        st = current_state()
        if (
            st["mode"] == "comfy"
            and st["comfy"] == "running"
            and st["nine_b"] == "parked"
        ):
            LAST_COMFY_ACTIVITY["at"] = time.time()
            return True, st, None
        set_mode("transition", swap_from=previous, reason=reason)

        st = current_state()
        if st["nine_b"] == "resident":
            if not ollama_stop(NINE_B):
                MODE["mode"] = previous
                MODE["last_error"] = "could not park the 9B"
                return False, current_state(), "could not park the 9B"
            if not wait_for_model(NINE_B, False, 60):
                MODE["mode"] = previous
                MODE["last_error"] = "9B did not stop"
                return False, current_state(), "the 9B did not stop"
            if not wait_for_vram_below(VRAM_FREE_MIB, 30):
                MODE["mode"] = previous
                MODE["last_error"] = "VRAM did not free after parking the 9B"
                return False, current_state(), "VRAM did not free after parking the 9B"

        if not comfy_is_up():
            if not start_comfy():
                log("ComfyUI failed to start; restoring LLM mode")
                ensure_llm(holder, "comfy start failed, restoring LLM")
                MODE["last_error"] = "ComfyUI failed to start"
                return (
                    False,
                    current_state(),
                    "ComfyUI failed to start; LLM mode restored",
                )

        LAST_COMFY_ACTIVITY["at"] = time.time()
        set_mode("comfy", swap_from=previous, reason=reason)
        return True, current_state(), None


def idle_restore_loop():
    """Background thread: if the GPU has sat in COMFY mode with no
    ComfyUI activity for the idle timeout, hand it back to the LLM.
    Disabled when idle_restore_min is 0."""
    while True:
        time.sleep(60)
        if CFG["idle_restore_min"] <= 0:
            continue
        if MODE["mode"] != "comfy":
            continue
        if comfy_queue_busy():
            continue
        last = LAST_COMFY_ACTIVITY["at"]
        if last and (time.time() - last) > CFG["idle_restore_min"] * 60:
            log("ComfyUI idle for %s min; restoring LLM mode" % CFG["idle_restore_min"])
            ensure_llm("gpu-orchestrator", "idle restore after %s min" % CFG["idle_restore_min"])


# ---------------------------------------------------------------- HTTP API

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, _fmt, *_args):
        pass

    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8", "replace"))
        except ValueError:
            return {}

    def do_GET(self):
        if self.path == "/health":
            st = current_state()
            self._send(200, {"ok": True, "service": "gpu-orchestrator", "mode": st["mode"]})
        elif self.path == "/state":
            self._send(200, current_state())
        elif self.path == "/":
            st = current_state()
            self._send(
                200,
                {
                    "service": "gpu-orchestrator",
                    "mode": st["mode"],
                    "nine_b": st["nine_b"],
                    "twenty_seven_b": st["twenty_seven_b"],
                    "comfy": st["comfy"],
                    "vram_used_mib": st["vram_used_mib"],
                    "vram_total_mib": st["vram_total_mib"],
                    "updated": st["updated"],
                },
            )
        else:
            self._send(404, {"ok": False, "error": "unknown path %s" % self.path})

    def do_POST(self):
        if self.path not in ("/acquire", "/ensure", "/release"):
            self._send(404, {"ok": False, "error": "unknown path %s" % self.path})
            return
        body = self._read_json()
        purpose = str(body.get("purpose", "llm")).lower()
        holder = str(body.get("holder", "unknown"))
        if purpose not in ("llm", "comfy"):
            self._send(400, {"ok": False, "error": "purpose must be llm or comfy"})
            return
        if self.path == "/release":
            if purpose == "comfy":
                LAST_COMFY_ACTIVITY["at"] = time.time()
            if body.get("restore_llm") and purpose == "comfy":
                ok, st, err = ensure_llm(holder, "release asked to restore LLM")
            else:
                ok, st, err = True, current_state(), None
            self._send(200, {"ok": ok, "mode": st["mode"], "state": st, "error": err})
            return
        reason = str(body.get("reason", "acquire %s by %s" % (purpose, holder)))
        if purpose == "llm":
            ok, st, err = ensure_llm(holder, reason)
        else:
            ok, st, err = ensure_comfy(holder, reason)
        self._send(200 if ok else 503, {"ok": ok, "mode": st["mode"], "state": st, "error": err})


# ---------------------------------------------------------------- CLI

def main(argv=None):
    global DRY_RUN
    parser = argparse.ArgumentParser(description="GPU orchestrator (Acer, RTX 2060, 6 GB VRAM)")
    parser.add_argument("--serve", action="store_true", help="run the HTTP daemon (default)")
    parser.add_argument("--state", action="store_true", help="print the GPU state and exit")
    parser.add_argument("--ensure-llm", action="store_true", help="bring the GPU to LLM mode")
    parser.add_argument("--ensure-comfy", action="store_true", help="bring the GPU to COMFY mode")
    parser.add_argument("--port", type=int, default=CFG["port"], help="daemon port (default 11436)")
    parser.add_argument("--dry-run", action="store_true", help="log what would happen, change nothing")
    args = parser.parse_args(argv)

    DRY_RUN = args.dry_run
    if DRY_RUN:
        log("dry-run mode: nothing will be started, stopped, loaded or unloaded")

    if args.state:
        print(json.dumps(current_state(), indent=2, sort_keys=True))
        return 0
    if args.ensure_llm:
        ok, st, err = ensure_llm("cli", "manual --ensure-llm")
        print(json.dumps({"ok": ok, "mode": st["mode"], "error": err}, indent=2))
        return 0 if ok else 1
    if args.ensure_comfy:
        ok, st, err = ensure_comfy("cli", "manual --ensure-comfy")
        print(json.dumps({"ok": ok, "mode": st["mode"], "error": err}, indent=2))
        return 0 if ok else 1

    # Default: serve.
    CFG["port"] = args.port
    server = ThreadingHTTPServer(("127.0.0.1", CFG["port"]), Handler)
    log("gpu-orchestrator listening on 127.0.0.1:%s (mode=%s)" % (CFG["port"], MODE["mode"]))
    threading.Thread(target=idle_restore_loop, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
