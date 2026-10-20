# Audit template — weekly / monthly / quarterly

Public, transparent audits of the J.A.R.V.I.S. estate's three release surfaces.

## Header

- Date (America/Toronto):
- Tier: weekly | monthly | quarterly
- Auditor: Release Bot (HgX's publishing office)

## Per surface — website / Dropbox / repo

- Current state (with versions, URLs, paths).
- What changed since the last audit.
- Verification performed and its result.
- Evidence references (commits, receipts, handoffs).

## Identity check

Grep all public surfaces for the principal's real name → expected 0 hits.

## Evidence cross-check

Every PROVEN claim in `EVIDENCE.md` still has its evidence attached.

## Tracked items

New TRACKED items opened; items closed (with proof) since last audit.

## Stability scoring

Recompute the stability score per `scores/README.md` rubric v1.0; append the
week to `scores/STABILITY.md` history (never rewrite). Log new corrections in
`scores/corrections.md`.

## Tier extras

- Monthly: rollup of the month's weeklies, trend notes.
- Quarterly: rollup of the quarter, maturity assessment (growth of the estate).

## Publication

Commit to `audits/<tier>/` in the repo, upload to Dropbox
`/J.A.R.V.I.S./audits/<tier>/`, append the outcome to the build log.
