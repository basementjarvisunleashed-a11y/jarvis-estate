# Roadmap Test Report — J.A.R.V.I.S. Doctoral Programme

*Ordered by HgX, evening of 2026-10-20 (America/Toronto): "test our road map."
Read-only audit. Nothing in the roadmap documents or the artifacts was edited.
Governing documents under test: `ROADMAP.md` (recorded 2026-10-08, the normative
source) and Paper IV v1.1 (`whitepaper/jarvis-roadmap-white-paper.md`), which by
its own rule (Paper IV, "The Roadmap as Normative Source", L25–29) is in error
wherever it disagrees with the roadmap.*

**Score: 37 of 58 checks PASS — 14 FAIL, 7 STALE.**

The roadmap's architecture is sound: the two governing documents agree with each
other on phases, invariants, obligations, and tables almost everywhere, and the
headline engineering numbers (Phase 0 freeze, Phase 1 proof, Phase 2 suites)
trace cleanly to artifacts. The failures concentrate in three places: status
surfaces that were not updated after 2026-10-19 (repo EVIDENCE.md, wiki,
release log), a specification-repository layout that was prescribed in detail
and then built differently without a recorded decision, and a small set of
numbers and counts that were asserted more strongly than their sources allow.

---

## Dimension 1 — Phase integrity (ROADMAP.md vs Paper IV)

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1.1 | All 8 phases (0–7) present in both documents, same order and objectives | PASS | ROADMAP.md §2 table (L44–56); Paper IV §§5–13 |
| 1.2 | Phase names/titles consistent (Freeze contracts / Formalize state machine / Verify invariants / Consistency / Idempotency / Security / Router / Doctoral evidence) | PASS | ROADMAP.md §2; Paper IV section titles §§5–13 (Phase 0 is split across §5 and §6 — presentation only) |
| 1.3 | Per-phase deliverables consistent between the two documents | PASS | ROADMAP.md §§3–10 vs Paper IV §§5.6–13.3 (ten-part evidence package identical, §13.3) |
| 1.4 | Exit criteria consistent (Paper IV checklists expand, do not contradict, the roadmap's criteria) | PASS | ROADMAP.md §§3–9 exit criteria; Paper IV §6.7, §7.9, §8.4, §9.9, §10.9, §11.7, §12.7 |
| 1.5 | The six gaps identical in both documents | PASS | ROADMAP.md L8–15; Paper IV §2.3/§3.1–3.6 |
| 1.6 | Minimum Viable Fix vs Full PhD Fix table identical | PASS | ROADMAP.md §12; Paper IV §15.2 (L2396–2420) — row-for-row identical |
| 1.7 | Thesis structure (10 chapters) and final sequence consistent | PASS | ROADMAP.md §10, closing sequence; Paper IV §13.4, Part 2 (L2520–2528) |

## Dimension 2 — Status truth

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 2.1 | Phase 0 completion claims vs artifacts (glossary, events, TLA+ spec, governance — all ratified v1.0.0, 2026-10-19) | PASS | `contracts/README.md` §(d); `contracts/glossary.md` header; `contracts/events.md` header; files present |
| 2.2 | Phase 1 claims on all surfaces vs `proofs/phase1-tlc-report.md` | PASS | Report: 3,266,929 distinct states, 205,173,020 generated, zero violations, six fixes; identical figures in CHANGELOG.md, wiki-draft/Doctoral-Programme.md L33, website; the non-exhaustion caveat is carried honestly on all three surfaces |
| 2.3 | Phase 1 closure satisfies Paper IV §7.9 exit criteria as written | **FAIL** | §7.9 requires: model under `proofs/state-machine/` (reality: `spec/state-machine.tla`; `proofs/` is flat), "the ten state variables of §7.2" (the implemented model adds `chain`, `intent`, `tap_digest`, `now` and restructures others — adaptations documented in the TLC report), and "Liveness shown — PO-12 holds" (TLC report: PO-12 "out of scope for Phase 1 safety checking"). Phase 1 was closed as proven on the safety results; the paper's checklist itself remains entirely unchecked (§7.9, L879–893). The gap is disclosed in the report — but the governing checklist and the closure basis were never reconciled |
| 2.4 | Phase 2 status (opened 2026-10-20; catalogue, matrix, L1 39/39, L2 10/10 + 53,079 rejections, L3 10/10, crosscheck 12/12) vs `tests/` artifacts | PASS | `tests/PHASE-2-RUN-REPORT-2026-10-20.md`; `tests/evidence/*.log` (rejections log: "TOTAL REFUSED: 53079"); `tests/PHASE-2-OPENING.md` |
| 2.5 | Roadmap documents' own status framing is current | **STALE** | Both documents are written wholly prospectively. Every Paper IV exit checklist (§6.7 L731, §7.9 L879, §8.4 L1099) stands unchecked although Phases 0–1 are closed and Phase 2 is open. §13.3 part 2 still reads "(TLA+ or Alloy — **open question**, pending the Month 2 decision)" (L2046–2069) — decided 2026-10-19. Execution has also outrun every published schedule (ROADMAP.md §11 Options A–C; Paper IV §14): Phases 0–1 completed in days, Phase 2 opened 2026-10-20, where Paper IV's programme places Phase 2 in Months 3–4. No schedule amendment is recorded; HgX's pacing directive of 2026-10-20 now governs |
| 2.6 | Specification-repository layout as prescribed (ROADMAP.md §0.4; Paper IV §6.5; §14 Month 1 deliverables) vs the repository as built | **FAIL** | Prescribed but **nonexistent**: `spec/state-machine.md`, `spec/invariants.md`, `spec/consistency.md`, `spec/idempotency.md`, `spec/security-threat-model.md`, `spec/router-policy.md`, `spec/approval-digest.md`; `contracts/watchtower.schema.json`, `evidence-packet.schema.json`, `approval-intent.schema.json`, `decision-packet.schema.json`, `artifact-manifest.schema.json`. Built instead: `spec/state-machine.tla` + `.cfg`, `contracts/*.md`, flat `proofs/`, `tests/layer1|layer2|layer3` (not `tests/contracts|properties|chaos`), `experiments/` empty. `contracts/README.md` §(d) honestly marks the missing files DRAFT 0.1.0 — but no recorded decision ever amended the prescribed layout |
| 2.7 | Phase 0 exit criterion "contract sketches complete" | PASS | Paper IV §6.7 words the criterion as sketches held in Appendix C (§16, L2588+) — which exist; the standalone schema *files* are 2.6's separate failure |
| 2.8 | Phase 0 decision sheet reflects the decisions taken | **STALE** | `phase-0-decision-sheet.md`: all seven items D1–D7 still show "☐ HgX's call: __________" blank, although D1, D2, D7 were decided 2026-10-19 (records live in `contracts/events.md` header, `contracts/README.md` §§(c)–(d), `contracts/glossary.md` §3) |

## Dimension 3 — Numbers audit

| # | Claim | Verdict | Traced to |
|---|---|---|---|
| 3.1 | 3,266,929 distinct states; 205,173,020 generated; zero invariant violations | PASS | `proofs/phase1-tlc-report.md`, "Verification result" |
| 3.2 | "Six spec fixes" | **FAIL** | The TLC report's own introduction states "TLC found **five** genuine spec bugs" — then enumerates Fix 1 through Fix 6 and concludes "after the six fixes above". Every other surface (CHANGELOG.md, wiki, website, run report) says six. The artifacts support **six**; the report's introduction contradicts its own body |
| 3.3 | 12 states; 21 transitions (T1–T21); 19 events | PASS | `spec/state-machine.tla` States set (L120); `contracts/events.md` §12 (L215–219); crosscheck 12/12 (`tests/evidence/2026-10-20-crosscheck.log`) |
| 3.4 | 27 invariants; 12 proof obligations (PO-1–PO-12); 10 "fixed" meanings; 13 failure conditions; 7 illegal states | PASS | ROADMAP.md §5, §4 (L190–215); Paper IV §8.1, §7.6 (L839–857), §7.5, §7.4 |
| 3.5 | Glossary: 69 terms, 25 conflicts, 6 unresolved | PASS | Counted directly in `contracts/glossary.md`: 69 term entries in §1, conflicts C-1–C-25 in §2, items U-1–U-6 in §3 |
| 3.6 | Doctoral evaluation scores: 8.3 overall; 9.1 / 9.2 / 9.3; empirical 6.0 | PASS | Paper IV Abstract (L13–23); ROADMAP.md header (L3–5). Traced to HgX's recorded evaluation of 2026-10-08 — there is **no standalone evaluation artifact** in the repository; the numbers rest on the operator's record |
| 3.7 | Clock-skew bound Δ = 60s | PASS | Ratified (glossary U-5); implemented: `spec/state-machine.cfg` — `Delta = 60` |
| 3.8 | "Counterexample at Δ = 300s" (stale grant honoured) | **FAIL** | Stated as fact in `phase-0-decision-sheet.md` D7 ("counterexample demonstrated at 300s") and `contracts/glossary.md` U-5 ("PO-2 fails at 300s"). The only source is Paper IV §7.8's results table (L864–878), which is explicitly headed "**illustrative** — a specimen of the results artefact Phase 1 must produce, **not results already obtained**". No run log records a 300s check. The claim outruns its evidence |
| 3.9 | §7.8 illustrative row "0 violations in 4.2M states" | PASS | Labelled illustrative in the paper itself (L864–866); no estate surface mistakes it for the real 3,266,929 figure |
| 3.10 | Paper IV = 110 pages | PASS | `pdfinfo` on `whitepaper/JARVIS-Roadmap-White-Paper.pdf`: Pages: 110 |
| 3.11 | Stability score 85 / 100 (baseline 2026-W43) | PASS | `jarvis-estate/scores/STABILITY.md` L9; `jarvis-estate/audits/weekly/2026-W43.md` |
| 3.12 | Dropbox archive size | **FAIL** | Two public surfaces conflict: `jarvis-estate/EVIDENCE.md` E-003 — "13 folders, **23 files**, byte-verified" (2026-10-19 16:41) vs website — "13 folders, **50 entries**, byte-verified" (2026-10-19 17:58). The later figure supersedes; E-003 was never updated. Neither count is re-verifiable from the artifacts in this repository |
| 3.13 | Phase 2 figures: L1 39/39; L2 10/10; 53,079 refusals; PT-4 2,000 sequences / 56,261 steps / 162 executions / 23 completions; crosscheck 12/12 | PASS | `tests/evidence/2026-10-20-layer1-rerun.log`, `-layer2-run.log`, `-layer2-rejections.log`, `-layer3-run.log`, `-crosscheck.log`; `tests/PHASE-2-RUN-REPORT-2026-10-20.md` §§1–4 |
| 3.14 | Router metrics count | PASS | Paper IV §12.4 defines **eleven** metrics (escalation precision and recall counted separately, L1874–1899); ROADMAP.md §9 lists ten lines with "escalation precision/recall" combined — same set, different presentation. Noted, not a contradiction |

## Dimension 4 — Cross-surface consistency

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 4.1 | Website (build-out, future, evidence sections) vs roadmap reality | PASS | `jarvis-estate/website/index.html`: "Phase 0 complete… contracts v1.0.0 normative", "Phase 1 proved them — 3,266,929 states model-checked, zero invariant violations", evidence ledger "Website public / Repository public", GitLab mirror the one Tracked item (updated 2026-10-20) |
| 4.2 | Repo `EVIDENCE.md` (the public evidence ledger) vs reality | **FAIL** | PRESENT section is headed "verified (checked 2026-10-19 ~17:35 ET)" and still states: Website — "Built + verified; **no public URL**"; Repo — "Committed… **not pushed**". Both have been false since the evening of 2026-10-19 (repo pushed ~21:30 ET; Pages site live and verified 2026-10-20). The ledger also contains **no Phase 0 or Phase 1 proven entries at all** — the doctoral programme's two closed phases are absent from the estate's own evidence ledger. Internal defect: F-003 sits in the FUTURE table carrying status "PROVEN" |
| 4.3 | Repo `CHANGELOG.md` vs reality | PASS | [2026-10-19] Phase 1 entry: exact figures, six fixes, non-exhaustion caveat — all match the TLC report |
| 4.4 | Wiki drafts vs reality | **STALE** | `wiki-draft/Doctoral-Programme.md` L33: the exhaustive run "remains desirable… and **is ongoing**" — it was stopped 2026-10-19 and its retest paused 2026-10-19 23:43, never resumed. L35: "**Phases 2–7 — not started.**" — Phase 2 opened 2026-10-20 18:00 ET. (The page's Phase 0/1 figures themselves are exact.) |
| 4.5 | `release-log/2026-10-20.md` vs reality | **STALE** | L65: "…Phase 2 awaiting HgX's word." True when written that morning; superseded at 18:00 the same day when HgX ordered Phase 2 opened |
| 4.6 | Repo `formal-spec/` copy completeness | **STALE** | The repo copy carries contracts, spec, and the Phase 1 report + exhaustive log, but no `tests/` tree (the entire Phase 2 package) and no `proofs/tlc-retest-2026-10-19.log` (present in the workspace). Publication is scheduled — the publishing house holds briefs for the 2026-10-21 02:00 commit — but at test time the public repo does not yet show Phase 2 |
| 4.7 | Goal workspace `GOAL.md` vs roadmap | PASS | Eight phases named correctly; roadmap path correct (`goals/j-a-r-v-i-s-doctoral-validation/GOAL.md`) |
| 4.8 | `contracts/README.md` cross-references to the roadmap | **FAIL** | §(a) cites the security spec as "(Paper IV §11; **Roadmap §11**)" and the router spec as "(Paper IV §12; **Roadmap §12**)". ROADMAP.md's Phase 5 is **§8** and Phase 6 is **§9** — the citations follow Paper IV's numbering while naming the roadmap. Minor, but in the governance document of a programme whose first law is one normative reference |
| 4.9 | `tests/PHASE-2-PLAN.md` pacing vs Paper IV §14 | **FAIL** | The plan states the three layers run "across the programme's Months 2–4 window". Paper IV §14 assigns Month 2 to Phase 1 modelling, Month 3 to "Phase 1 Results and Phase 2 Contract Tests", Month 4 to "Phase 2 Property and Chaos Tests" — Phase 2 occupies **Months 3–4**, not 2–4. Low severity; the estate's own newest plan misquotes the programme it cites |

## Dimension 5 — Internal consistency

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 5.1 | Invariant ID sequences complete, no gaps or collisions (C1–C5, A1–A7, E1–E5, S1–S5, R1–R5 = 27) in ROADMAP.md, Paper IV §8.1, Paper IV Appendix A, and `tests/invariant-catalogue.md` | PASS | All four sources enumerate the identical 27 IDs (crosscheck-verified) |
| 5.2 | Proof obligations PO-1–PO-12 complete and consistently mapped | PASS | Paper IV §7.6 (L839–857); the checked subset in `spec/state-machine.cfg` (SafetyInvs = PO1, PO2, PO4–PO8 + PO11 property) is documented in the TLC report, with PO-3/9/10 spot-checked and PO-12 deferred — disclosed, not silent |
| 5.3 | Event vocabulary count consistent inside Paper IV | **FAIL** | §6.4 (L649–681): fifteen roadmap events **plus four Phase 0 additions** = 19, matching the frozen `contracts/events.md` §12. But Appendix B (L2566–2587) is headed "The **fifteen** normative events" and lists only 15 — the appendix was never updated with the four additions the paper's own §6.4 adopts. A reader of the appendix alone takes away the wrong normative count |
| 5.4 | Terms used in the roadmap documents are defined in the frozen glossary | PASS | Spot-verified across `contracts/glossary.md` §1 (69 terms): approval intent, intent digest, evidence packet, idempotency key, capability, trust boundary, freshness, saga, escalation, scorecard, chaos test, property test, traceability matrix, shadow mode, repair/attention cost — all defined, one definition each |
| 5.5 | Implemented vocabulary matches Paper IV §7.2 verbatim | **FAIL** | §7.2 defines `approval_state` ∈ {none, requested, **granted**, denied, expired, recorded}. `spec/state-machine.tla` (L160–163) implements {none, requested, **tapped**, recorded, denied, expired}. The rename is deliberate and commented in the spec ("tapped vs recorded: the operator tapped; the SERVER persisted") and §7.2's own prose makes the same distinction — but the normative enum value differs between the paper and the ratified model. Low severity |
| 5.6 | Paper IV §13.5 contribution count | **FAIL** | L2094: "The J.A.R.V.I.S. programme claims **four** contributions" — the section then enumerates First, Second, Third, Fourth, and **Fifth** (the open reference implementation). Internal count error in the paper |
| 5.7 | Clock-skew quantities disambiguated | **FAIL** | Two different bounds circulate under one name: the ratified Δ = **60 seconds** (approval validity; glossary U-5: "The glossary's time-dependent terms… now use Δ = 60s") and Paper IV §9.9's Phase 3 exit criterion "Behaviour verified under clock skew (device timestamps **±5 minutes**)" — with §9's Open Question 3 simultaneously listing clock-skew tolerance as *unresolved*. No document states that these are different quantities (approval skew vs device-timestamp test range). Low–moderate severity: a Phase 3 implementer can conflate them |
| 5.8 | T6 joint-firing reading point (events.md §3: `artifact_produced` **and** `evidence_packet_created` fire jointly; the mechanised legal table admits each individually) | PASS | Disclosed in `tests/PHASE-2-RUN-REPORT-2026-10-20.md` §5 and the traceability matrix; suites follow the mechanised artifact. A documented reading point, not a hidden contradiction |
| 5.9 | ROADMAP.md §0.2 "proposed" transition skeleton vs the frozen transition table | PASS | The skeleton is labelled proposed; Paper IV §6.2 marks its five additions (T2, T8, T10, T19, T21) with asterisks and reconciliation decisions. No silent divergence |

## Dimension 6 — Open questions and decisions

| # | Question | State per the record | Verdict |
|---|---|---|---|
| 6.1 | D1 / OQ-4 — TLA+ or Alloy as primary language | **DECIDED 2026-10-19: TLA+** (Alloy secondary). Record: `contracts/events.md` header ("Proof language: TLA+ (decision D1, 2026-10-19)"); `contracts/README.md` §(d) | PASS |
| 6.2 | D2 — who resolves vocabulary conflicts | **DECIDED 2026-10-19: coordinator resolves, HgX ratifies.** Record: `contracts/glossary.md` header; `contracts/README.md` §(a) | PASS |
| 6.3 | D7 / U-5 — clock-skew bound Δ | **RATIFIED 2026-10-19: Δ = 60s.** Record: `contracts/README.md` §(c); glossary U-5; implemented in `state-machine.cfg` | PASS |
| 6.4 | U-1 — intent digest construction | **Decision RESOLVED 2026-10-19 (SHA-256 over canonical JSON)** — record: glossary §3. But the implementing deliverable does not exist: `spec/approval-digest.md` is still "DRAFT — to be written" (`contracts/README.md` §(d)) and `contracts/approval-intent.schema.json` is absent (see 2.6). Paper IV §14 makes the digest rule a Month 1 deliverable "stated precisely enough that two independent implementations produce the same digest" — that test cannot currently be run. A decision recorded; its artifact silently missing | **FAIL** |
| 6.5 | U-6 — back-edit Papers I–III or not | **RESOLVED 2026-10-19: papers stand as historical; glossary is the normative overlay.** Record: glossary §3 | PASS |
| 6.6 | D3 — isolation-level commitment (incl. Paper IV §11 Open Question 1: a *dated* commitment to Level 1) | **OPEN.** `contracts/README.md` §(c) records Paper IV's recommendation adopted as a working assumption "until ratified". No dated Level 1 commitment exists anywhere in the record | STALE (open, visibly so — no silent decision) |
| 6.7 | D4 — router live trials required? / can natural workload supply Stage 3 samples? | **OPEN**, same working-assumption record (README §(c)). Paper IV §12 Open Questions 1, 4, 5 also open | STALE (open, visibly so) |
| 6.8 | D5 / D6 with OQ-3 / OQ-1 / OQ-2 — expiry returns to `in_progress`; single `verifying` and `blocked` states | **Adopted as working assumptions, implemented** in the frozen table (T10) and the TLA+ model; `contracts/README.md` §(c) states they stand "until ratified". Transparent — recorded as unratified, not silently decided | PASS |
| 6.9 | Chaos-test harness choice (Paper IV §14, Month 4: "a dedicated test harness environment or… instrumented live paths") | **Silently resolved in practice.** Layer 3 was built as a third thing — a reference-model suite (`tests/layer3/chaos_model.py`) — and no document records a decision on the paper's either/or question, which remains formally open while its work proceeded | **FAIL** (low–moderate) |
| 6.10 | U-2 (revision token, Phase 3), U-3 (freshness values, Phase 3), U-4 (pause safe-point semantics, Phase 4); Paper IV §9 OQs 1–5, §10 OQs 1–5, §11 OQs 2–6, §12 OQs 1–6 | **OPEN**, each with a named owning phase in `contracts/glossary.md` §3 or the paper itself. No silent decisions found in any artifact | PASS |
| 6.11 | Attention-cost weighting; cost-unit exchange rate (Paper IV §12 OQs 2–3) | **OPEN** — asserted-not-measured, exactly as the paper states | PASS |

---

## Discrepancy register

Severity: **High** = a public or governing surface states something false about the programme's core record. **Moderate** = a claim outruns its evidence, or a governing checklist and reality were never reconciled. **Low** = a stale line, wrong citation, or count slip with limited blast radius.

| # | Severity | Discrepancy (sources quoted) | Artifacts support |
|---|---|---|---|
| R-1 | **High** | Repo `EVIDENCE.md`: "Website — no public URL"; "Repo — not pushed" (checked 2026-10-19 17:35) — vs website's own ledger ("Website public", "Repository public") and the fact of the live Pages site and pushed repo since 2026-10-19 evening. The ledger also omits Phases 0–1 entirely | The website and reality: both surfaces public; Phases 0–1 closed with evidence in `proofs/` and `contracts/` |
| R-2 | **High** | Prescribed repository layout (ROADMAP.md §0.4 and Paper IV §6.5 both promise `spec/state-machine.md`, five `contracts/*.schema.json`, `proofs/state-machine/`, etc.) vs the built tree, in which none of those files exist and the layout differs in every directory | The built tree (`jarvis-formal-spec/` listing); `contracts/README.md` §(d) concedes the files are unwritten drafts. No amendment decision is on record |
| R-3 | Moderate | Paper IV §7.9 exit criteria ("Liveness shown — PO-12 holds"; model "committed under `proofs/state-machine/`"; "the ten state variables of §7.2") vs Phase 1 closed as proven with PO-12 expressly out of scope, model in `spec/`, and a restructured variable set | The TLC report — its disclosure is honest; the unreconciled party is the paper's unchecked checklist |
| R-4 | Moderate | "Counterexample demonstrated at 300s" (decision sheet D7; glossary U-5: "PO-2 fails at 300s") vs Paper IV §7.8, whose table is headed "illustrative… not results already obtained" | Paper IV §7.8's own label: no 300s run exists in any log (`proofs/*.log`) |
| R-5 | Moderate | TLC report: "TLC found **five** genuine spec bugs" (introduction) vs its own Fix 1–Fix 6 and "after the six fixes" (result), and six on every other surface | Six — the enumerated fixes are the evidence |
| R-6 | Moderate | Paper IV Appendix B: "The **fifteen** normative events" vs Paper IV §6.4 + `contracts/events.md` §12: **19** canonical events (15 + 4 Phase 0 additions) | 19 — §6.4 and the ratified contract agree |
| R-7 | Moderate | Wiki `Doctoral-Programme.md`: "Phases 2–7 — **not started**" and the exhaustive run "**is ongoing**" vs Phase 2 opened 2026-10-20 and the exhaustive run stopped 2026-10-19 / retest paused 2026-10-19 23:43 | The workspace record (`tests/PHASE-2-OPENING.md`; `proofs/` logs) |
| R-8 | Low–moderate | Dropbox counts: `EVIDENCE.md` E-003 "13 folders, 23 files" vs website "13 folders, 50 entries" — both claiming byte-verification | The later figure (17:58, 2026-10-19) supersedes the earlier (16:41); neither is re-verifiable from this repository |
| R-9 | Low–moderate | Two clock-skew bounds under one name: ratified Δ = 60s vs Paper IV §9.9's "±5 minutes" test criterion, with §9 OQ-3 calling skew tolerance unresolved | The ratified 60s (cfg `Delta = 60`) governs approvals; the ±5-minute figure is an unratified Phase 3 test proposal. No document says so |
| R-10 | Low–moderate | Chaos harness (Paper IV §14 Month 4 open question: dedicated harness *or* instrumented live paths) — Layer 3 was built as a reference-model suite; the question was never decided on record | `tests/layer3/` — the work is real; the decision record is absent |
| R-11 | Low | Paper IV §13.5: "claims **four** contributions" — five are enumerated | The enumeration (First–Fifth) |
| R-12 | Low | `release-log/2026-10-20.md` L65: "Phase 2 awaiting HgX's word" — superseded the same evening (Phase 2 opened 18:00, 2026-10-20) | `tests/PHASE-2-OPENING.md` |
| R-13 | Low | `contracts/README.md` cites "Roadmap §11" (security) and "Roadmap §12" (router) — ROADMAP.md's are §8 and §9 | ROADMAP.md's own section numbering |
| R-14 | Low | `phase-0-decision-sheet.md`: all seven decision boxes blank although D1, D2, D7 were decided 2026-10-19 | The decision records in `contracts/` (events.md header; README §§(c)–(d); glossary §3) |
| R-15 | Low | Approval-state enum: Paper IV §7.2 `granted` vs `spec/state-machine.tla` `tapped` (deliberate, commented in the spec) | The ratified model — with the paper's prose (§7.2) making the same tapped/recorded distinction the rename encodes |
| R-16 | Low | `tests/PHASE-2-PLAN.md`: layers run "across the programme's Months 2–4 window" vs Paper IV §14 (Phase 2 = Months 3–4) | Paper IV §14's month map |

---

## Score

| Dimension | PASS | FAIL | STALE | Total |
|---|---:|---:|---:|---:|
| 1. Phase integrity | 7 | 0 | 0 | 7 |
| 2. Status truth | 4 | 2 | 2 | 8 |
| 3. Numbers audit | 11 | 3 | 0 | 14 |
| 4. Cross-surface consistency | 3 | 3 | 3 | 9 |
| 5. Internal consistency | 5 | 4 | 0 | 9 |
| 6. Open questions | 7 | 2 | 2 | 11 |
| **Total** | **37** | **14** | **7** | **58** |

**37 / 58 checks passed.**

The roadmap itself — phases, invariants, obligations, exit criteria, tables —
is internally coherent and faithful between its two governing documents
(Dimension 1: 7/7), and everything the estate claims about Phases 0–2 that can
be traced to an artifact, traces (Dimensions 2–3: the Phase 1 figures, the
glossary counts, the Phase 2 run numbers are all exact). What the test catches
is the paperwork around the proof: public ledgers and wiki pages a day behind
the facts, a repository layout promised in two documents and built in a third
shape, one illustrative table quietly promoted to a demonstrated result, and
exit checklists nobody went back to tick. None of it touches the proof. All of
it is fixable in an afternoon of amendments — on HgX's word, not this report's.

*Report filed 2026-10-20. Read-only: no artifact was modified by this test.*
