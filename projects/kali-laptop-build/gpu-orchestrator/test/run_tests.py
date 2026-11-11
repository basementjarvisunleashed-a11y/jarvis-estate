#!/usr/bin/env python3
"""Test runner for the GPU orchestrator.

Runs the orchestrator against fake Ollama, fake nvidia-smi and fake
ComfyUI (all local, no Acer, no real GPU) and checks the behaviour
HgX cares about: swaps just happen, in the safe order, and nothing
gets killed or reloaded mid-render.

Scenarios:
  1. state_reporting      mode/models/ComfyUI/VRAM are reported correctly
  2. acquire_llm_noop     acquire llm in LLM mode is a fast no-op
  3. acquire_comfy        parks the 9B, starts ComfyUI, mode becomes comfy
  4. acquire_llm_from_comfy  stops ComfyUI, loads 9B BEFORE 27B, 27B with
                          num_gpu 0, no eviction of the 9B
  5. keepalive_skip       keep-alive skips the 9B in comfy mode, pings
                          both in llm mode
  6. router_fail_open     router helper fails open when the orchestrator
                          is down, and triggers a swap when it is up
  7. comfy_busy_not_killed  a running render is not killed; the acquire
                          reports busy and ComfyUI survives

Usage:
  python3 test/run_tests.py
Exit code 0 if every scenario passes, 1 otherwise. On failure the temp
state directory is left in place and its path is printed.
"""

import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # the gpu-orchestrator folder
FAKES = os.path.join(HERE, "fakes")
sys.path.insert(0, FAKES)
sys.path.insert(0, ROOT)
import fake_gpu  # noqa: E402
import router_integration  # noqa: E402


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def http_get(url, timeout=10):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            return resp.status, json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except (urllib.error.URLError, OSError, TimeoutError):
        return None, None


def http_post(url, payload, timeout=120):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            return resp.status, json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", "replace")
            return exc.code, json.loads(body) if body else None
        except ValueError:
            return exc.code, None
    except (urllib.error.URLError, OSError, TimeoutError):
        return None, None


