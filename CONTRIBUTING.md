# Contributing to J.A.R.V.I.S.

This is an open-source operating system for a personal AI estate. It is built in the open. The operator is **HgX**.

## Ground rules

1. **Identity is absolute.** Never add real names, home addresses, public IPs, Wi-Fi details, passwords, tokens, Windows usernames, voice recordings, or other personal data — in code, docs, logs, or comments. Call the operator HgX. The public handle on X is `@hgxengineering`.
2. **Versioning law** ([`VERSIONING.md`](VERSIONING.md)). Every normative artifact carries a version. v0.x.x is a draft. v1.0.0 is ratified. Versions only move forward.
3. **Changelog discipline.** Every user-visible change gets a [`CHANGELOG.md`](CHANGELOG.md) entry.
4. **Evidence over claims.** Consequential runs end in inspectable evidence (`formal-spec/proofs/`, `release-log/`, [`EVIDENCE.md`](EVIDENCE.md)).
5. **One role per skill.** New capabilities arrive as new skills under `skills/`. Duties do not cross.
6. **Do not delete history.** A stale file can be marked deprecated. Logs stay. Corrections are new notes.

## Local Jarvis

The downloadable build lives in [`local-jarvis/`](local-jarvis/README.md) and has been in the tree since 2026-10-27. Changes there must keep placeholders (`CHANGE_ME`, `<user>`). Do not commit profiles, audio, model weights, or a real `.env`. `python -m py_compile` on `local-jarvis/*.py` runs in CI, as does gitleaks.

## How to propose a change

- **GitHub:** open an issue from [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/bug_report.md), then a pull request. The template is [`.github/pull_request_template.md`](.github/pull_request_template.md).
- **GitLab:** open an issue from [`.gitlab/issue_templates/`](.gitlab/issue_templates/bug.md), then a merge request.

## Release process

Releases are cut in the open: papers indexed under [`papers/`](papers/README.md) (there is no `doctrine/` directory), dated logs under [`release-log/`](release-log/), and the GitHub Pages homepage at the repository root kept current. `website/index.html` is the archived hub, not the page Pages serves. Nothing ships that cannot be published.

## Conduct and security

Participation follows [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Vulnerabilities go through [`SECURITY.md`](SECURITY.md), not a public issue.
