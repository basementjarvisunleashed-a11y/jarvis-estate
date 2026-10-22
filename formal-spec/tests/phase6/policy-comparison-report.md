# Phase 6 — Policy Comparison Report (Stage 2)

**Status:** v0.1-draft. Written 2026-10-22 under Phase 6 (Router Optimality),
on HgX's word ("Run the work layers", 2026-10-22 ~12:53 ET).
**Sources:** `layer2/` replay harness (evidence
`evidence/2026-10-22-phase6-layer2-metrics.json`); ROADMAP.md §9;
`experiment-protocol.md`; `weight-table.md`; `router-policy-spec.md`.

## 1. Method (what was actually done)

The L2 harness replayed 13 logged decisions through three policies —
unconstrained (RP-8a), cache-only (RP-8b), local heuristic (RP-8c) — and
computed the ten roadmap metrics per policy, **unweighted** (Q4: no
weighted comparison until he signs the weight table). Outcome metrics
cover only entries where the policy AGREED with the logged `action_taken`
(measured outcomes); disagreements are `counterfactual_unknown` — no
claim is made about what would have happened.

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

## 4. What the numbers do and do not say

- **They say:** the replay machinery works end to end — corpus loading,
  the three policies, the ten metrics, the honest counterfactual rule,
  the guardrail and fallback checks. The local policy is the only one
  that never violates the consequential-action guardrail, by construction.
- **They do not say:** which policy is optimal. The corpus is 12
  hand-built fixtures and 1 real entry; the agreed subsets differ per
  policy; the comparison is unweighted. Any "winner" read off these
  tables would be numerology, and this report refuses it.

## 5. What changes when the gates open

- **Weights signed (Q4):** the harness gains `--weighted` mode (WT-9);
  this report gains a weighted table beside the unweighted one. The
  unweighted tables stay — weights are a value judgement over
  measurement, not a substitute.
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

## Cross-references

- `../experiment-protocol.md` — the stage definitions this report follows.
- `../weight-table.md` — the gated weighted objective.
- `../evidence/2026-10-22-phase6-layer2-metrics.json` — the raw numbers.