def wait_for_http(url, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        status, _data = http_get(url, timeout=5)
        if status == 200:
            return True
        time.sleep(1)
    return False


class Ctx:
    def __init__(self):
        self.tmp = tempfile.mkdtemp(prefix="gpu-orchestrator-test-")
        self.state_dir = os.path.join(self.tmp, "state")
        os.makedirs(self.state_dir)
        self.bin_dir = os.path.join(self.tmp, "bin")
        os.makedirs(self.bin_dir)
        self.ollama_port = free_port()
        self.comfy_port = free_port()
        self.orch_port = free_port()
        self.orch_url = "http://127.0.0.1:%s" % self.orch_port
        self.ollama_url = "http://127.0.0.1:%s" % self.ollama_port
        self.comfy_url = "http://127.0.0.1:%s" % self.comfy_port
        self.orch_proc = None
        self.fake_ollama_proc = None
        self.results = []

    # -- paths ------------------------------------------------------
    def state_file(self, name):
        return os.path.join(self.state_dir, name)

    def orch_state_file(self):
        return os.path.join(self.tmp, "gpu-state.json")

    def orch_log_file(self):
        return os.path.join(self.tmp, "gpu-orchestrator.log")

    def comfy_dir(self):
        return os.path.join(self.tmp, "ComfyUI")

    # -- processes --------------------------------------------------
    def env(self):
        env = dict(os.environ)
        env["FAKE_STATE_DIR"] = self.state_dir
        env["PATH"] = self.bin_dir + os.pathsep + env.get("PATH", "")
        env["GPU_ORCH_OLLAMA_URL"] = self.ollama_url
        env["GPU_ORCH_COMFY_URL"] = self.comfy_url
        env["GPU_ORCH_COMFY_PORT"] = str(self.comfy_port)
        env["GPU_ORCH_COMFY_DIR"] = self.comfy_dir()
        env["GPU_ORCH_COMFY_PYTHON"] = sys.executable
        env["GPU_ORCH_COMFY_MAIN"] = os.path.join(FAKES, "fake_comfy.py")
        env["GPU_ORCH_COMFY_LOG"] = os.path.join(self.tmp, "comfyui.log")
        env["GPU_ORCH_COMFY_PID_FILE"] = os.path.join(self.tmp, "comfyui.pid")
        env["GPU_ORCH_STATE_FILE"] = self.orch_state_file()
        env["GPU_ORCH_LOG_FILE"] = self.orch_log_file()
        env["GPU_ORCH_IDLE_RESTORE_MIN"] = "0"
        env["GPU_ORCH_COMFY_GRACE_S"] = "10"
        return env

    def start_fake_ollama(self):
        cmd = [
            sys.executable,
            os.path.join(FAKES, "fake_ollama_server.py"),
            "--port",
            str(self.ollama_port),
            "--state-dir",
            self.state_dir,
        ]
        self.fake_ollama_proc = subprocess.Popen(
            cmd, env=self.env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if not wait_for_http(self.ollama_url + "/api/ps", timeout=15):
            raise RuntimeError("fake Ollama did not come up")

    def start_orchestrator(self):
        cmd = [
            sys.executable,
            os.path.join(ROOT, "gpu_orchestrator.py"),
            "--serve",
            "--port",
            str(self.orch_port),
        ]
        self.orch_proc = subprocess.Popen(
            cmd, env=self.env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if not wait_for_http(self.orch_url + "/health", timeout=15):
            raise RuntimeError("orchestrator did not come up")

    def stop_orchestrator(self):
        if self.orch_proc is not None:
            self.orch_proc.terminate()
            try:
                self.orch_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.orch_proc.kill()
            self.orch_proc = None

    def cleanup(self):
        self.stop_orchestrator()
        if self.fake_ollama_proc is not None:
            self.fake_ollama_proc.terminate()
            try:
                self.fake_ollama_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.fake_ollama_proc.kill()
            self.fake_ollama_proc = None
        # If a fake ComfyUI is still running, stop it via the orchestrator
        # state (it is a session leader; kill its process group by PID file).
        pid_file = os.path.join(self.tmp, "comfyui.pid")
        try:
            with open(pid_file) as fh:
                pid = int(fh.read().strip())
            try:
                os.killpg(pid, signal.SIGTERM)
            except (OSError, ProcessLookupError):
                pass
        except (OSError, ValueError):
            pass

    # -- fake state -------------------------------------------------
    def models(self):
        return fake_gpu.read_models()

    def vram(self):
        return fake_gpu.read_vram()

    def ollama_calls(self):
        return fake_gpu.read_log("ollama_calls.log")

    def orch_state(self):
        status, data = http_get(self.orch_url + "/state", timeout=10)
        return data if status == 200 else None

    def acquire(self, purpose, timeout=120):
        return http_post(
            self.orch_url + "/acquire",
            {"purpose": purpose, "holder": "test", "wait": True},
            timeout=timeout,
        )

    def record(self, name, passed, detail):
        self.results.append((name, passed, detail))
        print("%s %s -- %s" % ("PASS" if passed else "FAIL", name, detail), flush=True)


# ---------------------------------------------------------------- scenarios

def scenario_state_reporting(ctx):
    st = ctx.orch_state()
    if st is None:
        return False, "GET /state returned nothing"
    ok = (
        st.get("mode") == "llm"
        and st.get("nine_b") == "resident"
        and st.get("twenty_seven_b") == "resident"
        and st.get("comfy") == "stopped"
        and st.get("vram_used_mib") == 4962
        and st.get("vram_total_mib") == 6144
    )
    return ok, "state=%s" % json.dumps(st, sort_keys=True)


def scenario_acquire_llm_noop(ctx):
    before = len(ctx.ollama_calls())
    status, data = ctx.acquire("llm")
    after = len(ctx.ollama_calls())
    ok = (
        status == 200
        and data is not None
        and data.get("ok") is True
        and data.get("mode") == "llm"
        and after == before
    )
    return ok, "status=%s mode=%s new_calls=%s" % (status, data.get("mode") if data else None, after - before)


def scenario_acquire_comfy(ctx):
    before = len(ctx.ollama_calls())
    status, data = ctx.acquire("comfy")
    if status != 200 or not data or not data.get("ok"):
        return False, "acquire comfy failed: status=%s data=%s" % (status, data)
    models = ctx.models()
    vram = ctx.vram()
    comfy_up = http_get(ctx.comfy_url + "/", timeout=5)[0] == 200
    new_calls = ctx.ollama_calls()[before:]
    stopped_9b = any(c.get("action") == "stop" and c.get("model") == "qwen9b-abliterated" for c in new_calls)
    ok = (
        data.get("mode") == "comfy"
        and "qwen9b-abliterated" not in models
        and "huihui_ai/Qwen3.8-abliterated:27b" in models
        and comfy_up
        and stopped_9b
        and 2000 <= vram.get("used_mib", 0) <= 2200
    )
    return ok, "mode=%s 9b_parked=%s 27b=%s comfy_up=%s stopped_9b=%s vram=%s" % (
        data.get("mode"),
        "qwen9b-abliterated" not in models,
        "huihui_ai/Qwen3.8-abliterated:27b" in models,
        comfy_up,
        stopped_9b,
        vram.get("used_mib"),
    )


def scenario_acquire_llm_from_comfy(ctx):
    before = len(ctx.ollama_calls())
    status, data = ctx.acquire("llm")
    if status != 200 or not data or not data.get("ok"):
        return False, "acquire llm failed: status=%s data=%s" % (status, data)
    models = ctx.models()
    vram = ctx.vram()
    comfy_up = http_get(ctx.comfy_url + "/", timeout=5)[0] == 200
    new_calls = ctx.ollama_calls()[before:]
    loads = [c for c in new_calls if c.get("action") == "load"]
    order_ok = (
        len(loads) >= 2
        and loads[0].get("model") == "qwen9b-abliterated"
        and loads[1].get("model") == "huihui_ai/Qwen3.8-abliterated:27b"
    )
    num_gpu_ok = loads[1].get("num_gpu") == 0 if len(loads) >= 2 else False
    no_eviction = not any(c.get("evicted_9b") for c in new_calls)
    # The 9B load evicted the 27B (the real Acer failure); the
    # orchestrator must have restored it afterwards, in safe order.
    restored_after_eviction = bool(loads) and loads[0].get("evicted_27b") is True
    ok = (
        data.get("mode") == "llm"
        and not comfy_up
        and "qwen9b-abliterated" in models
        and "huihui_ai/Qwen3.8-abliterated:27b" in models
        and order_ok
        and num_gpu_ok
        and no_eviction
        and restored_after_eviction
        and vram.get("used_mib") == 4962
    )
    return ok, "mode=%s comfy_up=%s order_ok=%s num_gpu_0=%s no_eviction=%s restored_after_eviction=%s vram=%s loads=%s" % (
        data.get("mode"),
        comfy_up,
        order_ok,
        num_gpu_ok,
        no_eviction,
        restored_after_eviction,
        vram.get("used_mib"),
        [(c.get("model"), c.get("num_gpu")) for c in loads],
    )


def scenario_keepalive_skip(ctx):
    script = os.path.join(ROOT, "keep-brains-alive-v2.sh")
    env = ctx.env()
    env["GPU_ORCH_STATE_FILE"] = ctx.orch_state_file()
    env["GPU_ORCH_COMFY_URL"] = ctx.comfy_url
    env["GPU_ORCH_OLLAMA_URL"] = ctx.ollama_url

    # Case 1: mode is comfy -> skip the 9B, ping the 27B.
    with open(ctx.orch_state_file(), "w") as fh:
        json.dump({"mode": "comfy", "nine_b": "parked"}, fh)
    proc = subprocess.run(
        ["bash", script, "--dry-run"], env=env, capture_output=True, text=True, timeout=30
    )
    out1 = proc.stdout + proc.stderr
    comfy_ok = (
        "skipping 9B" in out1
        and "would ping 27B" in out1
        and "would ping 9B" not in out1
    )

    # Case 2: mode is llm and ComfyUI is down -> ping both.
    with open(ctx.orch_state_file(), "w") as fh:
        json.dump({"mode": "llm", "nine_b": "resident"}, fh)
    proc = subprocess.run(
        ["bash", script, "--dry-run"], env=env, capture_output=True, text=True, timeout=30
    )
    out2 = proc.stdout + proc.stderr
    llm_ok = "would ping 9B" in out2 and "would ping 27B" in out2 and "skipping 9B" not in out2
    ok = comfy_ok and llm_ok
    return ok, "comfy_case_ok=%s llm_case_ok=%s" % (comfy_ok, llm_ok)


def scenario_router_fail_open(ctx):
    # Orchestrator down: the router helper must fail open.
    ctx.stop_orchestrator()
    time.sleep(1)
    result_down = router_integration.ensure_gpu_llm(timeout=10, orchestrator_url=ctx.orch_url)
    down_ok = result_down.get("ok") is True and result_down.get("orchestrator") == "unreachable"

    # Orchestrator up, GPU in comfy mode: the helper must trigger a swap.
    ctx.start_orchestrator()
    status, data = ctx.acquire("comfy")
    if status != 200 or not data or not data.get("ok"):
        return False, "setup acquire comfy failed: %s %s" % (status, data)
    result_up = router_integration.ensure_gpu_llm(timeout=120, orchestrator_url=ctx.orch_url)
    st = ctx.orch_state()
    up_ok = result_up.get("ok") is True and st is not None and st.get("mode") == "llm"
    ok = down_ok and up_ok
    return ok, "down_fail_open=%s up_swapped_back=%s (mode=%s)" % (
        down_ok,
        up_ok,
        st.get("mode") if st else None,
    )


def scenario_comfy_busy_not_killed(ctx):
    status, data = ctx.acquire("comfy")
    if status != 200 or not data or not data.get("ok"):
        return False, "setup acquire comfy failed: %s %s" % (status, data)
    # Make the fake ComfyUI report a running render.
    busy_file = os.path.join(ctx.state_dir, "comfy_busy")
    with open(busy_file, "w") as fh:
        fh.write("1")
    status, data = ctx.acquire("llm", timeout=120)
    busy_failed_gracefully = (
        status == 503
        and data is not None
        and data.get("ok") is False
        and "busy" in str(data.get("error", "")).lower()
    )
    comfy_survived = http_get(ctx.comfy_url + "/", timeout=5)[0] == 200
    # Queue drains: remove the busy flag and acquire again.
    try:
        os.remove(busy_file)
    except OSError:
        pass
    status2, data2 = ctx.acquire("llm", timeout=120)
    recovered = status2 == 200 and data2 is not None and data2.get("ok") is True and data2.get("mode") == "llm"
    ok = busy_failed_gracefully and comfy_survived and recovered
    return ok, "busy_refused=%s comfy_survived=%s recovered=%s" % (
        busy_failed_gracefully,
        comfy_survived,
        recovered,
    )


# ---------------------------------------------------------------- main

def main():
    ctx = Ctx()
    # Install the fake `ollama` and `nvidia-smi` on PATH for the orchestrator.
    # Symlinks (not copies) so the fakes resolve fake_gpu.py via realpath.
    for name in ("ollama", "nvidia-smi"):
        src = os.path.join(FAKES, name)
        dst = os.path.join(ctx.bin_dir, name)
        os.symlink(src, dst)
    # Shared fake state: 9B on VRAM, 27B on CPU, ComfyUI stopped.
    fake_gpu.STATE_DIR = ctx.state_dir
    fake_gpu.reset_state()
    failed = False
    try:
        ctx.start_fake_ollama()
        ctx.start_orchestrator()
        scenarios = [
            ("state_reporting", scenario_state_reporting),
            ("acquire_llm_noop", scenario_acquire_llm_noop),
            ("acquire_comfy", scenario_acquire_comfy),
            ("acquire_llm_from_comfy", scenario_acquire_llm_from_comfy),
            ("keepalive_skip", scenario_keepalive_skip),
            ("router_fail_open", scenario_router_fail_open),
            ("comfy_busy_not_killed", scenario_comfy_busy_not_killed),
        ]
        for name, fn in scenarios:
            try:
                passed, detail = fn(ctx)
            except Exception as exc:  # noqa: BLE001 - report, do not crash
                passed, detail = False, "exception: %s" % exc
            ctx.record(name, passed, detail)
            if not passed:
                failed = True
    finally:
        ctx.cleanup()
    passed_n = sum(1 for _n, p, _d in ctx.results if p)
    total = len(ctx.results)
    print("---")
    print("%s/%s scenarios passed" % (passed_n, total))
    if failed:
        print("state directory left at: %s" % ctx.tmp)
        return 1
    shutil.rmtree(ctx.tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
