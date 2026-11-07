# Local Jarvis — the core stack: Kali, REA, and what's still pending

**J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System) — an open-source operating system for personal AI: one principal, a federation of durable roles, inspectable evidence, and human authority at every consequential boundary.**

Public identity: J.A.R.V.I.S. first and prominent. Operator: HgX. Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

**Status rule for this document:** every item is marked BUILT or PENDING. A PENDING item is planned only — it is not claimed as installed, running, or verified until HgX confirms it built. This document is the single consolidated record of the local Jarvis stack as of 2026-11-04. Platform 1.2.1.

---

## 1. The core — what J.A.R.V.I.S. is

- One principal (HgX). A federation of durable roles. Inspectable evidence. Human authority at every consequential boundary.
- Cloud JARVIS is sovereign. Local Jarvis executes only as specified in the GitHub README and `local-jarvis/README.md`.
- House rules: no deletions; a pull request for every GitHub change; no secrets in public; approval for each laptop change; every bot answers by voice memo.
- Open source from day one: code MIT, papers and docs CC-BY-4.0. Private life (family, finances, credentials, personal data) never appears in public materials.
- 1.0 = the course + all open-source hardware used in the course + the bracelet, all open source. The bracelet is one device in 1.0, not the whole of 1.0.

---

## 2. Jarvis on Kali — BUILT

**Hardware — built and verified:**

- Laptop: Acer Nitro AN515-55
- CPU: i7-10750H
- RAM: 64GB
- GPU: RTX 2060, about 6GB VRAM
- Storage: 512GB NVMe internal drive

**Platform — built and verified:**

- **Kali Linux, everything installed on the internal drive.** All tools updated, graphics driver installed, Bluetooth working, Wi-Fi working, login working.
- **Windows is no longer on the internal drive.** The Windows licence is motherboard-tied; a later reinstall via ISO is possible with no product key needed. This is a general licence note only; no product key or account detail is recorded here.
- The prior Windows build files are retained for reference only. The live platform is Kali Linux.
- The prior Windows guide is preserved in git history. The live guide is rewritten for Kali.

**Voice stack — built:**

- Mic → Whisper small.en → voice gate → orchestrator on port 8080 → Ollama `qwen3:8b` → tools / VLC / REA → Piper TTS (`en_GB-alan-medium`).
- The orchestrator listens only after you start it. The voice loop is deliberately not auto-started.
- The voice gate scores audio against the enrolled profile and drops the turn when the speaker is unenrolled.
- `jarvis.py` is a separate helper (list / play / pause / ask / say / listen / chat) on `qwen2.5:3b` via Ollama `/api/generate`. The voice loop does not use that model.
- Router v2.2, 50 second voice budget, 60 second client wait, freellmapi as fallback only.
- Plain VLC commands (`pause`, `play`, `resume`, `stop`, `next`, `skip`, `previous`, with an optional "hey jarvis") match a regex and run without a model round trip.
- VLC's HTTP remote and Ollama stay on localhost.

**Dashboard — BUILT, live on the Acer (2026-11-06):**

- Always-on dashboard on port **8899** (iPhone/iPad over the tailnet): GPU,
  temperatures, RAM, what's running, what each model is doing, local weather,
  Wi-Fi, REA status, models online/offline, last things REA did, media tile,
  live two-way conversation feed.
- **v8** is the previous dashboard, applied and live until 2026-11-07
  ~00:18 ET. Kept in the repo as history.
  Files: `local-jarvis/dashboard/v8/`.
- **v9 is the current dashboard, LIVE on the Acer (2026-11-07 ~00:18
  ET):** visual polish only — deeper dark, arc-reactor glow, cleaner
  type, room to breathe — and the webcam now sits in the MEDIA tile,
  directly beside the video player (no more floating webcam tile).
  Applied from the published copy (`local-jarvis/dashboard/v9/`), v8
  backed up to `dashboard.bak-v8`. Confirmed live by terminal output
  (`/api/status` 200, GPU 34°C, media mounted).
- v8 (redesign — one screen, no scrolling) is built, verified
  (2026-11-06 ~23:54 ET, 7 directives + 5 playback fixes, API 28/28,
  layout 31/31), PUBLISHED here (`local-jarvis/dashboard/v8/`) and
  APPLIED to the Acer (2026-11-07 ~00:00 ET, v7 backed up). Superseded
  by v9 as the live dashboard.
- v9 (visual polish — deeper dark, arc-reactor glow, cleaner type, the
  webcam beside the video player) is built, verified (API 28/28, layout
  35/35), PUBLISHED here (`local-jarvis/dashboard/v9/`) and APPLIED to
  the Acer (2026-11-07 ~00:18 ET, v8 backed up). **v9 is the live
  dashboard.**

**GPU orchestrator — DEPLOYED on the Acer (2026-11-06 ~23:50 ET):**

