#!/usr/bin/env python3
r"""
jarvis_lora_bridge.py  --  Laptop-side bridge for the Watch Off-Grid Jarvis link.

Reads framed text messages arriving from a gateway LoRa node (SX1280 2.4 GHz)
over USB serial, forwards the command text to the local Jarvis orchestrator,
gets qwen3's reply, truncates/chunks it to LoRa-sized frames, and writes the
frames back to serial for the gateway node to transmit to the watch.

TWO MODES:
  * CUSTOM  -- the gateway runs our Option-B firmware and speaks the ASCII
               protocol in PROTOCOL.md over a plain serial link (pyserial).
  * MESHTASTIC -- the gateway is a stock Meshtastic node; we use the meshtastic
               Python library instead of raw serial. See MESHTASTIC-OPTION.md.
               (That path is sketched at the bottom; this file focuses on CUSTOM.)

NOTHING here is run or installed by the scaffolding build. To use it later:
    python -m venv .venv && .venv\Scripts\activate
    pip install pyserial            # CUSTOM mode
    pip install meshtastic pypubsub # MESHTASTIC mode
    python jarvis_lora_bridge.py

This is well-commented scaffolding. Assumptions about the orchestrator API are
marked with TODO -- verify against the real orchestrator before relying on it.
"""

import os
import time
import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ----------------------------------------------------------------------------
# CONFIG  (edit these)
# ----------------------------------------------------------------------------
SERIAL_PORT      = os.environ.get("JV_LORA_COM", "COM5")  # gateway node COM port from env (Device Manager)
SERIAL_BAUD      = 115200                     # must match the firmware's Serial.begin()
ORCH_URL         = "http://127.0.0.1:8080"    # local Jarvis orchestrator
# Radio text is UNTRUSTED and must never reach the tool-capable /jarvis route (SAF).
# RECON_ROUTE = a NO-TOOLS orchestrator route. Default /recon is DOCUMENTED BUT NOT YET IMPLEMENTED
# in C:\Jarvis\orchestrator.py (needs HgX approval). Until it exists, radio chat replies "route missing".
ORCH_CHAT_PATH   = os.environ.get("JV_RECON_ROUTE", "/recon")
ORCH_TIMEOUT_S   = 40                         # nested timeouts: ingest 30 < orchestrator 40 < caller 45 < voice 50
MAX_FRAME        = 200                        # max BYTES per LoRa frame (see PROTOCOL.md)
MAX_REPLY_CHARS  = 400                        # truncate qwen3 replies before chunking
MODE             = os.environ.get("JV_LORA_MODE", "CUSTOM").upper()  # "CUSTOM" or "MESHTASTIC"
# --- Recon Kit (glasses vision) ---
INGEST_LOOK_URL  = "http://127.0.0.1:8767/look"  # laptop-ingest/recon_ingest.py (8767: avoids 8765 clash)
import hmac, hashlib, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
from jv_envelope import make as make_env  # noqa: E402
# HMAC key for LoRa frames comes ONLY from the environment (.env, gitignored).
LORA_KEY = os.environ.get("JV_LORA_KEY", "").encode()
REQUIRE_MAC = True                            # MANDATORY (Cartographer): startup refuses without JV_LORA_KEY
# Bearer token this bridge presents to laptop-ingest (must be one of JV_INGEST_TOKENS). Env only.
INGEST_TOKEN = os.environ.get("JV_INGEST_TOKEN", "")
# Shared token required on 127.0.0.1:8766/push (recon_ingest sends the same value). Env only.
PUSH_TOKEN   = os.environ.get("JV_PUSH_TOKEN", "")
# MESHTASTIC mode: only these node IDs (e.g. "!a1b2c3d4", comma list) may command the bridge.
MESH_ALLOW_NODES = {n.strip().lower() for n in os.environ.get("JV_MESH_ALLOW_NODES", "").split(",") if n.strip()}
# Reply-chunk retransmit (mirrors the watch: 3 retries at 4/8/16 s, then give up loudly).
REPLY_RETRY_S    = [4, 8, 16]
INGEST_TIMEOUT_S = 45                         # ingest now answers (or "queued") within ~30 s
PUSH_HOST        = "127.0.0.1"                # local-only push API for unsolicited results
PUSH_PORT        = 8766
RECON_PREFIX     = "RC:"                      # reply payload prefix the watch renders as a recon card

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("lora-bridge")

