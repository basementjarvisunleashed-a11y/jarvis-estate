# Phase 2 — Full-Sweep Run Report, 2026-10-20

*Ordered by HgX on the evening of 2026-10-20 (America/Toronto): re-run
Layer 1, build and run Layers 2 and 3, cross-check against all
artifacts, and file everything as evidence for the 2026-10-21 02:00
commit. Every number below was printed by the run it cites and is
filed, raw, in `tests/evidence/`. Nothing is summarised from memory.*

**Phase 2 remains OPEN.** These runs build the evidence base the
phase will be judged on; they do not close it, and no gate is declared
passed on their strength alone — the gates also require the missing
contract artifacts named in §6 below and, per Paper IV §8.4, the
suites running in CI / on schedule, runnable by third parties.

## 1. Layer 1 — re-run

- Command: `cd tests/layer1 && python3 -m unittest test_layer1_contracts -v`
- Evidence: `tests/evidence/2026-10-20-layer1-rerun.log`
- Observed: **Ran 39 tests — OK (39 passing, 0 failures).**
- The suite as built at the phase opening was re-run unmodified; the
  result reproduces the opening run exactly.

## 2. Layer 2 — property-based suite (new)

- Files: `tests/layer2/work_item_sim.py` (simulator over the Layer 1
  guard model, with the rejection ledger), `tests/layer2/test_layer2_properties.py`,
  `tests/layer2/run.sh`, `tests/layer2/README.md`.
- Command: `cd tests/layer2 && python3 -m unittest test_layer2_properties -v`
- Evidence: `tests/evidence/2026-10-20-layer2-run.log`;
  rejections in `tests/evidence/2026-10-20-layer2-rejections.log`.
- Observed: **Ran 10 tests — OK (10 passing, 0 failures).**
- Fixed seeds: PT-1 (20261020, 20261021, 20261022), PT-2 20261023,
  PT-3 20261024, PT-4 (20261025–20261029), PT-5 20261030 — recorded in
  the suite source and in the rejection log.
- Volumes and results, per property test (Paper IV §8.2):
  - **PT-1 mutation fuzz** (INV-A2, A3, A7): 900 mutated intents —
    450 mutated between tap and record, 450 between record and
    grant. Every mutation refused on digest mismatch; zero
    executions. An unmutated control intent records and executes.
  - **PT-2 expiry sweep** (INV-A4): 3,000 (expiry, attempt-time)
    samples spanning ±1 year; every attempt with `now ≥ expiry`
    refused at record and at grant, every live attempt honoured; the
    exact boundary `now == expiry` refused. Both branches exercised
    at volume (the suite asserts >1,000 samples per branch).
  - **PT-3 duplicate decision storm** (INV-A6, PO-9): 120 intents,
    1–50 duplicate grant deliveries each, ×1–3 network duplication,
    with interleaved duplicate taps and record retries. Exactly one
    recorded decision and exactly one execution per intent; the
    suite's internal count of refused duplicates exceeded 1,000.
  - **PT-4 random event sequences** (INV-C1–C5, A1, E1; PO-1, PO-2,
    PO-11): **2,000 sequences, 56,261 attempted steps, 162
    executions, 23 completions — all invariant assertions held**
    (printed by the suite; half the sequences driven to the approval
    gate first, half raw; state-aware draws in executing/verifying).
  - **PT-5 stale source injection** (INV-S1, S4, E5; PO-10): 2,000
    renderer readings — a stale reading never rendered `operational`;
    200 blocked items — the source-dependent guard
    (`blockage_cleared`, T8) refused on stale data and passed on
    fresh, both branches at volume.

### Rejection log — totals (whole Layer 2 run)

**53,079 attempted actions refused**, by the guard that refused them:

| Guard | Refusals |
|---|---:|
| illegal-transition | 37,765 |
| duplicate-tap-noop | 3,855 |
| record-without-tap | 3,778 |
| tap-without-request | 2,966 |
| approval-not-recorded | 1,933 |
| approval-expired | 1,476 |
| digest-mismatch | 926 |
| approval-not-expired | 210 |
| stale-source | 95 |
| completion-no-evidence | 49 |
| completion-acceptance-not-passed | 26 |

