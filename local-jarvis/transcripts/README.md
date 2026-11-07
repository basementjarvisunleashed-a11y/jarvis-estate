# Model responses — the transcript archive

**Standing order (HgX, 2026-11-07 ~00:31 ET): every model response gets
documented here — REA, the 9B (`qwen9b-abliterated`), the 27B
(`huihui_ai/Qwen3.8-abliterated:27b`), every time they respond. Cloud
(Grok) and free (FreeLLMAPI) too, if ever configured. Nothing summarized,
nothing trimmed: the full reply, as the model gave it.**

## How it works

- The Acer captures every response (router response tee, voice
  orchestrator log, REA history + evidence files) and sends each batch
  to the publishing house.
- The publishing house **scrubs every batch before it lands here** — no
  real name, no credentials, no private paths, no personal/family/
  financial details, no live location. Model replies can carry his
  commands and file contents, so nothing lands unscrubbed. Raw logs stay
  on the Acer and NEVER go to GitHub.
- One file per day: `YYYY-MM-DD.md`. Each entry, in order:

```markdown
## HH:MM:SS — <model> via <route>
**Prompt:** <the prompt, scrubbed>
**Response:**
<the full response, scrubbed>
```

## What we have now

- Capture starts 2026-11-07 ~00:31 ET. Before that, the router only
  logged decision lines (timestamp, route, model, prompt character
  count) — no prompt text, no response text. Past responses that were
  never logged in full can't be recovered; the archive starts from now.
- First batch (whatever was already logged: router.log,
  rea-history.jsonl, REA evidence files) lands here when the REA room
  sends it.

---

@basementjarvisu · basementjarvisunleashed@gmail.com