# ----------------------------------------------------------------------------
# PROTOCOL helpers (mirror PROTOCOL.md)
# ----------------------------------------------------------------------------
MAGIC = "JV1"

def crc16_ccitt(data: bytes, crc: int = 0xFFFF) -> int:
    """CRC-16/CCITT (poly 0x1021, init 0xFFFF)."""
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if (crc & 0x8000) else (crc << 1) & 0xFFFF
    return crc & 0xFFFF

# Anti-replay: every signed frame carries a monotonic counter (hex) BEFORE the MAC:
#   JV1|msgid|type|seq|total|payload|ctr|mac|crc
# TX counter and the highest RX counter seen are persisted outside synced trees.
CTR_FILE = os.environ.get("JV_LORA_CTR_FILE", r"C:\JarvisData\lora\counters.json")
_ctr_lock = threading.Lock()
def _load_ctr():
    try:
        with open(CTR_FILE, "r", encoding="utf-8") as fh:
            d = json.load(fh); return int(d.get("tx", 0)), int(d.get("rx", 0))
    except Exception:  # noqa
        return 0, 0
_TX_CTR, _RX_CTR = _load_ctr()
def _save_ctr():
    try:
        os.makedirs(os.path.dirname(CTR_FILE), exist_ok=True)
        with open(CTR_FILE, "w", encoding="utf-8") as fh:
            json.dump({"tx": _TX_CTR, "rx": _RX_CTR}, fh)
    except Exception as e:  # noqa
        log.warning("counter persist failed: %s", type(e).__name__)
def _next_tx():
    global _TX_CTR
    with _ctr_lock:
        _TX_CTR += 1; _save_ctr(); return _TX_CTR

def build_frame(msgid: str, mtype: str, seq: int, total: int, payload: str, ctr: int = None) -> str:
    """Assemble one signed protocol frame including counter, MAC and CRC."""
    body = "%s|%s|%s|%d|%d|%s" % (MAGIC, msgid, mtype, seq, total, payload)
    if REQUIRE_MAC:
        body += "|%x" % (ctr if ctr is not None else _next_tx())
        body += "|" + frame_mac(body)
    crc = crc16_ccitt(body.encode("utf-8"))
    return "%s|%04x" % (body, crc)

def frame_mac(body: str) -> str:
    """Truncated HMAC-SHA256 (8 hex) over the frame body. Mirrors main.cpp."""
    return hmac.new(LORA_KEY, body.encode("utf-8"), hashlib.sha256).hexdigest()[:8]

def parse_frame(line: str):
    """Parse and CRC-check a frame. Returns dict or None if invalid."""
    line = line.strip()
    if not line.startswith(MAGIC + "|"):
        return None
    try:
        body, crc_s = line.rsplit("|", 1)
        if crc16_ccitt(body.encode("utf-8")) != int(crc_s, 16):
            log.warning("CRC fail, dropping: %r", line)
            return None
        if REQUIRE_MAC:
            body, mac = body.rsplit("|", 1)
            if not hmac.compare_digest(mac, frame_mac(body)):
                log.warning("HMAC fail, dropping frame")   # fail closed
                return None
            body, ctr_s = body.rsplit("|", 1)
            ctr = int(ctr_s, 16)
            global _RX_CTR
            with _ctr_lock:
                if ctr <= _RX_CTR:                          # replay / stale -> drop
                    log.warning("replayed/stale counter %d <= %d, dropping", ctr, _RX_CTR)
                    return None
                _RX_CTR = ctr; _save_ctr()
        _magic, msgid, mtype, seq, total, payload = body.split("|", 5)
        return {"msgid": msgid, "type": mtype,
                "seq": int(seq), "total": int(total), "payload": payload}
    except Exception as e:  # noqa
        log.warning("parse error %s on %r", e, line)
        return None

