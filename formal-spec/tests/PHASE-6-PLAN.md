# Phase 6 — Router Optimality — Opening Package

**Status:** v0.1-draft (opening package, not the work). Written 2026-10-22 on
HgX's word ("Close phase five and open up phase six"). The work layers are
gated on his word after the walkthrough.

**Sources:** ROADMAP.md §9 (quoted verbatim throughout); the live router
skill at `~/workspace/custom-skills/local-usage-router/SKILL.md` (described
exactly as it is — never redesigned); `tests/PHASE-2-ROUTER-DEFERRAL.md`
(INV-R2/R3/R4 deferred here by design).

## Objective (ROADMAP.md §9, verbatim)

Turn the router from plausible heuristic into empirically justified control
policy.

## Research question (ROADMAP.md §9, verbatim)

> Under what conditions does the usage router improve accepted work while
> reducing cost, loops, repair, and attention cost?

## Policies to compare (ROADMAP.md §9, quoted)

Unconstrained orchestration; cache-only; local heuristic policy; TypeSafe
Jev backend; hybrid policy; learned policy (later).

## Objective function (ROADMAP.md §9, quoted)

Maximize
`accepted_work − human_repair_cost − attention_cost − financial_cost −
loop_penalty − latency_penalty`, subject to: no unauthorized consequential
action, no stale-state substitution, no hidden failure, no evidence
omission. (A cheap wrong answer is not optimal.)

## Metrics (ROADMAP.md §9, quoted)

Accepted work rate; human repair cost; cost per accepted artifact; latency;
loop rate; escalation precision/recall; false denial rate; stale-source
error rate; attention cost; evidence completeness.

## Experimental design (ROADMAP.md §9, quoted)

- **Stage 1 — Shadow logging** (current state supports this): extend router
  logs with outcome labels (outcome, human_repair, repair_time_minutes,
  cost_units, latency_seconds, attention_interruptions, evidence_complete).
- **Stage 2 — Offline replay**: replay historical decisions through
  alternate policies.
- **Stage 3 — Controlled live trials**: low-risk tasks under different
  policies; random assignment for eligible tasks only; never randomize
  consequential actions.
- **Stage 4 — Statistical evaluation**: acceptance rate, cost per artifact,
  repair rate, loop rate, latency, attention interruptions; Bayesian
  estimation for small samples.

## Router guardrails (ROADMAP.md §9, verbatim)

The router must never: approve consequential action; override approval
boundaries; authorize spending/sending/deletion; hide failures; suppress
evidence; substitute stale data; become a second orchestrator.

## Deliverables (ROADMAP.md §9, quoted)

Router policy specification; decision log schema; outcome label schema;
experiment protocol; policy comparison report; cost-attention-acceptance
dashboard; doctoral analysis chapter.

## Exit criteria (ROADMAP.md §9, verbatim)

"Router decisions linked to outcomes; local, cache-only, and unconstrained
baselines compared; Jev evaluated if approved; value supported by measured
evidence."

## Layers and gates

- **L1 — Policy spec.** The normative router policy contract
  (`spec/router-policy.md` — a Phase 6 artifact per the deferral record),
  decision-log schema, outcome-label schema, and the experiment protocol.
  States exactly what the router is: a gate, not a brain.
- **L2 — Replay harness.** Deterministic harness replaying logged router
  decisions through the alternate policies (local, cache-only,
  unconstrained), producing the policy comparison on measured history.
- **L3 — Live-trial design.** ONLY if HgX approves Stage 3 (per task class —
  see Q1/Q3 in the open questions): the trial protocol for eligible
  low-risk tasks. Not built by default; this phase does not randomize
  anything consequential on its own authority.
- **L4 — Comparison report + dashboard.** The policy comparison report and
  the cost-attention-acceptance dashboard, both resting on measured
  evidence only.

No layer advances without his word. Nothing here is ever called optimal
until the measurements say so.

## Head-start note — honest accounting (2026-10-22)

Phase 6 formalizes and evaluates what already runs. The estate's usage
router is live today, in **shadow mode**, under the local-usage-router
skill. Described exactly as the skill doc states it (never redesigned):

- **Purpose:** stop expensive work before it starts. A gate, not a brain —
  HgX's approvals and the estate's existing rules still govern everything
  consequential. Prefer the cheapest reliable path, never a cheap wrong one.
- **When to consult:** before live-browser work/deep research, retrying a
  failed approach, spawning a subagent, loading several specialized skills.
  Never for memory/context answers, single `browser.search`, file reads, or
  anything HgX asked to do directly and simply.
- **Kill switch (checked first, every time):** skip the router entirely when
  `~/workspace/usage-router/config.json` has `"enabled": false`, or when HgX
  says `bypass router` / `no router` / `skip the gate`.
- **Modes:** shadow (default) — evaluate, log the recommendation, continue
  on normal judgment; active — honor the router's action. HgX flips modes
  by saying so ("router active", "router shadow").
- **Decision state:** goal, kind, cached_artifact, cached_note,
  prior_error, same_error_count, sources_found, constraints.
- **Local decision policy (first match wins):** (1) irreversible actions
  escalate, always — the router never approves consequences; (2) retry
  budget — same operation, same error: at most 2 retries, then escalate;
  (3) loop detection — the same action proposed 3 times without measurable
  progress → deny, escalate to HgX; (4) cache preference — fresh cached
  artifact that answers the goal → use-cache, never re-fetch what is known;
  (5) subagent gating — spawn only for multi-step independent long-running
  work, otherwise do it directly; (6) browser gating — `browser.search` is
  cheap, the live browser / deep research only when current state is needed;
  (7) deferral — vague goal plus high cost → ask HgX one focused question.
  Actions: proceed | use-cache | defer | escalate | deny.
- **Logging:** every consultation appends one JSON line to
  `~/workspace/usage-router/logs/router-YYYY-MM-DD.jsonl`:
  `{ts, mode, state, recommendation, action_taken, note}`. In shadow mode,
  `action_taken` records what normal judgment did instead. HgX may ask
  "show me the router log" any time.
- **Optional Jev backend:** only on his explicit ask — he creates the key
  himself, stored via the Secure Vault flow (never in chat, never in a
  file), sends only the compact decision state (no names, no message
  contents, no PII); any backend failure falls back to the local policy
  immediately, logged. Until then `"backend": "local"`.

**The Phase 2 dispositions belong here by design**
(`tests/PHASE-2-ROUTER-DEFERRAL.md`, on his standing doctrine): INV-R2
(repeated identical error triggers escalation or path change), INV-R3
(repeated no-progress action denied), INV-R4 (fresh cache may suppress
refetch when sufficient) are uncovered by design in Phase 2 because the
router is estate runtime, not a contract artifact. Their behavioural proof
— against the real router, not a model — is Phase 6's programme. Companion
invariants INV-R1 (router recommends path only, never approves consequence)
and INV-R5 (router fallback preserves safety if external backend fails)
likewise get their full runtime proof here.

## Session log

- 2026-10-22 ~12:44 ET: Phase 6 opened on HgX's word ("Close phase five
  and open up phase six"). This opening package is the Phase 6 plan plus
  the open questions. The work layers open on his word after the
  walkthrough.
- Standing rules carried forward: never advance a phase without his
  explicit consent; ratified files untouched; no email/post/purchase
  without approval; the research pipeline stays sealed; the website
  stays as-is (logs only) per his 2026-10-21 hands-off order; the
  doctrines are described, never redesigned; the router is a gate, not
  a brain — it never approves consequences.
