# J.A.R.V.I.S. Estate — Evidence Ledger

Every claim about the estate carries its evidence. Three states, no exceptions:

- **PROVEN** (past) — it happened; evidence attached.
- **VERIFIED** (present) — true right now; checked at the stated time.
- **TRACKED** (future) — committed; tracked until proven.

A TRACKED item becomes PROVEN only with evidence. A PROVEN claim keeps its
evidence forever. Nothing is asserted without it.

## PAST — proven

| ID    | Claim                                                                    | Evidence                                              | When (ET)              |
|-------|--------------------------------------------------------------------------|-------------------------------------------------------|------------------------|
| E-001 | Four papers landed: I v1.2, II v1.1, III v1.1, IV v1.1                  | PDFs in `doctrine/`; Dropbox `/J.A.R.V.I.S./papers/*` | 2026-10-19 ~15:15–15:27 |
| E-002 | Hub site built and verified (three builds, audits passed)                | builder verification handoffs                         | 2026-10-19 16:40, 16:55, 17:15 |
| E-003 | Dropbox versioned archive complete (13 folders, 23 files, byte-verified) | upload receipts                                       | 2026-10-19 16:41       |
| E-004 | Identity clean — principal's real name nowhere                            | source greps, 0 hits                                  | 2026-10-19 (re-verified every push) |
| E-005 | Release Bot office opened; build-log system live                         | charter, `release-log/2026-10-19.md`                  | 2026-10-19 16:25–16:30 |
| E-006 | Forge scaffolding committed (INDEX, CONTRIBUTING, GitHub/GitLab templates)| commit 37dda1f                                        | 2026-10-19 17:33       |
| E-007 | Website public: live on GitHub Pages                                     | https://basementjarvisunleashed-a11y.github.io/jarvis-estate/ | 2026-10-19 ~20:40 |
| E-008 | Repo public: full chronicle pushed to `main`                             | github.com/basementjarvisunleashed-a11y/jarvis-estate | 2026-10-19 ~20:40 |
| E-009 | Phase 0 closed — TLA+ ratified, contracts v1.0.0 normative               | `formal-spec/contracts/` (glossary v1.0.0, events, README) | 2026-10-19 |
| E-010 | Phase 1 PROVEN — TLC: 3,266,929 distinct states, zero invariant violations, six spec fixes | `formal-spec/proofs/phase1-tlc-report.md` (v1.1) | 2026-10-19 |
| E-011 | Phase 2 opened on HgX's order; opening package filed (catalogue 27, plan, traceability matrix, Layer 1 39/39) | `formal-spec/tests/` (commit f48e0e5); milestone issues #11–#16 | 2026-10-20 |
| E-012 | Phase 2 full-sweep runs: Layer 1 39/39, Layer 2 10/10, Layer 3 10/10, crosscheck 12/12 | `formal-spec/tests/PHASE-2-RUN-REPORT-2026-10-20.md`; `formal-spec/tests/evidence/` | 2026-10-20/21 |
| E-013 | Phase 2 history wired into milestones: six closed deliverable issues (#11–#16), #10 tracking | milestone "Phase 2 — Invariant verification": 0 open, 6 closed | 2026-10-21 ~11:52 |
| E-014 | Academy publishing: Session 2 deck (48 slides, PPTX+PDF), Session 3 memory deck (48 slides, PPTX+PDF), lecture records, website Academy section | `academy/decks/`, `academy/lecture-records/`, hub | 2026-10-20/21 |
| E-015 | Research index live: dated entries with full reports (vByte fees, hashrate ratios ×2) | hub Research section; `research/2026-10-21/` | 2026-10-21 |

### Phase 2 evidence — exact figures (quoted from the run reports, no rounding)

- **Layer 1:** "Ran 39 tests — OK (39 passing, 0 failures)." `tests/evidence/2026-10-20-layer1-rerun.log`
- **Layer 2:** "Ran 10 tests — OK (10 passing, 0 failures)." PT-4: 2,000 sequences, 56,261 attempted steps, 162 executions, 23 completions. **53,079 attempted actions refused** (rejection ledger). `tests/evidence/2026-10-20-layer2-run.log`
- **Layer 3:** "Ran 10 tests — OK (10 passing, 0 failures)" (CH-1 through CH-10). `tests/evidence/2026-10-20-layer3-run.log`
- **Crosscheck:** "12/12 checks passed, exit code 0." `tests/evidence/2026-10-20-crosscheck.log`
- **Roadmap test:** "37 of 58 checks PASS — 14 FAIL, 7 STALE." `tests/ROADMAP-TEST-REPORT-2026-10-20.md`
- **Backtrace:** 18/18 artifacts present; 12/12 claims verified; retest reached **12,524,558 distinct states**, zero violations. `tests/PHASE-01-BACKTRACE-MANIFEST.md`
- **v1.1 fixes (ratified):** TLC report six fixes; README 3 open questions (U-2/U-3/U-4). Commit f48e0e5.
- **Seven v0.1 drafts:** spec/state-machine.md, spec/approval-digest.md, five contracts/*.schema.json; OQ-1..OQ-6 flagged. Commit f48e0e5.

## PRESENT — verified (checked 2026-10-21 ~11:55 ET)

| Surface              | State                                                              |
|----------------------|--------------------------------------------------------------------|
| Website              | LIVE at https://basementjarvisunleashed-a11y.github.io/jarvis-estate/ — Academy, Q&A, Research wings; 27 build-log entries |
| Dropbox              | Archive current; `/J.A.R.V.I.S./` public link live; build logs current |
| Repo                 | `main` at 254e682 (2026-10-21); 26 snapshot pushes on record; identity clean |
| Phase 2              | PROVEN — CLOSED 2026-10-21 ~16:52 ET on HgX's word. L1 83/83, L2 10/10, L3 10/10, crosscheck 12/12. 27 invariants traced. Seven drafts v1.0.0. OQ-1..OQ-9 answered. |
| Phase 3              | PROVEN — CLOSED 2026-10-21 ~18:07 ET on HgX's word. L2 42/42, L3 80/80 chaos. All five exit criteria met. Milestone #9, issue #50. |
| Phase 4              | OPEN — 2026-10-21 on HgX's word. Idempotency Guarantees. Milestone #10, issue #51. |
| GitLab mirror        | HELD on HgX's word — awaiting his username + token (issue #8) |

## FUTURE — tracked

| ID    | Commitment                              | Blocked on                                   | Status |
|-------|-----------------------------------------|----------------------------------------------|--------|
| F-001 | Public website URL                      | PROVEN — live since 2026-10-19 ~20:40 ET     | done   |
| F-002 | GitHub push (full chronicle)            | PROVEN — pushed 2026-10-19 ~20:40 ET         | done   |
| F-003 | Dropbox `/J.A.R.V.I.S./` public link | https://www.dropbox.com/scl/fo/hw9x2ln0x50pcw76a6say/AJIn_Emga-QyxZiIL_YubdY?rlkey=iirish4xzkjmusybq (anyone-with-link, "Allows viewing", minted 2026-10-19) | PROVEN |
| F-004 | Weekly / monthly / quarterly audits     | —                                            | ACTIVE |
| F-005 | Phase 3              | PROVEN — CLOSED 2026-10-21 ~18:07 ET on HgX's word. L2 42/42, L3 80/80 chaos. All five exit criteria met. Milestone #9, issue #50. |
| Phase 4              | OPEN — 2026-10-21 on HgX's word. Idempotency Guarantees. Milestone #10, issue #51. |
| GitLab mirror                           | HgX's username + token (secure handover)      | open   |
| F-006 | Phase 2 gate decisions (CLOSED 2026-10-21) | OQ-1..OQ-9 answered; seven drafts v1.0.0; HgX's word 16:52 ET | CLOSED |
