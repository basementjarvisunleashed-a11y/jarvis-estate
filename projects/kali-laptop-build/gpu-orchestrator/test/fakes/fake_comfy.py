#!/usr/bin/env python3
"""Fake ComfyUI for the GPU orchestrator tests.

Implements the endpoints the orchestrator uses:
  GET /         200 when up (the orchestrator's liveness check)
  GET /queue    {"queue_running": [...], "queue_pending": [...]}
  GET /history  {} (empty)

On start it adds 2000 MiB to the shared VRAM (SD 1.5's footprint) and
logs "started" to comfy.log. On SIGTERM/SIGINT it subtracts the 2000
MiB, logs "stopped", and exits cleanly -- so the orchestrator's
wait_for_vram_below sees the card free after it stops ComfyUI.

If the file `comfy_busy` exists in the state directory, /queue reports
a prompt running. The test creates/removes that file to prove the
orchestrator never kills a running render.

Usage:
  python3 fake_comfy.py --listen 127.0.0.1 --port 8188
  (FAKE_STATE_DIR env var points at the shared test state directory.)
"""

import argparse
import json
import os
import signal
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import fake_gpu  # noqa: E402

CLEANED_UP = False


def cleanup():
    global CLEANED_UP
    if CLEANED_UP:
        return
    CLEANED_UP = True
    fake_gpu.adjust_vram(-fake_gpu.VRAM_COMFY_MIB)
    fake_gpu.append_log("comfy.log", {"t": time.time(), "event": "stopped"})


def handle_signal(signum, _frame):
    cleanup()
    sys.exit(0)


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

    def do_GET(self):
        if self.path == "/":
            self._send(200, {"status": "ComfyUI (fake)"})
        elif self.path == "/queue":
            busy = os.path.exists(os.path.join(fake_gpu.STATE_DIR, "comfy_busy"))
            if busy:
                self._send(
                    200,
                    {
                        "queue_running": [["prompt-id-1", 1]],
                        "queue_pending": [],
                    },
                )
            else:
                self._send(200, {"queue_running": [], "queue_pending": []})
        elif self.path == "/history":
            self._send(200, {})
        else:
            self._send(404, {"error": "unknown path %s" % self.path})


def main():
    parser = argparse.ArgumentParser(description="Fake ComfyUI")
    parser.add_argument("--listen", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8188)
    args = parser.parse_args()
    fake_gpu.ensure_dir()
    fake_gpu.adjust_vram(fake_gpu.VRAM_COMFY_MIB)
    fake_gpu.append_log("comfy.log", {"t": time.time(), "event": "started", "port": args.port})
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    server = ThreadingHTTPServer((args.listen, args.port), Handler)
    print("fake ComfyUI on %s:%s" % (args.listen, args.port), flush=True)
    try:
        server.serve_forever()
    finally:
        cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
