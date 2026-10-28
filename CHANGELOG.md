# Changelog

All notable changes to the J.A.R.V.I.S. open-source release. Versions follow
the papers; the repo itself is tagged at release milestones. From 1.1.0 the
estate version also lives in `VERSION`.

## [1.2.1] — 2026-10-28 — night addendum

Patch on 1.2.0. Contract versions and paper versions are unchanged.
The 1.2.0 sections of `docs/logs/2026-10-27.md` are not rewritten.

### Added

- Addendum on the 2026-10-27 operations log, America/Toronto:
  - Three watchdog launcher lines in the box shell startup files were
    commented out, not deleted, and backed up. Policy: no launchers in
    startup files. The box shell was still hanging after 12:36 AM.
  - The voice loop and voice gate ran from about 11:38 PM to 12:15 AM
    (REA, at HgX's request). They stay off until HgX starts them. A
    single-instance lock and a start audit log remain.
  - At 12:47 AM, with HgX's admin approval: Remote Mouse firewall rules
    limited to the Private network, `OLLAMA_KEEP_ALIVE` changed from 24h
    to 4h and Ollama restarted, process-creation auditing turned on.
    ComfyUI already runs with `--disable-smart-memory`.
  - Risk: Ollama uses about 5.2 of 6 GB VRAM, so Whisper on CUDA may run
    out of memory. Cold voice turns take 6.0 s; warm turns take 1.7 s.
  - The free gateway has 0 provider keys and returns 503. Work is ongoing.
  - Still waiting on HgX: sshd password-login hardening, and a reboot.
- Homepage chronicle entry and version **1.2.1**.

### Notes

- No startup-file paths, backup paths, account names, addresses, or ssh
  configuration were added.
- Mailbox addresses that remained in the 2026-10-19 notes, and the same
  addresses elsewhere in the tree, now read as HgX's engineering inbox
  and the estate's inbox. The addresses themselves are not published.
  Loopback numeric addresses in the laptop notes and the Local Jarvis
  sources now read as localhost.
- The 1.2.0 entry below stays as it was written.

## [1.2.0] — 2026-10-28 — operations log for 2026-10-27

Next minor after 1.1.0. Contract versions and paper versions are unchanged.
Commissioned by HgX at 00:26 America/Toronto.

### Added

- `docs/logs/2026-10-27.md`, the public operations log from morning to night.
  Roster and personas, hand-off (code, pull requests, and router work to
  The Plugin Armoury; Security Audit Force is the security gate), router
  v2.2 at 17:28 (50 second voice budget, 60 second client wait, freellmapi
  as fallback only), the Grok Bot disk-full lockout and recovery, the
  hourly disk watch (45% alert, 50% cap), the night's StartupApproved
  efficiency pass, Cloud JARVIS's three inefficiencies, REA's list pending
  GO, and the Graphify how-to.
- README section **Recent**, pointing at that log.
- Homepage section for the same log. `VERSION` is **1.2.0**.
- [`INDEX.md`](INDEX.md) indexes graphs. None are published yet.

### Notes

- The freellmapi fallback address is not in the log. No keys, tokens,
  machine identifiers, or personal paths were added.
- StartupApproved disabled Discord, Acrobat Sync, Edge autolaunch, and
  Firefox. The disable can be undone. ComfyUI VRAM was freed. `qwen3:8b`
  stays warm for voice.
- REA's filing waited on the security gate. The same log now includes the night-of-27–28 laptop changelog: Security Audit Force cleared it, and each cleared item has a backup. Still open: FreeLLMAPI returns 503 with 0 provider keys, and the VoiceMeeter task error. sshd hardening and a reboot wait on HgX. No address, account name, or backup path is published.
- The 1.1.0 entry below stays as it was written.

## [1.1.0] — 2026-10-27 — estate roster

Next minor after the `v1.0.0` release tag. Contract versions and paper
versions are unchanged.

### Added

- `VERSION` declares estate **1.1.0**.
- README estate overview: Cloud JARVIS is the cloud brain and sovereign;
  Local Jarvis is on the owner's laptop; the chief of staff coordinates
  the worker bots and reports to both.
- Bot roster of nine workers, each with a persona: Image Forge (ComfyUI
  v0.43.0, flamboyant Renaissance painter), Security Audit Force (noir
  detective; the security gate), OpenMuse (serene Greek muse), The Free
  Model Gateway (freellmapi, Brooklyn hustler), Memory (ai-memory,
  Scottish librarian), HyperFrames (Hollywood director), The Plugin
  Armoury (Viking blacksmith; router and orchestration), Codebase
  Cartographer (Graphify, Victorian explorer), and REA, Reverse Engineer
  Anything (Cold War spy).
- Standing rules on the public record: no deletions; a pull request for
  every change; a security review before anything touches the laptop;
  every bot answers by voice memo.
- GitHub Pages homepage (`index.html`) carries the same overview,
  architecture, roster, and version.

### Changed

- Local Jarvis architecture: router v2.2 went live 2026-10-27 at 17:28
  America/Toronto. A voice turn has a 50 second budget. freellmapi is the
  fallback when Ollama is down. Ollama remains `qwen3:8b`. The orchestrator
  remains on port 8080. Voice remains Whisper and Piper.
- The downloadable `local-jarvis/` installer is unchanged. ComfyUI v0.43.0
  and freellmapi are on the laptop; they are not added to `install.ps1`.

### Notes

- About 15 free LLM provider keys were pooled on 2026-10-27 for The Free
  Model Gateway. No key material is in this repository.
- A box disk incident on 2026-10-27 was recovered. No host names, disk
  identifiers, or recovery steps are published.
- Earlier 2026-10-27 entries below stay as they were written.

## [2026-10-27] — public site and living docs

### Changed

- Root `index.html` is a static dark homepage: Local Jarvis, architecture,
  download, docs, research (`#research`), and the build chronicle. No
  third-party scripts. GitHub Pages still publishes `/` on `main`.
- Living docs (README, INDEX, CONTRIBUTING, SECURITY, papers, Academy,
  evidence) state the current fact: Local Jarvis is live on 2026-10-27
  in `local-jarvis/`.
- `website/index.html` stays as the archived white-paper hub, marked
  deprecated for publishing. Its relative Academy links now resolve from
  `website/` to the repository root.
- Link check runs in CI. Broken files and HTTP 404/410 fail the job.
  Timeouts and flaky external status codes do not.
- `index.html` gained a `#research` anchor so the research entry pages
  resolve.

### Notes

- Dropbox shares were checked on 2026-10-27 and ask for a login. URLs were
  not replaced.
- The 2026-10-19 Muse share returns "Shared link unavailable". The URL
  remains in the changelog below as history. The live site is GitHub Pages.
- Licenses were already present (MIT, CC-BY-4.0). None was added.
- `deployment-build-v1.0/` and `watchtower/STATUS.md` were not modified.
- Historical note on the unreleased section below: `doctrine/` was never a
  directory. Papers are indexed in `papers/`.

## [Unreleased]

### Added

- Release log begins: `release-log/2026-10-19.md` — dated build log with
  timestamps (America/Toronto), work hours, and comments. The formal log
  system started 2026-10-19 at HgX's order; entries before 16:30 ET are
  reconstructed at honest granularity.
- README: new "Following the build-out" section pointing readers at the
  versioned papers (`doctrine/`), the release log (`release-log/`),
  CHANGELOG.md, and the doctoral workstream (`formal-spec/`).
- Dropbox: immutable versioned archive under `/J.A.R.V.I.S./` — every paper
  version in `papers/<paper>/<version>/` with VERSIONS.md, the roadmap's own
  folder tree (`roadmap/formal-spec/phase-N/`), dated logs (markdown + PDF) in
  `logs/`. Root-level latest copies untouched; their share links keep working.

## [2026-10-27] — downloadable build

### Added

- Local Jarvis is downloadable and installable from
  [`local-jarvis/`](local-jarvis/README.md): a Windows 10/11 install guide
  (NVIDIA GPU, tested on an RTX 2060 6GB), idempotent `install.ps1`, and
  `.env.example` with placeholders only.
- `enroll.py` (5 takes, `--verify`), `jarvis.py` (`qwen2.5:3b`), and the
  two requirements files. `requirements-voice.txt` targets
  `C:\Jarvis\venv`. `requirements-orchestrator.txt` targets system
  Python 3.13 for the voice gate and enrollment.
- Optional logon tasks in `local-jarvis/tasks/`. The voice loop is
  deliberately not auto-started. `install.ps1` registers tasks only with
  `-RegisterTasks`, and only after the `<user>`, SID, and path
  placeholders are edited. It does not remove files or store secrets.
- `.gitignore` also covers `take*.wav`, `out/`, and `voices/*.onnx`.
  `.env.example` stays tracked; a real `.env` does not.

## [2026-10-27] — Local Jarvis laptop stack

### Added

- `local-jarvis/`: basement laptop stack. Orchestrator on port 8080
  (Ollama `qwen3:8b` via `/api/chat`, think off, regex fast path for VLC
  media commands, VLC HTTP remote on `localhost:8090`, read-only
  `rea_analyze`). Voice loop `jarvis_voice.py`: mic → Whisper `small.en`
  → speaker voice gate → `POST /jarvis` → Piper TTS. The voice loop does
  not auto-start.
- Voice gate threshold **0.45**, marked **UNCALIBRATED**, pending
  calibration for quiet voice, across the room, and unknown voice.
  Unenrolled voices are ignored.
- Passwords in the tree are the placeholder `CHANGE_ME` and must be set
  locally. Windows paths use `C:\Users\<user>`.
- Secret scanning with gitleaks on push and pull request, and a CI job
  that runs `python -m py_compile` on `local-jarvis/*.py`.
- `.gitignore` extended for voice profiles (`profiles.json`, `*.npy`),
  audio (`*.wav`, `*.mp3`), models (`*.onnx`, `*.onnx.json`, `*.gguf`,
  `pretrained_models/`), `.env*`, and `*.bak*`. `__pycache__` stays ignored.

## [2026-10-19] — Phase 1: TLC proof of the state machine

- 3,266,929 distinct states explored; zero invariant violations after six
  spec fixes (each found via a TLC counterexample, each fix principled).
- Chain-of-custody holds on all reachable states; failure semantics
  (fail closed, fail visible) verified.
- Caveat: state space not fully exhausted (~2M states still queued);
  exhaustive run desirable for the doctoral evidence package.

## [2026-10-19] — Phase 0: freeze the contracts (v0.1.0)

- Canonical glossary: 69 terms defined once, 25 vocabulary conflicts resolved
  — out for HgX's ratification (v1.0.0 on ratification).
- Work-state machine in TLA+: 12 states, 21 transitions; chain-of-custody
  enforced by construction (skipping a stage is unreachable).
- Canonical event vocabulary: 19 events, each with trigger, payload, and
  transition cross-references.
- Contract governance: ownership, SemVer, propose → evidence → ratify change
  process.

## [2026-10-19]

### Added

- White-paper trilogy rewritten with open source as the main vision:
  - Paper I — vision/doctrine (v1.2): fifth foundation principle, *open
    source from day one*; new Phase 8 — publish the reference implementation.
  - Paper II — backend technical (v1.1): open source woven through the
    foundation, skills, memory contracts, and acceptance tests.
  - Paper III — front-end (v1.1): open source as main vision; iPhone client
    framed as the open reference client.
  - Paper IV — doctoral roadmap, *From Doctrine to Proof* (v1.1, 110 pages):
    open source through every phase, new publication boundary, new risk R9
    (open-source publication hazards).
- Public hub site hosting all four papers (historical URL; on 2026-10-27
  the share returned "Shared link unavailable". The live site is GitHub
  Pages):
  https://muse.ai/s/j-a-r-v-i-s-white-paper-wxs6bxaxyuhxafxi
- `SYSTEM_PROMPT.md` — the release's identity rules: public references only
  as @hgxengineering; the principal's real name never in public material.
- Dual licensing: MIT for code/skills/tooling (`LICENSE`), CC-BY-4.0 for
  white papers and documentation (`LICENSE-CC-BY-4.0`).

### Notes

- Release identity: @hgxengineering (X), contact HgX's engineering inbox;
  Jarvis is @basementjarvisu on X; accounts under
  the estate's inbox.