def parse_frame_unsigned(line: str):
    """Split one of OUR OWN outbound frames (no verification) to re-sign it on resend."""
    try:
        body = line.strip().rsplit("|", 1)[0]
        if REQUIRE_MAC:
            body = body.rsplit("|", 2)[0]
        _m, msgid, mtype, seq, total, payload = body.split("|", 5)
        return {"msgid": msgid, "type": mtype, "seq": int(seq), "total": int(total), "payload": payload}
    except Exception:  # noqa
        return None

def chunk_text(text: str, max_frame: int, msgid: str, mtype: str):
    """Split reply text into frames that each fit max_frame bytes."""
    # Reserve room for the header+crc overhead by measuring a worst-case prefix.
    # Budget is in BYTES (UTF-8), not characters: one non-ASCII char can be 2-4 bytes.
    overhead = len(build_frame(msgid, mtype, 99, 99, "", ctr=0xFFFFFFFF).encode("utf-8"))
    budget = max(8, max_frame - overhead)
    pieces, cur, n = [], "", 0
    for ch in text:
        b = len(ch.encode("utf-8"))
        if cur and n + b > budget:
            pieces.append(cur); cur, n = "", 0
        cur += ch; n += b
    if cur or not pieces:
        pieces.append(cur)
    total = len(pieces)
    return [build_frame(msgid, mtype, i, total, p) for i, p in enumerate(pieces)]

# ----------------------------------------------------------------------------
# Orchestrator call  (TODO: match the real API shape)
# ----------------------------------------------------------------------------
def ask_jarvis(command_text: str) -> str:
    """
    Send the command to the local orchestrator and return a short reply string.

    ASSUMPTION / TODO: the orchestrator accepts a POST JSON {"text": ...} or
    {"message": ...} at ORCH_URL+ORCH_CHAT_PATH and returns JSON containing a
    reply field ("reply"/"response"/"text"). Adjust the payload/field names to
    the real orchestrator contract. If the orchestrator only speaks to Ollama,
    an alternative is to POST directly to http://127.0.0.1:11434/api/generate.
    """
    import urllib.request  # stdlib, no extra install for the HTTP call
    import urllib.error
    if ORCH_CHAT_PATH.rstrip("/").lower() == "/jarvis":
        log.error("refusing to forward radio text to tool-capable /jarvis (set JV_RECON_ROUTE)")
        return "Radio route blocked"
    payload = json.dumps({"text": command_text, "source": "watch-lora", "tools": False}).encode()
    req = urllib.request.Request(
        ORCH_URL + ORCH_CHAT_PATH, data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=ORCH_TIMEOUT_S) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        for k in ("reply", "response", "text", "message", "content"):
            if isinstance(data, dict) and k in data and data[k]:
                return str(data[k])
        return str(data)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return "AUTH"                               # fail closed, no failover
        if e.code == 404:
            return "Radio route missing (%s)" % ORCH_CHAT_PATH   # /recon not built yet (HgX)
        return "Jarvis error %d" % e.code
    except Exception as e:  # noqa
        log.error("orchestrator call failed: %s", type(e).__name__)
        return "Jarvis unreachable (%s)" % type(e).__name__

def ask_recon(prompt: str, msgid: str) -> str:
    """Watch 'recon' over LoRa -> laptop-ingest /look (source=lora)."""
    import urllib.request, urllib.error
    body = json.dumps(make_env(msgid or "0", "watch", "cmd", {"prompt": prompt, "via": "lora"})).encode()
    hdrs = {"Content-Type": "application/json"}
    if INGEST_TOKEN:
        hdrs["Authorization"] = "Bearer " + INGEST_TOKEN   # from env only, never logged
    req = urllib.request.Request(INGEST_LOOK_URL, data=body,
                                 headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=INGEST_TIMEOUT_S) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        p = data.get("payload", {}) if isinstance(data, dict) else {}
        return str(p.get("short") or p.get("text") or "No result")
    except urllib.error.HTTPError as e:
        log.error("ingest HTTP %d", e.code)
        return "AUTH" if e.code in (401, 403) else "Eyes error %d" % e.code   # auth fails closed
    except Exception as e:  # noqa
        log.error("ingest call failed: %s", e)
        return "Eyes offline (%s)" % type(e).__name__

