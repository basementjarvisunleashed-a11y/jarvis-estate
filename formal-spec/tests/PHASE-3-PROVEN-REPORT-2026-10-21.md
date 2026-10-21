# PHASE 3 — PROVEN VERIFICATION REPORT — 2026-10-21

**Order:** HgX, 2026-10-21 ~18:03 ET — "Make sure we check everything and we go to phase three proven. I don't want to close phase three yet — I want to get to phase three proven."
**Scope:** the entire `~/workspace/jarvis-formal-spec/tests/phase3/` tree (six v0.1-draft spec documents, the Layer 2 protocol harness, the Layer 3 chaos harness, evidence logs, integrity manifest).
**Method:** read-only audit except where noted; Python 3 stdlib only; no network, no git, no publishing. Fresh re-runs from clean state. Ratified files untouched (`spec/`, `contracts/` — verified by mtime and by content-diff, §4).
**Companions:** `tests/phase3/evidence/2026-10-21-phase3-integrity-manifest.tsv` (32 files: path, sha256, bytes, mtime UTC), `tests/phase3/evidence/2026-10-21-phase3-proven-{layer2,layer3}-rerun.log`.
**Status of the phase: PROVEN and OPEN.** Nothing ratified, no closure entry, per his explicit word.

---

## 1. Fresh re-runs (from clean state)

| Suite | Result | Evidence log |
|---|---|---|
| Layer 2 (protocol) | **42/42 OK** — `Ran 42 tests in 0.051s`, exit 0 | `tests/phase3/evidence/2026-10-21-phase3-proven-layer2-rerun.log` |
| Layer 3 (chaos) | **31 test methods / 80 adversarial cases OK** — `Ran 31 tests in 0.088s`, exit 0 | `tests/phase3/evidence/2026-10-21-phase3-proven-layer3-rerun.log` |

Re-run refusal counts are byte-identical to the original build: Layer 2 = 33 refused requests, Layer 3 = 137 refused requests (stale-revision 92, digest-lapse 33, stale-request 9, intent-invalid 2, stale-event 1). The re-run deterministically reproduced the build's verdicts — the harnesses are deterministic, not lucky.
Note: `run.sh` writes its dated logs (`2026-10-21-phase3-layer{2,3}.log` + rejections/verdicts logs) on each run; the sweep re-run refreshed those files in place. The `proven-*-rerun.log` files are the sweep's own console capture. Counts and refusal ledgers are unchanged.

## 2. Claim audit — every numbered claim, accounted for

Legend: **TESTED** = covered by at least one named test; **STATED** = a draft rule with no direct test (flagged honestly); **DEFERRED** = a documented open point awaiting his word.

### 2a. The hybrid table (consistency-model.md §3)

| # | Claim | Verdict | Coverage |
|---|---|---|---|
| HC-1 | Status viewing: eventual + freshness stamps | TESTED | ct2, sk6, pt4 (stale renders unknown, never current) |
| HC-2 | Evidence viewing: revision-stable reads | TESTED | ct6 (CR-7: new revision sealed, old immutable, renders pin) |
| HC-3 | Approval decision: strong authoritative consistency | TESTED | da1–da6, fv1–fv6, sm1–sm8, ar1–ar6 |
| HC-4 | Execution: linearized, single-writer | TESTED | rt11 (orchestrator is only writer), da1 (executed exactly once) |
| HC-5 | Memory correction: orchestrator-mediated reconciliation | TESTED | ct4 (CR-5: surfaces never reconcile against each other) |
| HC-6 | Live-source facts: read-current at decision time | TESTED | ct3 (CR-4: live source beats memory) |
| HC-7 | Artifact download: digest-verified bytes | TESTED (partial) | da5 (CR-8: artifact change invalidates approval — the binding half). The download-verification path itself is STATED, not adversarially tested. |
| HC-8 | Notification delivery: at-least-once hints, not state | TESTED | ct5 (CR-6: hint discarded, current state pulled) |

### 2b. "No device can become a source of truth" (consistency-model.md §6)

