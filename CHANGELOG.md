# Changelog

All notable changes to the J.A.R.V.I.S. open-source release. Versions follow
the papers; the repo itself is tagged at release milestones.

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

## [2026-10-27] — Local Jarvis laptop stack

### Added

- `local-jarvis/`: basement laptop stack. Orchestrator on port 8080
  (Ollama `qwen3:8b` via `/api/chat`, think off, regex fast path for VLC
  media commands, VLC HTTP remote on `127.0.0.1:8090`, read-only
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
- Public hub site hosting all four papers:
  https://muse.ai/s/j-a-r-v-i-s-white-paper-wxs6bxaxyuhxafxi
- `SYSTEM_PROMPT.md` — the release's identity rules: public references only
  as @hgxengineering; the principal's real name never in public material.
- Dual licensing: MIT for code/skills/tooling (`LICENSE`), CC-BY-4.0 for
  white papers and documentation (`LICENSE-CC-BY-4.0`).

### Notes

- Release identity: @hgxengineering (X), contact HgXengineering@gmail.com;
  Jarvis is @basementjarvisu on X; accounts under
  basementjarvisunleashed@gmail.com.
