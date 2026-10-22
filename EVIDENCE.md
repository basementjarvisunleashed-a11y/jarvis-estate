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
| E-004 | Identity clean — principal's real name nowhere                            | source greps, 0 hits                                  | 2026-10-19             |
| E-005 | Release Bot office opened; build-log system live                         | charter, `release-log/2026-10-19.md`                  | 2026-10-19 16:25–16:30 |
| E-006 | Forge scaffolding committed (INDEX, CONTRIBUTING, GitHub/GitLab templates)| commit 37dda1f                                        | 2026-10-19 17:33       |
| E-007 | Phase 0 closed — contracts frozen | formal-spec/contracts/ | 2026-10-19 |
| E-008 | Phase 1 closed — state-machine proof (TLC) | formal-spec/proofs/phase1-tlc-report.md | 2026-10-20 |
| E-009 | Phase 2 closed — L1 83/83, L2 10/10, L3 10/10, crosscheck 12/12 | formal-spec/tests/ | 2026-10-21 16:52 ET |
| E-010 | Phase 3 closed — L2 42/42, L3 80/80 chaos | formal-spec/tests/phase3/ | 2026-10-21 18:07 ET |
| E-011 | Phase 4 closed — L2 20/20, L3 15/15, 35 claims | formal-spec/tests/phase4/ | 2026-10-21 22:31 ET |
| E-012 | Phase 5 closed — L2 93/93, L3 34/34, 0 findings, 146/146 claims | formal-spec/tests/phase5/ | 2026-10-22 12:44 ET |

## PRESENT — verified (checked 2026-10-19 ~17:35 ET)

| Surface              | State                                                              |
|----------------------|--------------------------------------------------------------------|
| Website (j-a-r-v-i-s-hub) | Built + verified; **no public URL** — share refused 8×, platform-wide |
| Dropbox              | Archive current; log PDF re-rendered 17:33 ET                       |
| Repo                 | Committed through 37dda1f; staged locally; **not pushed**           |

## FUTURE — tracked

| ID    | Commitment                              | Blocked on                                   | Status |
|-------|-----------------------------------------|----------------------------------------------|--------|
| F-001 | Public website URL                      | platform share block; HgX's go               | open   |
| F-002 | GitHub push (full chronicle)            | basementjarvisunleashed account + HgX's word | open   |
| F-003 | Dropbox `/J.A.R.V.I.S./` public link | https://www.dropbox.com/scl/fo/hw9x2ln0x50pcw76a6say/AJIn_Emga-QyxZiIL_YubdY?rlkey=iirish4xzkjmusybq (anyone-with-link, "Allows viewing", minted 2026-10-19) | PROVEN |
| F-004 | Weekly / monthly / quarterly audits     | —                                            | ACTIVE |
