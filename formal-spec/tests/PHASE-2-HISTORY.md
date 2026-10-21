# Phase 2 — History of the Work

*A sourced, chronological record of everything done for Phase 2
(Invariant Verification) of the J.A.R.V.I.S. doctoral programme,
2026-10-20 → present. All times America/Toronto (EDT). Every figure below
is quoted from the report that produced it — never from memory. Phase 2
remains OPEN.*

## 2026-10-20 ~18:00 ET — Phase 2 opens on HgX's order

**Ordered by:** HgX, in the working conversation ("start the next phase
of our roadmap"). This is the standing law in action: no phase advances
without his explicit consent.

**Why it mattered:** Phase 1 had *proved* the state machine could not
reach illegal states (TLC, 3,266,929 distinct states, zero violations,
six counterexample fixes — `proofs/phase1-tlc-report.md`). Phase 2 asks
the harder question: do the estate's doctrine statements hold when the
system is *run* — fuzzed, expired, duplicated, taken offline? A proof
about a model is not a proof about behaviour. Phase 2 closes that gap.

**Produced:** `tests/PHASE-2-OPENING.md` (objective, entry criteria as
verified at opening, the 27 invariants, the three verification layers,
the exit criteria, and per-deliverable status), `tests/invariant-catalogue.md`
(27 invariants: C1–C5, A1–A7, E1–E5, S1–S5, R1–R5, verbatim statements,
doctrine sources, layer assignments, per-invariant status), and
`tests/traceability-matrix.md` (invariant → doctrine → enforcement/spec
artifact → test ID).

**Verified firsthand:** the Layer 1 suite — `tests/layer1/` (Python 3
stdlib `unittest`, parsing the real `contracts/events.md` and
`spec/state-machine.tla`) — ran **39 tests, 39 passing, 0 failures**.
Honest coverage position recorded at opening: 11 invariants
behaviourally covered, 4 at structural/machine level, 12 pending on
named artifacts that did not yet exist (packet/manifest schemas,
Watchtower contract, rendering surfaces, the usage router).

**The pacing directive (18:11 ET):** HgX's own words — *"Go hard on
Phase 2. Take our time with it — do not hurry it. Follow the roadmap.
Make sure it takes as long as the roadmap says it takes, go through
everything, document everything, comment everything, and show our proof
of work — that is the only way this becomes legitimate."* This directive
governs the whole phase. It is why this history exists.

## 2026-10-20 ~18:23–18:34 — The full sweep

**Ordered by:** HgX (evening order: re-run Layer 1, build and run
Layers 2 and 3, cross-check everything, file it all as evidence for the
nightly commit).

**Why it mattered:** Opening Layer 1 proved the *contracts* say the
right things. Layers 2 and 3 prove the *invariants* hold when the
system is attacked — approval fuzz, expiry sweeps, duplicate storms,
random event sequences, stale sources, and ten fault-injection chaos
scenarios. Per the plan's own rule, an invariant that has never
rejected anything is a claim, not a control — so the sweep's rejection
ledger is the point, not a footnote.

**Produced:** `tests/layer2/work_item_sim.py`,
`tests/layer2/test_layer2_properties.py`, `tests/layer3/chaos_model.py`,
`tests/layer3/test_layer3_chaos.py`, `tests/audit_crosscheck.py`,
and the raw evidence logs
(`tests/evidence/2026-10-20-layer1-rerun.log`,
`2026-10-20-layer2-run.log`, `2026-10-20-layer2-rejections.log`,
`2026-10-20-layer3-run.log`, `2026-10-20-crosscheck.log`),
all reported in `tests/PHASE-2-RUN-REPORT-2026-10-20.md`.

**Results, exactly as the run report gives them:**

- Layer 1 re-run: **Ran 39 tests — OK (39 passing, 0 failures).**
- Layer 2 (new): **Ran 10 tests — OK (10 passing, 0 failures).**
  - PT-1 mutation fuzz: 900 mutated intents, every mutation refused on digest mismatch, zero executions.
  - PT-2 expiry sweep: 3,000 (expiry, attempt-time) samples; every attempt with `now ≥ expiry` refused; the exact boundary `now == expiry` refused.
  - PT-3 duplicate decision storm: 120 intents with 1–50 duplicate grant deliveries; exactly one recorded decision and exactly one execution per intent; refused duplicates exceeded 1,000.
  - PT-4 random event sequences: **2,000 sequences, 56,261 attempted steps, 162 executions, 23 completions — all invariant assertions held.**
  - PT-5 stale source injection: 2,000 renderer readings — a stale reading never rendered `operational`.
- Rejections: **53,079 attempted actions refused** (largest: illegal-transition 37,765; duplicate-tap-noop 3,855; record-without-tap 3,778; tap-without-request 2,966; approval-not-recorded 1,933; approval-expired 1,476; digest-mismatch 926).
- Layer 3 (new): **Ran 10 tests — OK (10 passing, 0 failures)** — CH-1 through CH-10, all ten canonical chaos scenarios (offline approval replay, expiry mid-review, intent change after render, duplicate tap, backend change before refresh, router backend down, stale live source, subagent claim without evidence, digest mismatch, missing tests in packet).
- Cross-artifact audit: **12/12 checks passed, exit code 0** — catalogue = matrix = 27 invariants; events.md = 19 events; 12 states / 21 transitions / T1–T21 bindings; cfg names and all 9 SafetyInvs conjuncts; Phase 1 figures match every citation.

**Verified firsthand:** every run was observed at execution (18:26–18:33
ET, Python 3.12.3 stdlib); outputs filed raw, not summarised.
Harness defects found during the sweep (three) were fixed in the *test
code* and disclosed in the report — no ratified artifact was touched
(mtimes verified).

**Gaps recorded honestly in the same report:** CH-5/CH-6 at contract
level only (no Paper III client / router artifacts); INV-R2/R3/R4
uncovered (the usage router is estate runtime — a Phase 6 artifact);
INV-E2/E4 awaiting evidence-packet/artifact-manifest schema files
(the Layer 1 gate's remaining work); INV-E3/S3/S5 awaiting rendering
and Watchtower artifacts; INV-S5 uncovered (Paper III runtime).

## 2026-10-20 ~18:40 — The roadmap test

**Ordered by:** HgX ("test our road map"). Read-only audit — nothing in
the roadmap documents or artifacts was edited.

**Why it mattered:** A proof is only as legitimate as the paperwork
around it. The roadmap test turned the audit inward: 58 checks across
the two governing documents (ROADMAP.md, Paper IV v1.1), the artifacts,
and the public surfaces — asking whether what the estate *says* about
its programme matches what is *true*.

**Produced:** `tests/ROADMAP-TEST-REPORT-2026-10-20.md`.

**Result: 37/58 PASS — 14 FAIL, 7 STALE.** The architecture is sound
(Dimension 1: 7/7 — phases, invariants, obligations, and tables agree
between the two documents; headline engineering numbers trace to
artifacts). The failures are paperwork, not proof: the repo's public
EVIDENCE.md a day behind reality (R-1); the prescribed repository
layout built in a different shape with no amendment on record (R-2);
Paper IV's §7.9 exit checklist unreconciled with Phase 1's closure
terms (R-3); an "illustrative" 300-second counterexample quietly
promoted to a demonstrated result (R-4); the TLC report's intro saying
"five" bugs while enumerating six (R-5); the wiki still reading
"Phases 2–7 — not started" (R-7); and nine further low-severity
staleness items. Remedies were recorded as awaiting HgX's word — the
test audits; it does not amend.

## 2026-10-20 ~23:51 — Phase 0 + 1 evidence stress test

**Ordered by:** HgX (evening order: stress-test Phases 0 and 1 —
evidence, artifacts, all accounted for and backtraced before 02:00).

**Why it mattered:** Phase 2 builds on Phase 0 and 1. A later phase
cannot rest on a foundation that was never re-verified. The stress
test fingerprinted every artifact and backtraced every claim to its
file — so that any future claim about the early phases can be checked
against a fixed inventory, not against memory.

**Produced:** `tests/PHASE-01-BACKTRACE-MANIFEST.md` (inventory of 18
files with bytes, mtimes, sha256 prefixes; 13 claim rows backtraced to
evidence; findings D-A…D-F) and
`tests/evidence/2026-10-20-phase01-stress.log` (re-run outputs +
file digests).

**Results:** **18/18 artifacts PRESENT** (none missing); **12/12
claims PRESENT**, zero missing. Glossary counts verified by direct
count: 69 terms, 25 conflicts — both exact. Layer 1 re-ran 39/39
OK. Crosscheck ran 11/12 — the single failure was disclosed as an
honest limitation of the *check* (it cannot distinguish
log-attributed figures from other runs), not an error in the figures.

**The finding that corrected our own record (D-B):** estate summaries
had been saying the Phase 1 retest was "killed at 1.79M states." The
retest log's final progress line — 23:42:56 ET, one minute before the
23:43 pause order — reads **12,524,558 distinct states found, zero
invariant violations**. The 1.79M was a 23:05 reading. Verified
firsthand in the log (`proofs/tlc-retest-2026-10-19.log`). The record
was stronger than the summaries claimed — by sevenfold.

**Wording slips surfaced (staged, not applied):** D-A — the TLC
report's intro says "five" while its own body enumerates six;
D-C — `contracts/README.md` says "6 terms flagged unresolved" while
glossary §3 records U-1/U-5/U-6 RESOLVED 2026-10-19, leaving only
U-2/U-3/U-4 open. Proposed v1.1 drafts were staged under
`tests/staging/` awaiting HgX's word.

## 2026-10-20 ~23:58 — v1.1 fixes ratified

**Ordered by:** HgX ("let's fix all the bugs. Before the 2:12 commit").

**Why it mattered:** The versioning law is unforgiving in one way and
merciful in another: versions only move forward, and every correction
is documented — but a correction is always permitted, so a ratified
artifact never has to stay wrong.

**Produced:** `proofs/phase1-tlc-report.md` → v1.1 (intro now reads
"six", with a Version history entry recording the correction);
`contracts/README.md` → v1.1 (glossary row now reads "3 open questions
(U-2, U-3, U-4); 3 resolved at ratification (U-1, U-5, U-6)", with a
Version history entry). Nothing edited in place; both changes went up
a version, as the law requires. The staging drafts were marked
APPLIED.

**Verified firsthand:** both lines read back corrected; version
history entries appended; no other line changed.

## 2026-10-21 ~00:02–00:05 — The seven prescribed files, built

**Ordered by:** HgX (his answer to the roadmap test's R-2 / stress
test's D-D: the layout promised by ROADMAP §0.4 and Paper IV §6.5
named seven files that had never been built — "build them").

**Why it mattered:** Phase 2's Layer 1 gate had honestly flagged the
missing artifacts all along: the evidence-packet and artifact-manifest
schemas, the approval-intent and decision-packet schemas, the
Watchtower schema, the Markdown state-machine spec, and the
approval-digest spec implementing U-1. Every one of them is also
Phase 3's (Consistency Model) groundwork — revision tokens, freshness
values, and digest rules live in these files. Building them closed a
roadmap-test failure and opened the next phase's door in the same
stroke.

**Produced** (born as v0.1 drafts per the versioning law — new
artifacts are drafts; ratification is HgX's call), staged under
`tests/staging/prescribed-files/`:

1. `state-machine.md` — Markdown mirror of `spec/state-machine.tla`:
   12 states, all 21 transitions T1–T21 with prose guards, formal
   guard references, effects, and firing events; idempotency machinery;
   expiry semantics; chain of custody; clock-skew Δ=60s; forbidden
   transitions F1–F9; PO-12 liveness explicitly out of scope. No
   machine line required invention.
2. `approval-digest.md` — implements glossary U-1: SHA-256 over
   canonical JSON (sorted keys, no whitespace, UTF-8), with a real
   worked example — 249-byte canonical payload → digest
   `a5ba4f85e85058c009047fd497df0bfa97122822f5286551adba15fa18f63179`
   (computed with `hashlib`, byte-reproducible).
3. `contracts/approval-intent.schema.json` — intent fields incl.
   `intent_digest` (64-hex pattern). **Parses OK.**
4. `contracts/decision-packet.schema.json` — decision-packet fields
   incl. the Paper III invariant as documented `claimed_outcome`.
   **Parses OK.**
5. `contracts/evidence-packet.schema.json` — packet fields incl.
   required `gaps`, `source_observations`, `test_results`.
   **Parses OK.**
6. `contracts/artifact-manifest.schema.json` — artifact identity,
   revision, digest, provenance. **Parses OK.**
7. `contracts/watchtower.schema.json` — Watchtower state contract,
   closed state enum `operational|paused|degraded|unknown`.
   **Parses OK.**

**Open questions recorded — none silently resolved** (each with exact
source lines in `tests/staging/prescribed-files/BUILD-NOTES.md`):

- **OQ-1** — expiry type: integer (TLA+) or ISO-8601 string (Paper IV
  Appendix C.2)? Draft: integer epoch seconds.
- **OQ-2** — revision type: integer (TLA+/glossary) or string (App.
  C.2)? Draft: integer.
- **OQ-3** — digest binds six fields (TLA+ `DigestOf`) or eight
  (§6.6 "the rest" of the intent incl. `intent_id`, `work_id`)?
  Draft: eight.
- **OQ-4** — canonical-JSON details beyond the three rules (number
  encoding, Unicode normalisation, duplicate keys unspecified).
- **OQ-5** — evidence-packet Appendix C.1 sketch vs §6.6 text.
  Draft followed §6.6/`contracts/events.md`.
- **OQ-6** — who computes the digest when a worker prepares an
  intent (flagged for the Phase 4 idempotency spec).

## 2026-10-21 ~06:42 — Promoted and pushed, on his word

**Ordered by:** HgX ("push all of it").

**Why it mattered:** Drafts staged under `tests/staging/` are
honest work, but the programme's law is that the canonical record
lives in `spec/` and `contracts/`. Promotion moves the work from the
workbench to the record — as drafts, with the open questions still
flagged, because v0.1 is a draft, not a ratification.

**Produced:** the seven files promoted to canonical placement
(`spec/state-machine.md`, `spec/approval-digest.md`,
`contracts/*.schema.json` × 5), each carrying a promotion note:
promoted 2026-10-21 on HgX's order, v0.1 draft, formal ratification
to v1.0.0 remains his call, OQ-1..OQ-6 still flagged in
`tests/staging/prescribed-files/BUILD-NOTES.md`. All five schemas
verified parseable in canonical placement.

**Pushed:** the publishing house ran the full estate push —
**commit `f48e0e519a9d5aa993f6d555fecd561d1c78d71f`, 23 files on
main**: the complete `tests/` tree (Layers 1–3, evidence logs,
run reports, roadmap test report, backtrace manifest, staging
incl. v1.1-draft records and the seven drafts), the two ratified
v1.1 fixes, the seven promoted drafts, both audits (internal
pause→go audit; outside Qwen audit), the website build-log entry,
and the Dropbox filing per doctrine. Identity check clean (no real
name). The 02:12 standing nightly publish stays in place for
everything that follows.

## 2026-10-21 ~11:42 — Phase 2 day-work resumes

**Ordered by:** HgX ("Let's get back to phase two… start with what
else we need to run for phase two today. Start that up.")

**Why it mattered:** The pacing directive never said *wait* — it said
*don't hurry*. Phase 2's remaining work is finite and named, and the
discipline is to work it steadily, in the open, with every session
recorded.

**Underway:** fresh daily re-run of all three suites (evidence logs
dated 2026-10-21); new Layer 1 schema tests exercising the five v0.1
schema drafts against valid and fail-closed cases (mutated digests,
missing required fields, wrong enums, expired approvals) — closing
the "Layer 1 gate remainder" gap; and bookkeeping (plan and
traceability matrix updated, gaps marked closed or still open).

---

## Remaining Phase 2 items (the honest list)

1. **INV-R2 / R3 / R4 — uncovered.** The usage router is estate
   runtime outside this repository; `spec/router-policy.md` is a
   planned Phase 6 artifact. Cannot be mechanised in Phase 2.
2. **CH-5 / CH-6 full form — contract level only.** Need the Paper
   III client / router artifacts (revision-token refresh protocol,
   router backend) to run the scenarios as specified.
3. **INV-E3 / S3 / S5 — rendering artifacts.** E3's packet side is
   covered; the surface-rendering side, S3's degraded-requires-impairment
   rule, and S5's shared-surface redaction await rendering artifacts.
4. **OQ-1…OQ-6 — HgX's decisions.** The drafts carry documented
   choices; the calls are his. OQ-1 and OQ-2 (expiry/revision types)
   are the direct gate for Phase 3's revision protocol.
5. **Roadmap-test paperwork remedies — awaiting his word.**
   Living-doc fixes (repo EVIDENCE.md, wiki, decision-sheet boxes,
   citation corrections) via the publishing house; paper-count errata
   recorded under U-6, never edited.
6. **Phase-level gates (Paper IV §8.4):** suites wired into CI /
   scheduled runs; third-party runnability (the suites are stdlib-only
   and documented, but no external run has occurred).

**Phase 2 status: OPEN.** The evidence is published, the gaps are
named, and the phase closes on HgX's word, on evidence — the same
discipline as Phases 0 and 1.
