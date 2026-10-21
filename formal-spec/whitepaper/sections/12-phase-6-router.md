# Phase 6 — Router Optimality: From Plausible Heuristic to Measured Policy

*Paper IV, §12. Companion to the Phase 6 specification in the J.A.R.V.I.S. remediation roadmap. This section stands on the measured-evidence theme of the programme — the doctrine that claims must be earned by observation — without re-arguing the consistency (§9), idempotency (§10), or security (§11) machinery. Those phases supply the constraints; this phase supplies the experiment.*

## 12.1 The Research Question, Stated and Unpacked

> Under what conditions does the usage router improve accepted work while reducing cost, loops, repair, and attention cost?

"Improve accepted work" needs an operational definition before it can be measured, because "the router helped" is otherwise a feeling. In this phase it means: **a higher rate of work items reaching `completed` with their acceptance criteria passed and evidence attached (INV-C1), at equal or lower human repair cost, attention cost, and financial cost, with fewer loops and no increase in latency beyond the operator's tolerance** — all measured against the baselines in §12.2, on comparable tasks, with the analysis pre-registered (§12.5, Stage 4).

"Under what conditions" is the question's real content. The router is not hypothesized to be uniformly better; it is hypothesized to be better *for certain task classes* — the cache-friendly, the routine-shaped, the previously-seen — and possibly worse for others (novel tasks where a cache hit is a trap, ambiguous tasks where the cheapest path skips verification). The experiment's job is to draw that map: which tasks, which policies, which trade-offs. A router policy justified by measured outcomes, not intuition, is the phase's exit criterion — and "not intuition" cuts both ways, against both the router's advocates and its skeptics.

## 12.2 The Six Policies

**Unconstrained orchestration.** The null hypothesis in its most expensive form: the orchestrator plans and executes with every tool available, no routing gate, no cache consultation, full fan-out. *Strengths:* maximal capability on novel tasks; no routing overhead; the ceiling against which every policy's *quality* is measured. *Failure modes:* cost explosion on routine tasks (the §11.4 cost-explosion threat, realized); loops unbounded by any budget; attention cost unmeasured and therefore unmanaged. This policy is not a straw man — it is the estate's behavior before the router existed, and the comparison must be honest about what was lost as well as gained.

**Cache-only.** Answer from cache or decline: if a prior accepted artifact matches the brief sufficiently, serve it; otherwise escalate to the operator without attempting fresh work. *Strengths:* near-zero cost and latency on repeated tasks; the morning briefing that barely changed overnight is the canonical win. *Failure modes:* stale-state substitution dressed as efficiency — serving yesterday's answer to today's question (the exact failure §9.2's freshness rules and §11.5's stale-state narrative forbid at the consequence boundary); false confidence on tasks that *look* repeated but aren't. Cache-only is safe only where the freshness contract is enforced, which is why it is a policy *within* the governance model, not an alternative to it.

**Local heuristic policy.** The current production router: a local, no-external-API decision gate using hand-written rules — consult the cache first, bound retries (2 identical failures, then escalate), guard loops (3 repeats, then stop), prefer the cheapest sufficient path, escalate on uncertainty. Shadow mode by default; kill switch always available. *Strengths:* no data egress, no external dependency, predictable behavior, every rule inspectable by the operator. *Failure modes:* heuristics are brittle at the edges — the rule that handles 95% of briefs misroutes the 5% that matter most; hand-written thresholds drift out of calibration as the task mix changes; "prefer the cheapest sufficient path" degrades into "prefer the cheapest path" under pressure, which is how a cheap wrong answer gets recommended (see §12.3).

**TypeSafe Jev backend.** The optional external routing backend: task features are sent to the Jev service, which returns a recommended path with a confidence score; credentials held only in the Secure Vault, never in chat. *Strengths:* potentially better routing on novel tasks through a model trained on broader data; confidence scores enable calibrated escalation. *Failure modes:* data egress (task content leaves the estate — the privacy cost is real and must appear in the objective function); external dependency (the backend's outage becomes the estate's outage — INV-R5 requires the fallback to preserve safety); the confidence score is only as calibrated as the vendor's evaluation, which the estate cannot inspect. Evaluation of this policy requires the operator's explicit approval — it is never a default.

