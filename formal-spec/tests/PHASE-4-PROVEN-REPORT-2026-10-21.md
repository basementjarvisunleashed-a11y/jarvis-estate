# PHASE 4 — PROVEN VERIFICATION REPORT — 2026-10-21

**Order:** HgX, 2026-10-21 ~22:28 ET — "give me the list, rerun it."
**Scope:** the entire `~/workspace/jarvis-formal-spec/tests/phase4/` tree (five v0.1-draft spec documents, the Layer 2 protocol harness, the Layer 3 chaos harness, evidence logs, integrity manifest).
**Method:** read-only audit except where noted; Python 3 stdlib only; no network, no git, no publishing. Fresh re-runs from clean state. Ratified files untouched (`spec/`, `contracts/` — verified by mtime and by header, §4).
**Companions:** `tests/phase4/evidence/2026-10-21-phase4-integrity-manifest.tsv` (28 files: path, sha256, bytes, mtime), `tests/phase4/evidence/2026-10-21-phase4-proven-{layer2,layer3}-rerun.log`.
**Status of the phase: PROVEN and OPEN.** Nothing ratified, no closure entry, per his explicit word. Closure is his separate word.

---

## 1. Fresh re-runs (from clean state)

| Suite | Result | Evidence log |
|---|---|---|
| Layer 2 (protocol) | **20/20 OK** — `Ran 20 tests in 0.002s`, exit 0 | `tests/phase4/evidence/2026-10-21-phase4-proven-layer2-rerun.log` |
| Layer 3 (chaos) | **15 test methods OK** — `Ran 15 tests in 0.007s`, exit 0 | `tests/phase4/evidence/2026-10-21-phase4-proven-layer3-rerun.log` |

Re-run refusal counts are byte-identical to the original build: Layer 2 = 4 refused requests (unsafe-retry ×2, needs-fresh-ceremony, digest-mismatch), Layer 3 = 3 refused requests (all `unsafe-retry`: the blind retries the protocol must refuse). The full rejection ledgers diffed byte-identically against the build-time ledgers — the harnesses are deterministic, not lucky.
Note: `run.sh` dates its logs by system date; the sweep ran at 02:28 UTC (22:28 ET 2026-10-21), so it wrote `2026-10-22-phase4-layer{2,3}.log` alongside the original `2026-10-21-*` files, which are untouched. The `proven-*-rerun.log` files are the sweep's own console captures (copies of the fresh runs).

## 2. Claim audit — every numbered claim, accounted for

Legend: **TESTED** = covered by at least one named test; **STATED** = a draft rule with no direct test (flagged honestly); **DEFERRED** = a documented open point awaiting his word.

### 2a. Idempotency key (idempotency-key-spec.md K1–K6)

| # | Claim | Verdict | Coverage |
|---|---|---|---|
| K1 | The key binds exactly these eight fields — no more, no fewer | TESTED (partial) | The eight-field formula is the only one implemented (`idem.py` `KEY_FIELDS`); dt5/dt6 exercise it. No negative test asserts a deviant field set is rejected. |
| K2 | `revision` = revision at approval time, frozen at BIND (Q2 ruling) | TESTED | sr3 (revision frozen at BIND keeps the key stable across retries) |
| K3 | `device_session_id` excluded — key = effect, token = request (Q3 ruling) | TESTED | dt2 (two devices, one intent, one key, one execution) |
| K4 | Canonical form per the Phase 2 Q4 procedure | TESTED (by reuse) | The ratified Phase 2 Q4 procedure via `tests/phase3/layer2/digest.py`; not re-tested in Phase 4 |
| K5 | Deterministic at BIND: same approved intent → same key | TESTED | dt5 |
| K6 | A changed intent cannot ride an old key | TESTED | dt6 (changed target → different key; digest-first lapses) |

### 2b. Execution record (execution-record-spec.md ER1–ER6)

| # | Claim | Verdict | Coverage |
|---|---|---|---|
| ER1 | One record per key | TESTED | ad1 (one record holds under every interleaving), nl4 (flapping links converge on one record) |
| ER2 | Tool plane fires at most once per record (consequential) | TESTED | `effect_count ≤ 1` asserted in all 35 test methods |
| ER3 | Transitions follow only the machine's edges; no resurrection | STATED | The draft defines the machine; the harness's saga-surface methods follow it. No test asserts an illegal transition (e.g. `execution_requested → completed`) is refused. |
| ER4 | `execution_unknown` is visible, non-terminal | TESTED | ab1, ab2, ab4, nl1 |
| ER5 | `completed`/`cancelled` terminal and final | TESTED | dt3, sr4, sr6 (terminal records return the existing record) |
| ER6 | Every transition a sealed, logged event | TESTED | ab7 (asserts `sealed_log` entries for every state incl. `prepared`) |

