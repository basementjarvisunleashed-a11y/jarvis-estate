# Tonight's Runbook — REA + the 9B Working, No Excuses

**Status 2026-11-07: the session record from the dual-brain build night
(2026-11-05). Superseded as a runbook by
`local-jarvis/tonight-runbook-2026-11-06.md`; kept here as the record of
how the brains and the router were built. Note: the voice-loop plan it
references (`voice-loop-plan.md`) was never written as a separate file —
the loop was built from this runbook and patch v5.**

**HgX, 2026-11-05 ~16:18 ET: "When I get home, I want Dat Quen and REA working incredibly. As soon as I get home, I want to be impressed."**

Everything below is prepared. One step at a time, each reported before the next.

## Already done (before he gets home)
- [x] 27B tag verified: `huihui_ai/Qwen3.8-abliterated:27b` (18GB Q4_K_M, 256K)
- [x] Little router built + tested (small→9B, hard→27B, long→27B, log verified)
- [x] Import script ready (05-import-9b.sh) — 9B from LU into Ollama
- [x] Check + cleanup scripts ready (cleanup gated on the audit — see Step 3)

## The session (in order)
**FIRST — Mount the drive read-write and clean it out (HgX, 2026-11-05 ~17:22 ET — change of plan).** The first thing tonight, before anything else: mount the external drive read-write, inventory it, and clean it out with him — item by item, nothing deleted without his word on each thing. Only then do Steps 0–8, the camera, the voice loop, and the dashboard. Scripts ready: `mount-media-drive.sh` (mounts by label HgX, read-write — the earlier test mount was read-only) + `drive-inventory.sh` (read-only listing) — copy to the Acer with the folder.

**Step 0 — Copy the folder to the Acer.** Jarvis copies `acer-llm-consolidation/` to the Acer over SSH when the session starts. (~1 min)

**Step 1 — See the mess.** `./01-check.sh` — what is running, what is loaded, where the 9B GGUF lives, VRAM use. (~2 min)

**Step 2 — Move the 9B into Ollama.** `./05-import-9b.sh` — finds the GGUF, imports as `qwen9b-abliterated`, proves it answers on the GPU with thinking off. (~5–10 min)

**Step 3 — AUDIT: what uses each model? (NEW — HgX, 2026-11-05 ~16:39 ET).** The three models we were going to delete may be his voice work — long dictation and other voice-over installs. So before anything is deleted, we find out: search Local Jarvis (`~/Jarvis`, `~/jarvis-estate-main`), VoiceStudio, Hex dictation, and REA configs for `qwen3:8b`, `qwen2.5:3b`, `agents-a1-4b-heretic`; check which running processes call Ollama. The Hugging Face speech models (Whisper, Parakeet, OmniVoice — the ears) are separate and are NOT touched. (~5 min)

**Step 4 — Clean only what the audit proves unused.** `./02-cleanup.sh` — deletes ONLY the models the audit cleared (each confirmed), stops LU's engine. The 9B is safe inside Ollama by now, and anything voice needs stays. (~2 min)

**Step 5 — Pull the 27B.** `ollama pull huihui_ai/Qwen3.8-abliterated:27b` (~18GB — **the one slow step**; start it early and let it download while we do step 6).

**Step 6 — Start the router + pin the resident.** Set Ollama so the 9B stays loaded (`OLLAMA_MAX_LOADED_MODELS=2`, long keep-alive), then `python3 04-little-router.py` — one door on 127.0.0.1:11435, four routes: easy → 9B, hard → 27B, `"model": "cloud"` → Cloud Jarvis (Grokbot, needs the Grok key — if unset it answers 503), `"model": "free"` → FreeLLMAPI (:3001). Check `/health` (it reports all four routes). (~2 min)

**Step 7 — Point REA at the router and RUN THE DEMO — DONE 2026-11-05 ~19:01 ET.** (a) REA+Ghidra analysed /bin/ls (evidence ev_d0f6ae25, 32 segments); the 9B read the 8KB evidence and summarised it in 3 sentences (696 procedures, 536 strings) — via Ollama's native /api/chat, because the router's old OpenAI door ignored "think": false and timed out at 300s. Router REBUILT (native translation, keep_alive pinning: easy 24h, hard 1h), restarted, fast-tested (think:false answered in a breath, pin reads 24h). (b) Hard question through the router: 27B answered from system RAM. (c) Cloud: unconfigured (no Grok key yet). Free: FAILED — FreeLLMAPI answered "Invalid API key" (investigate later, not blocking).

**Step 8 — Picture brain: KEEP (HgX, 2026-11-05 ~17:05 ET — reversal).** No deletion. ComfyUI + proxy + OpenJutsu stay — needed for the dashboard, for explaining REA teardowns with images, and for the webcam. Whether it stays active all the time is a later call; when the 9B is working, the picture brain idles so the 9B holds the VRAM clean.

## Done means
- `ollama list` shows `qwen9b-abliterated` + `huihui_ai/Qwen3.8-abliterated:27b`, plus any model the audit said to keep.
- The 9B is resident on VRAM (`ollama ps` + `nvidia-smi`).
- The router answers on :11435 and `router.log` shows decisions.
- REA runs a real analysis through the router and the 9B answers it.
- Nothing else is running except what the audit kept and the picture brain (kept, activity decided later). One server, one resident brain, one door.

## Final project — the voice loop (after the webcam) — HgX, 2026-11-05 ~16:47 ET
**His order: by the end of tonight, talk to Jarvis and Jarvis takes commands and does everything.**
- Full plan: `~/workspace/family-bot/voice-loop-plan.md`.
- Steps: plug in the MaonoCaster over USB + webcam, list all four mics (webcam mic, laptop mic, MaonoCaster in 1, MaonoCaster in 2), test everything including the aux cable → read the Local Jarvis orchestrator config (ears/voice/hands) → point its brain at the router (`http://127.0.0.1:11435`, the 9B) → start the loop listening on all four mics → test in order: "open Firefox", "open a terminal", "list the files", "REA, analyze this file" → Jarvis speaks the result. Showpiece: **"VLC on, play the Sopranos"** (find where the Sopranos files live first). Room capture: record all four mics at once for live narration + multiple voices, transcribe with Whisper (diarization later).
- **Everybody is operator approved (HgX, 2026-11-05 ~16:52 ET): anyone may talk to Jarvis and give commands — including his son and guests downstairs. No voice check, no audio filter. The bar is reliability: last time was too janky to show off; it must just work, first time, in front of people.**
- Audio routing for Discord: PipeWire + qpwgraph + EasyEffects, labeled devices ("Discord Hears"); find the GitHub mixer installed last time (name not on record — check the machine, don't guess).
- Auto-listen on boot: only on his word, after the loop works.
- Done means: anyone speaks, the laptop acts, Jarvis speaks back — including REA by voice, and "VLC on, play the Sopranos" working first time. Discord sees labeled devices and hears only what we labeled for it.

## Standing rule (HgX, 2026-11-05 ~18:08 ET)
**Terminal scripts only.** Everything tonight is done by terminal script — no GUI steps anywhere. Every step in this runbook is a script or a command.