- Router-integrated GPU brain manager: keeps the 9B model resident on VRAM
  and the 27B model on RAM, hot-swaps on demand, never both generating at
  once. Files: `local-jarvis/gpu-orchestrator/` (test harness 7/7 green,
  twice). Router wired (easy route only), autostart installed, keep-alive
  v2 in, loop proven end to end (ComfyUI acquire freed the card to 132
  MiB; one easy call brought the 9B back, both brains resident, VRAM
  4,830 of 6,144). See `gpu-orchestrator/README.md` → "Deployed".

---

## 3. REA — BUILT

**REA (Reverse Engineer Anything) — built and ready for local app analysis:**

- **REA: `rea-agents@6.7.0`**, installed via `npx rea-agents setup`.
- REA reverse-engineering skill installed for CLI use.
- CLI: `npx rea-agents analyze /path/to/app`
- Deep analysis: Ghidra, guided reverse-engineering workflows installed.
- Status: REA is ready for local app analysis.

**What REA is for here:** the basement laptop that can rip apart anything, then put it back together with evidence. Local app analysis only — own devices and own targets only, consenting adults, controlled lab only, spine SEE → DOCUMENT → LOG → PREVENT.

---

## 4. The pending stack — PENDING, not built

**These are planned only. None are claimed as installed until HgX confirms them built.**

### 4.1 The local brain — dual brain, pending

- **Ollama check** — pending. The next step before any model pull.
- **Small model, resident on VRAM (fast low-end brain)** — pending. A small abliterated model under six gigabytes, resident on graphics memory, super fast, as the REA default.
- **Large model, resident on system memory (slow high-end brain)** — pending. A large abliterated 27B model on RAM, slow, for hard reasoning, long code, multi-step chains, and context beyond the small model's range. The large model's exact tag must be verified before pulling.
- **Switching logic (Usage Router + Model Router)** — pending. Default to the small VRAM model; escalate to the large RAM model on hard work or repeated failure; de-escalate afterwards. Never generating with both at once. Every switch logged.
- **No middle 8B test.** There is no middle test between the small and large models.

### 4.2 The seventeen software stacks — pending, in efficient order

Syllabus v1.0.1 counts seventeen local-only software stacks, in this efficient order. REA (item 1) is BUILT. Everything after REA is PENDING, to be installed one by one, in this order, only on HgX's order, in his lab only:

1. **REA** — BUILT (`rea-agents@6.7.0`).
2. **Quick tools** — PENDING: security-audit-skill (sandboxed), Graphify, HyperFrames.
3. **Ollama tools** — PENDING: FreeLLMAPI (routed to local Ollama), ai-memory.
4. **Heavy GPU, separate venvs** — PENDING: ComfyUI.
5. **DeepTutor** — PENDING.
6. **Prism** — PENDING.
7. **Macro, Kali only** — PENDING.
8. **Hacking-Tools gaps, one by one** — PENDING. The hacking-tools catalog is a reference map, not 900 installs: not all 900 run at once, not every listed item runs locally, installs wait for the Kali phase, one tool at a time and only on his order.
9. **Claude Plugins** — PENDING (requires Claude Code).
10. **VoiceStudio** — PENDING.
11. **GenOffice** — PENDING.
12. **Reference libraries, last** — PENDING.

(Syllabus v1.0.1 states seventeen items total; the groups above follow the syllabus's own ordering. Present planned stacks as planned, built stacks as built.)

### 4.3 Kali tools mapping into REA — PENDING

- Mapping the Kali toolset into REA workflows, so REA drives the local tools as one reverse-engineering bench. Pending.

### 4.4 Project 25 prove-out — PENDING

- Project 25 proves the entire suite — the whole course, the whole stack, the whole lab, end to end, with no faked passes. Pending. It runs right after the build, before other projects.

### 4.5 Three pillars — the shape of the stack

1. **Kali everything.** The whole platform on Kali Linux.
2. **REA everything, local model and local providers.** Reverse engineering on local models, local providers, local execution.
3. **Grokbot, cloud reasoning with local execution.** Cloud reasoning where it helps, execution always local.

---

## 5. Where this document lives

- This file: `local-jarvis/LOCAL-JARVIS-STACK.md` — the consolidated stack record.
- Current state snapshot: `local-jarvis/STATE-2026-11-07.md` — the exact moment, 2026-11-07 ~00:10 ET.
- Build plans: `local-jarvis/plans/` — the design records (dashboard, drive clean-out, C270 teardown, REA bench list).
- Pi 500+ rig: `local-jarvis/pi500/` — top 10, software stack, accessories (ordered + paid 2026-11-05).
- Platform record: `local-jarvis/PLATFORM-KALI.md` — the Kali + REA build record.
- Full guide: `local-jarvis/README.md` — install, voice loop, orchestrator, troubleshooting.
- Run it yourself: `local-jarvis/SETUP.md` — the whole system from this repo alone, in order.
- Course stacks: `course/syllabus/OPERATOR-PRIME-SYLLABUS-v1.0.1.md` — the seventeen stacks in course canon.
- Course site: `course/` — the platform section lists the stacks for students.

---

@basementjarvisu · basementjarvisunleashed@gmail.com
