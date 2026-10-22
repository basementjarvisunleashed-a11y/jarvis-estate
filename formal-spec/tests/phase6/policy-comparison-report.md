# Phase 6 — Policy Comparison Report (Stage 2)

**Status:** v0.1-draft. Written 2026-10-22 under Phase 6 (Router Optimality),
on HgX's word ("Run the work layers", 2026-10-22 ~12:53 ET).
**Sources:** `layer2/` replay harness (evidence
`evidence/2026-10-22-phase6-layer2-metrics.json`; weighted evidence
`evidence/2026-10-22-phase6-layer2-weighted-metrics.json` and
`evidence/2026-10-22-phase6-layer2-weighted.log`); ROADMAP.md §9;
`experiment-protocol.md`; `weight-table.md` (ALL SIGNED 2026-10-22);
`router-policy-spec.md`; real corpus
`~/workspace/usage-router/logs/router-backfill-2026-10-22.jsonl` (101
entries) + `router-2026-10-07.jsonl` (1 entry).

## 1. Method (what was actually done)

The L2 harness replayed 13 logged decisions through three policies —
unconstrained (RP-8a), cache-only (RP-8b), local heuristic (RP-8c) — and
computed the ten roadmap metrics per policy, **unweighted** (Q4: no
weighted comparison until he signs the weight table). Outcome metrics
cover only entries where the policy AGREED with the logged `action_taken`
(measured outcomes); disagreements are `counterfactual_unknown` — no
claim is made about what would have happened.

**Weighted run (2026-10-22 ~13:15 ET):** the weights are now SIGNED —
all six, 2026-10-22 ~13:09–13:14 ET, every default kept as proposed
(`weight-table.md`, "ALL SIX WEIGHTS SIGNED"; the weighted gate is
OPEN). The harness gained `--weighted` mode (WT-9, weights parsed from
the signed document, never hardcoded) and ran it against the REAL
corpus: 102 real entries (101 backfilled `router-backfill-2026-10-22.jsonl`
+ 1 original `router-2026-10-07.jsonl`), 0 synthetic. Evidence:
`evidence/2026-10-22-phase6-layer2-weighted-metrics.json`,
`evidence/2026-10-22-phase6-layer2-weighted.log`. The 12 synthetic
fixtures were run separately as a sanity check only — clearly labeled,
never merged into the evidence numbers.

## 2. The corpus — read this before the tables

| Corpus | n |
|---|---|
| Real router log (`~/workspace/usage-router/logs/router-2026-10-07.jsonl`) | **1** |
| Synthetic fixtures (`layer2/fixtures.json`, all marked `synthetic:true`) | 12 |
| **Total** | **13** |

The fixtures verify the machinery: all seven local rules fire, the
guardrail check trips on the baselines by design, the INV-R5 fallback
and Q2 Jev-refusal checks pass. **The tables below demonstrate the
method; they are not a verdict on the policies.** With one real entry,
no policy comparison can support an optimality claim — the report says
so, and the dashboard marks it.

## 3. Unweighted metric tables (measured on the corpus)

Recommendation distribution:

| Policy | proceed | use-cache | defer | escalate | deny |
|---|---|---|---|---|---|
| unconstrained | 13 | 0 | 0 | 0 | 0 |
| cache-only | 12 | 1 | 0 | 0 | 0 |
| local | 6 | 1 | 1 | 2 | 3 |

Agreement with logged action (decision metric, all 13 entries):

| Policy | agree | differ (counterfactual-unknown) |
|---|---|---|
| unconstrained | 7 | 6 |
| cache-only | 8 | 5 |
| local | 12 | 1 |

Outcome metrics (agreed + labeled entries only — different denominators,
**not directly comparable as policy quality**):

| Policy | labeled+agreed | accepted rate | repair min | interruptions | cost units | mean latency s |
|---|---|---|---|---|---|---|
| unconstrained | 6 | 0.6667 | 35 | 4 | 12 | 807.0 |
| cache-only | 7 | 0.7143 | 35 | 4 | 12 | 692.0 |
| local | 11 | 0.6364 | 25 | 6 | 12 | 321.09 |

Guardrail check (irreversible → escalate; F-01):

| Policy | violations |
|---|---|
| unconstrained | 1 (by design — the no-gate baseline) |
| cache-only | 1 (by design — cache-only has no gating) |
| local | 0 |

Invariant/behaviour checks:

| Check | Result |
|---|---|
| INV-R5: failing backend → local fallback, logged | pass |
| Q2: Jev backend refuses without his approval; nothing sent | pass |

Local rule coverage (all seven rules fired):

RP-6.1 ×1, RP-6.2 ×1, RP-6.3 ×1, RP-6.4 ×1, RP-6.5 ×2 (warranted + denied),
RP-6.6 ×4 (search-cheap, live-needed, curiosity, default ×3), RP-6.7 ×1.

## 3b. Weighted comparison (WT-9) — 102 real entries

Weights (signed, parsed from `weight-table.md`):
`score = 1.0·accepted_work − 5.0·human_repair_minutes −
10.0·attention_interruptions − 1.0·cost_units − 8.0·loops −
0.1·latency_over_budget_seconds`.

