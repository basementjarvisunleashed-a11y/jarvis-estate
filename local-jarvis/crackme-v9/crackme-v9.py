#!/usr/bin/env python3
"""crackme-v9.py — CrackMe v9 Sovereign REA runner, v1: recon + first-pass analysis.

Target: the BLA-hardened CrackMe v9 Sovereign vault (BLA 3.0, bankrupt
intensity, weaveScore 100). The vault is five files in
~/opt/bla/challenge/v9/hardened/ — license.cjs (201,111 bytes),
panel.html (126,216), policy.py (41,561), core.wasm.gz (21,393, about
6.88 MB raw), seal.json (569). All five SHA-256 digests were verified
against SEAL.json before this runner was built, and this runner
re-verifies them before it copies anything.

Goal: find the 16-character key. The unlock lives in the WASM (SHA-256
KDF + ARX + commitment layout, per DESIGN.md). Verify a candidate with
`node license.cjs <16-char-key>` in the WORKING COPY (unlocks the FLAG
on success, uniform DENIED otherwise, hard-fails on any tamper). The
public flag commitment is SHA-256(FLAG{...}) =
06772462f4ba0586ca27aaecf8fd4da5919a336b84f6855de009fc0751c5cf0e.

HARD RULES (proven in the C270 breakdown — do not violate):
  * Work on COPIES ONLY. The runner copies the five vault files to
    ~/crackme-v9/work/ and gunzips core.wasm.gz there. It NEVER writes
    to ~/opt/bla/challenge/v9/hardened/. The originals are read-only
    input. The license.cjs integrity self-check pins the sidecars, so
    any tamper hard-fails the gate — which is exactly why the runner
    verifies digests before and after every copy.
  * One 27B call per task, one section appended per call. Prompts are
    SHORT and CHUNKED (under 3500 chars each) — the 27B fails on long
    outputs (one-shot) but succeeds reliably on short, chunked prompts.
    It sometimes returns EMPTY replies; every call retries (4 attempts,
    backoffs 30/90/180s). A reply is read to its end before it is
    appended; a section is marked unverified when the reply ends
    mid-sentence or contradicts its own counts.
  * Calls use Ollama DIRECT (native /api/chat), NOT the router.
    think=true, num_ctx 4096, num_gpu 0, keep_alive 24h, timeout 1800s
    (30 min) per call.
  * Never run two 27B runners at the same time. No other 27B runner is
    running while this one runs.
  * Every capture, image, and test file lives under the home folder
    (~/crackme-v9/) — a reboot wipes the temporary folder.
  * Never uses elevated privileges. Never touches the dashboard, the
    webcam app, the brains, or the router. Never deletes anything.

WHAT v1 DOES (recon + first-pass analysis — NOT the full crack):
  1. Setup: verify the vault source digests, copy the five files to
     ~/crackme-v9/work/, gunzip core.wasm.gz -> core.wasm there, verify
     the gunzipped digest (b38e5d6b...) and size (6,883,604).
  2. Recon: file types, sizes, line counts; a pure-Python WASM section
     parser (exports, function/code counts, section sizes — no external
     tool needed); wabt wasm-objdump / wasm2wat if present (checked
     first, never assumed); a Node.js export cross-check if Node is
     present; structure excerpts from license.cjs, policy.py, panel.html
     (function names, key-check windows — the 201 KB license.cjs is
     NEVER fed whole to the 27B).
  3. Tool applicability: names all 15 REA tools and says which apply to
     a JS/WASM/Python vault and which do not, with a reason for each.
  4. Five 27B analysis calls (one per task, short prompts): license.cjs
     (the gate), WASM exports + seal.json (the unlock entry points),
     policy.py (the ledger), the WASM disassembly excerpt (only if
     wasm2wat worked), panel.html (the UI). Each finding is appended to
     ~/crackme-v9/report.md IMMEDIATELY after it lands (temp file +
     atomic replace), or an honest placeholder naming the tool and the
     reason when it fails.
  5. Candidate keys: if a 27B reply proposes a 16-character key
     (labelled KEY-CANDIDATE), the runner verifies at most 3 candidates
     with `node license.cjs <key>` in the WORKING COPY and records the
     result (UNLOCKED + FLAG, or DENIED). It does NOT brute-force and
     does NOT search the key space in v1 — that is a later round, only
     if the analysis points to a searchable space.
  6. Summary: what v1 found, what is still unknown, what the next
     round should do.

Resumable: re-running skips any 27B task whose section is already in
the report, and skips copying any working file whose digest already
matches. Expected total run: roughly 30-90 minutes (five short 27B
calls at ~5-27 min each, plus the WASM disassembly if wabt is present).

Stdlib only.
"""
import gzip
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import urllib.request

HOME = os.path.expanduser("~")
VAULT_DIR = os.path.join(HOME, "opt/bla/challenge/v9/hardened")
BASE_DIR = os.path.join(HOME, "crackme-v9")
WORK_DIR = os.path.join(BASE_DIR, "work")
REPORT = os.path.join(BASE_DIR, "report.md")
CALLS_LOG = os.path.join(BASE_DIR, "27b-calls.jsonl")
LOG_PATH = os.path.join(BASE_DIR, "crackme-v9.log")
STATUS_PATH = os.path.join(BASE_DIR, "status.txt")

# Expected digests from SEAL.json (verified by the recon run on
# 2026-11-10: all five matched exactly). The core.wasm digest is the
# raw (gunzipped) one from SEAL.json's artifacts.core.wasm entry.
EXPECTED = {
    "license.cjs": "a56604751015fe59c7a034dc30799c9286c45d0ae00b1f9df8e4ddc42457fec0",
    "panel.html": "b3e6787d8029cdb6caf4e500e2333648729390c967f981d56f279d77e7c58bbf",
    "policy.py": "a3ffe58c2dc7c1ac7d7f0605cfc1fad1fa1b20f83d4a42710051262c7a2c7e1c",
    "core.wasm.gz": "67aacf5c86c29572df02f142804fd6a784372705f4bc20d90f67942aa903dd96",
    "seal.json": "cbbd7a672a96170a95682d574fa6f31bfa1eb5e32ee88d2651bca471e5455085",
}
EXPECTED_CORE_WASM = "b38e5d6b7526ca515ac196f6da6ce76d7f1c8261eab9d599f1a466152371b44c"
EXPECTED_CORE_WASM_BYTES = 6883604
FLAG_SHA256 = "06772462f4ba0586ca27aaecf8fd4da5919a336b84f6855de009fc0751c5cf0e"
VAULT_FILES = ["license.cjs", "panel.html", "policy.py", "core.wasm.gz", "seal.json"]

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "huihui_ai/Qwen3.8-abliterated:27b"
OLLAMA_TIMEOUT = 1800  # seconds (30 minutes) — safety net; a short reply should land in ~5-10 min
MAX_ATTEMPTS = 4
RETRY_BACKOFFS = [30, 90, 180]

