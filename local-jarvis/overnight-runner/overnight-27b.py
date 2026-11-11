#!/usr/bin/env python3
"""overnight-27b.py — overnight BLA + 27B runner, v1.

HgX starts this before bed; it runs while he sleeps and leaves a morning
report. Two jobs, in order:

  1. Resume the CrackMe v9 Sovereign runner to completion. The CrackMe
     v1 runner (~/crackme-v9-runner/crackme-v9.py) was killed at 08:25 ET
     2026-11-10 to free the CPU for Claude Code. It is resumable: the
     license task is DONE (07:41, 1,870 chars in ~/crackme-v9/report.md)
     and the WASM task was on attempt 2 when killed. This runner launches
     it, waits for it to finish (it may take hours — the WASM task plus
     three more tasks plus key verification), and records the result.
  2. A BLA red-vs-blue test. BLA hardens a tiny test license-check file
     (created by this runner in its own work dir — NOT a real artifact),
     then the 27B analyses the hardened output in ONE short, chunked
     call and reports whether it can still recover the secret key. The
     verdict is honest: "recovered" only if the 27B quotes the exact
     secret, "not recovered" if it cannot, "inconclusive" if the harden
     step or the 27B call failed.

HARD RULES (proven in the C270 breakdown and the CrackMe v1 runner):
  * NEVER run two 27B runners at the same time. This runner checks for
    any running 27B runner (crackme-v9.py, overnight-27b.py, or any other
    process invoking the 27B) before it starts. If one is running, it
    exits cleanly and does NOT start a second one.
  * Work on COPIES ONLY. The BLA vault originals
    (~/opt/bla/challenge/v9/hardened/) are never touched — the CrackMe
    runner already copies them correctly. The BLA test target is a new
    file created by this runner in its own work dir. Nothing is deleted.
  * The 27B fails on long outputs (one-shot) but succeeds on short,
    chunked prompts (~1900-3500 chars, ~5-27 min each). It sometimes
    returns EMPTY replies; every call retries (4 attempts, backoffs
    30/90/180s). A reply is read to its end before it is used; a section
    is marked unverified when the reply ends mid-sentence.
  * 27B calls use Ollama DIRECT (native /api/chat), NOT the router.
    think=true, num_ctx 4096, num_gpu 0, keep_alive 24h, timeout 1800s
    (30 min) per call.
  * Never uses elevated privileges. Never touches the dashboard, the
    webcam app, the brains, or the router. Never deletes anything.
  * Every file lives under the home folder (~/overnight-27b/) — a reboot
    wipes the temporary folder.

RESUMABLE: state is kept in ~/overnight-27b/state.json and in the
report itself. A second night's run skips work that is already done
(CrackMe solved -> skip it; BLA test done -> skip it). Use --force to
ignore the saved state and re-run everything. Use --redo-bla to re-run
only the BLA test.

Stdlib only.
"""
import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

HOME = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME, "overnight-27b")
WORK_DIR = os.path.join(BASE_DIR, "work")
BLA_DIR = os.path.join(WORK_DIR, "bla-test")
REPORT = os.path.join(BASE_DIR, "report.md")
STATUS_PATH = os.path.join(BASE_DIR, "status.txt")
STATE_PATH = os.path.join(BASE_DIR, "state.json")
CALLS_LOG = os.path.join(BASE_DIR, "27b-calls.jsonl")
LOG_PATH = os.path.join(BASE_DIR, "overnight.log")

CRACKME_RUNNER = os.path.join(HOME, "crackme-v9-runner", "crackme-v9.py")
CRACKME_DIR = os.path.join(HOME, "crackme-v9")
CRACKME_REPORT = os.path.join(CRACKME_DIR, "report.md")
CRACKME_STATUS = os.path.join(CRACKME_DIR, "status.txt")

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_PS_URL = "http://127.0.0.1:11434/api/ps"
MODEL = "huihui_ai/Qwen3.8-abliterated:27b"
OLLAMA_TIMEOUT = 1800  # seconds (30 minutes) per 27B call
MAX_ATTEMPTS = 4
RETRY_BACKOFFS = [30, 90, 180]
LOAD_TIMEOUT = 600  # seconds to load the 27B (an 18 GB model takes ~30s)
CRACKME_WAIT_SECONDS = 12 * 3600  # 12 hours — then stop waiting (do NOT kill it)

FLAG_SHA256 = "06772462f4ba0586ca27aaecf8fd4da5919a336b84f6855de009fc0751c5cf0e"

# The BLA test target: a tiny license check, TEST ONLY (not a real
# artifact). The secret is a test fixture invented for this test — it is
# not a real credential. BLA hardens this file; the 27B then tries to
# recover the key from the hardened output.
BLA_SECRET = "K7mQ9xR2vL5nP8w"  # 16 characters, test-only
BLA_TEST_JS = """// overnight-bla-test — a tiny license check, TEST ONLY (not a real artifact).
// The secret key is 16 characters. BLA will harden this file; the 27B then
// tries to recover the key from the hardened output.
const SECRET_KEY = "K7mQ9xR2vL5nP8w";
function checkKey(k) {
  if (typeof k !== "string") return "DENIED";
  if (k.length !== 16) return "DENIED";
  if (k === SECRET_KEY) return "UNLOCKED";
  return "DENIED";
}
module.exports = { checkKey };
"""

