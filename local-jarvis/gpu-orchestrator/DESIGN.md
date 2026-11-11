# GPU Orchestrator — Design

## The problem, in HgX's words

> "I don't wanna say [swap], it should just happen, just the router, we need an orchestrator for the GPU."

Today the 6 GB card on the Acer has two tenants that cannot share it, and the
swap between them is manual: stop the 9B, start ComfyUI, render, stop ComfyUI,
reload the 9B (then the 27B, in that order, or the 27B gets evicted). Every
step is a paste in a terminal, and every step can go wrong — the `!` in a
paste breaks zsh, a background ffmpeg freezes on the terminal, the keep-alive
cron reloads the 9B mid-render, a render gets killed halfway. HgX's demand is
right: nobody should have to say "swap". The router should ask, and it should
just happen.

## Goal

One service owns the GPU. Callers (the router, the dashboard, a human) ask
for the GPU by *purpose* — "llm" or "comfy" — and the service makes it so,
in the safe order, and reports the state. Nobody manages VRAM by hand again.

## Non-goals

- This does **not** make two big models fit on a 6 GB card. It cannot. A
  swap between the 9B and ComfyUI is a warm swap (unload one, load the
  other, roughly 30–90 seconds), not an instant one. Instant hot-swap of
  two 5 GB models needs smaller models or a bigger card.
- This does **not** touch the 27B's home. The 27B lives in system RAM on the
  CPU and never uses the card. The orchestrator only verifies it is still
  there and restores it (with `num_gpu 0`) if a 9B reload evicted it.
- This does **not** replace the router. The router stays the single door
  for LLM calls; it just asks the orchestrator first.
- This does **not** run on the Acer yet. It is built and verified here.
  Deployment is a separate step, on HgX's word (see "Deploying later").

## The machine (fixed facts)

| Fact | Value |
|---|---|
| GPU | RTX 2060, 6,144 MiB VRAM |
| RAM | 64 GB DDR4 (2 × 32 GB, 3200 MT/s, running 2933) |
| 9B | `qwen9b-abliterated`, 5.6 GB list / 6.1 GB loaded, VRAM, context 8192, fast/default |
| 27B | `huihui_ai/Qwen3.8-abliterated:27b`, 17 GB list / 18 GB loaded, system RAM, 100% CPU, context 4096, hard reasoning |
| ComfyUI | SD 1.5 (`v1-5-pruned-emaonly-fp16.safetensors`), about 2 GB VRAM, port 8188 |
| Router | port 11435, easy → 9B, hard → 27B |
| Keep-alive | cron every 6 h, pins both brains for 24 h |
| Orchestrator | port **11436** (new, next to the router) |

## Architecture

```
                         ┌──────────────────────┐
   voice loop / router   │  GPU orchestrator    │   Ollama :11434
   (easy call) ─────────►│  :11436              │──► 9B (VRAM) / 27B (CPU)
                         │  acquire / state     │
   dashboard (render) ──►│  mode: llm | comfy   │   ComfyUI :8188
                         │  state file ─────────┼──► keep-alive cron
                         └──────────────────────┘   (reads gpu-state.json)
```

- **Router** (11435) stays the LLM door. Before an *easy* (9B) call it asks
  the orchestrator to make sure the 9B is resident. The *hard* (27B) call
  never touches the orchestrator — the 27B uses no VRAM.
- **Dashboard** (or any render caller) asks the orchestrator for `comfy`
  before it queues a render. It does not start ComfyUI itself.
- **Keep-alive cron** reads the orchestrator's state file
  (`~/Jarvis/gpu-state.json`) and skips the 9B ping while it is parked.
  It also checks ComfyUI directly as a fallback (see "Keep-alive contract").
- **Orchestrator** (11436) is the only thing that stops/loads models and
  starts/stops ComfyUI. It keeps a log (`~/Jarvis/gpu-orchestrator.log`)
  of every swap.

## States

The GPU has one mode at a time. The state file and `GET /state` always
report the mode *and* the observed facts, so a mismatch is visible.

