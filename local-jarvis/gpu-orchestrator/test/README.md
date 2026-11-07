# GPU orchestrator tests

Runs the orchestrator against fake Ollama, fake `nvidia-smi` and fake
ComfyUI — all local, no Acer, no real GPU.

## Run

```bash
cd ~/workspace/family-bot/gpu-orchestrator
python3 test/run_tests.py
```

Prints PASS/FAIL per scenario and exits 0 only if every scenario passes.
On failure the temp state directory is left in place and its path is
printed, so the fake Ollama call log and the orchestrator log can be
inspected.

## What the fakes model

- **Fake Ollama server** (`fakes/fake_ollama_server.py`): `/api/ps` and
  `/api/chat`. Loading the 9B adds 4830 MiB to VRAM; loading the 27B
  adds nothing (CPU) — but only if it is loaded with `num_gpu 0`. Load
  the 27B without `num_gpu 0` and it **evicts the 9B**, exactly like the
  real failure. Every call is logged to `ollama_calls.log`.
- **Fake `ollama` CLI** (`fakes/ollama`): `ps` and `stop`. The
  orchestrator parks the 9B with `ollama stop`, as on the Acer.
- **Fake `nvidia-smi`** (`fakes/nvidia-smi`): prints VRAM used/total
  from the shared `vram.json`, which the other fakes keep up to date.
- **Fake ComfyUI** (`fakes/fake_comfy.py`): `/` (200 when up), `/queue`
  (running/pending), `/history`. Adds 2000 MiB to VRAM on start,
  removes it on a clean stop. If `comfy_busy` exists in the state
  directory, `/queue` reports a prompt running.

## Scenarios

See `run_tests.py`: state reporting, the LLM fast-path no-op, the comfy
acquire (park 9B, start ComfyUI), the LLM acquire from COMFY mode (stop
ComfyUI, load 9B **before** 27B, 27B with `num_gpu 0`, no eviction),
the keep-alive skip logic, the router helper failing open when the
orchestrator is down, and a busy ComfyUI not being killed.
