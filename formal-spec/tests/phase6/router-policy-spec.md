# Router Policy Specification

**Status:** v0.1-draft. Written 2026-10-22 under Phase 6 (Router Optimality),
on HgX's word ("Run the work layers", 2026-10-22 ~12:53 ET).
**Sources:** ROADMAP.md §9 (quoted verbatim where noted);
`~/workspace/custom-skills/local-usage-router/SKILL.md` (the live router —
described exactly as it is, never redesigned);
`tests/PHASE-2-ROUTER-DEFERRAL.md` (INV-R2/R3/R4 deferred here by design);
`tests/PHASE-6-PLAN.md`; `tests/PHASE-6-OPEN-QUESTIONS.md` (all five answers,
2026-10-22 ~12:47–12:52 ET).
**Normative note:** `spec/router-policy.md` is the future normative location
for this contract (per the Phase 2 deferral record). This document is the
v0.1 draft; it does not write into `spec/` — ratified dirs are read-only.

## Version history

| Version | Date | Change |
|---|---|---|
| v0.1-draft | 2026-10-22 | Initial draft: six policies, seven-rule local policy as-is, guardrails verbatim, INV-R1…R5 mapping |

## 1. What the router is

**RP-1.** The usage router is a gate, not a brain. It answers one question
before expensive work begins: *is this the cheapest reliable path to the
result?* HgX's approvals and the estate's existing rules still govern
everything consequential.

**RP-2.** The router consults **before**: live-browser work / deep research,
retrying a failed approach, spawning a subagent, loading several
specialized skills for a single task. It does **not** consult for:
answering from memory or context, a single `browser.search`, reading files,
or anything HgX asked to do directly and simply. (Skill doc, quoted.)

**RP-3.** Kill switch — checked first, every time. The router is skipped
entirely and work proceeds normally when `~/workspace/usage-router/
config.json` has `"enabled": false`, or when HgX says `bypass router`,
`no router`, or `skip the gate`. (Skill doc, quoted.)

**RP-4.** Modes. **Shadow** (default): evaluate, log the recommendation,
continue on normal judgment; the log is the product. **Active**: honor the
router's action. HgX flips modes by saying so ("router active",
"router shadow"). Current mode lives in `config.json`. (Skill doc, quoted.)

## 2. The decision state (RP-5)

The compact state built before every decision, exactly as the skill doc
defines it:

```json
{
  "goal": "what HgX wants",
  "kind": "chat|lookup|research|browser|coding|write|account",
  "cached_artifact": false,
  "cached_note": "freshness and scope, if any",
  "prior_error": "last error, if retrying",
  "same_error_count": 0,
  "sources_found": 0,
  "constraints": "limits that apply"
}
```

## 3. The local decision policy — seven rules, as they are (RP-6)

First match wins. Quoted from the skill doc, not paraphrased:

1. **Irreversible actions escalate, always.** Anything that sends, spends,
   publishes, or deletes goes to HgX regardless of mode. The router never
   approves consequences.
2. **Retry budget.** Same operation, same error: at most **2 retries**, then
   `escalate` (try a fundamentally different approach, or ask HgX).
   Increment `same_error_count` per identical failure.
3. **Loop detection.** The same action proposed 3 times without measurable
   progress → `deny`, escalate to HgX with what was tried.
4. **Cache preference.** If a cached artifact or note answers the goal and
   is fresh → `use-cache`. Never re-fetch what is already known.
5. **Subagent gating.** Spawn only when the work is multi-step,
   independent of the chat reply, and long-running. Quick or single-step
   work → `deny`, do it directly.
6. **Browser gating.** `browser.search` for discovery is cheap — proceed.
   The live browser / deep research only when the answer needs current
   state (prices, availability, account data, live pages). Curiosity
   browsing → `deny`.
7. **Deferral.** If the goal is vague and the cost is high → `defer`: ask
   HgX one focused question first.

Actions: `proceed` | `use-cache` | `defer` | `escalate` | `deny`.

## 4. Router guardrails (ROADMAP.md §9, verbatim)

**RP-7.** The router must never: approve consequential action; override
approval boundaries; authorize spending/sending/deletion; hide failures;
suppress evidence; substitute stale data; become a second orchestrator.