**Hybrid policy.** Local heuristic as the gate, Jev as the consultant: routine-shaped tasks stay local; novel or high-uncertainty tasks consult the backend; the local policy retains veto and the kill switch covers both. *Strengths:* egress only where the expected gain justifies it; graceful degradation to local-only when the backend is unreachable. *Failure modes:* complexity — two policies means two failure surfaces and an arbitration rule between them that is itself a heuristic; the "expected gain" threshold for consulting the backend is another hand-tuned number awaiting measurement.

**Learned policy (later).** A policy trained on the estate's own labeled outcomes — the shadow logs of §12.5, Stage 1 — to predict the best path per task. *Strengths (projected):* calibrated to the operator's actual task mix and preferences rather than anyone's priors; improvable with data. *Failure modes (anticipated):* needs the labeled data this phase produces — it cannot be evaluated until Stage 1–2 have run; risks overfitting to a small, idiosyncratic task sample (one operator's life is a small dataset); a learned policy that drifts is harder to interrogate than a hand-written rule. It is listed so the experiment is designed to produce its training data, not so it can be compared today.

## 12.3 The Constrained Objective Function

```
Maximize:  accepted_work
           − human_repair_cost
           − attention_cost
           − financial_cost
           − loop_penalty
           − latency_penalty

Subject to: no unauthorized consequential action
            no stale-state substitution
            no hidden failure
            no evidence omission
```

**Each term, and why it is there.** *Accepted work* is the objective's north star: work items completed with acceptance passed and evidence attached — not work *attempted*, not work *claimed* (§11.5, subagent deception). *Human repair cost* is subtracted because a policy that produces work the operator must then fix has not produced value; it has produced homework. Repair is measured in operator minutes (§12.4), and it is the term that punishes the plausible-but-wrong artifact most directly. *Attention cost* is subtracted because interruptions are depletable (§11.1, asset 1): a policy that buzzes the wrist forty times to save ten cents has made a bad trade, and the objective function must be able to say so. *Financial cost* is subtracted in the estate's own cost units — API spend, compute, and any external fees. *Loop penalty* exists because loops are the failure mode that converts bounded cost into unbounded cost; the penalty is superlinear by design, so that a policy which occasionally loops badly is punished more than one which is consistently slightly slow. *Latency penalty* exists because the operator's time has a price even when he isn't repairing anything — waiting is a cost, and a policy that is cheap but glacial is not optimal.

**Each constraint, and why it is a constraint rather than a term.** A term is tradable: the optimizer may accept more latency for less cost. A constraint is not tradable: no amount of accepted work justifies an unauthorized consequential action. *No unauthorized consequential action* is a constraint because safety is not a preference to be weighted — it is the precondition for the estate's existence (Paper I's doctrine chain). *No stale-state substitution* is a constraint because a decision made on false facts is not a cheaper decision; it is a different, wrong decision (§11.5). *No hidden failure* is a constraint because an unobserved failure is the one failure the system cannot learn from or compensate for (§10.6). *No evidence omission* is a constraint because evidence is what makes the estate's claims checkable — including the claims of this very experiment (Phase 7). Putting any of these in the objective as a subtractable term would license the optimizer to trade them away at a sufficient price. There is no sufficient price.

**The key sentence.** *A cheap wrong answer is not optimal.* The objective function is built to reject exactly one seductive policy: the one that minimizes every cost term by producing fast, cheap, confident artifacts that the operator must then repair or discard. Such a policy scores brilliantly on cost and latency and fails the only term that matters first — accepted work — while accumulating human repair cost that wipes out its savings.

**Worked numeric example.** Two policies route one hundred comparable briefing tasks over a month. Units are normalized: one unit of accepted work = 1.0; repair, attention, and financial costs in operator-minute-equivalents and cost units converted at the estate's standard rate; penalties as defined in §12.4.