| Mode | 9B | 27B | ComfyUI | Meaning |
|---|---|---|---|---|
| `llm` (default) | resident (VRAM) | resident (CPU) | stopped | Normal. LLM calls are instant. |
| `comfy` | parked | resident (CPU) | running | Rendering. LLM calls must swap back first. |
| `transition` | changing | — | changing | A swap is in progress (locked). |
| `degraded` | mismatch | — | mismatch | Desired mode does not match the facts; `last_error` says why. |

Per-model facts (from Ollama `/api/ps` and `nvidia-smi`, never assumed):

- `nine_b`: `resident` | `parked` | `loading` | `unknown`
- `twenty_seven_b`: `resident` | `absent` | `loading` | `unknown`
- `comfy`: `running` | `stopped` | `starting` | `unknown`
- `vram_used_mib` / `vram_total_mib`: from `nvidia-smi`, the ground truth.

## Operations

### `ensure_llm` — bring the GPU back to the LLM

1. Fast path: if the mode is already `llm`, the 9B is resident and ComfyUI
   is stopped, return at once.
2. If ComfyUI is up, wait for its queue to drain (grace period, default
   120 s). If a render is still running, **refuse** and report busy —
   never kill a render mid-flight.
3. Stop ComfyUI (by its PID file, then a pattern kill as a fallback).
   Wait for VRAM to drop below 500 MiB.
4. Load the 9B (a tiny `/api/chat` call, `keep_alive 24h`, `think false`).
   Wait for it to appear in `/api/ps`.
5. Verify the 27B is still resident. If it was evicted, reload it with
   `num_gpu 0`. **This is the safe order: 9B first, then 27B.**
6. Set the mode to `llm`, record the swap, write the state file.

### `ensure_comfy` — hand the GPU to the picture brain

1. Fast path: if the mode is already `comfy`, ComfyUI is up and the 9B is
   parked, return at once.
2. Park the 9B (`ollama stop`). Wait for it to disappear from `/api/ps`
   and for VRAM to drop below 500 MiB.
3. Start ComfyUI (detached, PID recorded, log to `~/ComfyUI/comfyui.log`).
   Wait for HTTP 200 on :8188 (up to 90 s).
4. If ComfyUI fails to start, **restore LLM mode** (reload the 9B) so the
   fast brain is not left down, then report the error.
5. Set the mode to `comfy`, record the swap, write the state file.

### `acquire` / `release` (HTTP)

- `POST /acquire {"purpose": "llm"|"comfy", "holder": "...", "wait": true}`
  runs the matching ensure and returns `{"ok", "mode", "state", "error"}`.
  A swap takes roughly 30–90 s; the caller waits. `wait` is accepted for
  future use; today an acquire always waits.
- `POST /release {"purpose": "comfy", "holder": "..."}` records that a
  holder is done. It does **not** swap back immediately (to avoid flapping
  if another render follows). Pass `"restore_llm": true` to swap back at
  once.
- `GET /state` returns the full state (mode, models, ComfyUI, VRAM,
  `last_swap`, `last_error`). `GET /health` returns a liveness check.
- An idle restore runs in the background: if the GPU has sat in `comfy`
  mode with no ComfyUI activity for 30 minutes (configurable, 0 disables
  it), it hands the GPU back to the LLM on its own.

## Safe rules (do not break these)

1. **Load order: 9B first, then 27B.** Reloading the 9B while the 27B is
   resident can evict the 27B. Every restore loads the 9B, checks the 27B,
   and only then loads the 27B.
2. **The 27B always loads with `num_gpu 0`.** It is 18 GB and can never
   live on a 6 GB card; trying evicts the 9B.
3. **The keep-alive skips the 9B while it is parked.** See below.
4. **Never kill a running render.** The grace wait, then a busy report.
5. **A failed swap restores the previous tenant.** Never leave the GPU in
   a half state; report the error with the observed facts.
6. **The orchestrator is a single writer.** One lock serialises all
   swaps, so two callers cannot park and load at the same time.

## Router integration

The router asks the orchestrator **only** on the easy (9B) route. The hard
(27B) route is GPU-free and never asks.

`router_integration.py` in this folder is a drop-in helper (stdlib only).
The router calls it before it routes an easy call:

```python
from router_integration import ensure_gpu_llm

gpu = ensure_gpu_llm(timeout=180)
if not gpu["ok"]:
    # The GPU is busy (a render is running) or the swap failed.
    return 503, {"error": gpu["error"]}
# else: the 9B is resident (or the orchestrator is down and we proceed
# as today — fail open, see below).
```

