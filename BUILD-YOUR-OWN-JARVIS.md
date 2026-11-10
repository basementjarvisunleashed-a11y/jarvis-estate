# Build Your Own Jarvis

**J.A.R.V.I.S. — Joint Ambient Ready Variance Intelligence System.**

Your own Jarvis is a local, private personal intelligence that lives on
your machine: two local brains, one router, a voice, a screen, and REA
(reverse engineering). Nothing leaves the house unless you choose it.
This repository is the whole build. The course teaches you to operate
it. The website is the public face. The guide is also published as a
full page on the website:
[build-your-own-jarvis/](https://basementjarvisunleashed-a11y.github.io/jarvis-estate/build-your-own-jarvis/).

## The three things

| | What it is | Where it lives |
|---|---|---|
| **The course** | OPERATOR PRIME — Full-Spectrum Operator Systems, taught by HGX Academy. Fifteen modules M0–M14, fifty labs L1–L50 (all locked for 1.0), twenty-one checkpoints, Project 25 proves the entire suite, assessment 40/25/15/20. This is how you learn to operate the machine. | [Course website](https://basementjarvisunleashed-a11y.github.io/jarvis-estate/course/) · [Course index](course/README.md) · [Syllabus v1.0.1](course/syllabus/OPERATOR-PRIME-SYLLABUS-v1.0.1.md) |
| **The build** | The reference machine, documented file for file: Kali Linux, the two brains, the router, the voice loop, the dashboard, the GPU orchestrator, REA, and the plans behind them. The run-it-yourself guide is `local-jarvis/SETUP.md`. | [`local-jarvis/`](local-jarvis/) · [`local-jarvis/SETUP.md`](local-jarvis/SETUP.md) · [`local-jarvis/STATE-2026-11-10.md`](local-jarvis/STATE-2026-11-10.md) |
| **The website** | The public face: the hero, the basement lab, the Academy section, the build log, the papers. | [Main site](https://basementjarvisunleashed-a11y.github.io/jarvis-estate/) |

## What you need

- **A machine like the reference.** Acer Nitro: i7-10750H, 64 GB RAM,
  NVIDIA RTX 2060 (~6 GB VRAM), 512 GB NVMe. The RAM holds the big
  brain; the VRAM holds the fast brain; the NVMe holds everything. A
  close equivalent works — the guide names the reference so you know
  what each part is for, not so you must buy the same box.
- **Kali Linux**, installed on the internal drive. Everything in this
  build runs on Kali.
- **Time.** This is a build, not an install wizard. One step at a time,
  each verified before the next.
- **The rules** (below). They are not optional.

## The build, in order

### 1. Learn the spine — the course

Start with OPERATOR PRIME. Modules M0–M14, labs L1–L20 first (L21–L50
are the year), the seventeen stacks in the syllabus (REA first), and
Project 25 at the end, which proves the entire suite. You do not need
to finish the course before you start building — but the course is
where the discipline comes from: see, document, log, prevent.

### 2. Set up the machine — `local-jarvis/SETUP.md`

The whole system from this repo alone, in order: Kali and drivers →
Ollama → the brains → the router → the orchestrator → the voice loop →
the dashboard → the GPU orchestrator → REA. Every component, every
port, every verify step. If it is not in SETUP.md, it is not part of
the setup.

### 3. The two brains

- **The fast brain** — `qwen9b-abliterated`, resident on VRAM (~6 GB),
  context 8192. The default. REA and the voice loop talk to this one.
- **The hard brain** — `huihui_ai/Qwen3.8-abliterated:27b`, on system
  RAM (~18 GB), context 4096, 100% CPU. Slow by design. Hard reasoning,
  long code, multi-step chains only.
- **Never both generating at once.** One brain answers; the other waits.
- Models are named by tag only in this repo. **No weights are shipped.**
  You pull them yourself: `ollama pull qwen9b-abliterated` and
  `ollama pull huihui_ai/Qwen3.8-abliterated:27b`.

### 4. The router — one door (port 11435)

`local-jarvis/router/04-little-router.py` (stdlib only). One door for
everything: easy work → the 9B, hard work → the 27B (ask for it, or a
prompt over 8,000 characters), cloud → Grok (unconfigured — you bring
your own key), free → FreeLLMAPI (parked). Every routing decision is
logged. Ollama routes use native `/api/chat`, so `think` and
`keep_alive` are honoured.

### 5. The voice — Whisper, orchestrator, Piper (port 8080)

Mic → faster-whisper `small.en` → orchestrator `:8080` → the 9B →
Piper `en_GB-alan-medium`. Patch v5 is applied (deterministic
dispatcher). On our reference machine, everybody is operator approved —
anyone may talk to it. **On yours, you decide who may command it.**
The voice loop is deliberately not auto-started; start it when you are
ready to be heard.

### 6. The screen — the dashboard (port 8899)

`local-jarvis/dashboard/v12/` — the current dashboard, live on the
reference machine. One screen, no scroll: GPU, temperatures, RAM,
what's running, what each model is doing, REA status, the media tile
(two media roots — the iPad Pro MP4 folder primary, the drive
secondary — played in the tile or in VLC), the webcam beside the video
player, and the live two-way conversation feed. Served on the tailnet
so your phone sees it too.

### 7. REA — reverse engineering (own devices only)

`rea-agents@6.7.0` + Ghidra guided workflows. Point it at your own
apps and your own targets, and it takes them apart with evidence. The
teardown plans (`local-jarvis/plans/`) show how: enumerate, watch it
talk, make it work, document everything.

### The swap — the GPU orchestrator (port 11436)

The card holds one brain at a time. The orchestrator keeps the 9B
resident on VRAM and the 27B on RAM, and swaps on demand: when ComfyUI
needs the card, the 9B parks; when the next easy call arrives, the 9B
comes straight back. Deployed and proven on the reference machine —
the loop just happens.

## Keeping it honest

- **The state snapshot** (`local-jarvis/STATE-2026-11-07.md`) is the
  exact moment: the whole system, as it stands. A new dated snapshot
  lands whenever the state changes.
- **The transcripts** (`local-jarvis/transcripts/`) document every model
  response — the 9B, the 27B, REA — scrubbed, one file per day. If a
  brain said it, it is on record.
- **The build log** on the website records every release, dated, with
  the facts. Nothing is claimed done before it is verified.

## The hard rules

From the course, verbatim in spirit, binding on every build:

- Consenting adults. Controlled lab only. **Own devices and own targets
  only.**
- The spine: **SEE → DOCUMENT → LOG → PREVENT.**
- No face ID except consenting adults, lab only. Templates deleted. No
  family, no son, no strangers. Radio, drone, and laser rules as written
  in the course.
- Nothing is deleted. Nothing is overwritten. Every change is versioned.
- No personal data in public material — no real names, no credentials,
  no private paths, no family, no finances, no live location.

## Honest limits

- No weights are shipped, and no backup is shipped. You pull the models
  and you keep your own backup.
- The cloud brain is unconfigured out of the box; the free route is
  parked. Local first is the design, not a fallback.
- ComfyUI (the picture brain) is parked on the reference machine — the
  9B has the GPU. The iPad Kali build is parked too.
- The 27B is slow on CPU by design (~1–3 tokens a second). That is the
  price of a big brain with no cloud.
- The voice loop needs tuning on your machine — mics, levels, and the
  room itself are yours to get right.

## Where to start

1. Read the [course website](https://basementjarvisunleashed-a11y.github.io/jarvis-estate/course/)
   — Start here, then modules, then labs.
2. Read [`local-jarvis/SETUP.md`](local-jarvis/SETUP.md) — the whole
   build, in order.
3. Check [`local-jarvis/STATE-2026-11-07.md`](local-jarvis/STATE-2026-11-07.md)
   — the exact moment, so you know where the reference machine stands
   today.

Then build it. One step at a time, each verified before the next. You
have used computers your whole life. Now you operate them.

---

@basementjarvisu · basementjarvisunleashed@gmail.com
