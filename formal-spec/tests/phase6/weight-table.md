# Objective-Function Weight Table

**Status:** v0.1-draft. Written 2026-10-22 under Phase 6 (Router Optimality),
on HgX's word ("Run the work layers", 2026-10-22 ~12:53 ET).
**Sources:** ROADMAP.md §9 (objective function, quoted);
`tests/PHASE-6-OPEN-QUESTIONS.md` Q4 (2026-10-22 ~12:51 ET: propose
defaults in L1, he signs before any comparison runs).
**Signature status:** every weight below is **PROPOSED — FOR HIS
SIGNATURE**. No weighted comparison runs until he signs. The L2 harness
and L4 report compute unweighted metrics only.

## Version history

| Version | Date | Change |
|---|---|---|
| v0.1-draft | 2026-10-22 | Initial draft: proposed defaults, attention priced above compute |

## 1. The objective function (ROADMAP.md §9, quoted)

**WT-1.** Maximize `accepted_work − human_repair_cost − attention_cost −
financial_cost − loop_penalty − latency_penalty`, subject to: no
unauthorized consequential action, no stale-state substitution, no hidden
failure, no evidence omission. (A cheap wrong answer is not optimal.)

**WT-2.** The six terms are in different units (artifacts, minutes,
interruptions, cost units, events, seconds). Weights must therefore be
per-unit prices, not bare scalars. The table below proposes the units
and the default price for each.

## 2. Proposed weight table — FOR HIS SIGNATURE

| # | Term | Unit | Proposed default weight (per unit) | Rationale for the default |
|---|---|---|---|---|
| WT-3 | `accepted_work` | per accepted artifact | +1.0 (numeraire) | the thing being maximized; everything else is priced against it |
| WT-4 | `human_repair_cost` | per minute of his repair time | −5.0 | repair is his time spent fixing — priced at 5× an artifact's value per minute, because a minute of repair is a minute not spent on the work |
| WT-5 | `attention_cost` | per interruption | −10.0 | **attention priced above compute** — one interruption costs ten artifacts' worth; the router's whole purpose is to not waste the thing it measures |
| WT-6 | `financial_cost` | per cost unit | −1.0 | one-to-one with the artifact numeraire; API spend is real but cheap relative to his time |
| WT-7 | `loop_penalty` | per detected loop event | −8.0 | loops burn attention and compute together; priced near attention |
| WT-8 | `latency_penalty` | per second beyond the task's stated budget | −0.1 | latency is felt, not priced — a tenth of an artifact per second over budget |

**WT-9.** The proposed weighted objective:

`score = 1.0·accepted_work − 5.0·human_repair_minutes − 10.0·interruptions
− 1.0·cost_units − 8.0·loops − 0.1·latency_over_budget_seconds`

**WT-10.** The numbers above are proposals, not measurements. He may
ratify, override per weight, or replace the table. Until then, WT-9 is
not computed anywhere — the harness and report stay unweighted.

## 3. What the weights change (when signed)

**WT-11.** When (and only when) he signs, the L2 harness gains a
`--weighted` mode computing WT-9 per policy, and the L4 report adds a
weighted comparison table beside the unweighted one. The unweighted
tables remain — the weights are a value judgement layered over
measurement, never a substitute for it.

## Cross-references

- `router-policy-spec.md` — the policies compared.
- `decision-log-schema.md` — where the labels that feed WT-9 live.
- `experiment-protocol.md` EP-5 — the unweighted-only rule.