| # | Claim | Verdict | Coverage |
|---|---|---|---|
| NT-1 | No surface holds write authority | TESTED | rt11 (every transition names the orchestrator) |
| NT-2 | Renders labeled with provenance (revision + age) | TESTED (partial) | ct2, sk6, ot3 (unknown renders carry last honest age); F4. No test asserts "a render without provenance is a defect" as such. |
| NT-3 | Two surfaces disagreeing resolve to server state | TESTED | ct1 (CR-1), pt5 (recorded decision survives partition) |
| NT-4 | Offline surface holds no authority on reconnect | TESTED | ot4 (long offline → pull, never assert), pt1, pt6 |
| NT-5 | Approval authority lives in the record, not the tap | TESTED | fv1/fv2 (recorded decision), ot1 (tap is a gesture) |

### 2c. Revision protocol (revision-protocol.md §3, §5)

| # | Claim | Verdict | Coverage |
|---|---|---|---|
| R1 | Orchestrator holds the single current revision per work_id | TESTED | rt4 |
| R2 | Mutation accepted iff request.revision == current | TESTED | rt1 (held < current), rt2 (held > current), rt3 (missing) |
| R3 | Acceptance appends event, revision becomes revision+1 | TESTED | rt4 |
| R4 | No force flag, no override, no in-place upgrade | TESTED | rt5 |
| R5 | Reads pin revisions (never silently newer) | TESTED | ct6 (evidence pinning); rt10-adjacent |
| §5 step 1 | Session first (unknown-session) | TESTED | rt8, rt9, sm1 |
| §5 step 2 | Freshness: 60 s state/event, 300 s request (OP-1) | TESTED | rt6 (±300 exact boundary), rt7 (±60 exact boundary), sk1, sk2 |
| §5 step 3 | Intent liveness (exists, unexpired, digest recomputes) | TESTED | sm7, sm8, rp5 |
| §5 step 4 | Revision currency (stale-revision) | TESTED | rt1, rt2, sm4 |
| §5 step 5 | Digest binding for decide (digest-lapse, attested) | TESTED | da2, da6, sm4 (digest-before-currency for decide) |
| §6 | First valid decision recorded wins; duplicates read | TESTED | fv1–fv6 |

### 2d. Conflict resolution (conflict-resolution.md CR-1…CR-8)

| # | Claim | Verdict | Coverage |
|---|---|---|---|
| CR-1 | Server state wins (two devices, different status) | TESTED | ct1, pt5, pt2 |
| CR-2 | First valid decision recorded wins (adversarial) | TESTED | fv1–fv6, ar1–ar6 (18 interleavings), pt2, pt3, rp1, rp2, rp5, mx1–mx5 (34 mixed) |
| CR-3 | Stale cache renders unknown | TESTED | ct2, pt4, sk6 |
| CR-4 | Live source wins for current facts | TESTED | ct3 |
| CR-5 | Orchestrator reconciles durable contradictions | TESTED | ct4 |
| CR-6 | Notification is a hint, not truth | TESTED | ct5 |
| CR-7 | Evidence: new revision, old immutable | TESTED | ct6 |
| CR-8 | Artifact changed after approval → new approval required | TESTED | da5; orchestrator.py CR-8 invalidation |

### 2e. Age honesty (freshness-policy.md §3)

| # | Claim | Verdict | Coverage |
|---|---|---|---|
| F1 | Data renders with its age, or as unknown | TESTED | ct2, sk6 |
| F2 | fresh_until set by the orchestrator; surfaces don't extend | STATED | Used implicitly by ct2/sk6; no test asserts non-extension. |
| F3 | Future-dated stamps beyond the bound refused | TESTED | sk7 (future-dated event grants nothing) |
| F4 | Unknown render shows last honest age; never interpolates | TESTED | ot3, sk6 |

### 2f. Sequence diagrams (sequence-diagrams.md)

