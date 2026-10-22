# Phase 5 (Security Boundary Formalism) — PROVEN Sweep Report

**Date:** 2026-10-22 · **Authorization:** HgX's explicit word, 2026-10-22 ~12:40 ET ("Yeah, start running it").
**Sweep pattern:** Phase 3/4 proven-sweep — fresh re-runs, claim audit, no-ratified-touch, integrity manifest, exit-criteria mapping.
**Work tree:** `~/workspace/jarvis-formal-spec/tests/phase5/` (L1 drafts, `layer2/`, `layer3/`, `evidence/`).

## 1. Fresh re-runs (clean state, 2026-10-22 ~12:41 ET)

**Layer 2** (`tests/phase5/layer2/run.sh`):
- 93 passed, 0 failed, 66 refusals logged
- Per family: SP 21/21, TM 21/21, RP 5/5, DC 7/7, DF 15/15, HL 10/10, EL 14/14
- Matches the reported totals exactly (93/93, 66 refusals).

**Layer 3** (`tests/phase5/layer3/run.sh`):
- 34 passed, 0 failed, 165 refusals/flags logged, 34 case verdicts, 0 findings
- Per family: PI 10, SS 8, AF 8, SD 8 — all green
- Verdict tally: 26 held-refused, 2 held-flagged, 1 held-backstop, 5 clean-pass, **0 findings**
- Every verdict names a threat and a control; 0 missing IDs; 0 duplicate case IDs
- Matches the reported totals exactly (34/34, 165 events, 0 findings).

## 2. Byte-identity of evidence ledgers

Pre-run sha256 snapshot taken; post-run comparison:
- **Byte-identical (5/7):** layer2 rejections log, layer2 summary, layer3 rejections log, layer3 summary, layer3 verdicts JSONL
- **Differ (2/7):** the two verbose unittest logs — difference confined to the single
  `Ran N tests in X.XXXs` timing line per file (CPU-scheduling noise). No other
  wall-clock timestamps or dates appear in the logs; the 93/34 "ok" lines and the
  0 FAIL/ERROR counts were re-verified in the new logs.
- Substantive evidence (every refusal with cause, every count, every case verdict) is byte-identical.

## 3. Claim audit (146 numbered claims)

Every numbered claim verified present in its document with substantive content
(not just indexed): **146/146, 0 problems.**

- asset-register.md: AR-1…AR-15
- trust-boundaries.md: TB-1…TB-15 (incl. ASCII trust-boundary diagram)
- capability-matrix.md: CM-1…CM-14 (eight-field format §2; issuance/storage/rotation deferred)
- threat-catalogue.md: T-1…T-28, incl. T-26 (L)…T-28 (L)
- attack-trees.md: AT-1…AT-5 (AT-2 asserts every leaf names its control; no unstopped leaves)
- control-matrix.md: C-1…C-31 (incl. §5 "The L0 compensations (Q3)")
- session-lifecycle.md: SL-1…SL-27
- isolation-upgrade-roadmap.md: IU-1…IU-11

*Correction to the layer report:* the work report cited CM-1…CM-4 and AT-1…AT-4;
the documents in fact contain CM-1…CM-14 and AT-1…AT-5. The documents are
complete; the report's ranges were undercounted.

**Walkthrough answers baked in (all six, verified):**
- Q1 — session-lifecycle.md: enrollment, revocation, re-enrollment, expiry, six states (SL-1…SL-27)
- Q2 — T-8: false-outcome reporting as a named Tampering threat (read-after-write where supported, strongest-approval/manual where not)
- Q3 — control-matrix.md §5 documents L0 compensations; isolation-upgrade-roadmap.md has L0 honestly current, advance only on HgX's word
- Q4 — CM-1…CM-4: eight-field format (subject, action, object, scope, condition, expiry, approval requirement, evidence requirement) as normative vocabulary; issuance deferred (CM-13); contract-freeze token shape cited as reference only, nothing ratified (CM-14)
- Q5 — T-26 (L) protocol-shape-only ZK, T-27 (L) unmodeled fatigue dynamics, T-28 (L) L0 ceiling — each a named threat with a compensating control
- Q6 — TB-11…TB-15: custody doctrines as named boundaries, described exactly as ordered, never redesigned; **TB-14 names the live-location boundary while the custodian is never named outside its own chat** — the reservation ("where description would weaken a control, the control wins") is stated in the document's own header

