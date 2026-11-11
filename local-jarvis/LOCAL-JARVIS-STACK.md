# Local Jarvis — the core stack: Kali, REA, and what's still pending

**J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System) — an open-source operating system for personal AI: one principal, a federation of durable roles, inspectable evidence, and human authority at every consequential boundary.**

Public identity: J.A.R.V.I.S. first and prominent. Operator: HgX. Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

**Status rule for this document:** every item is marked BUILT or PENDING. A PENDING item is planned only — it is not claimed as installed, running, or verified until HgX confirms it built. This document is the single consolidated record of the local Jarvis stack as of 2026-11-11. Platform 1.2.1.

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

- Mic → Whisper small.en → orchestrator on port 8080 → Ollama `qwen9b-abliterated` (context 32768 since 2026-11-10) → tools / VLC / REA → Piper TTS (`en_GB-alan-medium`).
- The orchestrator listens only after you start it. The voice loop is deliberately not auto-started.
- The voice gate is DROPPED on HgX's order (2026-11-05) — everybody is operator-approved, no voice check. The gate files stay in the repo as built artifacts, not enforced.
- `jarvis.py` is a separate helper (list / play / pause / ask / say / listen / chat) on `qwen2.5:3b` via Ollama `/api/generate`. The voice loop does not use that model.
- Router v2.2, 50 second voice budget, 60 second client wait, freellmapi as fallback only.
- Plain VLC commands (`pause`, `play`, `resume`, `stop`, `next`, `skip`, `previous`, with an optional "hey jarvis") match a regex and run without a model round trip.
- VLC's HTTP remote and Ollama stay on localhost.

**Dashboard — BUILT, files on GitHub; live copy deleted from the laptop 2026-11-10:**

- Always-on dashboard on port **8899** (iPhone/iPad over the tailnet): GPU,
  temperatures, RAM, what's running, what each model is doing, local weather,
  Wi-Fi, REA status, models online/offline, last things REA did, media tile,
  live two-way conversation feed.
- **v8** is the previous dashboard, applied and live until 2026-11-07
  ~00:18 ET. Kept in the repo as history.
  Files: `local-jarvis/dashboard/v8/`.
- **v12 is the current dashboard, LIVE on the Acer (2026-11-08):**
  laptop camera stacked full-width below the C270; CPU temp + GPU on
  the top strip; whole page scrolls; REA tile shows the C270 breakdown;
  sports shrunk to one NFL line. Applied from the published copy
  (`local-jarvis/dashboard/v12/`), v11 backed up to `dashboard.bak-v11`.
  Confirmed live by terminal output (`/api/status` 200). Live copy deleted from the laptop 2026-11-10 (dashboard dir, backups, webcam app, task manager, night visuals, autostarts all off; :8899 + :8898 down); the v12 files stay on GitHub. Who deleted them is still unknown. The laptop
  camera shows color bars — a camera/firmware fault, not the dashboard;
  the thread is closed.
- v11 was applied 2026-11-07 evening and superseded by v12; its files
  were never sent to the publishing house, so v11 is recorded as a
  version line only, not as files.
- **v10 was the previous dashboard, LIVE on the Acer (2026-11-07
  ~00:45 ET):** two media roots, primary first — the iPad Pro MP4
  folder for VLC and in-browser playback, the drive secondary — and the
  webcam in the MEDIA tile, directly beside the video player.
  Applied from the published copy (`local-jarvis/dashboard/v10/`), v9
  backed up to `dashboard.bak-v9`.
- v8 (redesign — one screen, no scrolling) is built, verified
  (2026-11-06 ~23:54 ET, 7 directives + 5 playback fixes, API 28/28,
  layout 31/31), PUBLISHED here (`local-jarvis/dashboard/v8/`) and
  APPLIED to the Acer (2026-11-07 ~00:00 ET, v7 backed up). Superseded
  by v9 as the live dashboard.
- v9 (visual polish — deeper dark, arc-reactor glow, cleaner type, the
  webcam beside the video player) is built, verified (API 28/28, layout
  35/35), PUBLISHED here (`local-jarvis/dashboard/v9/`) and APPLIED to
  the Acer (2026-11-07 ~00:18 ET, v8 backed up). Superseded by v10 as
  the live dashboard.
- v10 (two media roots, primary first) is built, verified (API 38/38,
  layout 36/36), PUBLISHED here (`local-jarvis/dashboard/v10/`) and
  APPLIED to the Acer (2026-11-07 ~00:45 ET, v9 backed up). Superseded
  by v11, then v12, as the live dashboard.
- v12 is built, verified (API endpoints present, all six v12 changes
  confirmed in the files), PUBLISHED here
  (`local-jarvis/dashboard/v12/`) and APPLIED to the Acer (2026-11-08,
  v11 backed up). **Live copy deleted from the laptop 2026-11-10; the v12 files stay on GitHub.**

**GPU orchestrator — DEPLOYED on the Acer (2026-11-06 ~23:50 ET):**