The full log, with attempts/accepted per action, is the evidence file
named above. Guards exercised by refusal here have demonstrably
rejected something; that is the Layer 2 gate's standard.

## 3. Layer 3 — chaos suite (new)

- Files: `tests/layer3/chaos_model.py` (completion writer, router
  reference, client rendering rule), `tests/layer3/test_layer3_chaos.py`,
  `tests/layer3/run.sh`, `tests/layer3/README.md`.
- Command: `cd tests/layer3 && python3 -m unittest test_layer3_chaos -v`
- Evidence: `tests/evidence/2026-10-20-layer3-run.log`
- Observed: **Ran 10 tests — OK (10 passing, 0 failures)** — CH-1
  through CH-10, each a named scenario test:
  CH-1 offline approval replay (expired and mutated replays rejected;
  unchanged replay recorded by server validation; paused renders
  paused) · CH-2 expiry mid-review (grant at expiry+1 refused, T10 to
  `in_progress`, fresh intent then approved) · CH-3 intent change
  after card render (digest mismatch, rejected) · CH-4 duplicate tap
  (three grant deliveries, one recorded decision, one execution) ·
  CH-5 backend change before refresh (contract equivalents — see §6)
  · CH-6 router backend down (contract equivalents — see §6) · CH-7
  stale live source (renderer downgrades, T8 guard fails closed,
  packet must mark stale) · CH-8 subagent claim without evidence
  (escalated "claim without proof"; completion refused) · CH-9 digest
  mismatch (single-character flip; rejected; tamper signal recorded)
  · CH-10 missing tests in packet (missing result, failed result, and
  missing `gaps` each rejected by the completion writer; complete
  packet completes).

## 4. Cross-artifact consistency audit (new)

- File: `tests/audit_crosscheck.py` — run:
  `python3 tests/audit_crosscheck.py` (from `jarvis-formal-spec/`).
- Evidence: `tests/evidence/2026-10-20-crosscheck.log`
- Observed: **12/12 checks passed, exit code 0.** Catalogue = matrix
  = 27 invariants, ID sets equal; all 27 catalogue statements match
  ROADMAP.md §5 verbatim; events.md = 19 events; the .tla references
  T1..T21 and 17 events bind to T-numbers (T6 jointly), the two
  T-less events being exactly `brief_received` and
  `execution_started`; 12 states (3 terminal); 21 transitions in both
  artifacts; `state-machine.cfg` names (`SafetyInvs`,
  `PO11_TerminalAbsorbing`) and all 9 SafetyInvs conjuncts defined in
  the .tla; Phase 1 figures parsed from
  `proofs/phase1-tlc-report.md` (3,266,929 distinct states,
  205,173,020 generated, zero invariant violations, 6 fixes) match
  every citation of them in `tests/*.md`.

## 5. Harness corrections made during the sweep (test code only)

Recorded in the evidence-log headers as well; no ratified artifact
was touched at any point (verified by modification times: everything
under `contracts/`, `spec/`, `proofs/`, and `ROADMAP.md` predates
this session).

1. Layer 2, first invocation: simulator attribute `delegated_claim`
   shadowed the method of the same name — attribute renamed
   (`claim_asserted`).
2. Layer 2, PT-4 assertion semantics: completion is now judged on a
   snapshot taken at the completion transition (PO-1 binds
   preconditions at that moment); PT-4 also gained the guided/raw
   sequence mix and state-aware draws after a run in which uniform
   generation reached only 3 completions in 2,000 sequences —
   assertions were not weakened; the generator was made honest.
3. Layer 3, first invocation: CH-5/CH-8/CH-10 fired both T6 events
   sequentially; T6 is a joint firing represented in the legal table
   as one transition — the tests now fire it once, as specified.
4. Crosscheck, first invocation: 10/12 — both failures were parsing
   defects in the audit script itself (a dropped `INV-` key prefix;
   T-bindings read from a structure that cannot represent the joint
   T6). Corrected and re-run: 12/12.