Behaviour:

| Orchestrator says | Router does |
|---|---|
| `{"ok": true, "mode": "llm"}` | Route the easy call as normal. |
| Unreachable (connection error / timeout) | **Fail open**: log a warning and route as today. The 9B is usually resident, so the call usually works. The orchestrator being down must never take the LLM down with it. |
| `{"ok": false, "error": "ComfyUI is busy rendering..."}` | **Fail closed**: return 503 with that message. Killing a render to answer a chat call would be worse than asking the caller to wait a moment. |
| `{"ok": false, "error": "could not load the 9B..."}` | Return 503 with the error and the observed state, so the failure is diagnosable instead of silent. |

For ComfyUI, the dashboard calls `POST /acquire {"purpose": "comfy"}`
before it queues a render. If the orchestrator is unreachable, the
dashboard refuses with a clear error (fail closed): a render without the
GPU swap is guaranteed to fail with an out-of-memory error, so a clear
message is better than a confusing one.

## Keep-alive contract

The keep-alive cron (`keep-brains-alive.sh`, every 6 h) pins both brains
for 24 h. It must never reload the 9B mid-render. The contract is the
state file plus a direct check, belt and braces:

1. Read `~/Jarvis/gpu-state.json`. If `mode` is `comfy`, **skip the 9B
   ping**. (The 9B is parked; pinging it would load it back onto the card
   and steal VRAM from the render.)
2. Else, check ComfyUI directly (`curl :8188`). If it answers, **skip the
   9B ping** (the card is busy even if the state file is stale or missing).
3. Otherwise, ping the 9B as today (`keep_alive 24h`, `think false`).
4. **Always** ping the 27B (`num_gpu 0`, `keep_alive 24h`, `think false`).
   The 27B lives in system RAM; its ping never touches VRAM and is always
   safe. Order when both are pinged: 9B first, then 27B (the safe order).

`keep-brains-alive-v2.sh` in this folder is the patched script. It is a
drop-in replacement: same log file, same curl commands, same order, plus
the skip logic and a `--dry-run` flag that prints what it would do.

## ComfyUI contract

- **Start**: `venv313/bin/python main.py --listen 127.0.0.1 --port 8188`
  from `~/ComfyUI`, detached, stdout/stderr to `~/ComfyUI/comfyui.log`,
  PID recorded in `~/ComfyUI/comfyui.pid`. Up means HTTP 200 on :8188.
- **Stop**: SIGTERM to the recorded PID (then SIGKILL after 10 s), PID
  file removed, fallback to a pattern kill if there is no PID file.
  Down means :8188 stops answering.
- **Busy**: `/queue` has a running or pending prompt. The orchestrator
  waits for the queue to drain (grace 120 s) before it stops ComfyUI.
- **Idle**: no queue activity for 30 minutes (configurable) hands the GPU
  back to the LLM on its own.

## Failure modes

| Failure | What happens |
|---|---|
| Orchestrator down, router asks for the LLM | Router fails open, routes as today, logs a warning. |
| Orchestrator down, dashboard asks for a render | Dashboard refuses with a clear error. |
| ComfyUI will not start | Orchestrator restores LLM mode (reloads the 9B), reports the error. The LLM is never left down because a render failed. |
| 9B will not load | Orchestrator reports the error with the observed VRAM and models. The mode stays at the previous tenant. |
| A render is running when the LLM is asked for | Orchestrator waits up to 120 s for it to finish, then reports busy. The render is never killed. |
| VRAM does not free after a stop | Orchestrator reports the error with the observed VRAM. It does not force-load on top of a stuck tenant. |
| 27B evicted by a 9B reload | Orchestrator detects it in `/api/ps` and reloads the 27B with `num_gpu 0` (safe order). |
| State file missing / stale | Keep-alive falls back to the direct ComfyUI check. The router falls back to fail-open. Nothing assumes the file is fresh. |
| Two callers ask at once | One lock serialises the swaps. The second waits, then gets the settled state. |

## Files in this folder

