"""Shared state helpers for the GPU orchestrator test fakes.

All fakes share one state directory (FAKE_STATE_DIR), containing:
  models.json       loaded Ollama models {name: {processor, size, context}}
  vram.json         {"used_mib": N, "total_mib": 6144}
  ollama_calls.log  JSON lines, one per Ollama load/unload/stop call
  comfy.log         lines logged by the fake ComfyUI (start/stop)
  comfy_busy        present (any content) means a render is running

Writes are atomic (temp file + rename) so a reader never sees a half
written file. The fakes are sequential in the test, so no locking is
needed beyond that.
"""

import json
import os

STATE_DIR = os.environ.get("FAKE_STATE_DIR", "/tmp/gpu-orchestrator-test-state")

NINE_B = "qwen9b-abliterated"
TWENTY_SEVEN_B = "huihui_ai/Qwen3.8-abliterated:27b"

# VRAM (MiB) each tenant holds. Desktop alone is 132 MiB.
VRAM_DESKTOP_MIB = 132
VRAM_NINE_B_MIB = 4830
VRAM_COMFY_MIB = 2000
VRAM_TOTAL_MIB = 6144


def _path(name):
    return os.path.join(STATE_DIR, name)


def ensure_dir():
    os.makedirs(STATE_DIR, exist_ok=True)


def read_json(name, default):
    try:
        with open(_path(name)) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def write_json(name, data):
    ensure_dir()
    tmp = _path(name) + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, _path(name))


def append_log(name, entry):
    ensure_dir()
    with open(_path(name), "a") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def read_log(name):
    try:
        with open(_path(name)) as fh:
            return [json.loads(line) for line in fh if line.strip()]
    except (OSError, ValueError):
        return []


def read_vram():
    return read_json("vram.json", {"used_mib": VRAM_DESKTOP_MIB, "total_mib": VRAM_TOTAL_MIB})


def write_vram(used_mib):
    write_json("vram.json", {"used_mib": used_mib, "total_mib": VRAM_TOTAL_MIB})


def adjust_vram(delta_mib):
    vram = read_vram()
    used = max(0, vram.get("used_mib", VRAM_DESKTOP_MIB) + delta_mib)
    write_vram(used)
    return used


def read_models():
    return read_json("models.json", {})


def write_models(models):
    write_json("models.json", models)


def reset_state():
    """Initial fake GPU: 9B on VRAM, 27B on CPU, ComfyUI stopped."""
    write_models(
        {
            NINE_B: {"processor": "20%/80% CPU/GPU", "size": "6.1 GB", "context": 8192},
            TWENTY_SEVEN_B: {"processor": "100% CPU", "size": "18 GB", "context": 4096},
        }
    )
    write_vram(VRAM_DESKTOP_MIB + VRAM_NINE_B_MIB)
    for name in ("ollama_calls.log", "comfy.log"):
        try:
            os.remove(_path(name))
        except OSError:
            pass
    try:
        os.remove(_path("comfy_busy"))
    except OSError:
        pass