### 2c. Governed saga (saga-spec.md S1–S8)

| # | Claim | Verdict | Coverage |
|---|---|---|---|
| S1 | Saga: prepare → approval → execute → verify → record evidence → compensate; no step skipped/reordered | TESTED | The harness's saga-surface methods follow the order; dt7 (execute without approval refused) |
| S2 | Preparation needs no approval | TESTED (implicit) | Every test prepares without an approval first |
| S3 | Approval binds the exact target and effect | TESTED | dt6, ab6 (tampered digests refused) |
| S4 | Execution needs valid approval; at most once per key | TESTED | dt7 (no approval → refused), dt1 (never a second execution) |
| S5 | Verification per integration class | TESTED (partial) | Opaque-tool and read-after-write paths tested (ax1, nl2, nl3). The full eight-row per-class table is spec-level; production mechanics are P4-OP-2. |
| S6 | Consequential compensation = fresh ceremony (Q5 ruling) | TESTED | ab5 (compensation gets its own key, intent, approval; riding the original key refused) |
| S7 | Orchestrator signs worker-prepared digests (Q1 ruling) | TESTED | ab6 (worker intent signed; tampered digest refused) |
| S8 | No silent rollback of consequential effects | TESTED | ab5 (compensation refused without fresh ceremony) |

### 2d. Retry policy (retry-policy-matrix.md RF1–RF9)

| # | Claim | Verdict | Coverage |
|---|---|---|---|
| RF1 | Reads/verifies freely repeatable | STATED | Policy assertion — the harness implements execute-class lifecycles only |
| RF2 | Prepares repeatable iff reversible | STATED | Policy assertion — same boundary as RF1 |
| RF3 | Approvals recorded once; duplicates return same decision | TESTED | dt4 |
| RF4 | Executes at-most-once unless verified safe | TESTED | sr1 (unsafe refused, `attempt_count` unchanged), sr2 |
| RF5 | Compensations only if supported and approved | STATED (partial) | ab5 tests the fresh-ceremony half; "supported" is production semantics |
| RF6 | Memory writes reconciled, never duplicated | STATED | Policy assertion — same boundary as RF1 |
| RF7 | `safe_to_retry` true only when verified absent or safely repeatable; definitive failure sets it | TESTED | sr2 (verified absent still at-most-once), ax4 (failed executions retry safely, never duplicate); the build-time discrepancy fix (flag set on definitive failure) |
| RF8 | Flag false on ambiguity | TESTED | ab1, ab3, nl1 |
| RF9 | Refused retry changes nothing; `attempt_count` does not advance | TESTED | sr1 |

### 2e. Ambiguity protocol (ambiguity-protocol.md AP1–AP6)

| # | Claim | Verdict | Coverage |
|---|---|---|---|
| AP1 | Do not mark `completed` on ambiguity | TESTED | ab1, nl1, nl5 |
| AP2 | No auto-retry of consequential execution on ambiguity | TESTED | ab3; L3 ledger's 3 `unsafe-retry` refusals |
| AP3 | Verify externally if possible | TESTED | ab4, nl2, nl3, ax3 |
| AP4 | If unverifiable: mark unknown, escalate with next safe option | TESTED | ab2, ax1 |
| AP5 | Unknown surfaced on next pull + escalated hint (Q4 ruling) | TESTED | ab2 (pull returns unknown + safe options + `hint_emitted`) |
| AP6 | Notification carries no state — hint, not the record | TESTED | ab2 (asserts `observed_result` and `effect` absent from the hint) |

### 2f. Open points (globally numbered in the drafts)