| Term | Policy A (local heuristic) | Policy B (aggressive cache-only) |
|---|---|---|
| accepted_work | 82.0 | 61.0 |
| − human_repair_cost | −14.0 | −31.0 |
| − attention_cost | −6.0 | −11.0 |
| − financial_cost | −9.0 | −2.0 |
| − loop_penalty | −3.0 | −1.0 |
| − latency_penalty | −4.0 | −1.0 |
| **Objective value** | **46.0** | **15.0** |
| Constraints | all satisfied | **VIOLATED: stale-state substitution** (3 tasks served expired briefs as current) |

Policy B is cheaper on every cost term — one-seventh the financial cost, a quarter the latency penalty — and it is not optimal. It is not even eligible: three tasks violated the stale-state constraint, which disqualifies the policy regardless of its score. And even setting the violation aside, B's objective value (15.0) trails A's (46.0), because B's cheap answers required thirty-one units of human repair — the operator re-doing work the router claimed was done. The example is illustrative, not empirical; the experiment in §12.5 exists to replace these numbers with measured ones. But the shape of the lesson is the point: *the objective function must be able to prefer the expensive right answer over the cheap wrong one, and the constraints must be able to disqualify a policy that no score can redeem.*

## 12.4 Metric Definitions

Eleven metrics. Each is defined operationally — numerator, denominator, observation window — because a metric without these is an aspiration.

1. **Accepted work rate.** *Numerator:* work items reaching `completed` with acceptance passed and evidence attached. *Denominator:* work items accepted (entered `accepted` state). *Window:* per policy arm, per task class, over the trial period. Excludes items cancelled by operator choice — cancellation is not failure.

2. **Human repair cost.** *Numerator:* operator minutes spent correcting, redoing, or clarifying a policy-routed artifact. *Denominator:* accepted work items in the arm. *Window:* measured within 7 days of completion (repair after that is attributed to changing requirements, not routing). Unit: minutes; reported as mean and distribution, not just mean.