Corpus for this table: **102 real entries, 0 synthetic** (101 backfilled
2026-10-22 + the original 2026-10-07 self-test). Contributing entries per
policy = agreed with the logged `action_taken` AND outcome label known
(DL-4). Excluded: `action_taken` "unknown" (25 entries — can never agree),
agreed-but-outcome-unknown (2 per policy), policy disagreements
(counterfactual-unknown).

| Policy | contributing | accepted_work | repair min | interruptions | cost units | loops | latency OB | **WT-9 score** | guardrail violations |
|---|---|---|---|---|---|---|---|---|---|
| unconstrained (RP-8a) | 74 | 72 | 0 (74 unk) | 0 (74 unk) | 0 (74 unk) | 0 | 0 (74 unk) | **72.0** | 38 |
| cache-only (RP-8b) | 74 | 72 | 0 (74 unk) | 0 (74 unk) | 0 (74 unk) | 0 | 0 (74 unk) | **72.0** | 38 |
| local heuristic (RP-8c) | 45 | 45 | 0 (45 unk) | 0 (45 unk) | 0 (45 unk) | 0 | 0 (45 unk) | **45.0** | 0 |

Notes on the terms: `accepted_work` counts `outcome == "accepted"` only —
the 2 "repaired" and 1 "rejected" outcomes contribute 0 (stated, not
smoothed). All four numeric labels (`repair_time_minutes`,
`attention_interruptions`, `cost_units`, `latency_seconds`) are unknown
in every backfilled entry — they contribute 0 and are counted as unknown
(the harness never invents them). No state carries `action_repeat_count
>= 3`, so 0 loop events were detected; no state carries a latency budget,
so latency-over-budget is 0-by-unknown. **The weighted scores rest on
`accepted_work` alone — four of six terms have no data.**

Why local scores lower: of the 38 irreversible entries, local recommended
`escalate` on all of them (the guardrail firing, correctly). 29 of those
were logged with terminal action `proceed` — HgX's own approval was the
gate in every case — so they count as disagreements (counterfactual-unknown),
not contributions. The baselines "agree" with those 29 precisely because
they have no gate — and carry 38 guardrail violations each for it. Local
agreed with 47, all 45 contributing outcomes accepted (rate 1.0), 0
violations.

## 4. What the numbers do and do not say

- **They say:** the replay machinery works end to end — corpus loading,
  the three policies, the ten metrics, the honest counterfactual rule,
  the guardrail and fallback checks. The local policy is the only one
  that never violates the consequential-action guardrail, by construction.
- **They do not say:** which policy is optimal. The corpus is 12
  hand-built fixtures and 1 real entry; the agreed subsets differ per
  policy; the comparison is unweighted. Any "winner" read off these
  tables would be numerology, and this report refuses it.
- **The weighted table (§3b) does not say** that the no-gate baselines
  are "better" because they score 72.0 against local's 45.0. The score
  rewards agreement with logged terminal actions — and 29 of the
  baselines' agreements are irreversible actions the guardrail exists to
  gate (each one a guardrail violation; local has 0). Read with the
  violations column, the table says the opposite of what a naive ranking
  would claim: the local policy is the only one that never violates the
  consequential-action guardrail, and every outcome it agreed with was
  accepted. The weighted scores become a real comparison only when live
  labeled volume accumulates — repair minutes, interruptions, cost, and
  latency measured, not unknown.

## 5. What changes when the gates open

- **Weights signed (Q4):** ~~the harness gains `--weighted` mode (WT-9);
  this report gains a weighted table beside the unweighted one. The
  unweighted tables stay — weights are a value judgement over
  measurement, not a substitute.~~ **DONE 2026-10-22 ~13:14 ET** — all
  six weights signed, every default kept; `--weighted` mode built and
  run (§3b); the unweighted tables remain above.
- **Stage 1 volume:** as outcome labels accumulate on real decisions,
  the labeled+agreed denominators grow and stage 4 (Bayesian estimation
  for small samples) becomes meaningful. Today it is a method on paper.
- **Jev approved (Q2):** the RP-8d backend is exercised in replay; the
  report gains a fourth policy column. Until then, the column stays
  empty — by his decision, not by omission.
- **Stage 3 approved (Q1/Q3):** live-trial evidence enters under the
  ratified eligibility boundary. Not designed, not run, not claimed.

## 6. Limitations (stated, not footnoted)

L-1. One real decision. Everything measured about "the router" today is
really measured about the fixtures.
L-2. Outcome labels on fixtures are synthetic by construction; the
labeling method for real decisions (DL-3) is post-hoc judgment, not
ground truth.
L-3. Replay cannot observe counterfactuals — the agreed-only rule is
the honest boundary, and it shrinks every denominator.
L-4. The learned policy (RP-8f) and hybrid (RP-8e) are not evaluated.
L-5. The weighted scores (§3b) rest on `accepted_work` alone — four of
six WT-9 terms are zero-by-unknown across all 102 backfilled entries,
and 0 loop events were detectable. The backfill is Stage 2
reconstruction (the router was in shadow, never consulted), not live
Stage 1 data. The scores are a method demonstration with real entries,
not an optimality verdict.

## Cross-references

- `../experiment-protocol.md` — the stage definitions this report follows.
- `../weight-table.md` — the gated weighted objective.
- `../evidence/2026-10-22-phase6-layer2-metrics.json` — the raw numbers.
