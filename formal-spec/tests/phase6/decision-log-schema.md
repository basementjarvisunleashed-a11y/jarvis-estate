# Decision Log Schema (with Outcome Labels)

**Status:** v0.1-draft. Written 2026-10-22 under Phase 6 (Router Optimality),
on HgX's word ("Run the work layers", 2026-10-22 ~12:53 ET).
**Sources:** ROADMAP.md §9 (outcome-label fields, quoted);
`~/workspace/custom-skills/local-usage-router/SKILL.md` (current logging,
quoted); `tests/PHASE-6-OPEN-QUESTIONS.md` Q5 (2026-10-22 ~12:52 ET:
propose placement in L1, he ratifies).
**Custody status:** the placement, readers, and egress rules below are
**PROPOSED — FOR HIS RATIFICATION**. Nothing here is the rule until he
says so.

## Version history

| Version | Date | Change |
|---|---|---|
| v0.1-draft | 2026-10-22 | Initial draft: existing fields + outcome labels, proposed custody line |

## 1. The existing log record (DL-1)

Today, every consultation appends one JSON line to
`~/workspace/usage-router/logs/router-YYYY-MM-DD.jsonl` (skill doc,
quoted): `{ts, mode, state, recommendation, action_taken, note}`. In
shadow mode, `action_taken` records what normal judgment did instead.

Field definitions:

| Field | Type | Meaning |
|---|---|---|
| `ts` | ISO-8601 with offset | consultation time |
| `mode` | `shadow` \| `active` | router mode at consultation |
| `state` | object (RP-5 of router-policy-spec.md) | the compact decision state |
| `recommendation` | action (RP-6) | the router's answer |
| `action_taken` | action (RP-6) | what was actually done |
| `note` | string | free-text context |

## 2. The outcome labels (DL-2)

ROADMAP.md §9, stage 1, quoted: extend router logs with outcome labels
(outcome, human_repair, repair_time_minutes, cost_units,
latency_seconds, attention_interruptions, evidence_complete).

| Label | Type | Meaning |
|---|---|---|
| `outcome` | `accepted` \| `repaired` \| `rejected` \| `unknown` | what became of the work the decision enabled |
| `human_repair` | boolean | a human had to repair the result |
| `repair_time_minutes` | number ≥ 0 | minutes of human repair, 0 if none |
| `cost_units` | number ≥ 0 | cost units consumed by the work |
| `latency_seconds` | number ≥ 0 | wall-clock seconds for the work |
| `attention_interruptions` | integer ≥ 0 | times HgX was pulled in |
| `evidence_complete` | boolean | the evidence packet was complete |

**DL-3.** Labeling method (honest statement): outcome labels are assigned
after the fact — by Jarvis's post-hoc judgment on the record, or by HgX
directly. There is no automatic labeler. The labels are a claim about
what happened, written into the log; the comparison report treats them
as measured-with-method, not as ground truth. (Open point P6-OP-1.)

**DL-4.** An unlabeled decision (the common case today) carries no
outcome labels and is **excluded from outcome metrics**, counted only in
decision metrics. The harness does not invent labels.

## 3. Proposed placement, readers, egress — FOR HIS RATIFICATION (DL-5)

**DL-5a — Location (proposed):** the outcome labels ride on the same
JSONL lines as the decisions, in the existing directory
`~/workspace/usage-router/logs/`. One file, one record — no sidecar to
drift out of sync. **RATIFIED 2026-10-22 ~13:18 ET.**

**DL-5b — Readers (proposed):** Jarvis (the working room) only. No other
bot, chat, worker, or external system reads these logs — the labels are
a diary of his attention, and the custody doctrines say who may hold
what.

**DL-5c — Egress (proposed):** nothing leaves the estate. The single
exception: the compact decision state of RP-5 — and only that, no names,
no message contents, no PII — may be sent to the Jev backend, and only
with his explicit Jev approval (Q2). Outcome labels never leave the
estate under any policy in this phase.

**DL-5d.** Until he ratifies, DL-5a…DL-5c are proposals, and the logs
stay exactly as they are today (skill-doc behavior, Jarvis-only by
standing practice).

## Cross-references

- `router-policy-spec.md` — RP-5 decision state, RP-8 policies.
- `experiment-protocol.md` — stage 1 labeling workflow.
- `weight-table.md` — how labels feed the objective function.