| # | Status | Disposition |
|---|---|---|
| P4-OP-1 | External-system inventory (eight classification rows vs the estate's actual integrations) | DEFERRED — estate work beyond the spec; the saga is written correct for all eight rows regardless |
| P4-OP-2 | "Verified safe" production mechanics per integration class | DEFERRED — implementation depth; the spec's rules stand regardless |
| P4-OP-3 | `device_session_id` lifecycle | DEFERRED — carried from Phase 3 OP-3 → Phase 5 |
| P4-OP-4 | Escalated notification channel mechanics | DEFERRED — estate implementation; Q4 rules the shape |
| P4-OP-5 | Tool-plane truthfulness trust boundary | DEFERRED — → Phase 5 (security boundary formalism); recorded when the build-time discrepancy was fixed |

**Claims unaccounted for: none.** Every numbered claim is either tested by a named test, flagged as stated-but-not-directly-tested (K1 field-set negative, ER3 illegal-transition refusal, RF1/RF2/RF5-half/RF6 policy postures, S5 full per-class table), or a documented deferral awaiting his word. K4 is covered by the ratified Phase 2 Q4 procedure via reuse.

## 3. Answer verification — Q1–Q5 implemented as decided

| # | HgX's answer (2026-10-21 walkthrough) | Implementation | Verdict |
|---|---|---|---|
| Q1 | Orchestrator signs after recomputing and validating; authorship in provenance | `saga-spec.md` S7; `idem.py` `worker-intent-signed` log | VERIFIED |
| Q2 | Revision frozen at approval time (BIND) | `idempotency-key-spec.md` K2 | VERIFIED |
| Q3 | Key excludes `device_session_id` — effect vs request asymmetry | `idempotency-key-spec.md` K3 + §2.2 | VERIFIED |
| Q4 | Unknown surfaced on next pull + escalated hint (hint, not the record) | `ambiguity-protocol.md` AP5 + §4 visibility path; `execution-record-spec.md` ER4 | VERIFIED |
| Q5 | Fresh ceremony for consequential compensation | `saga-spec.md` S6 + §2.2; `execution-record-spec.md` §3.2 | VERIFIED |

## 4. Ratified-file integrity

The protected set: the seven v1.0.0 ratified drafts (`spec/state-machine.md`, `spec/approval-digest.md`, five `contracts/*.schema.json`) plus `contracts/events.md` v1.1.

| Check | Result |
|---|---|
| Any spec/ or contracts/ file modified during the Phase 4 work window (2026-10-21 18:33–18:37 ET) | **NONE** — all eight files carry 14:45–14:48 ET mtimes (the Phase 2 ratification/amendment window, on his word), predating Phase 4 |
| All seven ratified files still carry their v1.0.0 headers | **7/7 VERIFIED** |
| events.md still v1.1 | VERIFIED |

**Verdict: no ratified file was touched by any Phase 4 work.** All 19 Phase 4 files live under `tests/phase4/` (working-tree only).

## 5. Cross-reference audit

Every path and claim cited across the five drafts and both READMEs was checked against disk:

| Finding | Verdict |
|---|---|
| `ROADMAP.md`, `tests/PHASE-4-OPEN-QUESTIONS.md` | RESOLVE |
| `tests/phase3/revision-protocol.md`, `tests/phase3/sequence-diagrams.md`, `tests/phase3/conflict-resolution.md`, `tests/phase3/layer2/digest.py` | RESOLVE |
| `approval_digest` imported from `tests/phase3/layer2/digest.py` | RESOLVE — defined once in digest.py |
| All five sibling drafts cross-cited | RESOLVE |
| All 35 claim numbers K1–K6, ER1–ER6, S1–S8, RF1–RF9, AP1–AP6 present in their drafts | RESOLVE — 35/35 |
| All harness files cited (`idem.py`, `chaos.py`, six test files, both `run.sh`) | RESOLVE |

**Broken references: none.**

## 6. Integrity manifest

`tests/phase4/evidence/2026-10-21-phase4-integrity-manifest.tsv` — **28 files** fingerprinted (path, sha256, bytes, mtime). Excludes `__pycache__`/`*.pyc` (build artifacts, not source). Note: the manifest's own row fingerprints the file as it stood when its own row was written (self-referential; all other 27 rows are exact).

## 7. Exit-criteria verdict

ROADMAP.md §7's five exit criteria, mapped to covering tests:

| # | Exit criterion (verbatim) | Covering tests | Verdict |
|---|---|---|---|
| 1 | Duplicate taps cannot duplicate effects | dt1–dt7 (7), ad1–ad5 (13 adversarial scenarios), nl4; `effect_count ≤ 1` in all | **MET** |
| 2 | Network loss cannot silently complete | nl1–nl5 (5), ax3; severed mid-execution → `execution_unknown`, never silent | **MET** |
| 3 | Ambiguous consequential actions become visible unknown/failed | ab1–ab7 (7), ax1–ax5 (5); every unknown surfaced on pull with safe options + hint | **MET** |
| 4 | Retries only when safe | sr1–sr6 (6); unsafe retries refused without advancing `attempt_count` | **MET** |
| 5 | At-most-once demonstrable under test | `effect_count ≤ 1` asserted in all 35 test methods | **MET** |

## Verdict

**PHASE 4 IS PROVEN** — with the explicit noted items above: the stated-but-not-directly-tested halves (K1 field-set negative, ER3 illegal-transition refusal, RF1/RF2/RF5-half/RF6 policy postures, S5 full per-class table), and the documented open points P4-OP-1…P4-OP-5 awaiting his word (P4-OP-3 and P4-OP-5 → Phase 5). Every suite green on fresh re-runs (20/20 + 15/15), refusal ledgers byte-identical (deterministic, not lucky), every numbered claim accounted for, every cited path resolving, no ratified file touched, all five exit criteria evidenced.

**And it remains OPEN** — nothing ratified, no closure entry — per his explicit word. Closure is his separate word.

*Swept 2026-10-21 ~22:28–22:35 ET. The receipts are in `tests/phase4/evidence/`.*
