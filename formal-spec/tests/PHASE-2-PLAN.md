# Phase 2 — Programme Plan
## Invariant Verification · Opened 2026-10-20 on HgX's order

> Pacing directive (HgX, 2026-10-20): "Go hard on Phase 2. Take our time
> with it — do not hurry it. Follow the roadmap. Make sure it takes as long
> as the roadmap says it takes, go through everything, document everything,
> comment everything, and show our proof of work — that is the only way
> this becomes legitimate."

## The governing rule

Phase 2 closes when its exit criteria are met — not before, not on a date
invented for convenience. The roadmap (ROADMAP.md §5; Paper IV §8) allots
Phase 2's three layers run in sequence across the programme's Months 3–4
window (Paper IV §14: Month 3 — Phase 2 contract tests; Month 4 — Phase 2
property and chaos tests). Each layer has a gate; a layer opens only when the previous
layer's gate has passed and been recorded.

## Layers and gates

### Layer 1 — Static contract tests (opened 2026-10-20)
- Schema validation; unknown enums fail closed; missing fields fail;
  expired approvals fail; mutated digests fail; incomplete evidence
  cannot produce completion.
- Opening state: suite live, 39/39 passing against the real contracts
  and the TLA+ spec (verified 2026-10-20).
- Remaining Layer 1 work: the missing contract artifacts the suite
  honestly flags — evidence-packet schema and artifact-manifest schema
  (contracts/), Watchtower state-rendering schema, front-end contract
  note — each drafted, reviewed, and added to the contracts under
  Phase 0 governance, then covered by tests.
- Gate: every invariant assigned to Layer 1 in the catalogue is covered
  by an automated test whose output is on record.

### Layer 2 — Property-based tests (opens on Layer 1 gate)
- Random event sequences asserting the invariants: approval mutations,
  expiry times, duplicates, network loss, sub-agent claims, stale
  sources (PT-1…PT-5 per Paper IV §8.2).
- Rejection logs produced and kept — an invariant that has never
  rejected anything is a claim, not a control.
- Gate: property suites green over the agreed sequence volumes, with
  rejection logs filed as evidence.

### Layer 3 — Chaos tests (opens on Layer 2 gate)
- The ten canonical scenarios: device offline during approval; approval
  expiry mid-review; intent change after card render; duplicate tap;
  backend change before client refresh; router backend down; stale live
  source; sub-agent completion without evidence; digest mismatch;
  missing tests in the evidence packet (CH-1…CH-10 per Paper IV §8.2).
- Gate: all ten scenarios executed with results on record — passes and
  failures alike; a failure found here is a finding, not an embarrassment.

## Documentation and proof-of-work standard

- Every work session on Phase 2 produces: the artifact changed, the
  test command run, the observed output, and the date (America/Toronto).
- Test outputs and rejection logs are evidence: filed under tests/ and
  committed to the release repository by the publishing house; nothing
  is summarised from memory.
- The traceability matrix is a living document: an invariant's row is
  updated in the same session that changes its status.
- The build log records every Phase 2 session; the website chronicle
  and the Dropbox archive are kept current by the publishing house.
- Statuses are stated exactly: covered / partially covered / blocked on
  a named artifact. No status is rounded up.

## Exit criteria (ROADMAP.md §5, verbatim intent)

Every major doctrine statement has a testable invariant; all tests
automated; mutated or expired approval cannot pass; optimistic
completion fails tests; the suite is citable as empirical validation.
Phase 2 closes on HgX's word, on evidence — the same discipline as
Phases 0 and 1.

## Publication

- GitHub (jarvis-estate): the tests/ package, this plan, and all run
  evidence, committed with descriptive messages as the work lands.
- GitLab: the mirror carries the same record when it is pushed; the
  mirror remains tracked pending HgX's token handover.
- Dropbox: the phase record filed under /J.A.R.V.I.S./ per the
  versioning doctrine.