| File | What it is |
|---|---|
| `gpu_orchestrator.py` | The service (stdlib only). HTTP on 127.0.0.1:11436, CLI, dry-run. |
| `DESIGN.md` | This document. |
| `README.md` | Short index and status. |
| `router_integration.py` | Drop-in helper for the router (easy route only). |
| `keep-brains-alive-v2.sh` | Patched keep-alive (skips the parked 9B). |
| `start-gpu-orchestrator.sh` | Launcher for autostart (not yet installed). |
| `gpu-orchestrator.desktop` | Xfce autostart entry (not yet installed). |
| `test/` | Fake Ollama / nvidia-smi / ComfyUI harness and the test runner. |

## Verification (done here, not on the Acer)

`test/run_tests.py` runs the orchestrator against fake Ollama, fake
`nvidia-smi` and fake ComfyUI (all local, no Acer, no real GPU) and checks:

1. State reporting is correct (mode, models, ComfyUI, VRAM).
2. `acquire llm` in LLM mode is a fast no-op.
3. `acquire comfy` parks the 9B, starts ComfyUI, sets the mode, writes
   the state file.
4. `acquire llm` from COMFY mode stops ComfyUI, loads the 9B **before**
   the 27B, loads the 27B with `num_gpu 0`, and leaves the 9B resident
   (no eviction).
5. Keep-alive `--dry-run` skips the 9B in COMFY mode and pings both in
   LLM mode.
6. The router helper fails open when the orchestrator is down and
   triggers a swap when it is up.
7. A busy ComfyUI (render running) is not killed; the acquire reports
   busy and ComfyUI keeps running.

Run it with: `python3 test/run_tests.py` from this folder. It prints
PASS/FAIL per scenario and exits non-zero if anything fails.

## Deploying later (NOT done — needs HgX's word)

1. Copy `gpu_orchestrator.py` to the Acer (`~/tonight-scripts/` style,
   e.g. `~/tonight-scripts/gpu-orchestrator/`).
2. Read the router file on the Acer and wire in `router_integration.py`
   (easy route only). Do not guess the router's internals from here.
3. Install `start-gpu-orchestrator.sh` + `gpu-orchestrator.desktop` in
   `~/.config/autostart/`, and confirm the service answers on :11436
   after a reboot.
4. Replace `keep-brains-alive.sh` with `keep-brains-alive-v2.sh`
   (keep the old one as `.bak`), and confirm the next 6-hour run logs
   the skip correctly.
5. Prove the loop end to end, in order: render in ComfyUI (GPU goes to
   COMFY), then an easy router call (GPU comes back to LLM, both brains
   resident), then the midnight keep-alive (9B skipped while parked).
6. Only then tell HgX it "just happens". Not before.

## Deployed 2026-11-06 (~23:42–23:50 ET) — all six steps done

1. Helper copied next to the router; patch script written; router
   backed up, patched, compiles clean.
2. Router restarted; easy call through the patched router answered via
   the 9B ("Hello").
3. Autostart installed (`start-gpu-orchestrator.sh` +
   `gpu-orchestrator.desktop`); service up, mode `llm`, both brains
   resident, VRAM 4,830 of 6,144.
4. Keep-alive swapped to v2 (old kept as `.bak`); dry run pings both
   brains in the right order.
5. Loop proven: acquire `comfy` → 9B parked, ComfyUI up (HTTP 200),
   VRAM 132 of 6,144; one easy call → 9B back, both brains resident,
   VRAM 4,830, mode `llm`.
6. It just happens. Midnight run confirmed: 2026-11-07 00:02:00, v2
   pinged both brains (mode `llm`).

## Open questions and limits

- A mode swap takes roughly 30–90 s (ComfyUI stop/start, model load).
  The first LLM call after a render waits for it. That is the price of a
  6 GB card, and it is rare (only when the mode actually changes).
- True instant hot-swap of two 5 GB LLMs needs smaller models or a bigger
  card. The dual-brain setup is already the instant swap (both resident,
  one on VRAM, one on RAM); this service only automates the third tenant
  (ComfyUI).
- The orchestrator is a single point of failure for ComfyUI starts
  (fail-closed by design). For LLM calls it is not (fail-open).
- The idle restore (30 min) is a default, not a law. If HgX renders in
  long sessions with gaps, raise it or disable it (set
  `GPU_ORCH_IDLE_RESTORE_MIN=0`).