**Cross-reference integrity:**
- All T-/C-/AT-/SL-/TB-/AR-/CM-/IU- references resolve: 0 dangling
- Document section references (e.g. control-matrix.md §5): 0 broken
- Layer 3 verdict threat/control IDs: 0 unknown
- "Layer 2 test pointer" columns use descriptive labels (e.g. `test_session_replay_rejected`);
  spot-verified each maps to a real test (replay, digest mutation, strongest-approval);
  keyword coverage of all 42 distinct pointers in the test sources is complete

## 4. No-ratified-touch

- Working tree: 0 files under `spec/` or `contracts/` modified on 2026-10-22
- Repo (`jarvis-estate`, formal-spec/): `formal-spec/spec` and `formal-spec/contracts` clean at HEAD (`git status` empty)
- The sweep itself read `spec/`/`contracts/` only

## 5. Exit-criteria mapping (ROADMAP.md §8, verbatim)

> "Every consequential action has a named threat and control; prompt injection,
> stale state, and approval fatigue explicitly modeled; procedural isolation
> documented and compensated; controls testable; posture defensible without
> overclaiming."

1. **Every consequential action has a named threat and control** — T-1…T-28 each
   carry a control; C-1…C-31 map threat→control→test; AT-1…AT-5 every leaf names
   its control; CM-11 requires approval + evidence requirements on every
   consequential action. **MET.**
2. **Prompt injection, stale state, approval fatigue explicitly modeled** —
   T-22/T-13 (prompt injection, incl. egress), T-23/T-4 (stale-state
   manipulation / mutated intent), T-24/T-14/T-27 (approval fatigue as attack,
   attention exhaustion, unmodeled dynamics); Layer 3 PI(10)/SS(8)/AF(8) all
   green, 0 findings. **MET.**
3. **Procedural isolation documented and compensated** — control-matrix.md §5
   "The L0 compensations (Q3)"; isolation-upgrade-roadmap.md IU-1…IU-11 with L0
   honestly current; HL family verifies the compensations. **MET.**
4. **Controls testable** — 93 Layer 2 + 34 Layer 3 cases; non-mechanically-testable
   controls honestly flagged (5 flags) with verification methods
   (`layer2/review-procedure.md` for C-20). **MET.**
5. **Posture defensible without overclaiming** — honest limitations as named
   threats with controls (T-26 (L)…T-28 (L)); HL 10/10 verifies no privacy
   property is asserted from protocol-shape proofs; CM-14 cites the token shape
   as reference only; zero overclaim language in the eight drafts. **MET.**

## 6. Integrity manifest (33 files, sha256)

