# The Little Router — design (build at home, with HgX)

**Status 2026-11-07: the design record from 2026-11-05. The router is
built, patched with the GPU orchestrator wiring, and live on the Acer —
see `local-jarvis/router/README.md` and
`local-jarvis/STATE-2026-11-07.md`.**

## Goal
One door for everything. REA, Local Jarvis, Locally Uncensored (as a UI only),
and the voice loop all talk to the router; the router picks the brain. Easy
work goes to the 9B on VRAM; hard work goes to the 27B on RAM; asked-for
work goes to Cloud Jarvis (the Grokbot) or the free LLM. Every routing
decision is logged.

## The four routes (updated 2026-11-05 ~17:49 ET — HgX: add Cloud Jarvis + the free LLM)
- **Resident — Qwen 3.5 9B Abliterated, Q4_K_M (~5.5GB), on VRAM.** Ollama
  `keep_alive` long (e.g. 24h) so it stays loaded. REA default. Needs the VRAM
  free — ComfyUI holding VRAM evicts it (see PLAN.md: picture brain KEEP, but
  it idles while the 9B works).
- **Heavy — 27B, on system RAM (64GB).** Loaded on demand only (`keep_alive`
  short, or explicit load). Slow (~1–3 tok/s expected on CPU) — hard reasoning,
  long code, multi-step chains only. **Exact tag must be verified before pulling.**
- **Cloud — Cloud Jarvis, the Grokbot (remote, Grok-powered).** Asked for by
  name (`"model": "cloud"` / `"grok"`). Needs `CLOUD_JARVIS_URL` +
  `CLOUD_JARVIS_KEY` (Grok tokens); without the key it answers 503 "not
  configured" instead of breaking. Default URL is xAI's API base; confirm the
  model name and the key at home.
- **Free — the free LLM (FreeLLMAPI, local Docker on :3001).** Asked for by
  name (`"model": "free"`). No provider keys. Confirm the model name at home;
  if FreeLLMAPI is down, the route answers 502.

## Router — BUILT and TESTED (2026-11-05 ~16:17 ET; four routes 2026-11-05 ~17:49 ET; native translation 2026-11-05 ~18:58 ET)
File: `04-little-router.py` (stdlib-only Python, no dependencies).
- Listens on `127.0.0.1:11435`, exposes OpenAI-compatible `/v1/chat/completions`
  (+ `/health` — now reports all four routes and whether cloud is configured —
  and `/v1/models` passthrough).
- Default route: 9B. Hard route: 27B when the caller asks for it
  (`"model": "hard"` in the request) or the prompt is long (over 8,000 chars).
  Cloud route: `"model": "cloud"` / `"grok"`. Free route: `"model": "free"`.
- Logs every decision (timestamp, route, model, prompt chars, stream) to
  `router.log` — the Usage Router ledger.
- **Native translation (2026-11-05 ~18:58 ET — lesson from the REA bridge):**
  Ollama routes are translated to Ollama's native `/api/chat` before
  forwarding, because the native door is the one that obeys `"think"` and
  `"keep_alive"`. The OpenAI door silently ignored `"think": false`, so the
  9B thought its way through a 4,560-char REA evidence prompt and the call
  timed out at 300s; the same prompt through the native door answered at
  once. The router also pins the resident model by setting `keep_alive` on
  every Ollama call (easy 24h, hard 1h) — a plain call used to reset the
  9B's clock to Ollama's 5-minute default (seen 2026-11-05 ~18:54 ET).
  Responses are translated back to OpenAI shape; streaming is translated
  to SSE. Cloud and free stay OpenAI-shaped.
- **Test result (mock upstreams): all ten cases passed** — small prompt
  → native /api/chat, 9B, keep_alive 24h, OpenAI-shaped reply;
  `"model": "hard"` → native, 27B, keep_alive 1h; 9,000-char prompt → 27B;
  `"think": false` passes through to native; `"model": "cloud"` → Grok
  model + Bearer key; `"model": "free"` → FreeLLMAPI; `"grok"` alias
  → cloud; cloud without a key → 503; log verified (8 decisions).
- Start it on the Acer with: `python3 04-little-router.py`
- Later: the Usage Router classifies automatically (easy/hard) and the Model
  Router swaps models; never generate with both at once; de-escalate after
  hard work. That is the approved dual-brain design — this little proxy is
  step one of it.

## Wiring after the router exists
- REA agents → `http://127.0.0.1:11435` (OpenAI-compatible base URL).
- Local Jarvis orchestrator → same door.
- Locally Uncensored → point at Ollama (or the router) as its backend; its
  own engine stays OFF.
- Cloud Jarvis (Grokbot) → a route of the router (`"model": "cloud"`).
- FreeLLMAPI → a route of the router (`"model": "free"`).
- Test end to end: REA analyze on a small binary (9B answers fast) + one hard
  prompt forced to the 27B (slow, but works) + one `"model": "cloud"` and one
  `"model": "free"` if configured.

## Open questions for the home session
1. Exact 27B tag — verify before pulling.
2. Picture brain: KEEP (decided 2026-11-05 ~17:05 ET). Activity (always-on vs idle) is a later call.
3. Does anything else still need Locally Uncensored's own engine? (If not, it
   stays off permanently.)
4. Cloud Jarvis endpoint + Grok key — confirm at home. FreeLLMAPI model name — confirm at home.