| Diagram | Claim | Verdict | Coverage |
|---|---|---|---|
| (a) | Card on iPhone, approval on Watch | TESTED | fv1, fv2, ar1 |
| (b) | Conflicting approvals, deterministic winner, loser path | TESTED | fv6, ar1–ar6 (all interleavings), pt2 |
| (c) | Stale Watch cache renders unknown | TESTED | ct2, pt4, sk6 |
| (d) | Offline tap → nothing recorded, ever | TESTED | ot1–ot5, rp6, pt6, mx4 |

### 2g. Open points (globally numbered in the drafts)

| # | Status | Disposition |
|---|---|---|
| OP-1 | **RESOLVED** on HgX's word 2026-10-21 ~17:49 ET: keep both — 60 s state/event (Phase 0 U-5/D7 ratified), 300 s request (substrate reference) | Recorded in all five affected drafts' version histories (consistency-model.md, revision-protocol.md, conflict-resolution.md, sequence-diagrams.md, freshness-policy.md); tested at exact boundaries (rt6, rt7, sk1, sk2) |
| OP-2 | Basement laptop scope (home node vs out of scope) | DEFERRED — needs his word |
| OP-3 | device_session_id lifecycle (revocation modeled; re-enrollment/expiry) | DEFERRED — needs his word (Phase 5 candidate) |
| OP-5 | TTL numbers in cache-policy.md §3 (rules stand regardless) | DEFERRED — needs his word |
| OP-6 | Formal proof of the hybrid table | RECORDED as beyond exit criteria — not an omission, not a decision |
| OP-7 | Formal cadence/tier table (p99 expectations reference-anchored) | DEFERRED — needs his word |

**Claims unaccounted for: none.** Every numbered claim is either tested by a named test, flagged as stated-but-not-directly-tested (HC-7 download half, NT-2 provenance-defect assertion, F2 non-extension), or a documented deferral awaiting his word.

## 3. Answer verification — Q1–Q4 implemented as decided

| # | HgX's answer (2026-10-21 walkthrough) | Implementation | Verdict |
|---|---|---|---|
| Q1 | Deployment loop as reference; iPhone as trusted enrollment/command surface | `consistency-model.md` §1, §4, §7: the loop (SERVE→SENSE→QUEUE→REVIEW→MAINTAIN) as reference writer; iPhone trusted-surface = enrollment + presentation, not write authority; the roadmap's "clients may NOT become a second orchestrator" applied to the iPhone | VERIFIED |
| Q2 | iPhone + Watch in scope; iPad/TV/Vision Pro pull-only | `consistency-model.md` §3.1; `cache-policy.md` §5: pull-only surfaces bounded exactly by their pull contracts, hold no revision pins, no decision receipts | VERIFIED |
| Q3 | Survey parallel — informs, doesn't block | `PHASE-3-OPEN-QUESTIONS.md`: recorded 2026-10-21 ~17:42 ET; no spec implementation expected (process decision) | VERIFIED (as recorded) |
| Q4 | Substrate adopted as reference; spec normative | Layer 2/3 harnesses reuse `orchestrator.py` conventions from the substrate; all six drafts cite the substrate as reference with the spec normative over it (`consistency-model.md` §7: "The substrate is evidence, not law") | VERIFIED |
| OP-1 | Keep both bounds | Recorded in the version histories of all five affected drafts (grep-confirmed `OP-1 RESOLVED` in consistency-model.md, revision-protocol.md, conflict-resolution.md, sequence-diagrams.md, freshness-policy.md) | VERIFIED |

## 4. Ratified-file integrity

The protected set: the seven v1.0.0 ratified drafts (`spec/state-machine.md`, `spec/approval-digest.md`, five `contracts/*.schema.json`) plus `contracts/events.md` v1.1.

| Check | Result |
|---|---|
| Any spec/ or contracts/ file with mtime inside the Phase 3 work window (2026-10-21 17:45–18:05 ET) | **NONE** — the only 2026-10-21 mtimes are 14:45 ET (events.md v1.1 amendment) and 14:48 ET (the seven ratifications) — both Phase 2 work, both on his word |
| All seven ratified files still carry their v1.0.0 headers | **7/7 VERIFIED** |
| events.md still v1.1 | VERIFIED |