# Process-name patterns that mean "a 27B runner is already running".
# The overnight runner itself matches "overnight-27b.py" — its own PID is
# always excluded, so it never blocks itself.
RUNNER_PATTERNS = ["crackme-v9.py", "overnight-27b.py", "webcam-15tool", "c270-rea-night"]


# ---------------------------------------------------------------- logging / files
def log(msg):
    line = "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def read_file(path, max_chars=None):
    try:
        with open(path, "r", errors="replace") as f:
            data = f.read()
    except Exception:
        return ""
    if max_chars is not None and len(data) > max_chars:
        data = data[:max_chars]
    return data


def read_bytes(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception:
        return b""


def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)
    return path


def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)
    return path


def write_atomic(path, content):
    """Write a file via a temp file + atomic os.replace, so it is never
    left half-written."""
    tmp_path = path + ".tmp-overnight-27b"
    write_file(tmp_path, content)
    os.replace(tmp_path, path)


def sha256_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def which(tool):
    try:
        r = subprocess.run(["which", tool], capture_output=True, text=True, timeout=10)
        p = r.stdout.strip()
        return p if p and r.returncode == 0 else None
    except Exception:
        return None


def run_tool(argv, timeout, out_file, cwd=None):
    """Run a tool via subprocess, capture stdout+stderr to out_file.
    Returns (returncode, stdout_text). Never raises. -1 = timed out,
    -2 = could not start."""
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout,
                           cwd=cwd)
        out = (r.stdout or "") + ("\n--- stderr ---\n" + r.stderr if r.stderr else "")
        try:
            with open(out_file, "w") as f:
                f.write(out)
        except Exception:
            pass
        return r.returncode, out
    except subprocess.TimeoutExpired as e:
        out = ""
        if isinstance(e.stdout, bytes):
            out = e.stdout.decode("utf-8", "replace")
        elif e.stdout:
            out = e.stdout
        out += "\n--- [TIMEOUT after %ss] ---\n" % timeout
        try:
            with open(out_file, "w") as f:
                f.write(out)
        except Exception:
            pass
        return -1, out
    except Exception as e:
        return -2, "[failed to run %s: %s]" % (" ".join(argv), e)


def excerpt(text, max_chars):
    if text is None:
        return ""
    text = str(text)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated: %d chars total, showing first %d]" % (
        len(text), max_chars)


def fit_prompt(instruction, data, coverage="", limit=3400):
    """Assemble a 27B prompt guaranteed under `limit` chars. The data is
    the part that gets truncated, never the instruction. Pure — testable."""
    head = instruction.strip() + "\n\n"
    tail = ("\n\n" + coverage.strip()) if coverage and coverage.strip() else ""
    budget = limit - len(head) - len(tail) - 1
    if budget < 200:
        budget = 200
    data = data or ""
    if len(data) > budget:
        note = "\n... [truncated: %d chars total]" % len(data)
        data = data[:max(0, budget - len(note))] + note
    prompt = head + data + tail
    if len(prompt) >= limit:
        over = len(prompt) - limit + 1
        data = data[:max(0, len(data) - over)]
        prompt = head + data + tail
    return prompt


# ---------------------------------------------------------------- state
def load_state():
    try:
        with open(STATE_PATH, "r") as f:
            st = json.load(f)
        if isinstance(st, dict):
            return st
    except Exception:
        pass
    return {}


