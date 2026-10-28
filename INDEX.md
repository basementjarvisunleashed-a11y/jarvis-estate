# J.A.R.V.I.S. Estate — Repository Index

Public record. Estate version **1.2.1** ([`VERSION`](VERSION)). The operator is **HgX**. No real names.

**Cloud JARVIS** is the cloud brain and sovereign. **Local Jarvis** is on the owner's laptop (Ollama `qwen3:8b`, orchestrator on port 8080, Whisper and Piper, router v2.2 since 17:28 America/Toronto, a 50 second voice budget, a 60 second client wait, freellmapi only when Ollama is down). The **chief of staff** coordinates nine worker bots and reports to both. The roster is in [`README.md`](README.md#bot-roster). The 2026-10-27 operations log is [`docs/logs/2026-10-27.md`](docs/logs/2026-10-27.md). The downloadable Windows build is [`local-jarvis/`](local-jarvis/README.md). The public site is the repository root `index.html`, served by GitHub Pages from `main` at <https://basementjarvisunleashed-a11y.github.io/jarvis-estate/>.

## Runtime

| Path | What it is |
|---|---|
| [`local-jarvis/`](local-jarvis/README.md) | Windows 10/11 laptop stack. `install.ps1`, voice loop, orchestrator on port 8080. Placeholders only. Not auto-started. |
| [`watchtower/`](watchtower/README.md) | Honest uptime monitor. Live states are in `STATUS.md`. |
| [`skills/`](skills/) | Eight roles: `betting-engine`, `bitcoin-x-memes`, `gameday-bot`, `overlord-bot`, `tax-bot`, `team-deployment`, `tickler-bot`, `usage-router`. |

## Doctrine

The white papers are indexed in [`papers/`](papers/README.md). There is no `doctrine/` directory in this repository. Paper IV's source is [`formal-spec/whitepaper/`](formal-spec/whitepaper/jarvis-roadmap-white-paper.md). The full in-browser reader is the archived hub [`website/index.html`](website/index.html).

| # | Paper | Version | Pages | Landed |
|---|---|---|---|---|
| I | Vision | v1.2 | 14 | 2026-10-19 |
| II | Technical | v1.1 | 20 | 2026-10-19 |
| III | Front end | v1.1 | 20 | 2026-10-19 |
| IV | Roadmap to proof | v1.1 | 110 | 2026-10-19 |

Dropbox share URLs are listed in `papers/README.md`. Checked 2026-10-27, those shares respond with a Dropbox login page. They were not replaced.

## Formal specification (`formal-spec/`)

- `contracts/` — glossary and event vocabulary (v1.0.0), governance in `README.md`.
- `spec/` — `state-machine.tla` and the TLC config.
- `proofs/` — Phase 1 model-checking evidence.
- `tests/` — phase results. Phases 0–5 are closed. Phase 6 is open.

Versioning law: [`VERSIONING.md`](VERSIONING.md). v0.x.x is a draft. v1.0.0 is ratified. Versions only move forward.

## Graphs

Codebase Cartographer's Graphify commands, as recorded on 2026-10-27. The how-to is in [`docs/logs/2026-10-27.md`](docs/logs/2026-10-27.md).

| Command | What it is for |
|---|---|
| `graphify update` | Refresh the graph |
| `graphify explain` | Explain a node |
| `graphify path` | Show a path between nodes |
| `graphify affected` | Show what a change touches |

Published graph artifacts:

| Graph | Where | Published |
|---|---|---|
| — | None in the public tree as of estate 1.2.0 | — |

A graph is added as a row here when it is published. It is not written into an older day log after the fact.

## Chronicle

- [`docs/logs/2026-10-27.md`](docs/logs/2026-10-27.md) — operations log for 2026-10-27, with the 1.2.1 addendum.
- [`release-log/`](release-log/) — dated logs from 2026-10-19 onward, America/Toronto.
- [`CHANGELOG.md`](CHANGELOG.md) — notable changes.
- [`EVIDENCE.md`](EVIDENCE.md) — claims and their evidence.
- [`academy/`](academy/README.md) — the course: index, history, decks, lecture records.
- [`research/`](research/README.md) — research notes by day.
- [`audits/`](audits/TEMPLATE.md) and [`scores/`](scores/README.md) — audits and the stability score.

## Root files

- [`README.md`](README.md) — overview, install, architecture.
- [`SYSTEM_PROMPT.md`](SYSTEM_PROMPT.md) — operating identity and public-identity rules.
- [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
- [`LICENSE`](LICENSE) — MIT for code. [`LICENSE-CC-BY-4.0`](LICENSE-CC-BY-4.0) — papers and docs.

## Forge

- [`.github/`](.github/pull_request_template.md) — issue templates, pull-request template, Validate, gitleaks, Local Jarvis `py_compile`, and link check.
- [`.gitlab/`](.gitlab/issue_templates/bug.md) — GitLab issue templates.
- [`.gitignore`](.gitignore) — voice profiles, audio, models, and secrets stay untracked.

`website/index.html` is the archived white-paper hub. Do not publish that file as the homepage. The live page is the root `index.html`.