## 5. The six policies (RP-8)

The comparison policies of ROADMAP.md §9, defined as the replay harness
implements them. Policies 1–3 and 5 are evaluated in this phase; policy 4
is built Jev-ready but not run (Q2: only on his explicit approval);
policy 6 is later.

**RP-8a — Unconstrained orchestration.** The no-gate baseline. Every
consultation answers `proceed`. This is the "what if the router didn't
exist" control arm — expensive paths are never gated, never cached, never
deferred.

**RP-8b — Cache-only.** The cache-preference baseline. Rule RP-6.4 applied
whenever a fresh cached artifact or note answers the goal (`use-cache`);
every other decision answers `proceed` directly. This is a *definitional
choice of this spec* (see P6-OP-4): cache-only isolates the value of
caching from the value of gating.

**RP-8c — Local heuristic.** The seven rules of RP-6 applied in order,
first match wins. This is the live router as it runs today (shadow mode,
`"backend": "local"`).

**RP-8d — TypeSafe Jev backend.** The harness exposes the backend as a
pluggable interface: the compact decision state of RP-5 is the only
payload, and the backend's answer replaces the local recommendation.
**Not evaluated in this phase.** Q2's answer (2026-10-22 ~12:48 ET):
evaluate Jev only on HgX's explicit approval — the harness is built
Jev-ready, the trial waits for his word and his key. No API spend, no
data egress, no endpoint called, until then. (Skill doc: he creates the
key himself via the Secure Vault flow; any backend failure falls back to
local immediately, logged.)

**RP-8e — Hybrid.** Defined as a policy shape for a later trial: local
policy first; on `defer` or `escalate` outcomes, consult the backend
before acting. Not evaluated without the Jev approval (Q2).

**RP-8f — Learned policy (later).** Out of scope for this phase's
harness. Named here only because the roadmap names it.

## 6. INV-R1…R5 — the Phase 2 deferral, owned (RP-9)

`tests/PHASE-2-ROUTER-DEFERRAL.md` deferred INV-R2/R3/R4 here by design;
INV-R1 and INV-R5 are companions. Each invariant, its rule embodiment,
and its Phase 6 proof vehicle:

| Invariant (ROADMAP.md §5, verbatim) | Rule embodiment | Proof vehicle |
|---|---|---|
| **INV-R1:** router recommends path only, never approves consequence | RP-6 rule 1 (irreversible actions escalate, always) + RP-7 guardrail | L2 replay: zero consequential approvals across the corpus |
| **INV-R2:** repeated identical error triggers escalation or path change | RP-6 rule 2 (retry budget, ≤2 retries then escalate) | L2 replay: escalation after exactly 2 identical failures |
| **INV-R3:** repeated no-progress action denied | RP-6 rule 3 (3rd no-progress proposal → deny) | L2 replay: denial on the 3rd no-progress proposal |
| **INV-R4:** fresh cache may suppress refetch when sufficient | RP-6 rule 4 (use-cache when fresh and sufficient) | L2 replay: no refetch when the cached artifact answers |
| **INV-R5:** router fallback preserves safety if external backend fails | Jev section: any backend failure → local immediately, logged | L2 harness: forced backend failure → local decision, logged fallback |

## 7. Honest limits of this spec

**RP-10.** This spec does not claim the local policy is optimal — that is
the phase's research question, to be answered by measured evidence
(stages 1–2 now, per Q1).

**RP-11.** The real decision-log corpus today is one entry
(`router-2026-10-07.jsonl`, the 2026-10-07 self-test). The replay harness
verifies its machinery against labeled synthetic fixtures and the one
real entry; the comparison report states this plainly. Volume must grow
through stage 1 before stage 4 means anything.

## Cross-references

- `decision-log-schema.md` — the log and outcome-label fields.
- `experiment-protocol.md` — stages 1–2 protocol, stage 3 eligibility
  framework (for his line-by-line ratification).
- `weight-table.md` — proposed weight defaults (for his signature).
- `layer2/` — the replay harness implementing RP-8a…RP-8e.
- `../PHASE-6-OPEN-QUESTIONS.md` — Q1…Q5 answers.
