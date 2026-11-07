# Acer LLM Consolidation — Home Session Plan

**Status 2026-11-07: the build record from the dual-brain build night
(2026-11-05). The brains and the router are built, proven and deployed
— the live state is in `local-jarvis/SETUP.md` and
`local-jarvis/STATE-2026-11-07.md`. This plan is the record of how they
were built, not the current state.**

**HgX's decision, 2026-11-05 ~16:09–16:10 ET. Nothing runs until he is home, step by step, on his word.**

## CORRECTION — deletion PAUSED (HgX, 2026-11-05 ~16:39 ET)
- HgX: the three Ollama models slated for deletion (qwen3:8b, qwen2.5:3b, agents-a1-4b-heretic) may be from his voice work — long dictation and other voice-over installs. They may need to stay.
- **Nothing is deleted until the audit says what each model is actually used for.** The audit (new step 3) checks what references each model: Local Jarvis config, VoiceStudio, Hex dictation, REA configs, and any running process calling Ollama.
- The 9B still moves into Ollama first (unchanged). The 27B still gets pulled into Ollama (unchanged). Only the deletion step changes: delete ONLY what the audit proves unused.
- Voice for Jarvis (him speaking to Jarvis, Jarvis speaking to him) — design parked for later, on his word. Idea on the table: the voice pipeline's *brain* could be the 9B instead of its own small models. Honest note: the 9B is a text brain — it can do the thinking, but it cannot hear (Whisper does that) or speak (Piper/speechbrain does that). Those stay.

## The decision
- **KEEP ONLY TWO MODELS:**
  1. **Qwen 3.5 9B Abliterated** — already downloaded (currently lives in Locally Uncensored). The single resident on VRAM (RTX 2060, 6GB). REA's default brain.
  2. **The 27B model** — on system RAM (64GB), for hard reasoning only. **NOTE: the 27B pull is still pending — its exact tag must be verified before pulling (standing rule).**
- **DELETE ONLY WHAT THE AUDIT PROVES UNUSED:** candidates are qwen3:8b, qwen2.5:3b, agents-a1-4b-heretic (Ollama models), plus Locally Uncensored's duplicate engine and its model files — **only after the 9B is confirmed inside Ollama AND the audit confirms each one is unused.**
- **PICTURE BRAIN (ComfyUI + comfy-api-proxy + OpenJutsu) — KEEP (HgX, 2026-11-05 ~17:05–17:06 ET — reversal of the conditional-delete):** it STAYS. Needed for the dashboard visuals, for explaining REA teardowns with images, and for the webcam work. He was right initially. Whether it stays ACTIVE all the time is decided later; it is NOT deleted. (Note: the 9B needs ~5.5GB of the 6GB VRAM, and ComfyUI holding most of the VRAM is exactly why the 9B was slow in LU — so when the 9B is working, the picture brain idles; activity is the later call, deletion is off the table.)

## Sequencing — the critical catch
**Move the 9B into Ollama BEFORE deleting anything.** The 9B currently lives in Locally Uncensored. Deleting first would destroy the very model we are keeping. Order:
1. `01-check.sh` (read-only): what is running, what is loaded, where the 9B GGUF actually lives, VRAM use, disk use.
2. Import the 9B GGUF into Ollama (`ollama create qwen9b-abliterated -f Modelfile` pointing at the GGUF found in step 1). Verify it loads on GPU (`ollama ps`, `nvidia-smi`).
3. **AUDIT (new, added 2026-11-05 ~16:39 ET): what uses each of qwen3:8b, qwen2.5:3b, agents-a1-4b-heretic?** Search Local Jarvis (`~/Jarvis`, `~/jarvis-estate-main`), VoiceStudio, Hex dictation, and REA configs for the model names; check which running processes call Ollama. The Hugging Face speech models (Whisper, Parakeet, OmniVoice — the ears) are separate from Ollama and are NOT touched by any of this. Nothing is deleted until this step says a model is unused.
4. `02-cleanup.sh`: remove ONLY the models the audit proved unused (each confirmed one by one), stop LU's engine. LU model files deleted only after step 2 is verified.
5. Verify the 27B tag, then pull the 27B (RAM model). Test it loads on CPU/RAM.
6. Build the little router (`03-router.md`): one door, four routes — easy → 9B on VRAM, hard → 27B on RAM, `"model": "cloud"` → Cloud Jarvis (Grokbot), `"model": "free"` → FreeLLMAPI; every routing decision logged.
7. Point REA and everything else at the router. Test REA end to end.
8. Picture brain: KEEP — no deletion (HgX 2026-11-05 ~17:05 ET). Whether it stays active all the time is decided later.

