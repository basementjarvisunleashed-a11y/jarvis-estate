# GPU Orchestrator

Makes VRAM swaps on the Acer automatic, so HgX never has to say "swap" or
run a manual park/resume — it just happens, through the router.

**Status: built and verified here. NOT deployed to the Acer, NOT delivered
to HgX.** Deployment is a separate step, on HgX's word (see
`DESIGN.md` → "Deploying later").

## Files

| File | What it is |
|---|---|
| `gpu_orchestrator.py` | The service (stdlib only). HTTP on 127.0.0.1:11436, CLI, dry-run. |
| `DESIGN.md` | The full design: states, operations, safe rules, router and keep-alive contracts, failure modes, deployment steps. |
| `router_integration.py` | Drop-in helper for the router (easy route only). Fail open when the orchestrator is down; fail closed when the GPU is busy. |
| `keep-brains-alive-v2.sh` | Patched keep-alive: skips the 9B ping while it is parked. |
| `start-gpu-orchestrator.sh` | Launcher for autostart (not yet installed). |
| `gpu-orchestrator.desktop` | Xfce autostart entry (not yet installed). |
| `test/` | Fake Ollama / nvidia-smi / ComfyUI harness and the test runner. |

## Verify (here, no Acer needed)

```bash
cd ~/workspace/family-bot/gpu-orchestrator
python3 -m py_compile gpu_orchestrator.py router_integration.py
python3 test/run_tests.py
```

The test runner prints PASS/FAIL per scenario and exits non-zero if
anything fails. It covers: state reporting, the fast-path no-op, the
comfy acquire (park 9B, start ComfyUI), the LLM acquire from COMFY mode
(stop ComfyUI, load 9B **before** 27B, 27B with `num_gpu 0`, no eviction),
the keep-alive skip logic, the router helper failing open when the
orchestrator is down, and a busy ComfyUI not being killed.

## The one-line summary

One service owns the 6 GB card. Callers ask by purpose (`llm` or
`comfy`); the service parks and loads in the safe order and reports the
state. The router asks before an easy call. The keep-alive reads the
state file and never reloads a parked 9B mid-render.
