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

### Layer 1 gate remainder — CLOSED 2026-10-21
- The five v0.1 schema drafts (built 2026-10-20/21, promoted to
  `contracts/` on HgX's word 2026-10-21) are now covered:
  `tests/layer1/test_schema_examples.py` (stdlib-only schema
  validator + worked examples + failing cases), 23/23 passing,
  evidence `tests/evidence/2026-10-21-schema-tests.log`.
- Closed gaps: INV-E2 (revision binding, SCH-EP-01/03), INV-E4
  (required `gaps`, SCH-EP-02), INV-S2 substrate (Watchtower closed
  enum, SCH-WT-01/02), approval-intent/decision-packet guard coverage
  (SCH-AI-*, SCH-DP-*).
- D-D closed: all seven prescribed files built 2026-10-21 as v0.1
  drafts and promoted to `spec/` + `contracts/` (`spec/state-machine.md`,
  `spec/approval-digest.md`, five schemas); open questions OQ-1..OQ-6
  recorded in `tests/staging/prescribed-files/BUILD-NOTES.md`.

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

## Session log — 2026-10-21 (full re-run with the nine answers, on HgX's order ~13:00 ET)

- Re-ran the ENTIRE Phase 2 verification with all nine answered questions baked in as the run configuration (`tests/PHASE-2-OPEN-QUESTIONS.md`).
- Fresh counts, quoted exactly: Layer 1 **64/64 OK** (39 contract + 25 schema); Layer 2 **10/10 OK** (PT-4: 2,000 sequences, 55,983 attempted steps, 168 executions, 22 completions — all invariant assertions held); **53,003** attempted actions refused, by guard; Layer 3 **10/10 OK**; crosscheck **12/12** (Q9 improvement exercised).
- Configuration verified: integer expiry/revision in fixtures; eight-field digest bound in `INTENT_FIELDS` (CT-A2 + PT-1 mutation pool cover all eight); sketch names in EP schema tests; crosscheck 12/12.
- Harness corrections (test code only, no ratified file touched): (1) all five `contracts/*.schema.json` stripped to pure JSON (trailing markdown promotion notes removed; content retained in `$comment` and BUILD-NOTES.md); (2) digest model extended six→eight fields per Q3, both layers' fixtures + mutation pools updated; (3) Layer 2 rejection-log filename made date-derived after the hardcoded 2026-10-20 name overwrote the prior day's local copy (2026-10-20 data survives in the committed repo and the 2026-10-20 report).
- Evidence: `tests/evidence/2026-10-21-rerun-{layer1,layer2,layer3,crosscheck}.log`, `tests/evidence/2026-10-21-layer2-rejections.log`.
- Report: `tests/PHASE-2-RUN-REPORT-2026-10-21.md` (committee-grade; nine answers as configuration; gaps stated plainly).
- **Phase 2 remains OPEN** on HgX's word (Q8). Remaining by design: INV-R2/R3/R4 (Phase 6), CH-5/CH-6 depth, E3/S3/S5 rendering, events.md amendment pending, Q2-vs-sketch type coherence open, CI/third-party runnability.

## Session log — 2026-10-21 (day work, on HgX's order ~11:42 ET)

- Fresh re-runs: Layer 1 39/39 OK; Layer 2 10/10 OK (PT-4: 2,000
  sequences, 56,261 steps, 162 executions, 23 completions — exact
  reproduction of the 2026-10-20 volumes); Layer 3 10/10 OK;
  crosscheck 11/12 (the single failure is the documented honest
  limitation on run-attributed state figures in the backtrace manifest —
  see the 2026-10-20 run report §5; the check-improvement proposal
  still needs HgX's word); new schema suite 23/23 OK.
- Evidence: `tests/evidence/2026-10-21-layer1-rerun.log`,
  `2026-10-21-layer2-run.log`, `2026-10-21-layer3-run.log`,
  `2026-10-21-crosscheck.log`, `2026-10-21-schema-tests.log`.
- **Phase 2 remains OPEN.** Remaining items, stated exactly:
  (a) INV-R2/R3/R4 uncovered — the usage router is estate runtime;
  mechanised only in Phase 6 (`spec/router-policy.md` planned);
  (b) CH-5/CH-6 run at contract level only — full form needs the
  Paper III client/router artifacts (no artifact in this repository);
  (c) INV-E3/S3/S5 rendering side pending — packet side of E3 now
  schema-backed (v0.1 draft), S3 schema-level only, S5 uncovered
  (Paper III shared surfaces); (d) open questions OQ-1..OQ-6 from the
  seven-file build still need HgX's word (revision/expiry types gate
  the Phase 3 revision protocol); (e) CI/scheduled-run wiring and
  third-party runnability per Paper IV §8.4.

## Publication

- GitHub (jarvis-estate): the tests/ package, this plan, and all run
  evidence, committed with descriptive messages as the work lands.
- GitLab: the mirror carries the same record when it is pushed; the
  mirror remains tracked pending HgX's token handover.
- Dropbox: the phase record filed under /J.A.R.V.I.S./ per the
  versioning doctrine.