# The Node.js export cross-check script (written to work/ by the runner,
# then run with `node`). It compiles the WASM module and prints its
# exports/imports as JSON. Kept tiny on purpose.
NODE_EXPORTS_SCRIPT = """const fs = require("node:fs");
const bytes = fs.readFileSync(process.argv[2]);
const mod = new WebAssembly.Module(bytes);
console.log(JSON.stringify({
  exports: WebAssembly.Module.exports(mod),
  imports: WebAssembly.Module.imports(mod)
}, null, 2));
"""

# ---------------------------------------------------------------- logging
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

def write_report_atomic(report_path, content):
    """Write the full report via a temp file + atomic os.replace, so the
    file is never left half-written (a crash mid-write cannot corrupt it)."""
    tmp_path = report_path + ".tmp-crackme-v9"
    write_file(tmp_path, content)
    os.replace(tmp_path, report_path)

def sha256_file(path):
    """SHA-256 hex digest of a file, or None if it cannot be read."""
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
    """Return the path of a tool, or None if not found."""
    try:
        r = subprocess.run(["which", tool], capture_output=True, text=True, timeout=10)
        p = r.stdout.strip()
        return p if p and r.returncode == 0 else None
    except Exception:
        return None

def run_tool(argv, timeout, out_file, cwd=None):
    """Run a tool via subprocess, capture stdout+stderr to out_file.
    Returns (returncode, stdout_text). Never raises on tool failure.
    returncode -1 means the tool timed out; -2 means it could not start."""
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
        out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
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
    """Truncate text to a char budget (keeps the 27B input small)."""
    if text is None:
        return ""
    text = str(text)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated: %d chars total, showing first %d]" % (
        len(text), max_chars)

def fit_prompt(instruction, data, coverage="", limit=3400):
    """Assemble a 27B prompt that is guaranteed under `limit` chars.

    instruction + data (capped to fit) + coverage line. The data is the
    part that gets truncated, never the instruction. The final guard
    hard-trims the data if anything still overflows, so the returned
    prompt is always strictly under `limit`. Pure — testable."""
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


# ---------------------------------------------------------------- WASM parser (pure Python, stdlib only)
# WASM binary layout: magic b"\x00asm" + version (4 bytes), then
# sections: id (1 byte) + size (LEB128) + payload. Section ids:
# 0 Custom, 1 Type, 2 Import, 3 Function, 4 Table, 5 Memory, 6 Global,
# 7 Export, 8 Start, 9 Element, 10 Code, 11 Data, 12 DataCount.
# Export entry: name (LEB128 length + UTF-8) + kind (1 byte:
# 0 func, 1 table, 2 mem, 3 global) + index (LEB128).
# This parser needs no external tool — it always works on the Acer.
WASM_KINDS = {0: "func", 1: "table", 2: "mem", 3: "global"}