One modelling fact worth the committee's attention, surfaced by the
sweep and already noted in the traceability matrix: the cross-built
legal table admits each T6 event individually
(`artifact_produced`, `evidence_packet_created`), while events.md §3
specifies a joint firing. The suites follow the table (the mechanised
artifact); the joint-firing refinement is a documented reading point,
not a discrepancy this sweep introduced or hid.

## 6. Gaps and failures — stated plainly

No test failed in the final runs. The gaps are absences, and they are
the same ones the catalogue carried into the sweep, now narrowed:

1. **INV-C4 (CH-5 full form)** — no Paper III client or
   revision-token refresh protocol exists in this repository. CH-5
   asserts the contract-level equivalents (authoritative state
   governs rendering on read; packet revision binding). The scenario
   cannot run in full until the front-end contract artifact exists.
2. **INV-R1 / INV-R5 (CH-6 full form)** — the usage router is estate
   runtime outside this repository; `spec/router-policy.md` is a
   planned Phase 6 artifact. CH-6 asserts the router contract at
   reference level (named-policy fallback, fallback logged,
   recommendations never cross the consequence boundary).
   INV-R2, R3, R4 remain entirely uncovered — no artifact mechanises
   them yet.
3. **INV-E2 / INV-E4 (schema level)** — the evidence-packet and
   artifact-manifest schema files described in `contracts/README.md`
   do not yet exist under `contracts/`. Their rules (revision
   binding; required `gaps`; completeness against the brief's tests)
   are now enforced by the Layer 3 completion-writer model and
   rejected correctly in CH-5/CH-10 — but a model of a schema is not
   the schema. Drafting those two artifacts under Phase 0 governance
   is the Layer 1 gate's remaining work.
4. **INV-E3 (rendering side)** — the packet side is covered (CH-7:
   stale observations must be marked, not omitted); "missing evidence
   renders as missing" on a surface still awaits a rendering artifact.
5. **INV-S2 / INV-S3** — S2's rendering rule is covered at contract
   level (CH-1); the Watchtower schema artifact is still absent, and
   S3 (degraded requires observed impairment) remains uncovered —
   it needs the Watchtower health-signal contract.
6. **INV-S5** — shared-surface redaction: uncovered; Paper III
   runtime territory, no artifact in this repository.
7. **Phase-level gates not yet met** (PHASE-2-PLAN; Paper IV §8.4):
   the missing contract artifacts above; suites wired into CI /
   scheduled runs; third-party runnability (the suites are stdlib-only
   and documented, but no external run has occurred). Phase 2
   therefore remains open, with Layers 1–3 built and evidenced.

## 7. Status updates filed with this sweep

Per the plan's living-document rule, the same session that changed a
status updated it: `tests/invariant-catalogue.md` (22 status cells +
header + coverage summary) and `tests/traceability-matrix.md`
(test column extended to L1 · L2 · L3, 22 rows). The crosscheck was
re-run after the edits: still 12/12.

## 8. Evidence manifest

| File | Bytes |
|---|---:|
| `tests/evidence/2026-10-20-layer1-rerun.log` | 5,391 |
| `tests/evidence/2026-10-20-layer2-run.log` | 2,759 |
| `tests/evidence/2026-10-20-layer2-rejections.log` | 2,264 |
| `tests/evidence/2026-10-20-layer3-run.log` | 1,826 |
| `tests/evidence/2026-10-20-crosscheck.log` | 1,688 |
| `tests/layer2/work_item_sim.py` | 17,329 |
| `tests/layer2/test_layer2_properties.py` | 18,553 |
| `tests/layer2/run.sh` | 220 |
| `tests/layer2/README.md` | 2,365 |
| `tests/layer3/chaos_model.py` | 5,848 |
| `tests/layer3/test_layer3_chaos.py` | 16,379 |
| `tests/layer3/run.sh` | 201 |
| `tests/layer3/README.md` | 1,550 |
| `tests/audit_crosscheck.py` | 8,613 |
| `tests/invariant-catalogue.md` (status updates) | 10,451 |
| `tests/traceability-matrix.md` (status updates) | 7,064 |
| `tests/PHASE-2-RUN-REPORT-2026-10-20.md` | this file |

All runs: Python 3.12.3, standard library only, on 2026-10-20
between 18:26 and 18:33 EDT (America/Toronto).
