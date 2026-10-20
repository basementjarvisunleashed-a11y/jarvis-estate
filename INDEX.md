# J.A.R.V.I.S. Estate — Repository Index

Public, sanitized release. Identity: **@hgxengineering** (no real names anywhere).

## Doctrine — the white papers (`doctrine/`)

| #   | Paper              | File                                        | Version | Pages | Landed     |
|-----|--------------------|---------------------------------------------|---------|-------|------------|
| I   | Vision / Doctrine  | `jarvis-white-paper-v1.2.pdf`               | v1.2    | 14    | 2026-10-19 |
| II  | Technical          | `jarvis-technical-white-paper-v1.1.pdf`     | v1.1    | 20    | 2026-10-19 |
| III | Front-End          | `jarvis-frontend-white-paper-v1.1.pdf`      | v1.1    | 20    | 2026-10-19 |
| IV  | Roadmap (to Proof) | `jarvis-roadmap-white-paper-v1.1.pdf`      | v1.1    | 110   | 2026-10-19 |

Open source from day one is the foundation of all four (Paper I, 5th principle).

## Formal specification (`formal-spec/`) — the doctoral validation programme

- `contracts/` — normative contracts: `glossary.md` (v1.0.0, ratified),
  `events.md` (v1.0.0), `README.md` (governance).
- `spec/` — `state-machine.tla` (TLA+ work-state machine, the proof language),
  `state-machine.cfg` (TLC model-checker config).
- `proofs/` — `phase1-tlc-report.md` (Phase 1 model-checking evidence).

Versioning law: `VERSIONING.md` — v0.x.x = draft, v1.0.0 = ratified, versions only move forward.

## Release log (`release-log/`)

Dated build logs — `YYYY-MM-DD.md`: every release with date, timestamps
(America/Toronto), hours worked, and comments. The estate's chronicle, kept from
2026-10-19 to the final build-out.

## Skills (`skills/`) — one role per skill, duties never cross

`betting-engine`, `bitcoin-x-memes`, `gameday-bot`, `overlord-bot`, `tax-bot`,
`team-deployment`, `tickler-bot`, `usage-router`.

## Watchtower (`watchtower/`)

The estate monitor: `watchtower.py` (portable, stdlib-only), `services.yaml`
manifest (see `services.example.yaml`), live `STATUS.md`. Silent unless something
changed or needs attention.

## Root files

- `README.md` — what this is, and "Following the build-out" (how to track progress).
- `SYSTEM_PROMPT.md` — the operating identity and rules.
- `VERSIONING.md` — the versioning law.
- `CHANGELOG.md` — what changed, per release.
- `INDEX.md` — this file.
- `CONTRIBUTING.md` — how to contribute.
- `LICENSE` — MIT (code). `LICENSE-CC-BY-4.0` — CC-BY-4.0 (papers and docs).

## Forge scaffolding

- `.github/` — issue templates and pull-request template (GitHub).
- `.gitlab/` — issue templates (GitLab).
- `.gitignore` — runtime and local artifacts never committed.