def _read_uleb(data, pos):
    """Read one unsigned LEB128 from data at pos. Returns (value, new_pos).
    Raises ValueError on truncation or an over-long encoding."""
    result = 0
    shift = 0
    start = pos
    while True:
        if pos >= len(data):
            raise ValueError("truncated LEB128 at offset %d" % start)
        b = data[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
        if shift > 63:
            raise ValueError("LEB128 too long at offset %d" % start)
    return result, pos

def parse_wasm(data):
    """Parse a WASM binary (bytes) into a summary dict.

    Returns {"valid": bool, "error": str-or-None,
             "exports": [(name, kind, index), ...],
             "function_count": int, "code_count": int,
             "import_count": int, "imported_funcs": int,
             "sections": [(id, size), ...], "bytes": int}.
    Never raises — a truncated or invalid binary returns valid=False
    with the error named. Pure — testable with a fake WASM binary."""
    out = {"valid": False, "error": None, "exports": [],
           "function_count": 0, "code_count": 0,
           "import_count": 0, "imported_funcs": 0,
           "sections": [], "bytes": len(data) if data else 0}
    if not data or len(data) < 8:
        out["error"] = "too short for a WASM module (%d bytes)" % (len(data) if data else 0)
        return out
    if data[0:4] != b"\x00asm":
        out["error"] = "bad magic (not \\0asm)"
        return out
    if data[4:8] != b"\x01\x00\x00\x00":
        out["error"] = "unsupported WASM version %s" % data[4:8].hex()
        return out
    pos = 8
    try:
        while pos < len(data):
            sec_id = data[pos]
            pos += 1
            sec_size, pos = _read_uleb(data, pos)
            if pos + sec_size > len(data):
                out["error"] = ("section %d truncated (claims %d bytes, "
                                "%d remain)" % (sec_id, sec_size, len(data) - pos))
                return out
            payload = data[pos:pos + sec_size]
            out["sections"].append((sec_id, sec_size))
            if sec_id == 2:  # Import
                p = 0
                count, p = _read_uleb(payload, p)
                out["import_count"] = count
                for _ in range(count):
                    mlen, p = _read_uleb(payload, p)
                    p += mlen
                    flen, p = _read_uleb(payload, p)
                    p += flen
                    kind = payload[p]
                    p += 1
                    if kind == 0:
                        out["imported_funcs"] += 1
                        _t, p = _read_uleb(payload, p)
                    elif kind == 1:
                        p += 1  # table element type
                        _lim, p = _read_uleb(payload, p)
                        if _lim & 0x01:
                            _mx, p = _read_uleb(payload, p)
                    elif kind == 2:
                        _lim, p = _read_uleb(payload, p)
                        if _lim & 0x01:
                            _mx, p = _read_uleb(payload, p)
                    elif kind == 3:
                        p += 2  # value type + mutability
            elif sec_id == 3:  # Function
                p = 0
                count, p = _read_uleb(payload, p)
                out["function_count"] = count
            elif sec_id == 7:  # Export
                p = 0
                count, p = _read_uleb(payload, p)
                for _ in range(count):
                    nlen, p = _read_uleb(payload, p)
                    name = payload[p:p + nlen].decode("utf-8", "replace")
                    p += nlen
                    kind = payload[p]
                    p += 1
                    idx, p = _read_uleb(payload, p)
                    out["exports"].append((name, WASM_KINDS.get(kind, "kind%d" % kind), idx))
            elif sec_id == 10:  # Code
                p = 0
                count, p = _read_uleb(payload, p)
                out["code_count"] = count
            pos += sec_size
    except (ValueError, IndexError) as e:
        out["error"] = "parse failed at offset %d: %s" % (pos, e)
        return out
    out["valid"] = True
    return out

def wasm_summary_text(parsed):
    """One-paragraph text summary of a parse_wasm result, for the report
    and for the 27B prompt. Pure — testable."""
    if not parsed.get("valid"):
        return "WASM parse FAILED: %s" % (parsed.get("error") or "unknown error")
    ex = parsed["exports"]
    ex_line = ", ".join("%s (%s, #%d)" % (n, k, i) for n, k, i in ex[:20])
    if len(ex) > 20:
        ex_line += ", ... (%d more)" % (len(ex) - 20)
    total_funcs = parsed["imported_funcs"] + parsed["function_count"]
    return ("WASM: %d bytes, %d sections, %d imports (%d imported "
            "functions), %d declared functions, %d code bodies, %d total "
            "functions. Exports (%d): %s."
            % (parsed["bytes"], len(parsed["sections"]),
               parsed["import_count"], parsed["imported_funcs"],
               parsed["function_count"], parsed["code_count"],
               total_funcs, len(ex), ex_line or "[none]"))

# ---------------------------------------------------------------- excerpt extractors (pure, testable)
def js_function_names(text, cap=40):
    """Function / binding names found in JS text. Regex-based; returns a
    deduplicated list in first-seen order, capped. Pure — testable."""
    names = []
    seen = set()
    patterns = [
        r"function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(",
        r"(?:var|let|const)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*function\s*\(",
        r"(?:var|let|const)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",
        r"([A-Za-z_$][A-Za-z0-9_$]*)\s*:\s*function\s*\(",
        r"([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*\(\)\s*=>",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text or ""):
            n = m.group(1)
            if n not in seen:
                seen.add(n)
                names.append(n)
            if len(names) >= cap:
                return names
    return names

def py_defs(text, cap=40):
    """Top-level and method def/class names in Python text. Pure — testable."""
    names = []
    seen = set()
    for m in re.finditer(r"(?m)^(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)", text or ""):
        n = m.group(1)
        if n not in seen:
            seen.add(n)
            names.append(n)
    for m in re.finditer(r"(?m)^\s+def\s+([A-Za-z_][A-Za-z0-9_]*)", text or ""):
        n = m.group(1)
        if n not in seen:
            seen.add(n)
            names.append(n)
        if len(names) >= cap:
            break
    return names[:cap]

def find_window(text, markers, before=25, after=25, budget=1500):
    """Find the first line matching any marker (in priority order) and
    return a window of lines around it, capped at `budget` chars.

    Returns (window_text, marker_found_or_None, line_number_or_-1).
    Markers are matched as plain substrings, case-sensitive first, then
    case-insensitive. Pure — testable."""
    if not text:
        return "", None, -1
    lines = text.splitlines()
    for marker in markers:
        for i, line in enumerate(lines):
            if marker in line:
                start = max(0, i - before)
                end = min(len(lines), i + after + 1)
                window = "\n".join(lines[start:end])
                return excerpt(window, budget), marker, i + 1
    for marker in markers:
        low = marker.lower()
        for i, line in enumerate(lines):
            if low in line.lower():
                start = max(0, i - before)
                end = min(len(lines), i + after + 1)
                window = "\n".join(lines[start:end])
                return excerpt(window, budget), marker, i + 1
    return "", None, -1

def interesting_strings(text, keywords, cap=10):
    """Quoted string literals (6-80 chars) containing any keyword.
    Pure — testable."""
    out = []
    seen = set()
    for m in re.finditer(r'"([^"\n]{6,80})"', text or ""):
        s = m.group(1)
        low = s.lower()
        if any(k.lower() in low for k in keywords):
            if s not in seen:
                seen.add(s)
                out.append(s)
            if len(out) >= cap:
                break
    return out

def html_structure(text):
    """Title, script-tag count, and JS function names in an HTML file.
    Pure — testable."""
    if not text:
        return {"title": "", "script_tags": 0, "functions": []}
    m = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
    title = (m.group(1).strip() if m else "")
    scripts = len(re.findall(r"<script", text, re.I))
    return {"title": title, "script_tags": scripts,
            "functions": js_function_names(text, cap=40)}

def extract_wat_excerpt(wat_text, export_names, budget=2000):
    """A disassembly excerpt from WAT text, centred on the first export
    name that appears in it. Returns (excerpt, matched_name_or_None).
    Falls back to the first `budget` chars when no export name is found
    (obfuscated exports). Pure — testable."""
    if not wat_text:
        return "", None
    for name in export_names or []:
        if name and name in wat_text:
            idx = wat_text.find(name)
            start = max(0, idx - 300)
            end = min(len(wat_text), start + budget)
            return wat_text[start:end], name
    return wat_text[:budget], None


# ---------------------------------------------------------------- 27B call
def reply_complete(markers, min_chars, min_markers, reply):
    """True if the reply looks like a real answer for this item.

    Requires a minimum length and at least `min_markers` of the given key
    markers (case-insensitive). A reply that is empty, a fragment, or about
    something else counts as failed and is retried."""
    if not reply or len(reply.strip()) < min_chars:
        return False
    low = reply.lower()
    hits = sum(1 for m in markers if m.lower() in low)
    return hits >= min_markers

def call_27b_item(prompt, task_id, markers, min_chars=150, min_markers=1):
    """Call the 27B for one crackme-v9 item via Ollama native /api/chat
    (NOT the router). Timeout is 1800s (30 min) per attempt — a short
    reply should land in ~5-10 min; 30 min is the safety net. 4 attempts
    per item, backoffs 30/90/180s. A reply that is received but incomplete
    (missing the item's key content) counts as a failed attempt and is
    retried. On success, logs the call to 27b-calls.jsonl (response
    capture) and saves the reply to a per-item file, then returns the
    reply text. Returns None if all attempts fail."""
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

# ---------------------------------------------------------------- prompt builders (all under 3500 chars by construction)
KEY_NOTE = ("If a 16-character key is visible in the excerpts below, quote "
            "it exactly and label it KEY-CANDIDATE.")

def build_license_prompt(func_names, key_window, key_marker, key_line, size_bytes):
    """Short 27B prompt for the license.cjs gate analysis. Pure — testable."""
    instruction = (
        "This is CrackMe v9 Sovereign, a BLA-hardened entitlement gate "
        "(license.cjs, %d bytes, BLA 3.0 bankrupt hardening). The "
        "16-character key is checked here and the unlock lives in a WASM "
        "module (core.wasm). Below are the function names found in "
        "license.cjs and an excerpt around the key check (matched on %s, "
        "line %d), plus the integrity self-check that pins the sidecars "
        "(it SHA-256s core.wasm, panel.html, policy.py plus a seed and "
        "throws 'integrity binding mismatch' on tamper). In 5-8 bullet "
        "points, explain: (1) where and how the 16-character key is "
        "checked (length and format), (2) how license.cjs calls into the "
        "WASM (which export, what arguments), (3) what KDF / ARX / "
        "commitment code exists in the JS itself, (4) what an attacker "
        "must recover to find the key. Do not invent findings that are "
        "not in the excerpts below. %s"
        % (size_bytes, key_marker or "no marker", key_line, KEY_NOTE))
    data = ("Function names (%d): %s\n\nKey-check excerpt:\n%s"
            % (len(func_names), ", ".join(func_names) if func_names else "[none found]",
               key_window or "[no key-check excerpt found]"))
    return fit_prompt(instruction, data, "File: license.cjs, %d bytes." % size_bytes)

def build_wasm_prompt(wasm_text, seal_text):
    """Short 27B prompt for the WASM exports + seal.json analysis. Pure — testable."""
    instruction = (
        "The CrackMe v9 unlock lives in core.wasm (6.88 MB raw, "
        "BLA-hardened). Below are its exports, function and code counts, "
        "and the full seal.json (569 bytes, the runtime one-way seal). In "
        "5-8 bullet points, explain: (1) which exports are the unlock "
        "entry points, (2) what the seal binds (revision + "
        "certificateSha256) and how it is pinned at runtime, (3) what the "
        "commitment layout looks like (the design note says SHA-256 KDF + "
        "ARX + commitment), (4) which functions look like KDF / ARX / "
        "commitment code. Do not invent findings that are not in the data "
        "below. %s" % KEY_NOTE)
    data = ("WASM summary:\n%s\n\nseal.json:\n%s" % (wasm_text, seal_text))
    return fit_prompt(instruction, data, "Files: core.wasm (6,883,604 bytes), seal.json (569 bytes).")

def build_policy_prompt(defs, window, marker, line, size_bytes):
    """Short 27B prompt for the policy.py ledger analysis. Pure — testable."""
    instruction = (
        "policy.py is the hardened Python quota ledger in the CrackMe v9 "
        "vault (%d bytes). Below are its functions and classes and an "
        "excerpt around the key / unlock / seal markers (matched on %s, "
        "line %d). In 5-8 bullet points, explain: (1) what the ledger "
        "does, (2) how it relates to the 16-character key and the unlock, "
        "(3) any key material, canary honeypots, or decoys, (4) whether "
        "it verifies anything itself. Do not invent findings that are not "
        "in the excerpts below. %s"
        % (size_bytes, marker or "no marker", line, KEY_NOTE))
    data = ("Functions/classes (%d): %s\n\nExcerpt:\n%s"
            % (len(defs), ", ".join(defs) if defs else "[none found]",
               window or "[no excerpt found]"))
    return fit_prompt(instruction, data, "File: policy.py, %d bytes." % size_bytes)

def build_wat_prompt(wat_excerpt, matched_name):
    """Short 27B prompt for the WASM disassembly excerpt. Pure — testable."""
    instruction = (
        "This is a disassembly excerpt (WAT text) from core.wasm, the "
        "BLA-hardened WASM that holds the CrackMe v9 unlock (SHA-256 KDF "
        "+ ARX + commitment layout). The excerpt is centred on the export "
        "%s. In 5-8 bullet points, explain: (1) what this function does, "
        "(2) whether it is KDF / ARX / commitment code and how you can "
        "tell, (3) the key operations (SHA-256 constants, rotates, memory "
        "layout), (4) what input it takes and what it outputs. Do not "
        "invent findings that are not in the excerpt below. %s"
        % (matched_name or "[no export matched — first bytes of the module]",
           KEY_NOTE))
    return fit_prompt(instruction, wat_excerpt, "File: core.wat (disassembly of core.wasm).")

def build_panel_prompt(struct, window, marker, line, size_bytes):
    """Short 27B prompt for the panel.html UI analysis. Pure — testable."""
    instruction = (
        "panel.html is the hardened operator UI in the CrackMe v9 vault "
        "(%d bytes). Below is its structure (title, script count, "
        "function names) and an excerpt around the key / unlock markers "
        "(matched on %s, line %d). In 5-8 bullet points, explain: (1) "
        "what the UI does, (2) any key / unlock logic in the HTML or its "
        "inline JS, (3) whether it calls license.cjs or the WASM, (4) any "
        "canary / honeypot. Do not invent findings that are not in the "
        "excerpts below. %s"
        % (size_bytes, marker or "no marker", line, KEY_NOTE))
    data = ("Title: %s\nScript tags: %d\nFunctions (%d): %s\n\nExcerpt:\n%s"
            % (struct.get("title") or "[none]",
               struct.get("script_tags", 0),
               len(struct.get("functions", [])),
               ", ".join(struct.get("functions", [])) or "[none found]",
               window or "[no excerpt found]"))
    return fit_prompt(instruction, data, "File: panel.html, %d bytes." % size_bytes)

# ---------------------------------------------------------------- report append
_report_header_written = [False]

def append_section(report_text, subsection):
    """Append one v1 subsection to the report text and return the new full
    text. The first call also writes the v1 header + intro (dated today)
    so the addendum is clearly separated from anything else in the file.
    The caller writes the returned text via write_report_atomic. The
    original report content is never deleted or edited in place — only
    appended to."""
    today = time.strftime("%Y-%m-%d")
    out = report_text
    if not out.endswith("\n"):
        out += "\n"
    if not _report_header_written[0]:
        if "# CrackMe v9" not in out:
            out += (
                "\n# CrackMe v9 — REA breakdown (v1, %s)\n\n"
                "Target: the BLA-hardened CrackMe v9 Sovereign vault (BLA "
                "3.0, bankrupt intensity, weaveScore 100). Five files in "
                "~/opt/bla/challenge/v9/hardened/ — license.cjs (201,111), "
                "panel.html (126,216), policy.py (41,561), core.wasm.gz "
                "(21,393, about 6.88 MB raw), seal.json (569). All five "
                "SHA-256 digests were verified against SEAL.json before "
                "this run, and this runner re-verifies them before it "
                "copies anything. Work is done on COPIES in "
                "~/crackme-v9/work/ only; the originals are never modified. "
                "Goal: the 16-character key. The unlock lives in the WASM "
                "(SHA-256 KDF + ARX + commitment layout). v1 is recon + "
                "first-pass analysis — it does NOT search the key space. "
                "That is a later round, only if the analysis points to a "
                "searchable space.\n"
                % today)
        _report_header_written[0] = True
    out += "\n" + subsection.strip() + "\n"
    return out

def append_to_report(subsection):
    """Append one v1 subsection to report.md (atomic replace, so the file
    is never left half-written). Returns the new file size in bytes, or
    None if the write failed."""
    try:
        current = read_file(REPORT)
    except Exception as e:
        log("  ERROR: could not read report: %s" % e)
        return None
    new_text = append_section(current, subsection)
    try:
        write_report_atomic(REPORT, new_text)
    except Exception as e:
        log("  ERROR: could not write report: %s" % e)
        return None
    return len(new_text.encode("utf-8"))

def task_done(marker):
    """True if the report already contains a task's section marker — used
    for resumability (re-running skips completed tasks). Pure — testable
    on a given report text via task_done_in."""
    return task_done_in(read_file(REPORT), marker)

def task_done_in(report_text, marker):
    """True if `marker` appears in `report_text`. Pure — testable."""
    return marker in (report_text or "")


# ---------------------------------------------------------------- setup (copies only — the vault is never modified)
def setup_vault():
    """Verify the vault source digests, copy the five files to WORK_DIR,
    gunzip core.wasm.gz -> core.wasm there, and verify the gunzipped
    digest and size. Returns True on success, False on any mismatch
    (the run stops — it never proceeds on tampered copies). Reads the
    vault; never writes to it."""
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        os.makedirs(WORK_DIR, exist_ok=True)
    except Exception as e:
        log("  setup FAILED: could not create dirs: %s" % e)
        return False
    if not os.path.isdir(VAULT_DIR):
        log("  setup FAILED: vault dir not found: %s" % VAULT_DIR)
        return False
    # 1. Verify the SOURCE digests first (the recon already confirmed
    #    them; re-check so a tampered source can never be copied).
    for name in VAULT_FILES:
        src = os.path.join(VAULT_DIR, name)
        if not os.path.isfile(src):
            log("  setup FAILED: vault file missing: %s" % src)
            return False
        got = sha256_file(src)
        if got != EXPECTED[name]:
            log("  setup FAILED: source digest mismatch for %s (got %s, "
                "expected %s) — refusing to copy" % (name, got, EXPECTED[name]))
            return False
        log("  source %s: digest OK (%d bytes)" % (name, os.path.getsize(src)))
    # 2. Copy to the working dir (skip any file whose digest already matches).
    for name in VAULT_FILES:
        src = os.path.join(VAULT_DIR, name)
        dst = os.path.join(WORK_DIR, name)
        if os.path.isfile(dst) and sha256_file(dst) == EXPECTED[name]:
            log("  work %s: already present, digest OK — skipping copy" % name)
            continue
        try:
            shutil.copyfile(src, dst)
        except Exception as e:
            log("  setup FAILED: could not copy %s: %s" % (name, e))
            return False
        if sha256_file(dst) != EXPECTED[name]:
            log("  setup FAILED: copy digest mismatch for %s" % name)
            return False
        log("  work %s: copied, digest OK" % name)
    # 3. Gunzip core.wasm.gz -> core.wasm in the WORKING COPY only
    #    (this mirrors run.mjs, which gunzips into a temp dir before
    #    invoking license.cjs — the integrity check reads core.wasm).
    wasm_path = os.path.join(WORK_DIR, "core.wasm")
    if (os.path.isfile(wasm_path)
            and sha256_file(wasm_path) == EXPECTED_CORE_WASM
            and os.path.getsize(wasm_path) == EXPECTED_CORE_WASM_BYTES):
        log("  work core.wasm: already present, digest OK — skipping gunzip")
    else:
        try:
            with gzip.open(os.path.join(WORK_DIR, "core.wasm.gz"), "rb") as f:
                raw = f.read()
            write_bytes(wasm_path, raw)
        except Exception as e:
            log("  setup FAILED: could not gunzip core.wasm.gz: %s" % e)
            return False
        if sha256_file(wasm_path) != EXPECTED_CORE_WASM:
            log("  setup FAILED: gunzipped core.wasm digest mismatch")
            return False
        if os.path.getsize(wasm_path) != EXPECTED_CORE_WASM_BYTES:
            log("  setup FAILED: gunzipped core.wasm size mismatch "
                "(got %d, expected %d)"
                % (os.path.getsize(wasm_path), EXPECTED_CORE_WASM_BYTES))
            return False
        log("  work core.wasm: gunzipped, digest OK (%d bytes)" % EXPECTED_CORE_WASM_BYTES)
    return True

# ---------------------------------------------------------------- recon
def recon_files():
    """File types, sizes, and line counts for the five working copies.
    Returns a report-section text block. Never raises."""
    lines = []
    file_cmd = which("file")
    for name in VAULT_FILES + ["core.wasm"]:
        p = os.path.join(WORK_DIR, name)
        if not os.path.isfile(p):
            lines.append("- %s: MISSING from the working copy" % name)
            continue
        size = os.path.getsize(p)
        ftype = ""
        if file_cmd:
            try:
                r = subprocess.run([file_cmd, "-b", p], capture_output=True,
                                   text=True, timeout=15)
                ftype = (r.stdout or "").strip()
            except Exception:
                ftype = ""
        if name == "core.wasm":
            magic = read_bytes(p)[:4]
            ftype = (ftype + " | magic %s" % ("\\0asm (valid WASM)" if magic == b"\x00asm" else magic.hex()))
        elif name.endswith((".cjs", ".py", ".html", ".json")):
            try:
                with open(p, "r", errors="replace") as f:
                    nlines = sum(1 for _ in f)
                ftype = (ftype + " | %d lines" % nlines) if ftype else ("%d lines" % nlines)
            except Exception:
                pass
        lines.append("- %s: %d bytes%s" % (name, size, (" — " + ftype) if ftype else ""))
    return "\n".join(lines)

def recon_wasm(ctx):
    """WASM recon: pure-Python parse (always works), wabt if present,
    Node export cross-check if Node is present. Fills ctx with the
    parsed data and the .wat excerpt info. Returns a report-section text
    block. Never raises."""
    wasm_path = os.path.join(WORK_DIR, "core.wasm")
    data = read_bytes(wasm_path)
    parsed = parse_wasm(data)
    ctx["wasm_parsed"] = parsed
    ctx["wasm_text"] = wasm_summary_text(parsed)
    lines = [ctx["wasm_text"]]
    # wabt — checked first, never assumed.
    wasm_objdump = which("wasm-objdump")
    wasm2wat = which("wasm2wat")
    ctx["wabt_present"] = bool(wasm_objdump or wasm2wat)
    if wasm_objdump:
        rc, out = run_tool([wasm_objdump, "-x", wasm_path], timeout=120,
                           out_file=os.path.join(WORK_DIR, "wasm-objdump.txt"))
        lines.append("- wasm-objdump -x: rc=%s (output in work/wasm-objdump.txt, %d chars)"
                     % (rc, len(out)))
        log("  wasm-objdump -x: rc=%s" % rc)
    else:
        lines.append("- wasm-objdump: NOT installed (wabt absent)")
    if wasm2wat:
        rc, out = run_tool([wasm2wat, wasm_path, "-o", os.path.join(WORK_DIR, "core.wat")],
                           timeout=300,
                           out_file=os.path.join(WORK_DIR, "wasm2wat-log.txt"))
        wat_path = os.path.join(WORK_DIR, "core.wat")
        ok = os.path.isfile(wat_path) and os.path.getsize(wat_path) > 0
        ctx["wasm2wat_ok"] = ok
        lines.append("- wasm2wat: rc=%s, core.wat %s (%s bytes)"
                     % (rc, "written" if ok else "NOT written",
                        os.path.getsize(wat_path) if ok else 0))
        log("  wasm2wat: rc=%s, core.wat %s" % (rc, "written" if ok else "missing"))
        if ok:
            wat_text = read_file(wat_path)
            export_names = [n for n, _k, _i in parsed.get("exports", [])]
            ex, matched = extract_wat_excerpt(wat_text, export_names, budget=2000)
            ctx["wat_excerpt"] = ex
            ctx["wat_matched"] = matched
            lines.append("- WAT excerpt: %d chars, centred on export %s"
                         % (len(ex), matched or "[none matched — first bytes of the module]"))
    else:
        ctx["wasm2wat_ok"] = False
        lines.append("- wasm2wat: NOT installed (wabt absent) — no disassembly excerpt; "
                     "the WASM task will analyse the export list instead")
    # Node export cross-check (Node is on the machine; the script compiles
    # the module and prints exports/imports as JSON).
    node = which("node")
    if node:
        script_path = os.path.join(WORK_DIR, "wasm-exports.cjs")
        write_file(script_path, NODE_EXPORTS_SCRIPT)
        rc, out = run_tool([node, script_path, wasm_path], timeout=120,
                           out_file=os.path.join(WORK_DIR, "wasm-node-exports.txt"))
        try:
            obj = json.loads(out.split("--- stderr ---")[0])
            n_exp = len(obj.get("exports", []))
            n_imp = len(obj.get("imports", []))
            lines.append("- Node WebAssembly.Module: rc=%s, %d exports, %d imports "
                         "(cross-check in work/wasm-node-exports.txt)" % (rc, n_exp, n_imp))
            ctx["node_exports"] = obj
        except Exception:
            lines.append("- Node WebAssembly.Module: rc=%s, output not JSON "
                         "(see work/wasm-node-exports.txt)" % rc)
        log("  Node export cross-check: rc=%s" % rc)
    else:
        lines.append("- Node: NOT found — no export cross-check")
    return "\n".join(lines)

TOOL_APPLICABILITY = """## Tool applicability — which of the 15 REA tools fit a JS/WASM/Python vault

The vault is JavaScript + WebAssembly + HTML + Python (local files, no
network, no native binary). Not every REA tool applies — the ones that do
not are named here with the reason, not forced.

Applies now:
- **The 27B model** — the main engine. It reads JS, Python, and WASM text
  in chunks and explains the gate, the KDF/ARX/commitment code, and the
  key flow. (Five calls in v1, one per task, short prompts.)
- **Node.js** — runs and inspects license.cjs; the gate itself is Node.
  Also the export cross-check (WebAssembly.Module.exports) and the
  candidate-key verification (`node license.cjs <key>`).
- **wabt (wasm2wat / wasm-objdump)** — disassembles core.wasm. Checked
  at run time, never assumed; if it is absent, the WASM task analyses the
  export list instead and the disassembly task is a placeholder.
- **ImHex** — pattern-matches the WASM binary and the JS for the KDF/ARX/
  commitment constants (SHA-256 initial values, rotate amounts, the seed
  string). A later round can run a .hexpat against core.wasm.

Applies later (advanced, deferred):
- **Frida** — hook the Node process while license.cjs runs and watch the
  key flow into the WASM. Only if the static path stalls; not in v1.

Does NOT apply (named with the reason — not forced):
- **Detect-It-Easy** — PE/ELF packer detection; the vault is JS/WASM/
  Python text, not a PE/ELF binary.
- **capa** — capability detection for PE/ELF/Mach-O; not for JS/WASM/Python.
- **LIEF** — parses PE/ELF/Mach-O; WASM is a different binary format that
  LIEF does not parse.
- **Ghidra** — native-binary decompiler; it has no WASM processor in the
  stock install, so it cannot decompile core.wasm. (It could analyse the
  node binary itself, but that is not the unlock logic.)
- **GhidraMCP** — depends on Ghidra; same reason as Ghidra.
- **angr** — symbolic execution for native architectures (x86/ARM/MIPS);
  WASM is not a supported angr architecture.
- **objection** — mobile runtime instrumentation (Android/iOS); this is a
  desktop Node.js process, not a mobile app.
- **jadx** — Android DEX decompiler; there is no APK or DEX here.
- **Apktool** — Android APK tool; no APK here.
- **ILSpy** — .NET decompiler; no .NET assembly here.
- **asar** — Electron archive tool; there is no .asar here (panel.html is
  a plain HTML file).
- **mitmproxy** — HTTP proxy; the vault is local files, no network traffic
  to intercept.
- **Wireshark / tshark** — packet capture; no network traffic in this
  challenge.
"""


# ---------------------------------------------------------------- 27B tasks (one call per task, one section per call)
def _run_task(task_id, marker, prompt, markers, section_title, ctx_key, ctx):
    """Run one 27B task: skip if its section is already in the report
    (resumable), else call the 27B once and append the findings — or an
    honest placeholder when the 27B gives no reply. Returns
    (outcome, reply_or_None). outcome is "ok", "partial", or "failed"."""
    today = time.strftime("%Y-%m-%d")
    if task_done(marker):
        log("  [%s] already in the report — skipping (resumable)" % task_id)
        return "skipped", None
    log("  [%s] prompt: %d chars" % (task_id, len(prompt)))
    reply = call_27b_item(prompt, task_id, markers=markers,
                          min_chars=150, min_markers=1)
    if reply is None:
        note = ("### %s (%s)\n\n"
                "[%s — 27B gave no reply: the prompt was sent (%d chars) "
                "but the 27B gave no usable reply after 4 attempts, so no "
                "findings are recorded here. The recon data is saved in "
                "~/crackme-v9/work/ and can be read by hand.]\n"
                % (section_title, today, task_id, len(prompt)))
        append_to_report(note)
        log("  [%s] 27B gave no reply — placeholder written" % task_id)
        return "partial", None
    # A reply that ends mid-sentence is marked unverified, not presented
    # as a clean finding (the C270 lesson: read the reply to its end).
    unverified = ""
    tail = reply.strip()[-120:]
    if not reply.strip().endswith((".", "!", "?", ":", '"', "'", ")", "]", "}")):
        unverified = ("\n\n[Note: the 27B reply ends mid-sentence, so this "
                      "section is UNVERIFIED — treat its last claims with "
                      "caution.]\n")
    section = ("### %s (%s)\n\n%s%s\n"
               % (section_title, today, reply.strip(), unverified))
    append_to_report(section)
    log("  [%s] ok — %d chars appended" % (task_id, len(reply)))
    return "ok", reply

def task_license(ctx):
    """Task A — license.cjs, the gate."""
    tid = "crackme-v9-license"
    marker = "### license.cjs (crackme-v9"
    text = read_file(os.path.join(WORK_DIR, "license.cjs"))
    funcs = js_function_names(text)
    window, marker_found, line_no = find_window(
        text, ["DENIED", "unlock", "verify", "createHash", "sha256", "length"],
        before=25, after=25, budget=1200)
    strs = interesting_strings(text, ["sha256", "DENIED", "FLAG", "key", "unlock", "seal", "v9p"], cap=8)
    ctx["license_funcs"] = funcs
    ctx["license_window"] = window
    prompt = build_license_prompt(funcs, window, marker_found, line_no,
                                  os.path.getsize(os.path.join(WORK_DIR, "license.cjs")))
    if strs:
        prompt = prompt + "\n\nInteresting strings: %s" % ", ".join(strs)
    return _run_task(tid, marker, prompt,
                     markers=["key", "license", "wasm", "denied"],
                     section_title="license.cjs (crackme-v9",
                     ctx_key=None, ctx=ctx)

def task_wasm(ctx):
    """Task B — WASM exports + seal.json, the unlock entry points."""
    tid = "crackme-v9-wasm"
    marker = "### core.wasm + seal.json (crackme-v9"
    seal_text = read_file(os.path.join(WORK_DIR, "seal.json"))
    prompt = build_wasm_prompt(ctx.get("wasm_text", ""), seal_text)
    return _run_task(tid, marker, prompt,
                     markers=["wasm", "export", "seal", "unlock"],
                     section_title="core.wasm + seal.json (crackme-v9",
                     ctx_key=None, ctx=ctx)

def task_policy(ctx):
    """Task C — policy.py, the Python ledger."""
    tid = "crackme-v9-policy"
    marker = "### policy.py (crackme-v9"
    text = read_file(os.path.join(WORK_DIR, "policy.py"))
    defs = py_defs(text)
    window, marker_found, line_no = find_window(
        text, ["sha256", "key", "unlock", "seal", "FLAG", "DENIED"],
        before=20, after=20, budget=1200)
    prompt = build_policy_prompt(defs, window, marker_found, line_no,
                                 os.path.getsize(os.path.join(WORK_DIR, "policy.py")))
    return _run_task(tid, marker, prompt,
                     markers=["policy", "python", "ledger", "key"],
                     section_title="policy.py (crackme-v9",
                     ctx_key=None, ctx=ctx)

def task_wat(ctx):
    """Task D — WASM disassembly excerpt. Only if wasm2wat worked; else
    an honest placeholder naming wabt as missing."""
    tid = "crackme-v9-wat"
    marker = "### core.wasm disassembly (crackme-v9"
    today = time.strftime("%Y-%m-%d")
    if task_done(marker):
        log("  [%s] already in the report — skipping (resumable)" % tid)
        return "skipped", None
    if not ctx.get("wasm2wat_ok") or not ctx.get("wat_excerpt"):
        note = ("### core.wasm disassembly (crackme-v9, %s)\n\n"
                "[core.wasm disassembly — not available: wasm2wat (wabt) "
                "is not installed on this machine, so no .wat was produced "
                "and the 27B had no disassembly to analyse. The WASM "
                "export list (task B) is the fallback. Install wabt and "
                "re-run to enable this task.]\n" % today)
        append_to_report(note)
        log("  [%s] wasm2wat missing — placeholder written" % tid)
        return "failed", None
    prompt = build_wat_prompt(ctx["wat_excerpt"], ctx.get("wat_matched"))
    return _run_task(tid, marker, prompt,
                     markers=["wasm", "func", "sha", "kdf"],
                     section_title="core.wasm disassembly (crackme-v9",
                     ctx_key=None, ctx=ctx)

def task_panel(ctx):
    """Task E — panel.html, the operator UI."""
    tid = "crackme-v9-panel"
    marker = "### panel.html (crackme-v9"
    text = read_file(os.path.join(WORK_DIR, "panel.html"))
    struct = html_structure(text)
    window, marker_found, line_no = find_window(
        text, ["key", "unlock", "verify", "seal", "license"],
        before=20, after=20, budget=1200)
    prompt = build_panel_prompt(struct, window, marker_found, line_no,
                                os.path.getsize(os.path.join(WORK_DIR, "panel.html")))
    return _run_task(tid, marker, prompt,
                     markers=["panel", "html", "ui", "key"],
                     section_title="panel.html (crackme-v9",
                     ctx_key=None, ctx=ctx)

# ---------------------------------------------------------------- candidate keys
def extract_candidates(replies, cap=3):
    """Extract 16-character key candidates from 27B replies.

    Only tokens on a line containing the word "key" (case-insensitive)
    count — a bare 16-char token elsewhere is not a proposed key.
    Deduped, in first-seen order, capped at `cap`. Pure — testable."""
    out = []
    seen = set()
    for reply in replies:
        if not reply:
            continue
        for line in reply.splitlines():
            if "key" not in line.lower():
                continue
            for m in re.finditer(r"\b([A-Za-z0-9]{16})\b", line):
                tok = m.group(1)
                if tok not in seen:
                    seen.add(tok)
                    out.append(tok)
                if len(out) >= cap:
                    return out
    return out

def verify_flag(flag_text):
    """True if SHA-256 of the FLAG text matches the public commitment.
    Pure — testable."""
    if not flag_text:
        return False
    return sha256_text(flag_text.strip()) == FLAG_SHA256

def verify_candidates(candidates):
    """Verify up to 3 candidate keys with `node license.cjs <key>` in the
    WORKING COPY (never the original). Returns (results, solved) where
    results is a list of (candidate, outcome, detail) and solved is True
    only when a candidate unlocked AND the FLAG's SHA-256 matched the
    public commitment. Never raises."""
    results = []
    solved = False
    node = which("node")
    if not node:
        for cand in candidates:
            results.append((cand, "not-run", "Node.js not found — cannot verify"))
        return results, False
    for cand in candidates:
        out_file = os.path.join(WORK_DIR, "verify-%s.txt" % cand)
        rc, out = run_tool([node, os.path.join(WORK_DIR, "license.cjs"), cand],
                           timeout=60, out_file=out_file, cwd=WORK_DIR)
        if "integrity binding mismatch" in out:
            results.append((cand, "TAMPER",
                            "license.cjs threw 'integrity binding mismatch' — "
                            "the working copy failed its self-check (rc=%s); "
                            "the vault copies may be wrong" % rc))
            continue
        m = re.search(r"FLAG\{[^}]*\}", out)
        if m:
            flag = m.group(0)
            match = verify_flag(flag)
            results.append((cand, "UNLOCKED" if match else "UNLOCKED-UNVERIFIED",
                            "FLAG: %s (SHA-256 %s the public commitment %s)"
                            % (flag, "MATCHES" if match else "does NOT match", FLAG_SHA256[:16] + "...")))
            if match:
                solved = True
            continue
        if "DENIED" in out:
            results.append((cand, "DENIED", "gate returned DENIED (rc=%s)" % rc))
            continue
        results.append((cand, "UNKNOWN",
                        "no FLAG and no DENIED in the output (rc=%s); raw output "
                        "in work/verify-%s.txt" % (rc, cand)))
    return results, solved

# ---------------------------------------------------------------- summary + status + main
def write_status(result, detail, tasks=None, candidates=None, solved=False,
                 new_size=None):
    lines = [
        "result: %s" % result,
        "time: %s" % time.strftime("%Y-%m-%d %H:%M:%S"),
        "report: %s" % REPORT,
        "detail: %s" % detail,
    ]
    if tasks:
        lines.append("tasks: %s" % ", ".join("%s=%s" % (k, v) for k, v in tasks))
    if candidates is not None:
        lines.append("candidates_tried: %d" % len(candidates))
    lines.append("solved: %s" % ("yes" if solved else "no"))
    if new_size is not None:
        lines.append("new_report_bytes: %d" % new_size)
    try:
        write_file(STATUS_PATH, "\n".join(lines) + "\n")
    except Exception:
        pass

def main():
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        os.makedirs(WORK_DIR, exist_ok=True)
    except Exception:
        pass
    log("crackme-v9 v1 starting — CrackMe v9 Sovereign, recon + first-pass analysis")
    log("vault: %s" % VAULT_DIR)
    log("work: %s (copies only — the originals are never modified)" % WORK_DIR)
    log("report: %s" % REPORT)
    log("model: %s (Ollama %s, think=true, num_ctx 4096, num_gpu 0, "
        "keep_alive 24h, timeout %ss)" % (MODEL, OLLAMA_URL, OLLAMA_TIMEOUT))
    orig_bytes = len(read_file(REPORT).encode("utf-8"))
    log("report: %d bytes (original)" % orig_bytes)
    # 1. Setup.
    if not setup_vault():
        msg = "setup failed — vault digests did not verify (see the log); nothing was analysed"
        log("FAILED: " + msg)
        write_status("failed", msg)
        print("FAILED — " + msg)
        return 1
    log("setup: vault verified and copied to the working dir")
    ctx = {}
    # 2. Recon — files (once).
    if not task_done("## Recon — files"):
        files_text = recon_files()
        append_to_report("## Recon — files (%s)\n\n%s\n" % (time.strftime("%Y-%m-%d"), files_text))
        log("recon: files section appended")
    else:
        log("recon: files section already in the report — skipping")
    # 3. Recon — WASM (once).
    if not task_done("## Recon — WASM"):
        wasm_text = recon_wasm(ctx)
        append_to_report("## Recon — WASM (%s)\n\n%s\n" % (time.strftime("%Y-%m-%d"), wasm_text))
        log("recon: WASM section appended")
    else:
        # Re-parse for the tasks (cheap — no 27B call, no tool run).
        recon_wasm(ctx)
        log("recon: WASM section already in the report — re-parsed for the tasks")
    # 4. Tool applicability (once).
    if not task_done("## Tool applicability"):
        append_to_report(TOOL_APPLICABILITY)
        log("tool applicability section appended")
    else:
        log("tool applicability section already in the report — skipping")
    # 5. Five 27B tasks, one call each, one section each.
    outcomes = {}
    replies = []
    for fn, name in [(task_license, "license"), (task_wasm, "wasm"),
                     (task_policy, "policy"), (task_wat, "wat"),
                     (task_panel, "panel")]:
        log("[%s] starting" % name)
        outcome, reply = fn(ctx)
        outcomes[name] = outcome
        replies.append(reply)
    # 6. Candidate keys (at most 3, verified in the working copy only).
    candidates = extract_candidates(replies)
    if candidates:
        log("candidate keys found in 27B replies: %s" % ", ".join(candidates))
    else:
        log("no candidate 16-char key in any 27B reply — nothing to verify")
    results, solved = verify_candidates(candidates)
    if not task_done("## Candidate keys"):
        if results:
            body = []
            for cand, outcome, detail in results:
                body.append("- `%s`: **%s** — %s" % (cand, outcome, detail))
            append_to_report("## Candidate keys (%s)\n\n%s\n"
                             % (time.strftime("%Y-%m-%d"), "\n".join(body)))
        else:
            append_to_report("## Candidate keys (%s)\n\nNo 16-character key "
                             "candidate appeared in any 27B reply, so nothing "
                             "was verified. (v1 does not search the key space.)\n"
                             % time.strftime("%Y-%m-%d"))
        log("candidate keys section appended (%d tried, solved=%s)"
            % (len(results), solved))
    else:
        # Already verified in an earlier run — the tasks were skipped, so
        # this run found no new candidates. Preserve the solve state from
        # the report instead of downgrading it: a confirmed solve is
        # recorded as "**UNLOCKED**" (the exact marker; the unverified
        # form is "**UNLOCKED-UNVERIFIED**" and does not match it).
        existing = read_file(REPORT)
        solved = "**UNLOCKED**" in existing and "FLAG{" in existing
        log("candidate keys section already in the report — skipping "
            "(solved preserved: %s)" % solved)
    # 7. Summary.
    if not task_done("## Summary — v1 findings"):
        ok = [k for k, v in outcomes.items() if v == "ok"]
        partial = [k for k, v in outcomes.items() if v in ("partial", "failed")]
        skipped = [k for k, v in outcomes.items() if v == "skipped"]
        summary = (
            "## Summary — v1 findings and next steps (%s)\n\n"
            "v1 (recon + first-pass analysis) is done. 27B tasks: %d ok "
            "(%s), %d partial/failed (%s), %d skipped as already done (%s). "
            "Candidate keys tried: %d. Solved: %s.\n\n"
            "What is still unknown after v1: the exact KDF/ARX/commitment "
            "steps inside core.wasm, and the key itself (unless a candidate "
            "above unlocked it). What the next round should do: (1) deeper "
            "WASM reverse engineering on the specific export the analysis "
            "names (disassemble that function, trace the KDF/ARX/commitment "
            "by hand or with angr-style analysis if it fits); (2) a "
            "key-space search ONLY if the analysis identifies a searchable "
            "space (a pattern, a dictionary, or a reduced alphabet) — never "
            "a blind brute-force; (3) a Frida hook on the Node process "
            "while license.cjs runs, if the static path stalls. The vault "
            "originals were never modified; everything v1 did is in "
            "~/crackme-v9/ (working copies in work/, findings in report.md).\n"
            % (time.strftime("%Y-%m-%d"), len(ok), ", ".join(ok) or "none",
               len(partial), ", ".join(partial) or "none",
               len(skipped), ", ".join(skipped) or "none",
               len(results), "YES — the FLAG above is verified" if solved else "no"))
        append_to_report(summary)
        log("summary section appended")
    new_bytes = len(read_file(REPORT).encode("utf-8"))
    if solved:
        result = "solved"
        detail = ("SOLVED — a candidate key unlocked the gate and the FLAG's "
                  "SHA-256 matches the public commitment; report now %d bytes "
                  "(was %d)" % (new_bytes, orig_bytes))
    elif all(v in ("ok", "skipped") for v in outcomes.values()):
        result = "ok"
        detail = ("all five 27B tasks done (ok or already done); %d candidate(s) "
                  "tried, none unlocked; report now %d bytes (was %d)"
                  % (len(results), new_bytes, orig_bytes))
    else:
        result = "partial"
        detail = ("some 27B tasks failed or gave no reply (placeholders "
                  "written); %d candidate(s) tried; report now %d bytes "
                  "(was %d)" % (len(results), new_bytes, orig_bytes))
    log("DONE: " + detail)
    write_status(result, detail,
                 tasks=[(k, v) for k, v in outcomes.items()],
                 candidates=results, solved=solved, new_size=new_bytes)
    print("DONE — " + detail)
    print("Report: %s" % REPORT)
    return 0

if __name__ == "__main__":
    sys.exit(main())

