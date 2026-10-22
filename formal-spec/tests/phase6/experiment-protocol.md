# Experiment Protocol

**Status:** v0.1-draft. Written 2026-10-22 under Phase 6 (Router Optimality),
on HgX's word ("Run the work layers", 2026-10-22 ~12:53 ET).
**Sources:** ROADMAP.md §9 (stages, quoted); `tests/PHASE-6-PLAN.md`;
`tests/PHASE-6-OPEN-QUESTIONS.md` Q1/Q3 (2026-10-22 ~12:47–12:49 ET).
**Gate status:** stages 1–2 are authorized now (Q1). Stage 3 is NOT
designed as trials — only the eligibility framework below, which is
**PROPOSED — FOR HIS LINE-BY-LINE RATIFICATION** (Q3). No live trial
exists on this protocol's authority alone.

## Version history

| Version | Date | Change |
|---|---|---|
| v0.1-draft | 2026-10-22 | Initial draft: stages 1–2 protocol, stage 3 eligibility framework, stage 4 method |

## Stage 1 — Shadow logging (EP-1)

**EP-1.** The router already logs every consultation (shadow mode, the
default). Stage 1 extends those log lines with the outcome labels of
`decision-log-schema.md` DL-2, labeled after the fact per DL-3.

**EP-2.** Volume target (honest): there is no volume target. The corpus
today is one entry. Stage 1 accumulates labels as work happens; the
replay harness reads whatever is there. Stage 4 is aspirational until
the labeled corpus has real volume (see EP-8).

## Stage 2 — Offline replay (EP-3)

**EP-3.** The L2 replay harness (`layer2/`) replays each logged decision
through the alternate policies of `router-policy-spec.md` RP-8a…RP-8c
(unconstrained, cache-only, local heuristic) — plus the Jev-ready
interface of RP-8d, which is never called without his approval.

**EP-4.** For each replayed decision, the harness records what each
policy *would have* recommended, then computes the ten roadmap metrics
per policy: accepted work rate; human repair cost; cost per accepted
artifact; latency; loop rate; escalation precision/recall; false denial
rate; stale-source error rate; attention cost; evidence completeness.

**EP-5.** All stage-2 comparisons are **unweighted** — raw metric tables
only. The weighted objective function waits for his signature on the
weight table (`weight-table.md`, Q4). The report states plainly what
the weights will change when signed.

## Stage 3 — NOT designed; eligibility framework only (EP-6)

Per Q1 (2026-10-22 ~12:47 ET): stage 3 live trials happen only later, on
his word, per task class. What this protocol provides now is the
eligibility boundary, **proposed, for his line-by-line ratification**
(Q3). No class below is eligible until he says so.

**EP-6a — Proposed eligible (low-risk, read-only, no external
visibility):** single `browser.search` discovery lookups; file reads;
memory/context lookups; cache-preferred fetches of already-known
artifacts.

**EP-6b — Absolutely excluded (proposed):** anything consequential —
send, spend, publish, delete; anything touching a custody doctrine —
money (Money Bot), calendar/email/tasks (Tickler Bot), health (Dr Bot,
sealed), food (Food Bot), research (Research Bot, sealed lab), live
location (the eye in the sky, never named); anything with external
visibility (posts, messages, published pages); anything requiring his
approval (the trial must never consume the approval it is measuring).

**EP-6c.** Even after ratification, stage 3 requires a separate explicit
order naming the task class. This protocol never self-authorizes a
trial.

## Stage 4 — Statistical evaluation (EP-7)

**EP-7.** The method, when the corpus warrants it: per-policy acceptance
rate, cost per artifact, repair rate, loop rate, latency, attention
interruptions; **Bayesian estimation for small samples** (roadmap,
quoted) — credible intervals on each metric, priors stated in the
report, not hidden.

**EP-8.** Honest status: with a labeled corpus of one entry (today),
stage 4 is a method on paper, not a result. The L4 report marks every
comparison "insufficient volume" where the intervals would be
meaningless. No credible interval is ever presented from an empty
corpus.

## Cross-references

- `router-policy-spec.md` — the policies replayed.
- `decision-log-schema.md` — the labels stage 1 writes.
- `weight-table.md` — the gated weighted comparison.
- `layer2/` — the stage-2 replay harness.