## Safety notes
- Deleted Ollama models can be re-downloaded — the risk is time, not loss. The 9B GGUF must be confirmed inside Ollama before ANY deletion.
- Nothing here runs without HgX at the keyboard, one step at a time, each step reported before the next.

## READY FOR TONIGHT (2026-11-05 ~16:17 ET — HgX: "make sure everything is ready")
- **27B tag VERIFIED (twice):** `huihui_ai/Qwen3.8-abliterated:27b` — 18GB Q4_K_M, 256K context, on Ollama (121K pulls). Ollama's own page states it plainly: "an uncensored version of Qwen/qwen38 created with abliteration." It does the heavy jobs: hard reasoning, long code, multi-step work, 256K context, tools + thinking (+ vision). Slow on RAM by design (~1–3 tok/s expected) — heavy brain only. Fallback: `huihui_ai/qwen3.5-abliterated:27b` (17GB). Pull command for tonight: `ollama pull huihui_ai/Qwen3.8-abliterated:27b`.
- **Memory map (corrected 2026-11-05 ~16:20 ET — the card is 6GB VRAM, not 8GB):** 27B = 18GB on system RAM (64GB total, ~46GB left for OS/Kali/Ghidra/REA). 9B = ~5.5GB on VRAM, nearly filling the 6GB card — nothing else lives on VRAM. Both loaded at once (OLLAMA_MAX_LOADED_MODELS=2), never generating simultaneously.
- **Little router BUILT and TESTED (four routes, 2026-11-05 ~17:49 ET; native translation 2026-11-05 ~18:58 ET):** `04-little-router.py` (stdlib-only, no dependencies). Ollama routes are translated to native `/api/chat` (the door that obeys `"think"` and `"keep_alive"` — the OpenAI door ignored `"think": false` and a 4,560-char REA bridge call timed out at 300s; the same prompt via native answered at once). Router pins keep_alive on every Ollama call (easy 24h, hard 1h). Tested 2026-11-05 against mock upstreams — all ten cases passed (native translation, keep_alive pinning, think passthrough, OpenAI-shaped replies, cloud/free, 503 without key, log verified). Cloud needs `CLOUD_JARVIS_URL` + `CLOUD_JARVIS_KEY` (Grok tokens); free needs `FREELLM_URL` (default http://127.0.0.1:3001). Run it on the Acer with: `python3 04-little-router.py` (listens 127.0.0.1:11435).
- **9B import script READY:** `05-import-9b.sh` — finds the 9B GGUF in LU's files, builds the Modelfile, imports as `qwen9b-abliterated`, proves it answers on the GPU.
- **Run order tonight:** 1) `01-check.sh` → 2) `05-import-9b.sh` → 3) **AUDIT** (what uses each model) → 4) `02-cleanup.sh` (only what the audit proves unused) → 5) pull the 27B → 6) start the router → 7) point REA at `http://127.0.0.1:11435` → 8) picture brain: KEEP. Then: the camera, the voice loop, and the dashboard (ready by bedtime).
- Files: `~/workspace/family-bot/acer-llm-consolidation/` — copy the folder to the Acer when home.