**Verdict: no ratified file was touched by any Phase 3 work.** (Note: the working tree's `spec/`/`contracts/` differ from the Oct-19 committed snapshot in `~/workspace/jarvis-estate/formal-spec/` — e.g. the ratified drafts and the contracts/README.md v1.1 entry — but all such differences predate Phase 3 and were committed/pushed via the publishing route during Phase 2. Nothing moved during Phase 3.)

## 5. Cross-reference audit

Every file path and test name cited across the six drafts, both READMEs, and the evidence logs was checked against disk:

| Finding | Verdict |
|---|---|
| All `tests/phase3/*.md`, `tests/PHASE-3-*.md`, `ROADMAP.md`, `contracts/events.md` refs | RESOLVE — 10/10 |
| All `~/workspace/jarvis-deploy/phase1/{pull,loop}.py`, `phase2/{contracts,enrollment}.py` refs | RESOLVE — 4/4 |
| All README-cited harness files (`orchestrator.py`, `clients.py`, `digest.py`, `chaos.py`, all 11 test files) | RESOLVE — 15/15 |
| All 14 docstring draft-section cites (`revision-protocol.md §5/§6`, `cache-policy.md §4`, `sequence-diagrams.md (b)/(d)`, `consistency-model.md` NT-1) | RESOLVE — sections exist |
| `conflict-resolution.md:102` cites bare `events.md` (shorthand for `contracts/events.md`) | NOTED — resolves, stylistic shorthand only |

**Broken references: none.**

## 6. Integrity manifest

`tests/phase3/evidence/2026-10-21-phase3-integrity-manifest.tsv` — **32 files** fingerprinted (path, sha256, bytes, mtime UTC). All 32 have mtimes on 2026-10-21 (the Phase 3 build day). No `__pycache__`, no `.pyc`, no files >1 MB, no TODO/FIXME/XXX in the markdown.

## 7. Exit-criteria verdict

ROADMAP.md §6's five exit criteria, mapped to covering tests:

| # | Exit criterion (verbatim) | Covering tests | Verdict |
|---|---|---|---|
| 1 | No device can become a source of truth | rt11, ct1, ot1/ot2, ot4, fv1/fv2, ar1–ar6, pt5, pt6, sk3, sk4a/b, rp1, rp4, mx1–mx5; NT-1…NT-5 operationalization | **MET** |
| 2 | Approval conflicts resolve deterministically | fv1–fv6, sm4, ar1–ar6 (18 interleavings), pt2, pt3, rp1, rp2, rp5, mx1–mx5 (34 mixed) | **MET** |
| 3 | Stale data cannot masquerade as current | rt1–rt5, ct2, sk1, sk2, sk6, pt4, mx4; F1–F4 | **MET** |
| 4 | Offline taps cannot become approvals | ot1–ot5, pt1, pt6, rp6, mx4; sequence (d) | **MET** |
| 5 | Behavior tested under clock skew and network loss | sk1–sk7 (15 skew cases at exact boundaries), pt1–pt7 (7 partition cases), mx1–mx5 (34 mixed chaos incl. 24-order fuzz), ot offline paths; both OP-1 bounds (60 s / 300 s) at exact boundaries | **MET** |

## Verdict

**PHASE 3 IS PROVEN** — with the explicit noted items above: three stated-but-not-directly-tested halves (HC-7 download-verification path, NT-2 provenance-defect assertion, F2 non-extension), and the documented open points OP-2/OP-3/OP-5/OP-7 awaiting his word (OP-1 resolved on his word; OP-6 recorded as beyond exit criteria). Every suite green on fresh re-runs (42/42 + 80/80), every numbered claim accounted for, every cited path resolving, no ratified file touched, all five exit criteria evidenced.

**And it remains OPEN** — nothing ratified, no closure entry — per his explicit word of 2026-10-21 ~18:03 ET.

*Swept 2026-10-21 ~18:05–18:15 ET. The receipts are in `tests/phase3/evidence/`.*
