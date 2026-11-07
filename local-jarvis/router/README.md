# Model router — `04-little-router.py` (2026-11-06)

The single door for LLM calls on the Acer: easy calls go to the 9B,
hard calls go to the 27B. Port **11435**.

**Status: live on the Acer.** This file is the snapshot from the Acer
source parcel of 2026-11-06 23:36 ET (`jarvis-acer-source-2026-11-06.zip`).

**What it carries:**

- Easy → `qwen9b-abliterated` (VRAM, fast); hard →
  `huihui_ai/Qwen3.8-abliterated:27b` (system RAM, CPU-only —
  `num_gpu 0`, the 2026-11-06 CPU fix).
- Cloud route (Grok) unconfigured; free route on port 3001
  (FreeLLMAPI, fallback only).
- 24-hour pins (`KEEP_ALIVE_EASY=24h`, `KEEP_ALIVE_HARD=24h` in the
  autostart launcher).

**Post-snapshot change — read this before wiring it in:** the live
router on the Acer was patched *after* this snapshot (~23:44 ET) to call
the GPU orchestrator before an easy call (`router_integration.py` in
`local-jarvis/gpu-orchestrator/`, `ensure_gpu_llm(timeout=180)`, fail
open when the orchestrator is down, fail closed with 503 when the GPU
is busy rendering). This published file predates that wiring. To
reproduce the live router, take this file and apply the wiring exactly
as documented in `gpu-orchestrator/DESIGN.md` → "Router integration".
The wiring itself is proven: after the patch, an easy call through the
router answered via the 9B ("Hello"), and the full swap loop was proven
the same night (see `gpu-orchestrator/README.md` → "Deployed").

**Test it:** `local-jarvis/scripts/jarvis-router-both-brains-test.sh`
asks an easy question (expect the 9B) and a hard question (expect the
27B, CPU-only), and prints the model the router reports for each.
