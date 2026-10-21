# Changelog

All notable changes to the J.A.R.V.I.S. open-source release. Versions follow
the papers; the repo itself is tagged at release milestones.

## [Unreleased]

### Added

- Research: `research/Bitcoin-vByte-Fee-Stats-2026-04-21-to-2026-10-21.md` —
  Bitcoin fee rates per vByte, six-month statistics (2026-04-21 →
  2026-10-21), commissioned by HgX, prepared by Research Bot. Floor-fee
  regime: median 1.0 sat/vB nearly throughout; largest intraday spike p90
  4.08 sat/vB (Jun 9). Published on the hub (new Research section);
  scrubbed — public on-chain statistics only.
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