- Router-integrated GPU brain manager: keeps the 9B model resident on VRAM
  and the 27B model on RAM, hot-swaps on demand, never both generating at
  once. Files: `local-jarvis/gpu-orchestrator/` (test harness 7/7 green,
  twice). Router wired (easy route only), autostart installed, keep-alive
  v2 in, loop proven end to end (ComfyUI acquire freed the card to 132
  MiB; one easy call brought the 9B back, both brains resident, VRAM
  4,830 of 6,144). See `gpu-orchestrator/README.md` → "Deployed".

**Brains autostart — INSTALLED + VERIFIED (2026-11-08):** both brains
load in ~41 seconds at reboot (9B ctx 8192 at load time, 27B ctx 4096,
both 24-hour pins). Files: `local-jarvis/autostart/` (scrubbed).
Update done 2026-11-10: the live `start-brains.sh` now loads
`qwen9b-abliterated-32k` with `num_ctx` 32768 at boot (backup
`start-brains.sh.bak-32kmodel`); the repo copy predates that update.
`keep-brains-alive.sh` was updated to 32k too (line 63, cron present).
**"Build it all"** (2026-11-10 ~09:08 ET): daytime = Claude Code
(9B-32k) + REA + tools, interactive; nighttime = 27B + BLA overnight
runners. The overnight runner v1 is installed at
`~/overnight-27b-runner/` (resumes CrackMe, then one BLA red-vs-blue
smoke test; HgX starts it tonight before bed). **Orchestrator SAF-01**
(PR #67, merged 2026-11-10 15:19 ET): the voice orchestrator binds
loopback by default; non-loopback needs `JARVIS_TOKEN`; Host-header +
JSON-body request gate; VLC probe starts from `main()`.

---

## 3. REA — BUILT

**REA (Reverse Engineer Anything) — built and ready for local app analysis:**

- **REA: `rea-agents@6.7.0`**, installed via `npx rea-agents setup`.
- REA reverse-engineering skill installed for CLI use.
- CLI: `npx rea-agents analyze /path/to/app`
- Deep analysis: Ghidra, guided reverse-engineering workflows installed.
- **All 15 REA tools installed 2026-11-07:** Detect-It-Easy 4.0.0,
  capa v10.0.0, ImHex 1.38.1, LIEF 0.16.2, Ghidra (two copies: apt
  12.1.4 + upstream 12.2), GhidraMCP 2.0 (port 8081, VERIFIED LIVE 2026-11-11 — PR #81; listens only while Ghidra is open with a program loaded), angr 10.0.5, Frida 17.26.2, objection 1.12.5, jadx 1.5.6,
  Apktool 3.0.3, ILSpy ilspycmd 11.2.0.10050, asar 4.3.1, mitmproxy
  12.3.1, Wireshark 4.6.9. Teach guide:
  `local-jarvis/rea-tools/rea-tool-usage-guide.md`; registry
  `~/Jarvis/rea-toolset.md` lives on the Acer.
- **C270 15-tool breakdown — CLOSED 2026-11-08:** 373 functions
  decompiled, 6,037 packets / 233 MB live pcap, 83.0% isochronous.
  Verdict: stock, clean UVC device. Figures in
  `local-jarvis/STATE-2026-11-11.md`; the full consolidated report
  lives on the Acer, not yet sent.
- **BLA 3.2.3 (counter-REA defense, not a REA tool)** — installed
  2026-11-10; 14/14 benchmark (internal modeled estimates, caveated
  in `STATE-2026-11-11.md`).

**X-post 10 MCP tools — morning 2026-11-11:** FastAPI-MCP 0.4.0
installed (venv ~/opt/fastapi-mcp-venv, Python 3.14.10; library only);
Shodan MCP 1.0.37 built (~/opt/mcp-shodan) and wired into Claude Code
+ Cursor (SHODAN_API_KEY set, never published; agents need a restart);
awesome-mcp-servers catalog cloned (~/opt/awesome-mcp-servers, 43,159
objects, 546.32 MiB, reference only); catalog pointer in all 4 REA/BLA
skill files (Cursor REA pointer done 10:18 ET). Still to do: TalkToFigma
(needs Bun first) and ElevenLabs MCP (repo archived/deprecated — hosted
MCP recommended); held: Blender, Unity, Apple MCP. Full record:
`local-jarvis/XPOST-10-TOOLS-2026-11-11.md`; state:
`local-jarvis/STATE-2026-11-11.md`.
- Status: REA is ready for local app analysis.

**What REA is for here:** the basement laptop that can rip apart anything, then put it back together with evidence. Local app analysis only — own devices and own targets only, consenting adults, controlled lab only, spine SEE → DOCUMENT → LOG → PREVENT.

---

## 4. The pending stack — partly built, partly pending

**Items marked BUILT are installed and verified. PENDING items are
planned only — not claimed as installed until HgX confirms them built.**

### 4.1 The local brain — dual brain, BUILT

- **Ollama check** — BUILT. Ollama running on `127.0.0.1:11434`.
- **Small model, resident on VRAM (fast low-end brain)** — BUILT.
  `qwen9b-abliterated-32k` (custom model, FROM `qwen9b-abliterated`,
  `num_ctx` 32768, temperature 0.7), ~7.1 GB loaded, context 32768
  since 2026-11-10 (was 8192), super fast, the REA default. The
  original 8192 model still exists in Ollama but is no longer loaded
  at boot.
- **Large model, resident on system memory (slow high-end brain)** —
  BUILT. `huihui_ai/Qwen3.8-abliterated:27b`, ~18 GB loaded, 100% CPU,
  `num_gpu 0`, context 4096, for hard reasoning, long code, multi-step
  chains, and context beyond the small model's range. New on disk, not
  loaded: `huihui_ai/Qwen3.8-abliterated:27b-omb-64k` (17 GB, pulled
  ~11h ago, 2026-11-11).
- **Switching logic (Usage Router + Model Router)** — BUILT. Default
  to the small VRAM model; escalate to the large RAM model on hard work
  or repeated failure; de-escalate afterwards. Never generating with
  both at once. Every switch logged. Router on :11435; GPU orchestrator
  on :11436 swaps the card without a spoken command (deployed
  2026-11-06, loop proven). Both brains autostart at reboot (~41s)
  and stay pinned 24h (keep-alive every 6h).
- **No middle 8B test.** There is no middle test between the small and large models.

### 4.2 The seventeen software stacks — pending, in efficient order

Syllabus v1.0.1 counts seventeen local-only software stacks, in this efficient order. Items 1–4 are BUILT; items 5–8 are PENDING; item 9 is PARTIAL; items 10–11 are installed but not running/verified; item 12 is PENDING. Installs happen one by one, in this order, only on HgX's order, in his lab only:

1. **REA** — BUILT (`rea-agents@6.7.0`).
2. **Quick tools** — BUILT: security-audit-skill (sandboxed), Graphify 0.9.102, HyperFrames (CLI 0.9.13, platform 1.2.1).
3. **Ollama tools** — BUILT: FreeLLMAPI (routed to local Ollama, port 3001, fallback only), ai-memory 3.4.0 running.
4. **Heavy GPU, separate venvs** — BUILT: ComfyUI 0.44.0 (SD 1.5), installed in its own venv, runs only through the GPU orchestrator; DOWN/parked standing, ran 2026-11-07 for 36 GPU-night visuals.
5. **DeepTutor** — PENDING.
6. **Prism** — PENDING.
7. **Macro, Kali only** — PENDING.
8. **Hacking-Tools gaps, one by one** — PENDING. The hacking-tools catalog is a reference map, not 900 installs: not all 900 run at once, not every listed item runs locally, installs wait for the Kali phase, one tool at a time and only on his order.
9. **Claude Plugins** — PARTIAL: Claude Code 2.1.322 installed via Free Claude Code 6.19.6 (2026-11-10, server :8082) and WORKING — first fcc-claude answer 2026-11-10 08:46 ET via the custom `qwen9b-abliterated-32k` model; the plugins themselves unconfirmed. **Qwen Code 0.27.1** installed 2026-11-10 (local Ollama 9B-32k config given, test confirmed 2026-11-10 20:07 ET — item #7 DONE). **OpenMausBot 0.1.151 (the Grok Bot)** installed + running 2026-11-10 — Claude skills ON (REA + BLA skills load), MCP servers OFF, Engines step DONE via PATH shim 2026-11-11 07:19 ET (item #8 DONE); the GUI Engines step does not exist in this install.
10. **VoiceStudio** — INSTALLED 0.5.7, launched once (home screen verified), not running.
11. **GenOffice** — INSTALLED 0.12.852, launch not yet verified.
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
- Current state snapshot: `local-jarvis/STATE-2026-11-11.md` — the exact moment, 2026-11-11 ~10:17 ET. (STATE-2026-11-10.md + STATE-2026-11-07.md stay as history.)
- Build plans: `local-jarvis/plans/` — the design records (dashboard, drive clean-out, C270 teardown, REA bench list).
- Pi 500+ rig: `local-jarvis/pi500/` — top 10, software stack, accessories (ordered + paid 2026-11-05).
- Platform record: `local-jarvis/PLATFORM-KALI.md` — the Kali + REA build record.
- Full guide: `local-jarvis/README.md` — install, voice loop, orchestrator, troubleshooting.
- Run it yourself: `local-jarvis/SETUP.md` — the whole system from this repo alone, in order.
- Course stacks: `course/syllabus/OPERATOR-PRIME-SYLLABUS-v1.0.1.md` — the seventeen stacks in course canon.
- Course site: `course/` — the platform section lists the stacks for students.

---

@basementjarvisu · basementjarvisunleashed@gmail.com