3. **Cost per accepted artifact.** *Numerator:* total financial cost units (API, compute, external fees) consumed by the arm. *Denominator:* accepted work items. *Window:* trial period. This is the efficiency metric; it is meaningless without the repair cost beside it (§12.3's key sentence).

4. **Latency.** *Numerator:* seconds from brief acceptance to completed-or-escalated. *Denominator:* work items in the arm. *Window:* trial period. Reported as median and 95th percentile — the operator experiences the tail, not the mean.

5. **Loop rate.** *Numerator:* work items triggering the loop guard (3 repeats) or retry budget (2 identical failures). *Denominator:* work items in the arm. *Window:* trial period. A loop that the guard catches is still a loop; the metric counts the trigger, not the escape.

6. **Escalation precision.** *Numerator:* escalations where the operator's intervention changed the outcome (the escalation was *necessary*). *Denominator:* all escalations. *Window:* trial period. High precision means the router escalates only when it should.

7. **Escalation recall.** *Numerator:* cases where operator intervention was necessary and the router escalated. *Denominator:* all cases where intervention was necessary (including those found by audit). *Window:* trial period. High recall means the router doesn't silently bungle what it should have escalated. Precision and recall are reported separately because the failure modes differ: low precision wastes attention; low recall causes harm.

8. **False denial rate.** *Numerator:* tasks the router declined or over-escalated that a baseline policy would have completed acceptably. *Denominator:* tasks handled by the arm. *Window:* trial period. The timidity metric — a router that never fails because it never tries is not optimal either.

9. **Stale-source error rate.** *Numerator:* decisions later shown to rest on stale facts (audit-detected). *Denominator:* consequential decisions in the arm. *Window:* trial period, with a 30-day audit tail. Any nonzero value here is also a constraint investigation (§12.3), not just a metric.

10. **Attention cost.** *Numerator:* operator interruptions attributable to the arm — notifications, approval requests, escalations, clarifications. *Denominator:* accepted work items. *Window:* trial period. Weighted by surface: a wrist buzz counts more than a batched iPad review, because interruption is not fungible (Paper III's notification discipline).

11. **Evidence completeness.** *Numerator:* completed items whose evidence packets pass the schema and acceptance checks on first audit. *Denominator:* completed items. *Window:* trial period. The metric that guards the experiment's own integrity: a policy that completes work without evidence is manufacturing the appearance of accepted work.

## 12.5 Experimental Design: Four Stages

### Stage 1 — Shadow Logging

The current estate already supports this: the router runs in shadow mode, logging its recommendations alongside the path actually taken. Stage 1 extends the log schema with outcome labels, so that recommendations can later be joined to results. The extended JSON log record, annotated field by field:

```json
{
  "ts": "2026-10-08T20:31:00Z",        // decision time; joins to work-item history (§9.4)
  "work_id": "wi-2026-10-08-118",      // which work item this decision served
  "policy": "local-heuristic",         // policy name + version: "local-heuristic/v3"
  "policy_version": "v3",              // version pinned; comparisons are version-to-version
  "task_class": "briefing-daily",      // task class, from the controlled vocabulary (§12.5 Stage 3)
  "task_features": {                   // features the policy saw: novelty, cache age, estimated cost
    "novelty": 0.2,
    "cache_age_hours": 14.0,
    "estimated_cost_units": 3.0
  },
  "recommended_path": "cache-refresh", // what the router recommended
  "confidence": 0.81,                  // router's self-reported confidence, if any
  "path_taken": "cache-refresh",       // what actually happened (may differ: operator override, kill switch)
  "override": false,                   // true if the operator or orchestrator overrode the recommendation
  "outcome": "accepted",               // OUTCOME LABEL: accepted | repaired | escalated | failed | cancelled
  "human_repair": false,               // OUTCOME LABEL: did the operator have to fix the artifact?
  "repair_time_minutes": 0,            // OUTCOME LABEL: minutes of repair, 0 if none
  "cost_units": 2.7,                   // OUTCOME LABEL: actual financial cost consumed
  "latency_seconds": 41,               // OUTCOME LABEL: acceptance-to-completion seconds
  "attention_interruptions": 1,        // OUTCOME LABEL: wrist buzzes, approvals, escalations caused
  "evidence_complete": true,           // OUTCOME LABEL: evidence packet passed first audit
  "loop_triggered": false,             // OUTCOME LABEL: loop guard or retry budget fired
  "constraint_flags": []               // OUTCOME LABEL: any of the four constraints touched — must be empty
}
```

Every field with an OUTCOME LABEL is written after the fact — by the orchestrator observing the work item's lifecycle, not by the router grading itself. The router that scores its own homework is the experiment's first confound, and the schema prevents it structurally: recommendation fields are written at decision time, outcome fields at completion time, by different writers.

### Stage 2 — Offline Replay

Historical shadow logs are replayed through alternate policies: for each logged decision, each candidate policy is asked what it *would have* recommended given the same task features, and the recommendation is scored against the observed outcome. The evaluation protocol is four questions, asked in order:

**Q1 — Choice.** *What would the alternate policy have recommended, given exactly the task features the original policy saw?* No peeking at the outcome; the replay harness supplies features only. A policy that cannot answer from features alone is not replayable and is excluded from this stage.

**Q2 — Outcome delta.** *Given the observed outcome of the path actually taken, would the alternate recommendation plausibly have changed the outcome class (accepted / repaired / escalated / failed)?* Scored conservatively: the alternate wins the point only if its recommended path dominates on the observed evidence (e.g., the taken path looped and the alternate would have served cache). Ties go to the observed path — replay must not manufacture victories.

**Q3 — Cost delta.** *What is the estimated difference in cost, latency, and attention between the recommended and taken paths?* Estimated from the policy's historical averages on the same task class, not from imagination. This is where cache-only's cheapness and the heuristic's overhead are quantified against each other on identical tasks.

**Q4 — Robustness.** *Does the alternate policy's advantage (or disadvantage) hold across task classes, or is it concentrated in one class?* A policy that wins overall by dominating one frequent class while failing a rare-but-consequential class is not better — it is lucky about the task mix. Q4 is the question that prevents the experiment from recommending a policy that is optimal on average and dangerous at the margins.

Replay's known limitation is stated upfront: it measures *recommendation quality* against observed outcomes, not *causal effect* — the alternate path was never taken, so its true outcome is counterfactual. Stage 3 exists to supply the causality that Stage 2 cannot.

### Stage 3 — Controlled Live Trials

Low-risk tasks are randomly assigned across policy arms, and outcomes are measured with the Stage 1 schema. Three design elements need precise definition.

**Eligibility criteria for low-risk tasks.** A task is eligible for randomized routing if and only if *all* of the following hold: (a) it is non-consequential — no external effect, no publication, no transmission, no state change outside the estate's scratch space; (b) it is reversible — any artifact it produces can be discarded without trace; (c) it requires no approval-path decision — the task never reaches §9.6's seven steps; (d) its bounded cost is below the per-brief cap with 10× headroom (a runaway cannot hurt); (e) its task class has at least 30 historical observations, so the arm comparison has a baseline. Briefings, draft summaries, and cache-refresh reads are the canonical eligible classes. Anything else — anything the operator would notice going wrong — is excluded.

**The five policy arms.** Unconstrained orchestration; cache-only; local heuristic; TypeSafe Jev backend; hybrid. The learned policy is excluded — it does not exist yet, and randomizing tasks to a non-existent arm is not an experiment. Each arm runs the same eligibility filter, the same outcome schema, and the same kill switch.

**Why consequential actions are never randomized.** Random assignment is the experiment's engine and its ethical boundary. Assigning a consequential action — a publication, a send, a deletion — to a policy *for the sake of comparison* would mean deliberately exposing the operator to a worse-than-necessary risk of harm in order to learn something. The estate's doctrine does not permit using the operator as a test subject: the constraint set of §12.3 binds the experiment as well as the policies. Randomization applies only where every arm's worst case is a wasted few minutes and a discarded draft. The trial measures routing quality on safe tasks and *generalizes with stated uncertainty* to the rest — it does not purchase certainty with the operator's safety.

### Stage 4 — Statistical Evaluation

**Comparison metrics.** Arms are compared on the eleven metrics of §12.4, with accepted work rate, human repair cost, and attention cost as the primary trio — the terms the research question names. Cost per accepted artifact and latency are secondary; the remaining six are diagnostic (they explain *why* an arm won or lost) and constraint-adjacent (stale-source errors trigger investigation, not just scoring).

**Small-sample guidance.** The estate has one operator and a modest task volume; the trial will not produce thousands of observations per arm. The analysis is therefore designed for small samples from the start:

- *Bayesian estimation* over null-hypothesis testing: report posterior distributions for each metric's arm difference (e.g., "the probability that the hybrid arm's repair cost is lower than the heuristic's is 0.87"), not p-values. With small samples, the question is never "is the difference significant" but "how large is it plausibly, and how sure are we."
- *Paired task comparisons:* where the same task class recurs (the daily briefing is the same task every day), compare arms on matched pairs rather than pooled means — pairing removes the largest source of variance, which is the tasks themselves.
- *Pre-registered analysis:* the primary trio, the comparison method, and the decision rule ("adopt the hybrid arm for eligible tasks if its posterior probability of lower repair cost exceeds 0.9 with no attention-cost regression") are written down before Stage 3 begins. The analyst does not get to shop for the metric that flatters the preferred policy.
- *What NOT to claim:* no claim of significance from underpowered comparisons; no generalization from eligible (safe, routine) tasks to consequential tasks — the trial's writ does not run there; no causal claim from Stage 2 replay alone; no "the router is optimal" full stop — only "policy P outperformed policy Q on task class C, under these conditions, with this uncertainty." The experiment's credibility depends on the modesty of its claims matching the size of its data.

## 12.6 Router Guardrails: Eight Things the Router Must Never Do

Each with its one-line rationale — the guardrails are constraints (§12.3) restated as prohibitions, because a constraint the engineers cannot recite is a constraint that will be violated.

1. **Never approve a consequential action.** *Rationale:* approval is the operator's exclusive authority (§11.1, asset 2); a router that approves has become a second principal.
2. **Never override approval boundaries.** *Rationale:* the seven-step flow (§9.6) and its failure branches are not routing suggestions; no path recommendation may shorten, skip, or reinterpret them.
3. **Never authorize spending.** *Rationale:* money movement requires the strongest verification and the operator's explicit consent (§10.8); cost optimization must never become cost authorization.
4. **Never authorize sending or deletion.** *Rationale:* external effects are irreversible or near-irreversible (§10.8); the router's writ ends at the consequence boundary.
5. **Never hide failures.** *Rationale:* a hidden failure is the one failure the system cannot learn from, compensate for, or show the operator (§12.3, constraint 3); silent-by-default means silent *operation*, never silent *failure*.
6. **Never suppress evidence.** *Rationale:* evidence is what makes every claim in this paper checkable — including the router's own performance claims (§12.4, metric 11).
7. **Never substitute stale data.** *Rationale:* a decision on false facts is not a cheaper decision but a wrong one (§11.5); freshness is a constraint, not a cost term.
8. **Never become a second orchestrator.** *Rationale:* the single-writer rule (§9.3) is structural; a router that coordinates subagents, accepts briefs, or maintains authoritative state has violated the architecture no matter how well it routes.

(The roadmap's compact list groups spending, sending, and deletion under one item; they are separated here because the rationale differs — money, utterance, and destruction fail differently — while the prohibition is identical.)

## 12.7 Phase 6 Exit Criteria

- [ ] Router decisions are linked to outcomes: every Stage 1 log record carries outcome labels written by the orchestrator, not the router.
- [ ] Local, cache-only, and unconstrained baselines are compared on the eleven metrics, with the analysis pre-registered before live trials.
- [ ] The Jev backend is evaluated if and only if the operator approves: no data egress for experimentation without explicit consent.
- [ ] The router policy's value is supported by measured evidence: the adopted policy is named, its winning conditions are stated, its uncertainty is quantified, and its guardrails are tested — not asserted.
- [ ] Methodology and results published openly: the pre-registered protocol, the labelled decision history (sanitised), and the analysis are released so the router's measured comparison can be re-analysed by anyone — the evaluation is a public experiment, not a private verdict.

## Open Questions

1. **The generalization gap.** Stage 3 randomizes only safe, routine tasks; the router's value proposition includes novel and consequential-adjacent tasks. How far may the trial's findings be generalized, and what additional evidence (structured operator review? expert audit?) would license generalization to tasks the trial cannot touch?
2. **Attention-cost weighting.** Metric 10 weights a wrist buzz above a batched iPad review — but by how much? The weights encode a theory of the operator's attention that is currently asserted, not measured. Whose calibration study sets them?
3. **The cost-unit exchange rate.** The objective function converts operator minutes, API spend, and latency into commensurable units. The exchange rate is a value judgment disguised as arithmetic — who sets it, and how often is it re-examined?
4. **Learned-policy data sufficiency.** Stage 1–2 produce the learned policy's training data as a side effect. How many labeled decisions, across how many task classes, constitute a sufficient training set for one operator's estate — and who decides the policy is ready to join the arms as a sixth?
5. **Pre-registration amendment.** If Stage 3 reveals a flaw in the pre-registered analysis (a metric misdefined, a confound unanticipated), what is the legitimate procedure for amending the registration without destroying its credibility? The protocol needs a stated amendment rule before the trial begins.
6. **Constraint violation as data.** If an arm violates a constraint during trials (a stale substitution, a hidden failure), the arm is disqualified — but the violation is also the most informative event of the trial. How are disqualified-arm data handled in the analysis: excluded entirely, or analyzed separately as failure case studies for Phase 7?
