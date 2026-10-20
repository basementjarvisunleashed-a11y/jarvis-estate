# Contributing to J.A.R.V.I.S.

Welcome. This is an open-source operating system for personal AI, and it is
built in the open from day one.

## Ground rules

1. **Identity is absolute.** Never add real names, personal addresses, credentials,
   financial details, or any private data — in code, docs, logs, or comments.
   Public identity is `@hgxengineering` only.
2. **Versioning law** (`VERSIONING.md`). Every normative artifact carries a version:
   v0.x.x = draft, v1.0.0 = ratified. Versions only move forward; every change is
   committed with a reason.
3. **Changelog discipline.** Every user-visible change gets a `CHANGELOG.md` entry.
4. **Evidence over claims.** Consequential runs end in inspectable evidence
   (reports under `formal-spec/proofs/`, logs under `release-log/`).
5. **One role per skill.** New capabilities arrive as new skills under `skills/`;
   duties never cross between roles.

## How to propose a change

- **GitHub:** open an issue from `.github/ISSUE_TEMPLATE/`, then a pull request
  (see `.github/pull_request_template.md`).
- **GitLab:** open an issue from `.gitlab/issue_templates/`, then a merge request.

## Release process

Releases are cut by the estate's release office: versioned papers under
`doctrine/`, dated logs under `release-log/`, and the website hub kept current.
Nothing ships that cannot be published.