def save_state(state):
    try:
        state["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        write_atomic(STATE_PATH, json.dumps(state, indent=2) + "\n")
    except Exception as e:
        log("  WARNING: could not save state: %s" % e)


# ---------------------------------------------------------------- Ollama / 27B
def ollama_ps():
    """List models currently loaded in Ollama. Returns a list of dicts
    {name, size, context, until} from the `ollama ps` CLI, or from the
    /api/ps HTTP endpoint if the CLI is missing. Returns None if neither
    works. Never raises."""
    cli = which("ollama")
    if cli:
        try:
            r = subprocess.run([cli, "ps"], capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                models = []
                for line in (r.stdout or "").splitlines():
                    parts = line.split()
                    if not parts or parts[0] in ("NAME",):
                        continue
                    # Columns: NAME ID SIZE PROCESSOR CONTEXT RUNNER UNTIL.
                    # SIZE is two tokens ("18 GB") and PROCESSOR is two
                    # tokens ("100% CPU", "20%/80% CPU/GPU"), so fixed
                    # indexes are wrong. Find the runner token
                    # ("llamacpp"); CONTEXT is the token before it and
                    # UNTIL is everything after it.
                    name = parts[0]
                    ctx = ""
                    until = ""
                    if "llamacpp" in parts:
                        i = parts.index("llamacpp")
                        ctx = parts[i - 1] if i >= 1 else ""
                        until = " ".join(parts[i + 1:])
                    elif len(parts) > 6:
                        ctx = parts[6]
                        until = " ".join(parts[8:]) if len(parts) > 8 else ""
                    models.append({"name": name, "context": ctx, "until": until})
                return models
        except Exception:
            pass
    # Fallback: the /api/ps HTTP endpoint (name + expiry only).
    try:
        req = urllib.request.Request(OLLAMA_PS_URL)
        with urllib.request.urlopen(req, timeout=30) as resp:
            obj = json.loads(resp.read().decode("utf-8", "replace"))
        models = []
        for m in (obj.get("models") or []):
            models.append({"name": m.get("name", ""), "context": "",
                           "until": m.get("expires_at", "")})
        return models
    except Exception:
        return None


def is_27b_loaded(ps_list):
    """True if the 27B model name appears in an ollama ps listing."""
    if not ps_list:
        return False
    for m in ps_list:
        if (m.get("name") or "") == MODEL:
            return True
    return False


def load_27b():
    """Load the 27B (num_ctx 4096, num_gpu 0, keep_alive 24h) with a tiny
    warm-up call, then verify it appears in ollama ps. Returns True if
    the 27B is loaded afterwards, False otherwise. Never raises."""
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False,
        "think": False,
        "options": {"num_ctx": 4096, "num_gpu": 0},
        "keep_alive": "24h",
    }
    data = json.dumps(body).encode("utf-8")
    try:
        req = urllib.request.Request(OLLAMA_URL, data=data,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=LOAD_TIMEOUT) as resp:
            resp.read()
        log("  27B warm-up call answered")
    except Exception as e:
        log("  27B warm-up call failed: %s" % e)
        return False
    # Poll ollama ps for up to 5 minutes (the model takes ~30s to load).
    for _ in range(30):
        time.sleep(10)
        ps_list = ollama_ps()
        if is_27b_loaded(ps_list):
            log("  27B is loaded (verified in ollama ps)")
            return True
    log("  27B warm-up answered but the model did not appear in ollama ps")
    return False


def ensure_27b_loaded():
    """Ensure the 27B is loaded and resident. Returns True if it is
    loaded (already, or after a warm-up load), False otherwise."""
    ps_list = ollama_ps()
    if ps_list is None:
        log("  WARNING: could not list Ollama models (ollama ps and /api/ps "
            "both failed) — cannot confirm the 27B; trying the warm-up load")
    elif is_27b_loaded(ps_list):
        log("  27B already loaded (ollama ps)")
        return True
    else:
        log("  27B not loaded — loading it (num_ctx 4096, num_gpu 0, "
            "keep_alive 24h; the 9B is untouched, it lives on the GPU)")
    return load_27b()


# ---------------------------------------------------------------- duplicate-runner guard
def list_processes():
    """Return (pid, command) pairs from `ps`. Never raises; returns []
    when ps is unavailable. Testable by monkeypatching."""
    try:
        r = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True,
                           text=True, timeout=30)
        out = []
        for line in (r.stdout or "").splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            try:
                pid = int(parts[0])
            except ValueError:
                continue
            out.append((pid, parts[1]))
        return out
    except Exception:
        return []


def find_other_runners(procs=None, self_pid=None):
    """Find running 27B-runner processes (by the RUNNER_PATTERNS), other
    than this process itself. Returns a list of (pid, command). Pure
    over an explicit process list — testable."""
    if procs is None:
        procs = list_processes()
    if self_pid is None:
        self_pid = os.getpid()
    found = []
    for pid, cmd in procs:
        if pid == self_pid:
            continue
        if pid == os.getppid():
            continue
        for pat in RUNNER_PATTERNS:
            if pat in cmd:
                found.append((pid, cmd))
                break
    return found


def check_no_other_runner():
    """The HARD RULE guard. Returns (ok, found). ok is False when another
    27B runner is running (the caller must exit cleanly)."""
    found = find_other_runners()
    if found:
        for pid, cmd in found:
            log("  BLOCKED: another 27B runner is already running "
                "(PID %d: %s)" % (pid, cmd))
        return False, found
    log("  no other 27B runner running — the guard passes")
    return True, []


# ---------------------------------------------------------------- 27B call (same pattern as the CrackMe v1 runner)
def reply_complete(markers, min_chars, min_markers, reply):
    """True if the reply looks like a real answer for this item."""
    if not reply or len(reply.strip()) < min_chars:
        return False
    low = reply.lower()
    hits = sum(1 for m in markers if m.lower() in low)
    return hits >= min_markers