def handle_command(command: str, msgid: str) -> str:
    """Route a watch command. 'recon' / 'recon:<prompt>' -> glasses vision; else qwen3."""
    c = command.strip()
    if c.lower().startswith("recon"):
        prompt = c.split(":", 1)[1].strip() if ":" in c else ""
        return RECON_PREFIX + shorten(ask_recon(prompt, msgid))
    return shorten(ask_jarvis(c))

def shorten(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= MAX_REPLY_CHARS else text[:MAX_REPLY_CHARS - 1] + "\u2026"

# ----------------------------------------------------------------------------
# CUSTOM mode main loop  (pyserial)
# ----------------------------------------------------------------------------
SER_LOCK = threading.Lock()

def write_line(ser, s: str):
    with SER_LOCK:
        ser.write((s + "\n").encode())

def start_push_server(send_text):
    """127.0.0.1-only API so laptop-ingest can push glasses results to the watch.
    POST /push {"msgid": "7f", "text": "RC:..."}"""
    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != "/push":
                self.send_response(404); self.end_headers(); return
            tok = self.headers.get("X-JV-Push-Token", "")
            if not PUSH_TOKEN or not hmac.compare_digest(tok, PUSH_TOKEN):   # shared secret, fail closed
                log.warning("push rejected: auth")
                self.send_response(401); self.send_header("Content-Length", "0"); self.end_headers(); return
            n = min(int(self.headers.get("Content-Length", 0)), 2048)
            try:
                d = json.loads(self.rfile.read(n) or b"{}")
                send_text(str(d.get("msgid", "0"))[:4] or "0", str(d.get("text", ""))[:MAX_REPLY_CHARS])
                self.send_response(200)
            except Exception as e:  # noqa
                log.warning("push failed: %s", e); self.send_response(400)
            self.send_header("Content-Length", "0"); self.end_headers()
        def log_message(self, *a):
            pass
    srv = HTTPServer((PUSH_HOST, PUSH_PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    log.info("push API on %s:%d", PUSH_HOST, PUSH_PORT)

def run_custom():
    import serial  # pip install pyserial
    log.info("Opening %s @ %d (CUSTOM mode)", SERIAL_PORT, SERIAL_BAUD)
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)

    # Outbound reply chunks awaiting a watch ACK: (msgid, seq) -> [frame, tries, next_at]
    unacked = {}
    un_lock = threading.Lock()

    def send_reply(msgid, text):
        for seq, out in enumerate(chunk_text(text, MAX_FRAME, msgid, "R")):
            write_line(ser, out)
            with un_lock:
                unacked[(msgid, seq)] = [out, 0, time.time() + REPLY_RETRY_S[0]]
            time.sleep(0.2)  # small gap so the radio keeps up

    def resend_loop():
        while True:
            time.sleep(1)
            now = time.time()
            with un_lock:
                due = [(k, v) for k, v in unacked.items() if v[2] <= now]
            for k, v in due:
                if v[1] >= len(REPLY_RETRY_S):
                    log.error("reply %s chunk %d never ACKed after %d retries - giving up", k[0], k[1], v[1])
                    with un_lock: unacked.pop(k, None)
                    continue
                # Re-sign with a fresh counter so the watch's replay check accepts it.
                f = parse_frame_unsigned(v[0])
                out = build_frame(k[0], "R", k[1], f["total"], f["payload"]) if f else v[0]
                write_line(ser, out)
                v[0] = out; v[1] += 1
                v[2] = now + (REPLY_RETRY_S[v[1]] if v[1] < len(REPLY_RETRY_S) else REPLY_RETRY_S[-1])
                log.info("resent reply %s chunk %d (try %d)", k[0], k[1], v[1])

    threading.Thread(target=resend_loop, daemon=True).start()
    push = send_reply
    start_push_server(push)
    # Reassembly buffers for multi-chunk inbound commands: msgid -> {seq: payload}
    inbox = {}
    try:
        while True:
            raw = ser.readline().decode("utf-8", "replace")
            if not raw.strip():
                continue
            frame = parse_frame(raw)
            if not frame:
                continue

            # ACK every good data frame (cmd). (A/N/P frames are not re-ACKed.)
            if frame["type"] == "C":
                ack = build_frame(frame["msgid"], "A", frame["seq"],
                                  frame["total"], "%s:%d" % (frame["msgid"], frame["seq"]))
                write_line(ser, ack)

                buf = inbox.setdefault(frame["msgid"], {})
                buf[frame["seq"]] = frame["payload"]
                if len(buf) < frame["total"]:
                    continue  # wait for the rest of a chunked command
                command = "".join(buf[i] for i in sorted(buf))
                del inbox[frame["msgid"]]
                log.info("CMD %s: %r", frame["msgid"], command)

                reply = handle_command(command, frame["msgid"])
                log.info("REPLY %s: %r", frame["msgid"], reply)
                send_reply(frame["msgid"], reply)

            elif frame["type"] == "A":
                # Watch ACK for one of our reply chunks: payload "msgid:seq".
                try:
                    a_id, a_seq = frame["payload"].split(":", 1)
                    with un_lock: unacked.pop((a_id, int(a_seq)), None)
                except ValueError:
                    pass
            elif frame["type"] == "N":
                # NACK: resend that chunk on the next loop tick.
                try:
                    n_id, n_seq = frame["payload"].split(":", 1)
                    with un_lock:
                        if (n_id, int(n_seq)) in unacked: unacked[(n_id, int(n_seq))][2] = 0
                except ValueError:
                    pass
            elif frame["type"] == "P":
                log.info("presence from %s", frame["payload"])
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        log.info("serial closed")

# ----------------------------------------------------------------------------
# MESHTASTIC mode  (sketch -- full detail in MESHTASTIC-OPTION.md)
# ----------------------------------------------------------------------------
def run_meshtastic():
    # pip install meshtastic pypubsub
    import meshtastic.serial_interface
    from pubsub import pub

    iface = meshtastic.serial_interface.SerialInterface(devPath=SERIAL_PORT)

    # SAF: Meshtastic mode needs the SAME guarantees as CUSTOM: allowlisted watch node AND a
    # signed JV1 frame (HMAC + counter) inside the text message. Anything else is dropped.
    def on_receive(packet, interface):
        dec = packet.get("decoded", {})
        if dec.get("portnum") != "TEXT_MESSAGE_APP":
            return
        sender = str(packet.get("fromId") or "").lower()
        if sender not in MESH_ALLOW_NODES:
            log.warning("mesh: dropping text from non-allowlisted node")
            return
        frame = parse_frame(dec.get("text") or "")
        if not frame or frame["type"] != "C":
            log.warning("mesh: dropping unsigned/invalid frame")
            return
        log.info("mesh CMD %s: %r", frame["msgid"], frame["payload"])
        reply = handle_command(frame["payload"], frame["msgid"])
        for out in chunk_text(reply, MAX_FRAME, frame["msgid"], "R"):
            interface.sendText(out, destinationId=sender)   # direct to the watch, not broadcast

    pub.subscribe(on_receive, "meshtastic.receive")
    def mesh_push(mid, t):
        for out in chunk_text(t, MAX_FRAME, mid, "R"):
            for node in MESH_ALLOW_NODES:
                iface.sendText(out, destinationId=node)
    start_push_server(mesh_push)
    log.info("Meshtastic bridge up. Ctrl+C to quit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        iface.close()

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # Fail closed at startup (SAF/Cartographer): signing + push secret are mandatory.
    if len(LORA_KEY) < 16:
        sys.exit("Refusing to start: JV_LORA_KEY missing or < 16 bytes (set it in the gitignored .env)")
    if len(PUSH_TOKEN) < 24:
        sys.exit("Refusing to start: JV_PUSH_TOKEN missing or < 24 chars (shared with recon_ingest)")
    if ORCH_CHAT_PATH.rstrip("/").lower() == "/jarvis":
        sys.exit("Refusing to start: JV_RECON_ROUTE must not be the tool-capable /jarvis route")
    if MODE == "MESHTASTIC" and not MESH_ALLOW_NODES:
        sys.exit("Refusing to start MESHTASTIC mode: JV_MESH_ALLOW_NODES (watch node ID) not set - mode disabled")
    if MODE == "MESHTASTIC":
        run_meshtastic()
    else:
        run_custom()