```
./asset-register.md|6431|6c2b09ff481c9ca9e4bbf1b8fdf7ad450f99f70bb6047b2bacc45345b0ff0b62
./attack-trees.md|7420|15dfc70ccd4e2b124569d0183a5e9cdb2acd463f6ce5dde88d9fcf15491271ba
./capability-matrix.md|9106|2c45d17bdbb83d53de549eed34678b09c9aba0cf5973411006dd0dd1a32a806a
./control-matrix.md|9470|f00a3ae2801bfeb88ca948e3768bf1d40e8f7e93f2f1c0245209687db9dd02e8
./evidence/2026-10-22-phase5-layer2-rejections.log|7496|0ab09c3720240451c42ca95bbe9de419a574f8bceabe6ca439f88a84d078a8bc
./evidence/2026-10-22-phase5-layer2-summary.txt|369|c4ca3c0f347d6fc1b457b5bbc43382d360407e3892c4e5a1b2002fdffeb275e8
./evidence/2026-10-22-phase5-layer2.log|11577|a0449ec7bef592c6c23cd85aa5177fd75ba766daa5af180d1ac068ab0084e1a9
./evidence/2026-10-22-phase5-layer3-rejections.log|21855|408e33425cbd2b0312ee53d12ba2449913d769ba3f063f4846d8967b38d9615d
./evidence/2026-10-22-phase5-layer3-summary.txt|582|3976ba80df8beeff5d4403f8b4e7a9ce80152fc9579a82aa7c9f20adca5763f6
./evidence/2026-10-22-phase5-layer3-verdicts.jsonl|6888|2a9f2fe51751d625a3b831227c350f5287813daa410e3cabb3b7f327010a24d9
./evidence/2026-10-22-phase5-layer3.log|6885|d1a543793708a2a9e3842ab3b0ba99dc331bd810366541291434f088b4c0eb42
./isolation-upgrade-roadmap.md|5524|d9eeacf5458f1ec42e83bf47f3d826e544fce44a2c37107ecfe2ac36eff1d105
./layer2/README.md|5095|7dc9b370fbe01301cc618d5c5a91057e9a665ca4b99f7dcc2e0cc075012b31d4
./layer2/estate.py|41139|ea953e57ab6818f81cf026be0dd23b30386085d084ce502c29a44fe2159b0530
./layer2/review-procedure.md|1926|2e97edc1b7c4a8321500c25f0bc369c52d6ba08329abfa616a24b17821f2e8d1
./layer2/run.sh|2202|088b2aecd8621164bfbb82e5ac3c59caeb2551d441ee7f84a7ee5bb420885887
./layer2/test_disclosure.py|6114|8fb740451d2dae5fba4b191a76c26eb5e2f2d4bbb8702e7e83fadeaa0507b7c5
./layer2/test_dos_fatigue.py|10280|5b1e27a33d8d9d954660dbc5da52e0c31b49f14cdb68c3ba963ec8c486e76cc1
./layer2/test_elevation.py|10188|0cfde2e1b536bd83ad03f1899f3f724c49bc75389c56fbf85d52eeaf1565b010
./layer2/test_honest_limits.py|6140|ffaa97dd7a80eda8e0437df375f3bb58b55667b3d762d09ad555a0a2b63773ce
./layer2/test_repudiation.py|5326|c4521d16f967619ffedfe9c260f7393363fcda8cf7422b1e235a6e841d7d1730
./layer2/test_spoofing.py|14108|54885c9a20fc0929b8d58d80b7412d911ad51b9064a07a85616384764d30c5be
./layer2/test_tampering.py|11533|4607a6bf7637a92ab97245a4263b5415d8b6904859ac3425ac8de3ef01bbc53a
./layer3/README.md|5455|b329fb2b94570413218d99cffdbc1673a73b5b500dfdf1ec778080df309f2b0a
./layer3/adversary.py|18535|9034c75d6bf2648e111768692d01a6b825447c0d9a41aaa16b77f61891534639
./layer3/run.sh|3998|74aa7f526a933aab37fe635398f0b611f178926b6a15f3e06d201992547e5e43
./layer3/test_approval_fatigue.py|13340|cb24acc231f4219db4ce2d7f077bc891cecdd5c01213d63102ec44c7b74df9c1
./layer3/test_prompt_injection.py|11656|1e51a88c4981090508090f8ade7375b53c30f30b5e488059a1f1f31674ec5cbd
./layer3/test_stale_state.py|11965|b6db0f49f8745730e4dece7455c988a0cf2601e5832069860cdeb2c891781483
./layer3/test_subagent_deception.py|11276|880de7e91cd765e0e6fc418faeeea174624c92a2e2a7a5a184185cdc8d8c20ee
./session-lifecycle.md|8128|16f7d517f135cb864f183d71a49d4ced47a82851b33330198e22d8c13057d9a9
./threat-catalogue.md|9848|6e72393222ff19d0ea529984dc3d882d1b08727ecf74dd92087b1502a6fa2f05
./trust-boundaries.md|9064|ce87639969085e51a10bbb019110230cd1cca13a11b9bf38e466f83746b12506
```

*Note: the two verbose log hashes above are the post-sweep re-run values (timing-line
variance only, §2). __pycache__ directories excluded.*

## 7. Open points (flagged, not blocking)

P5-OP-0…P5-OP-8 await HgX's word, per the layer report (asset-count note, role-bot
matrix rows, third validation at tool plane, bot names verbatim, grant.approval
session binding, card-rendering depth, session expiry duration, second-device
enrollment gesture, L1 scoping priority). None blocks the exit criteria.

`tests/phase5/` is not yet present in the repo (publishing-house push of the work
layers still pending confirmation at sweep time) — outside this sweep's scope.

## VERDICT

**PROVEN — all exit criteria met.**