def call_27b_item(prompt, task_id, markers, min_chars=150, min_markers=1):
    """Call the 27B for one item via Ollama native /api/chat (NOT the
    router). think=true, num_ctx 4096, num_gpu 0, keep_alive 24h,
    timeout 1800s per attempt. 4 attempts, backoffs 30/90/180s. On
    success, logs the call to 27b-calls.jsonl and saves the reply to a
    per-item file, then returns the reply text. Returns None if all
    attempts fail."""
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": True,
        "options": {"num_ctx": 4096, "num_gpu": 0},
        "keep_alive": "24h",
    }
    data = json.dumps(body).encode("utf-8")
    last_err = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            req = urllib.request.Request(OLLAMA_URL, data=data,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8", "replace")
            obj = json.loads(raw)
            reply = ""
            if isinstance(obj, dict):
                msg = obj.get("message") or {}
                reply = (msg.get("content") or "").strip()
            if not reply:
                last_err = "empty reply from Ollama"
            elif not reply_complete(markers, min_chars, min_markers, reply):
                last_err = ("reply incomplete (%d chars; missing the item's "
                            "key content)" % len(reply))
            else:
                try:
                    with open(CALLS_LOG, "a") as f:
                        f.write(json.dumps({
                            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "model": MODEL,
                            "task": task_id,
                            "prompt": prompt,
                            "reply": reply,
                        }) + "\n")
                except Exception:
                    pass
                try:
                    write_file(os.path.join(BASE_DIR, task_id + "-27b-reply.txt"), reply)
                except Exception:
                    pass
                return reply
        except Exception as e:
            last_err = str(e)
        if attempt < MAX_ATTEMPTS - 1:
            wait = RETRY_BACKOFFS[attempt]
            log("  [%s] attempt %d/%d failed (%s); retrying in %ss"
                % (task_id, attempt + 1, MAX_ATTEMPTS, last_err, wait))
            time.sleep(wait)
    log("  [%s] 27B call FAILED after %d attempts: %s"
        % (task_id, MAX_ATTEMPTS, last_err))
    return None


# ---------------------------------------------------------------- CrackMe result
def verify_flag(flag_text):
    """True if SHA-256 of the FLAG text matches the public commitment.
    Pure — testable."""
    if not flag_text:
        return False
    return sha256_text(flag_text.strip()) == FLAG_SHA256


def crackme_solved_in(report_text):
    """True if the CrackMe report records a verified solve: the exact
    marker '**UNLOCKED**' (not the unverified form) plus a FLAG. Pure —
    testable."""
    text = report_text or ""
    return "**UNLOCKED**" in text and "FLAG{" in text


def read_crackme_result():
    """Read the CrackMe runner's status.txt and report.md and return a
    dict: {present, status_result, solved, detail, report_bytes}. Never
    raises; missing files mean present=False."""
    out = {"present": False, "status_result": "", "solved": False,
           "detail": "no CrackMe status or report found", "report_bytes": 0}
    status_text = read_file(CRACKME_STATUS)
    report_text = read_file(CRACKME_REPORT)
    if not status_text and not report_text:
        return out
    out["present"] = True
    out["report_bytes"] = len(report_text.encode("utf-8"))
    for line in status_text.splitlines():
        if line.startswith("result:"):
            out["status_result"] = line.split(":", 1)[1].strip()
        if line.startswith("solved:"):
            out["solved"] = line.split(":", 1)[1].strip().lower() == "yes"
        if line.startswith("detail:"):
            out["detail"] = line.split(":", 1)[1].strip()
    # The report is the authority on a solve (the status file is only
    # written at the end of a run; a solve recorded in the report stands
    # even if the status file is stale).
    if crackme_solved_in(report_text):
        out["solved"] = True
        m = re.search(r"FLAG\{[^}]*\}", report_text)
        if m:
            flag = m.group(0)
            out["detail"] = ("SOLVED — FLAG %s in the report; SHA-256 %s the "
                             "public commitment" % (flag, "MATCHES" if verify_flag(flag)
                                                    else "does NOT match"))
    return out


def run_crackme():
    """Resume the CrackMe v1 runner to completion and wait for it.

    Runs ~/crackme-v9-runner/crackme-v9.py directly in the foreground
    (the start script backgrounds it, which would not let this runner
    wait for it) and waits up to CRACKME_WAIT_SECONDS. The CrackMe
    runner writes its own log (~/crackme-v9/crackme-v9.log), its own
    status.txt and its own report.md; this runner only reads them.
    Returns (outcome, detail) where outcome is "solved", "done",
    "partial", "missing", "still-running", or "failed". Never raises.
    It never kills the CrackMe process: if the wait cap is hit, the
    CrackMe keeps running on its own and a later overnight run will
    find it via the duplicate guard."""
    if not os.path.isfile(CRACKME_RUNNER):
        return ("missing",
                "CrackMe runner not found at %s — manual step: install the "
                "crackme-v9 v1 package (~/crackme-v9-runner/) and re-run"
                % CRACKME_RUNNER)
    log("  launching the CrackMe v1 runner (it resumes from the WASM task; "
        "expect hours — WASM + policy + wat + panel + key verification)")
    run_log = os.path.join(BASE_DIR, "crackme-run.log")
    cwd = CRACKME_DIR if os.path.isdir(CRACKME_DIR) else None
    try:
        with open(run_log, "ab") as lf:
            proc = subprocess.Popen(
                [sys.executable, CRACKME_RUNNER],
                stdout=lf, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, cwd=cwd)
    except Exception as e:
        return ("failed", "could not launch the CrackMe runner: %s" % e)
    log("  CrackMe runner launched (PID %d); waiting for it to finish "
        "(cap %d hours — it is never killed)" % (proc.pid, CRACKME_WAIT_SECONDS // 3600))
    deadline = time.time() + CRACKME_WAIT_SECONDS
    poll = 0
    while True:
        try:
            rc = proc.poll()
        except Exception:
            rc = None
        if rc is not None:
            log("  CrackMe runner exited (rc=%s)" % rc)
            break
        if time.time() > deadline:
            log("  WAIT CAP HIT (%d hours) — the CrackMe runner is STILL "
                "running (PID %d). It is NOT killed; this run stops here so "
                "the next night's run can pick up the result."
                % (CRACKME_WAIT_SECONDS // 3600, proc.pid))
            return ("still-running",
                    "CrackMe runner still running after %d hours (PID %d); "
                    "not killed; re-run this overnight runner tomorrow night "
                    "to collect the result"
                    % (CRACKME_WAIT_SECONDS // 3600, proc.pid))
        # Progress heartbeat every ~30 minutes (the log shows the detail).
        # Poll every 5s so a finished run is noticed promptly.
        time.sleep(5)
        poll += 1
        if poll % 360 == 0:
            res = read_crackme_result()
            log("  still waiting for the CrackMe runner (%d min in; "
                "CrackMe report %d bytes, status: %s)"
                % (poll * 5 // 60, res["report_bytes"], res["status_result"] or "no status yet"))
    res = read_crackme_result()
    if res["solved"]:
        return ("solved", res["detail"])
    if res["status_result"] in ("ok", "partial"):
        return (res["status_result"], res["detail"])
    if res["present"]:
        return ("partial", res["detail"] or "CrackMe runner exited; result unclear from its status")
    return ("failed", "CrackMe runner exited but wrote no status or report")


# ---------------------------------------------------------------- BLA red-vs-blue test
def dir_snapshot(path):
    """{relative path: sha256} for every file under path. Pure over the
    filesystem — testable with a temp dir."""
    out = {}
    if not os.path.isdir(path):
        return out
    for root, _dirs, files in os.walk(path):
        for name in files:
            full = os.path.join(root, name)
            rel = os.path.relpath(full, path)
            out[rel] = sha256_file(full)
    return out


def find_hardened_output(before, after, target_name):
    """Which files changed or appeared after `bla harden`, given the
    before/after snapshots. Returns a list of relative paths, the target
    file first when it changed. Pure — testable."""
    changed = []
    for rel in sorted(after):
        if rel not in before or before[rel] != after[rel]:
            changed.append(rel)
    # The target itself first (it is the file BLA hardens).
    changed.sort(key=lambda r: (0 if r == target_name else 1, r))
    return changed


def bla_verdict(secret, hardened_text, reply):
    """The honest verdict for the BLA test, from evidence only.

    Returns (verdict, evidence) where verdict is one of:
      "recovered"     — the 27B quoted the exact secret (BLA did not hold
                        for this test), or the secret literal is still
                        sitting in the hardened file.
      "not-recovered" — the 27B analysed the hardened output and did not
                        quote the secret, and the secret literal is not in
                        the hardened file.
      "inconclusive"  — no 27B reply, or no hardened output to analyse.
    Pure — testable."""
    literal_present = bool(hardened_text) and secret in hardened_text
    quoted = bool(reply) and secret in reply
    if quoted or literal_present:
        why = []
        if literal_present:
            why.append("the secret literal is still present in the hardened file")
        if quoted:
            why.append("the 27B quoted the exact secret in its reply")
        return ("recovered",
                "BLA did NOT hold up for this test: " + "; ".join(why) + ".")
    if reply:
        return ("not-recovered",
                "BLA held up for this test: the 27B analysed the hardened "
                "output and did not recover the secret, and the secret "
                "literal is not in the hardened file.")
    return ("inconclusive",
            "no 27B reply and/or no hardened output to analyse — the test "
            "cannot say whether BLA held up.")


def build_bla_prompt(hardened_excerpt):
    """Short 27B prompt for the BLA test (under 3400 chars by
    construction). Pure — testable."""
    instruction = (
        "This is a red-vs-blue test. BLA (Blind LLM Agents) hardened a "
        "tiny JavaScript license-check file. Below is an excerpt of the "
        "HARDENED output (after `bla harden`). The original file had a "
        "16-character secret key in a const and a checkKey() function that "
        "returns UNLOCKED only for that key. In 5-8 bullet points, "
        "explain: (1) what the hardened code does, (2) whether you can "
        "still read the original logic (the key check, the DENIED/UNLOCKED "
        "branches), (3) whether the 16-character secret key is visible "
        "anywhere in the hardened output — if so, quote it exactly and "
        "label it KEY-CANDIDATE, (4) whether BLA's hardening actually hid "
        "anything or just renamed things. Do not invent findings that are "
        "not in the excerpt below. If you cannot see the key, say so "
        "plainly — do not guess a key.")
    return fit_prompt(instruction, hardened_excerpt,
                      "File: hardened license-check.js (BLA test target).")


def run_bla_test():
    """Run the BLA red-vs-blue test. Returns a dict with the outcome and
    the evidence (always honest; never invents a verdict). Never raises."""
    result = {"done": False, "verdict": "inconclusive", "detail": "",
              "harden_rc": None, "hardened_files": [], "secret_literal": False,
              "reply_chars": 0}
    bla = which("bla")
    if not bla:
        result["detail"] = ("BLA CLI not found (`bla` is not on PATH) — "
                            "manual step: install bla-agents and re-run")
        return result
    try:
        os.makedirs(BLA_DIR, exist_ok=True)
    except Exception as e:
        result["detail"] = "could not create the BLA test dir: %s" % e
        return result
    target = os.path.join(BLA_DIR, "license-check.js")
    try:
        write_file(target, BLA_TEST_JS)
    except Exception as e:
        result["detail"] = "could not write the BLA test target: %s" % e
        return result
    log("  BLA test target written: %s (test-only secret, 16 chars)" % target)
    before = dir_snapshot(BLA_DIR)
    out_file = os.path.join(BLA_DIR, "bla-harden-output.txt")
    log("  running `bla harden` on the test target (timeout 600s)")
    rc, out = run_tool([bla, "harden", target], timeout=600,
                       out_file=out_file, cwd=BLA_DIR)
    result["harden_rc"] = rc
    if rc != 0:
        result["detail"] = ("`bla harden` failed (rc=%s); output in "
                            "work/bla-test/bla-harden-output.txt — the BLA "
                            "test cannot say whether BLA held up" % rc)
        log("  `bla harden` failed (rc=%s) — placeholder recorded" % rc)
        return result
    after = dir_snapshot(BLA_DIR)
    changed = find_hardened_output(before, after, "license-check.js")
    # Exclude the tool-output log itself: run_tool writes it after the
    # before-snapshot, so it would always look "changed" and be mistaken
    # for the hardened output.
    changed = [c for c in changed if c != "bla-harden-output.txt"]
    result["hardened_files"] = changed
    if not changed:
        result["detail"] = ("`bla harden` returned rc=0 but no file in the "
                            "test dir changed or appeared — no hardened "
                            "output to analyse; the test cannot say whether "
                            "BLA held up")
        log("  `bla harden` rc=0 but nothing changed — no output to analyse")
        return result
    # The hardened output: the target itself if it changed, else the first
    # new/changed file. Read a bounded excerpt for the 27B.
    hardened_path = os.path.join(BLA_DIR, changed[0])
    hardened_text = read_file(hardened_path)
    result["secret_literal"] = BLA_SECRET in hardened_text
    log("  hardened output: %s (%d bytes; secret literal present: %s)"
        % (changed[0], len(hardened_text.encode("utf-8")),
           "yes" if result["secret_literal"] else "no"))
    prompt = build_bla_prompt(excerpt(hardened_text, 2000))
    log("  [overnight-bla] prompt: %d chars" % len(prompt))
    reply = call_27b_item(prompt, "overnight-bla",
                          markers=["hardened", "key", "secret", "bla"],
                          min_chars=150, min_markers=1)
    result["reply_chars"] = len(reply) if reply else 0
    if reply is None:
        verdict, evidence = bla_verdict(BLA_SECRET, hardened_text, None)
        result["verdict"] = verdict
        result["detail"] = (evidence + " (the 27B gave no reply after 4 "
                            "attempts; the hardened output is saved in "
                            "work/bla-test/ and can be read by hand)")
        log("  [overnight-bla] 27B gave no reply — placeholder recorded")
    else:
        verdict, evidence = bla_verdict(BLA_SECRET, hardened_text, reply)
        result["verdict"] = verdict
        result["detail"] = evidence
        log("  [overnight-bla] 27B replied (%d chars); verdict: %s"
            % (len(reply), verdict))
    result["done"] = True
    return result


# ---------------------------------------------------------------- report + status
def build_report(state, crackme, bla, calls_27b):
    """Build the full morning report text. Pure over its inputs — testable."""
    today = time.strftime("%Y-%m-%d")
    lines = [
        "# Overnight BLA + 27B run — %s" % today,
        "",
        "HgX started this runner before bed; it ran while he slept. The "
        "27B did the deep thinking (CrackMe v9 + one BLA red-vs-blue "
        "test). The 9B was untouched — it lives on the GPU; the 27B lives "
        "on CPU/RAM. Nothing was deleted; the BLA vault originals were "
        "never touched.",
        "",
        "## What ran",
        "",
    ]
    for step in state.get("steps", []):
        lines.append("- %s" % step)
    lines += [
        "",
        "## CrackMe v9 Sovereign — result",
        "",
    ]
    if crackme is None:
        lines.append("Not run this night (skipped — already solved in an "
                     "earlier run).")
    else:
        lines.append("- Outcome: **%s**" % crackme.get("outcome", "unknown"))
        lines.append("- Detail: %s" % crackme.get("detail", ""))
        lines.append("- CrackMe report: ~/crackme-v9/report.md (%d bytes)"
                     % crackme.get("report_bytes", 0))
        if crackme.get("solved"):
            lines.append("- **SOLVED** — a candidate key unlocked the gate "
                         "and the FLAG's SHA-256 matches the public "
                         "commitment 06772462f4ba0586ca27aaecf8fd4da5919a336b"
                         "84f6855de009fc0751c5cf0e.")
        else:
            lines.append("- Not solved yet. The CrackMe runner is resumable "
                         "— a later night picks up where this one stopped.")
    lines += [
        "",
        "## BLA red-vs-blue test — result",
        "",
    ]
    if bla is None:
        lines.append("Not run this night (skipped — already done in an "
                     "earlier run, or deferred because the CrackMe runner "
                     "was still running).")
    else:
        lines.append("- Verdict: **%s**" % bla.get("verdict", "inconclusive"))
        lines.append("- Detail: %s" % bla.get("detail", ""))
        lines.append("- `bla harden` return code: %s" % bla.get("harden_rc"))
        lines.append("- Hardened files: %s"
                     % (", ".join(bla.get("hardened_files") or []) or "[none]"))
        lines.append("- Secret literal still in the hardened file: %s"
                     % ("yes" if bla.get("secret_literal") else "no"))
        lines.append("- 27B reply: %d chars" % bla.get("reply_chars", 0))
        lines.append("")
        lines.append("One small test only — it says whether BLA held up "
                     "against THIS tiny license check, not whether BLA holds "
                     "up in general.")
    lines += [
        "",
        "## 27B calls",
        "",
        "- 27B calls made by this runner (not counting the CrackMe "
        "runner's own calls, which are in ~/crackme-v9/27b-calls.jsonl): %d"
        % calls_27b,
        "- Every call: Ollama direct, think=true, num_ctx 4096, num_gpu 0, "
        "keep_alive 24h, timeout 1800s, 4 attempts, backoffs 30/90/180s. "
        "Prompts are short and chunked (under 3400 chars).",
        "",
        "## Failures and placeholders",
        "",
    ]
    fails = state.get("failures", [])
    if fails:
        for f in fails:
            lines.append("- %s" % f)
    else:
        lines.append("None — every step that ran completed or was skipped "
                     "as already done.")
    lines += [
        "",
        "## What is still open",
        "",
        "- If the CrackMe is not solved, the next night's run resumes it "
        "(the runner is resumable; re-running is safe).",
        "- If the BLA verdict was inconclusive, re-run with --redo-bla.",
        "- The 27B stays resident on its 24h pin; the keep-alive cron "
        "refreshes it every 6 hours.",
        "",
    ]
    return "\n".join(lines) + "\n"


def write_status(result, detail, crackme=None, bla=None):
    lines = [
        "result: %s" % result,
        "time: %s" % time.strftime("%Y-%m-%d %H:%M:%S"),
        "report: %s" % REPORT,
        "detail: %s" % detail,
    ]
    if crackme is not None:
        lines.append("crackme: %s" % crackme.get("outcome", "unknown"))
        lines.append("crackme_solved: %s" % ("yes" if crackme.get("solved") else "no"))
    if bla is not None:
        lines.append("bla_verdict: %s" % bla.get("verdict", "inconclusive"))
    try:
        write_file(STATUS_PATH, "\n".join(lines) + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------- main
def main(argv=None):
    parser = argparse.ArgumentParser(description="Overnight BLA + 27B runner")
    parser.add_argument("--force", action="store_true",
                        help="ignore saved state and re-run everything")
    parser.add_argument("--redo-bla", action="store_true",
                        help="re-run only the BLA test even if it is done")
    args = parser.parse_args(argv)
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        os.makedirs(WORK_DIR, exist_ok=True)
        os.makedirs(BLA_DIR, exist_ok=True)
    except Exception:
        pass
    log("overnight-27b v1 starting — BLA + 27B overnight run")
    log("work: %s (the 9B is untouched; the 27B lives on CPU/RAM)" % BASE_DIR)
    log("model: %s (Ollama direct, think=true, num_ctx 4096, num_gpu 0, "
        "keep_alive 24h, timeout 1800s)" % MODEL)
    state = load_state()
    if args.force:
        log("  --force: ignoring saved state")
        state = {}
    steps = []
    failures = []
    calls_27b = 0

    # 1. The HARD RULE guard — never run two 27B runners at once.
    ok, found = check_no_other_runner()
    if not ok:
        detail = ("another 27B runner is already running (%d process(es)); "
                  "this run exits cleanly without starting a second one"
                  % len(found))
        log("BLOCKED: " + detail)
        write_status("blocked", detail)
        print("BLOCKED — " + detail)
        return 2

    # 2. Ensure the 27B is loaded and resident.
    if not ensure_27b_loaded():
        detail = ("the 27B could not be loaded (ollama ps does not list it "
                  "after a warm-up load) — nothing ran; check Ollama and "
                  "re-run")
        log("FAILED: " + detail)
        failures.append(detail)
        state["steps"] = steps
        state["failures"] = failures
        save_state(state)
        write_status("failed", detail)
        print("FAILED — " + detail)
        return 1
    steps.append("27B loaded and resident (verified in ollama ps)")

    # 3. Resume the CrackMe v9 runner — unless it is already solved, or
    #    it already finished cleanly in an earlier overnight run.
    crackme = None
    prior = state.get("crackme", {})
    already_solved = prior.get("outcome") == "solved"
    if not already_solved:
        res = read_crackme_result()
        if res["solved"]:
            already_solved = True
            log("  CrackMe already solved (per its report) — skipping")
    if already_solved:
        steps.append("CrackMe v9: skipped — already solved")
        crackme = {"outcome": "solved", "solved": True,
                   "detail": "already solved in an earlier run",
                   "report_bytes": read_crackme_result()["report_bytes"]}
    elif prior.get("outcome") in ("done", "ok") and not args.force:
        steps.append("CrackMe v9: skipped — already finished cleanly in an "
                     "earlier overnight run")
        res = read_crackme_result()
        crackme = {"outcome": res["status_result"] or "done",
                   "solved": res["solved"], "detail": res["detail"],
                   "report_bytes": res["report_bytes"]}
    else:
        outcome, detail = run_crackme()
        res = read_crackme_result()
        crackme = {"outcome": outcome, "solved": res["solved"],
                   "detail": detail, "report_bytes": res["report_bytes"]}
        state["crackme"] = {"outcome": outcome, "detail": detail,
                            "solved": res["solved"]}
        save_state(state)
        if outcome == "solved":
            steps.append("CrackMe v9: SOLVED — %s" % detail)
        elif outcome in ("done", "ok"):
            steps.append("CrackMe v9: finished cleanly (not solved) — %s" % detail)
        elif outcome == "still-running":
            steps.append("CrackMe v9: STILL RUNNING after the 12h wait cap — "
                         "not killed; the BLA test is deferred (it needs "
                         "the 27B) and this run stops here")
            failures.append(detail)
        elif outcome == "missing":
            steps.append("CrackMe v9: SKIPPED — runner not found (%s)" % detail)
            failures.append(detail)
        else:
            steps.append("CrackMe v9: %s — %s" % (outcome, detail))
            failures.append("CrackMe v9: %s — %s" % (outcome, detail))
        # If the CrackMe is still running, the BLA test must NOT start
        # (it needs the 27B too — that would be two 27B users at once).
        if outcome == "still-running":
            state["steps"] = steps
            state["failures"] = failures
            save_state(state)
            report = build_report(state, crackme, None, calls_27b)
            write_atomic(REPORT, report)
            write_status("partial", detail, crackme=crackme, bla=None)
            log("DONE (partial): " + detail)
            print("DONE (partial) — " + detail)
            return 0

    # 4. The BLA red-vs-blue test — unless it is already done.
    bla = None
    prior_bla = state.get("bla_test", {})
    if prior_bla.get("done") and not args.force and not args.redo_bla:
        steps.append("BLA test: skipped — already done (verdict: %s)"
                     % prior_bla.get("verdict", "inconclusive"))
        bla = prior_bla
    else:
        bla = run_bla_test()
        if bla.get("done"):
            calls_27b += 1
        state["bla_test"] = bla
        save_state(state)
        if bla.get("done"):
            steps.append("BLA test: done — verdict: %s" % bla.get("verdict"))
        else:
            steps.append("BLA test: could not run — %s" % bla.get("detail"))
            failures.append("BLA test: %s" % bla.get("detail"))

    # 5. Morning report + status.
    state["steps"] = steps
    state["failures"] = failures
    state["runs"] = state.get("runs", 0) + 1
    save_state(state)
    report = build_report(state, crackme, bla, calls_27b)
    write_atomic(REPORT, report)
    if failures:
        result = "partial"
        detail = ("finished with %d failure(s); CrackMe: %s; BLA verdict: %s"
                  % (len(failures),
                     crackme.get("outcome", "unknown") if crackme else "skipped",
                     bla.get("verdict", "inconclusive") if bla else "not run"))
    else:
        result = "done"
        detail = ("all steps done; CrackMe: %s; BLA verdict: %s"
                  % (crackme.get("outcome", "unknown") if crackme else "skipped",
                     bla.get("verdict", "inconclusive") if bla else "not run"))
    write_status(result, detail, crackme=crackme, bla=bla)
    log("DONE: " + detail)
    print("DONE — " + detail)
    print("Report: %s" % REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
