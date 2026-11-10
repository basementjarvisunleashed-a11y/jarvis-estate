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
| E-001 | Four papers landed: I v1.2, II v1.1, III v1.1, IV v1.1                  | Dropbox `/J.A.R.V.I.S./papers/*` (a `doctrine/` directory was named in early notes and was never in this repo). In-repo text: `formal-spec/whitepaper/`, archived hub `website/index.html`. | 2026-10-19 ~15:15–15:27 |
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

## PRESENT — verified (checked 2026-11-09 ~09:11 ET)

| Surface              | State                                                              |
|----------------------|--------------------------------------------------------------------|
| Local Jarvis         | **Live in the repository** — Kali Linux laptop platform (live 2026-11-04) in `local-jarvis/` (platform record `PLATFORM-KALI.md`). Prior Windows build files retained for reference. Voice loop is not auto-started. Placeholders only. |
| Public site (GitHub Pages) | **Live** — https://basementjarvisunleashed-a11y.github.io/jarvis-estate/ — fetched in the 2026-W46 audit (homepage "J.A.R.V.I.S. — Estate 1.2.1", chronicle newest 2026-10-28) |
| Website artifact (`j-a-r-v-i-s-hub`) | Last recorded share state remains `shared: false` (audit 2026-W46). GitHub Pages is the public site. `website/index.html` is the archived hub, not the homepage. |
| Dropbox              | Archive present; audits/weekly holds 2026-W43/W44/W45 (W46 uploaded by this audit); scores/ holds updated versions; logs current through build-log-2026-11-09. Folder share link returns a Dropbox login page to anonymous fetchers (re-verified 2026-11-01; see F-006) |
| Muse share           | https://muse.ai/s/j-a-r-v-i-s-white-paper-wxs6bxaxyuhxafxi returned "Shared link unavailable" on 2026-10-27. |
| Repo                 | Local `master` at 7168f4a (Academy Session 7 log 2026-11-05) before this audit's commit, **not pushed**; canonical `main` at 728bc84 (nightly publish 2026-11-09), `VERSION` 1.2.1, in sync with `origin/main` (0 ahead/behind — W45's ahead-1 resolved by nightly publish) |

## FUTURE — tracked

| ID    | Commitment                              | Blocked on                                   | Status |
|-------|-----------------------------------------|----------------------------------------------|--------|
| F-001 | Public website URL                      | GitHub Pages is live (see PRESENT). The Muse artifact share is still unshared under the 2026-W44 FULL STOP. Closing F-001 still needs HgX's word on which URL the item means. | open   |
| F-002 | GitHub push (full chronicle)            | `origin/main` is the public chronicle. The 2026-W44 note about an unpushed local `master` is a point-in-time audit, not the state of this public repository on 2026-10-27. | open   |
| F-003 | Dropbox `/J.A.R.V.I.S./` public link | https://www.dropbox.com/scl/fo/hw9x2ln0x50pcw76a6say/AJIn_Emga-QyxZiIL_YubdY?rlkey=iirish4xzkjmusybq (anyone-with-link, "Allows viewing", minted 2026-10-19) | PROVEN |
| F-004 | Weekly / monthly / quarterly audits     | —                                            | ACTIVE |
| F-005 | Reconcile local ledger with published ledger (E-007–E-012, Phases 0–5) | publishing-house reconciliation | open |
