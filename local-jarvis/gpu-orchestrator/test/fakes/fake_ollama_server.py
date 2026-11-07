#!/usr/bin/env python3
"""Fake Ollama HTTP server for the GPU orchestrator tests.

Implements the two endpoints the orchestrator uses:
  GET  /api/ps    list loaded models (from the shared models.json)
  POST /api/chat  load/unload a model, return a canned "Pong" reply

It models the real VRAM behaviour the orchestrator must respect:
  - Loading the 9B adds 4830 MiB to VRAM (unless already loaded).
  - Loading the 27B adds nothing to VRAM (it lives on CPU) -- but only
    if it is loaded with num_gpu 0. If the 27B is loaded WITHOUT
    num_gpu 0, the fake EVICTS the 9B (removes it, frees its VRAM) and
    records evicted_9b=true in the call log. That is how the test proves
    the orchestrator always passes num_gpu 0 for the 27B.
  - Reloading the 9B (a fresh load) while the 27B is resident EVICTS
    the 27B (records evicted_27b=true). That is the failure observed on
    the Acer; it is how the test proves the orchestrator restores the
    27B afterwards, in the safe order (9B first, then 27B).
  - A call with keep_alive 0 unloads the model.

Every call is appended to ollama_calls.log (JSON lines) so the test can
verify the load order (9B before 27B) and the num_gpu values.

Usage:
  python3 fake_ollama_server.py --port 11434 --state-dir /tmp/state
  (FAKE_STATE_DIR env var also works; --state-dir wins.)
"""

import argparse
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import fake_gpu  # noqa: E402


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
        if self.path == "/api/ps":
            models = fake_gpu.read_models()
            entries = []
            for name, info in models.items():
                entries.append(
                    {
                        "name": name,
                        "model": name,
                        "size": info.get("size", ""),
                        "details": {"parameter_size": info.get("size", "")},
                        "processor": info.get("processor", ""),
                    }
                )
            self._send(200, {"models": entries})
        else:
            self._send(404, {"error": "unknown path %s" % self.path})

    def do_POST(self):
        if self.path != "/api/chat":
            self._send(404, {"error": "unknown path %s" % self.path})
            return
        body = self._read_json()
        model = str(body.get("model", ""))
        keep_alive = body.get("keep_alive", "24h")
        options = body.get("options") or {}
        num_gpu = options.get("num_gpu")
        models = fake_gpu.read_models()
        entry = {
            "t": time.time(),
            "model": model,
            "num_gpu": num_gpu,
            "keep_alive": keep_alive,
        }

        # keep_alive 0 unloads the model.
        if keep_alive == 0 or keep_alive == "0":
            if model in models:
                del models[model]
                fake_gpu.write_models(models)
                if model == fake_gpu.NINE_B:
                    fake_gpu.adjust_vram(-fake_gpu.VRAM_NINE_B_MIB)
            entry["action"] = "unload"
            fake_gpu.append_log("ollama_calls.log", entry)
            self._send(200, {"model": model, "message": {"role": "assistant", "content": "unloaded"}, "done": True})
            return

        # Load the model.
        evicted_9b = False
        evicted_27b = False
        if model == fake_gpu.TWENTY_SEVEN_B and num_gpu != 0:
            # Real behaviour: the 27B cannot live on a 6 GB card, and
            # trying evicts the 9B. Model it so the test can catch it.
            if fake_gpu.NINE_B in models:
                del models[fake_gpu.NINE_B]
                fake_gpu.adjust_vram(-fake_gpu.VRAM_NINE_B_MIB)
                evicted_9b = True
            models[model] = {"processor": "100% CPU (spilled)", "size": "18 GB", "context": 4096}
        elif model == fake_gpu.TWENTY_SEVEN_B:
            models[model] = {"processor": "100% CPU", "size": "18 GB", "context": 4096}
        elif model == fake_gpu.NINE_B:
            if model not in models:
                fake_gpu.adjust_vram(fake_gpu.VRAM_NINE_B_MIB)
                # Real behaviour (observed on the Acer): reloading the 9B
                # while the 27B is resident can evict the 27B. Model it
                # deterministically so the test proves the orchestrator
                # restores the 27B afterwards, in the safe order.
                if fake_gpu.TWENTY_SEVEN_B in models:
                    del models[fake_gpu.TWENTY_SEVEN_B]
                    evicted_27b = True
            models[model] = {"processor": "20%/80% CPU/GPU", "size": "6.1 GB", "context": 8192}
        else:
            models[model] = {"processor": "100% CPU", "size": "1 GB", "context": 4096}
        fake_gpu.write_models(models)
        entry["action"] = "load"
        entry["evicted_9b"] = evicted_9b
        entry["evicted_27b"] = evicted_27b
        fake_gpu.append_log("ollama_calls.log", entry)
        self._send(
            200,
            {
                "model": model,
                "created_at": "2026-11-06T22:00:00Z",
                "message": {"role": "assistant", "content": "Pong"},
                "done": True,
            },
        )


def main():
    parser = argparse.ArgumentParser(description="Fake Ollama server")
    parser.add_argument("--port", type=int, default=11434)
    parser.add_argument("--state-dir", default=None)
    args = parser.parse_args()
    if args.state_dir:
        fake_gpu.STATE_DIR = args.state_dir
    fake_gpu.ensure_dir()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print("fake Ollama on 127.0.0.1:%s (state %s)" % (args.port, fake_gpu.STATE_DIR), flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
