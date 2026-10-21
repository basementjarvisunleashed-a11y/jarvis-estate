# 14. The Twelve-Month Programme

## 14.1 How This Schedule Is Built

The roadmap offers three pacing options: a 12-week engineering fix (Option A), a 6-month doctoral validation (Option B), and a 12–18 month full PhD track (Option C). This section maps a concrete twelve-month programme from Option B extended to a full year — the middle path, given the room it needs. The first six months carry the engineering weight: freezing contracts, proving the state machine, verifying invariants, and defining consistency and idempotency. The middle of the year carries the security formalisation and the router evaluation, which need the earlier phases stable before they can be measured honestly. The final quarter integrates the evidence and writes the thesis. Nothing in this schedule adds to the roadmap's phases; it sequences them, names their artifacts, and states what "done" looks like at each month boundary — because a programme without checkable month boundaries is a wish with a calendar.

Two conventions govern the whole schedule. First, the estate's own rule — no proof, no done — applies to the programme itself: a month is not complete when its calendar page turns but when its exit criteria are evidenced. Second, every scheduling assumption this paper is unsure about is marked as an **Open question** in bold, so the operator (HgX) can resolve it rather than discovering it mid-year.

## Month 1 — Phase 0: Freeze the Contracts

**Objective.** Produce the single canonical specification that every later phase works from. Month 1 reconciles the three white papers into one normative vocabulary, freezes the canonical glossary, the work-state machine, and the event vocabulary, and stands up the versioned specification repository that will hold every artifact the programme produces. This month also executes the first eight of the roadmap's fifteen immediate next actions: the repository itself, the frozen state machine, the glossary, the doctrine-to-invariant list, the approval-intent digest rule, the consistency guarantee matrix, the idempotency key schema, and the first draft of the threat model document. The discipline of the month is subtraction: every concept gets one definition and one owner, and anything that cannot be defined precisely enough to be tested is cut or marked as an **Open question** for later resolution.

**Deliverables.**
- Canonical glossary (all terms defined once, with owners) committed to `spec/`.
- Canonical work-state machine: the twelve states, the transition skeleton, and the guard table in `spec/state-machine.md`.
- Canonical event vocabulary: all fifteen events with normative definitions, in `spec/events.md`.
- Specification repository with the roadmap's layout (`spec/`, `contracts/`, `tests/`, `proofs/`, `experiments/`), versioned and reviewable.
- Approval-intent digest rule: the exact construction of the intent digest (fields, hash, canonicalisation) in `spec/approval-digest.md`.
- Consistency guarantee matrix and idempotency key schema, drafted for refinement in Months 5–6.
- Threat-model document skeleton (asset register and trust-boundary list) for completion in Month 7.
- Contract schema drafts: `contracts/evidence-packet.schema.json`, `contracts/approval-intent.schema.json`, `contracts/watchtower.schema.json`, `contracts/decision-packet.schema.json`, `contracts/artifact-manifest.schema.json`.

**Exit criteria.**
- All three white papers reconciled into one normative spec; no two documents define the same concept differently.
- Every state, event, contract, and invariant has a named owner.
- The repository is versioned, and the operator can review any concept's single definition.
- The digest rule is stated precisely enough that two independent implementations produce the same digest for the same intent.

**Dependencies.** The three white papers as source material (Papers I–III). The operator's approval of the reconciliation where the papers' vocabularies genuinely conflict — **Open question**: whether vocabulary conflicts are resolved by the operator at a Month 1 review or delegated to the chief of staff with operator ratification.

## Month 2 — Phase 1: The Formal Model

**Objective.** Convert the frozen state machine into a formal model in the chosen specification language and state the failure model it will be checked against. This is the month where the estate commits to a modelling language — TLA+ or Alloy, per the roadmap's recommendation — writes the state variables, transition guards, and illegal-state definitions, and defines the failure model (network interruption, expired approval, mutated intent, duplicate tap, stale live source, missing evidence, subagent completion without proof, router failure, device clock skew, out-of-order events, missing permissions, credential challenge, operator pause). The ten "what fixed means" statements from the roadmap become the proof obligations. The month's intellectual work is the failure model: a proof under unstated assumptions is decoration, so every assumption is written down where a future examiner can attack it.

**Deliverables.**
- Formal model in the chosen language covering the twelve states, the transition skeleton, and the guard table.
- Proof obligations document: the ten "what fixed means" statements rendered as checkable properties.
- Failure model document: the thirteen failure conditions with precise definitions of what each assumes.
- Counterexample log (initial): any illegal states found during model development, with resolutions.

**Exit criteria.**
- The model type-checks / parses in the chosen tool and covers every transition in the skeleton.
- All ten proof obligations are stated as properties the model checker can evaluate.
- The failure model is explicit, and each assumption is reviewable by the operator.
- The modelling-language decision (TLA+ vs Alloy) is recorded with reasons — **Open question** until Month 2.

**Dependencies.** Month 1's frozen state machine and event vocabulary; without them the model has nothing to formalise. The language decision blocks all modelling work, so it is taken in the first week.

## Month 3 — Phase 1 Results and Phase 2 Contract Tests

**Objective.** Run the model checker to completion and begin the invariant verification with Layer 1: static contract tests. The first half of the month is adversarial work on the model — running the proof obligations, examining counterexamples, weakening guards deliberately to confirm the model can fail, and documenting the results. The second half converts the doctrine-to-invariant list from Month 1 into the Layer 1 contract test suite: schema validation, unknown-enum fail-closed, missing-field rejection, expired-approval rejection, mutated-digest rejection, and the rule that incomplete evidence cannot produce completion. This month also builds two of the roadmap's test harnesses: the mutated/expired approval harness and the duplicate-tap chaos test.

**Deliverables.**
- Model-checker results for all ten proof obligations, with the full output archived in `proofs/`.
- Counterexample report: every counterexample found, its cause, and its resolution (or the weakened guard that produced it, kept as a regression case).
- Layer 1 contract test suite, automated and passing against the current estate semantics.
- Test harnesses for mutated/expired approvals and duplicate approval taps (roadmap next actions 10 and 11).

**Exit criteria.**
- The model checker finds no reachable illegal state under the stated failure model.
- Every weakened guard tested produces a counterexample (the model is genuinely stressed, not decorative).
- All Layer 1 contract tests pass, and mutated or expired approvals demonstrably cannot pass them.
- The invariant traceability matrix is started: each invariant linked to its doctrine statement and its test.

**Dependencies.** Month 2's model and failure model. The estate's current approval and evidence semantics must be observable enough to test against — if the live estate has drifted from the frozen spec, the drift is recorded rather than silently accommodated (see the estate-drift risk in Section 15).

## Month 4 — Phase 2 Property and Chaos Tests

**Objective.** Complete the invariant verification with Layers 2 and 3: property-based tests over random event sequences and the full chaos suite. Where Month 3 tested the contracts statically, Month 4 tests the estate's behaviour under adversarial conditions: approval mutations, expiry timing, duplicate taps, network loss, subagent claims without evidence, stale sources, device offline during approval, intent change after card render, backend change before client refresh, router backend down, digest mismatch, and missing tests in evidence packets. This month also builds the remaining roadmap test harnesses: the stale-source test, the delegation-without-proof test, and the shared-surface redaction test (next actions 12–14).

**Deliverables.**
- Layer 2 property-based test suite: random event-sequence generators with invariant assertions, covering approval mutations, expiry times, duplicates, network loss, subagent claims, and stale sources.
- Layer 3 chaos test suite: the full adversarial catalogue from the roadmap, each with setup, fault injection, and expected fail-closed behaviour.
- Test harnesses for stale sources, delegation without proof, and shared-surface redaction.
- Completed invariant traceability matrix: invariant → doctrine → code → test, for all 27 invariants.

**Exit criteria.**
- Every major doctrine statement has a testable invariant, and every invariant has at least one test in each applicable layer.
- All tests automated; the suite runs in CI (or the estate's equivalent continuous check) with no manual steps.
- Optimistic completion fails the tests: no path to `completed` exists without evidence and acceptance.
- The chaos suite is citable as empirical validation: each test documents the fault, the expected behaviour, and the observed behaviour.

**Dependencies.** Month 3's contract tests and traceability matrix. The chaos tests need a test environment that can inject the faults without touching the live estate — **Open question**: whether the estate stands up a dedicated test harness environment or runs chaos tests against instrumented live paths with safeguards.

## Month 5 — Phase 3: Consistency

**Objective.** Define and test the multi-device consistency contract. Month 5 writes the consistency model specification — the hybrid guarantee table (eventual status, revision-stable evidence, strongly consistent approvals, linearised consequential execution), the single-authoritative-writer architecture, the event-sourced work-state shape, the revision-token protocol, and the approval flow in which the client renders from hints and the server alone records decisions. It then tests the contract: approval conflicts between devices, stale-cache rendering, clock skew, network loss during approval, and the offline-tap case. The conflict-resolution table from the roadmap becomes a test matrix: every row gets a test, and the hardest row — two devices attempting the same approval — gets the most attention.

**Deliverables.**
- Consistency model specification: guarantee table, writer architecture, event-sourced state shape, revision protocol, approval flow sequence.
- Conflict-resolution table with a test for every row.
- Multi-device sequence diagrams for the approval flow, the conflict cases, and the offline-tap case.
- Device cache policy and freshness policy documents.
- Multi-device test suite including clock-skew and network-loss injection.

**Exit criteria.**
- No device can become a source of truth under test: every client mutation path is validated server-side.
- Approval conflicts resolve deterministically: the same conflict always produces the same resolution.
- Stale data cannot masquerade as current: expired freshness renders as unknown or reduced confidence.
- Offline taps cannot become approvals: the pending-gesture case is tested and fails closed.

**Dependencies.** Months 1–4: the frozen vocabulary, the proven state machine, and the invariant suite. The consistency tests assume the approval-binding semantics are already verified; Month 5 tests their multi-device behaviour, not the binding itself.

## Month 6 — Phase 4: Idempotency

**Objective.** Specify and test the transactional semantics of consequential action: the idempotency key schema, the execution-record lifecycle, the governed saga pattern, the retry policy matrix, and the ambiguity-handling protocol. Month 6 answers the question the estate has never formally answered: what happens when a consequential action is attempted twice, or when its outcome is unknown. The deliverable that matters most is the ambiguous-outcome protocol — the rule that an unverifiable consequential execution becomes visible `unknown` or `failed`, never silent completion — because that is the case where real systems double-spend. The external-system classification table (native idempotency, read-after-write, no-idempotency high-risk, reversible, irreversible, financial, publication, deletion) is completed for every integration the estate actually uses.

**Deliverables.**
- Idempotency key specification: `hash(work_id, intent_id, intent_digest, action, target, scope, revision, operation_class)` with canonicalisation rules.
- Execution-record schema and the lifecycle states (`prepared → approved → execution_requested → execution_started → execution_observed / execution_failed / execution_unknown → completed / cancelled`).
- Governed saga specification: prepare → approval → execute → verify → record evidence → compensate, with the approval requirements at each step.
- Retry policy matrix by operation class; ambiguity-handling protocol.
- External-system classification for every live integration.
- Duplicate-tap and offline-approval test suites; ambiguous-outcome verification tests.

**Exit criteria.**
- Duplicate taps cannot duplicate effects under test: the second tap returns the existing decision and state.
- Network loss cannot silently complete: the ambiguous case renders as visible unknown/failed.
- Retries occur only when the safe-to-retry flag is set; at-most-once is demonstrable under test.
- Every consequential integration is classified, and high-risk integrations (no idempotency, no verification) have their strengthened-approval or manual-execution handling documented.

**Dependencies.** Month 5's consistency contract (the approval flow the saga builds on) and Months 3–4's invariant suite (INV-A6 on duplicate taps, INV-E on evidence). The external-system classification needs an accurate inventory of the estate's integrations — connectors, publishing paths, financial paths — which the operator confirms.

## Month 7 — Phase 5: Threat Model and Capability Matrix

**Objective.** Convert the estate's honest limitations into a formal security model. Month 7 writes the asset register (operator attention, approval authority, credentials, personal data across its classes, artifacts, evidence packets, logs, connectors, runtime, router state), draws the trust-boundary map across the ten named boundaries, builds the capability matrix (subject, action, object, scope, condition, expiry, approval requirement, evidence requirement), and writes the threat catalogue: STRIDE plus the four agent-specific threats the roadmap names — prompt injection, stale-state manipulation, approval fatigue, and subagent deception. Attack trees are drawn for the highest-risk paths (approval forgery, intent mutation, evidence fabrication), and the control matrix names the control for every consequential action. The month's discipline is the same as the thesis's: no overclaiming. Procedural isolation is documented as Level 0 and compensated, not disguised.

**Deliverables.**
- Asset register and trust-boundary diagram (ten boundaries).
- Capability matrix covering every consequential action.
- Threat catalogue: STRIDE analysis plus prompt injection, stale-state manipulation, approval fatigue, subagent deception — each with named controls.
- Attack trees for the highest-risk paths; control matrix mapping threats to controls to tests.
- Isolation upgrade roadmap (Levels 0–5) with the evaluation criteria for each level.

**Exit criteria.**
- Every consequential action has a named threat and a named control.
- Prompt injection, stale state, and approval fatigue are explicitly modelled with controls and tests, not mentioned in passing.
- Procedural isolation is documented with its compensating controls; nothing in the model implies a stronger isolation than exists.
- The controls are testable: each control maps to at least one test in the Month 8 suite.

**Dependencies.** Months 1–6: the threat model must describe the system as specified and verified, not as originally imagined. Any drift between the estate and the frozen spec must be reconciled before the model is written, or the model describes a fiction.

## Month 8 — Phase 5 Security Tests and Isolation Level 1

**Objective.** Test the security model and implement the first isolation upgrade. Month 8 builds the security test suite from the control matrix — mutated-intent tests, artifact-tamper tests, log-tamper-evidence tests, memory-poisoning tests, prompt-injection egress tests, approval-fatigue metric tests, subagent-deception tests — and executes the Level 1 isolation upgrade: per-scope directories, path contracts, handoff-only cross-role access, and audit logging. Level 1 is deliberately unglamorous: it is filesystem and access discipline, not cryptography, and its value is that it makes the procedural isolation auditable. The month also evaluates, without yet implementing, whether Levels 2–5 are warranted — the isolation cost-benefit analysis that Section 15 names as a risk.

**Deliverables.**
- Security test suite mapped to the control matrix, automated where possible.
- Level 1 isolation implementation: per-scope directory layout, path contracts, handoff-only cross-role access rules, audit log format and retention.
- Isolation cost-benefit analysis for Levels 2–5: what each level would cost (engineering effort, operational friction, attention cost) against what it would buy.
- Updated threat catalogue entries reflecting Level 1 controls.

**Exit criteria.**
- Every control in the matrix has at least one passing test; every test maps to a control.
- Level 1 is implemented and its audit logs are reviewable by the operator.
- The cost-benefit analysis is written and reviewed: the decision to stop at Level 1 (or proceed) is recorded with reasons — **Open question** until Month 8.
- The security posture is defensible without overclaiming: the documentation states Level 1 plainly.

**Dependencies.** Month 7's threat model and control matrix. The Level 1 implementation needs operator approval for the directory and access changes, since they touch the live estate layout.

## Month 9 — Phase 6: Shadow Logging and Offline Replay

**Objective.** Begin the router evaluation with the two stages that require no live experimentation: shadow logging with outcome labels, and offline replay. Month 9 extends the router's decision logs — the usage router is already in shadow mode under local policy, so the logging infrastructure exists — with the outcome-label schema from the roadmap (outcome, human_repair, repair_time_minutes, cost_units, latency_seconds, attention_interruptions, evidence_complete), and produces the first router shadow report (roadmap next action 15). It then replays the labelled historical decisions through the alternate policies — cache-only, local heuristic, unconstrained orchestration, the hybrid — to produce the first comparative results. This month is also where the measurement apparatus for attention cost is built and its noise characterised, honestly, before any live trial depends on it.

**Deliverables.**
- Outcome-label schema and the extended decision-log format, documented and implemented.
- First router shadow report: decisions logged, outcomes labelled, baselines described.
- Offline replay harness and the replay results: each historical decision evaluated under each alternate policy.
- Attention-cost measurement method with its noise characterisation and stated limitations.
- Experiment protocol for the Month 10 live trials, pre-registered: eligible task classes, randomisation method, metrics, and stop rules.

**Exit criteria.**
- Router decisions are linked to labelled outcomes in the logs; the link is auditable.
- Local, cache-only, and unconstrained baselines are compared on replay data with the stated objective function.
- The attention-cost measurement exists, its noise is quantified, and its limitations are written down.
- The live-trial protocol is pre-registered and approved by the operator before any live trial runs — no trial begins without this.

**Dependencies.** Months 1–8: the router evaluation must measure the specified, verified system. The shadow logs need several weeks of labelled data, so labelling begins the moment the schema is implemented — **Open question**: whether Month 9's replay window is long enough to yield usable sample sizes, or whether labelling must begin earlier (in Month 1) as a background activity.

## Month 10 — Phase 6: Controlled Live Trials

**Objective.** Run the controlled live trials of routing policies on eligible low-risk tasks. Month 10 executes the pre-registered protocol: random assignment of eligible tasks across the policies under test, with the router guardrails enforced throughout — the router never approves consequential action, never overrides approval boundaries, never hides failure, never suppresses evidence. Consequential actions are never randomised; they always take the governed path. The month's work is operational as much as statistical: monitoring the trials, enforcing the stop rules, labelling outcomes as they land, and protecting the operator's attention throughout — the trial must not become the thing that attention-cost measurement warns about.

**Deliverables.**
- Live-trial dataset: task assignments, policy per task, outcomes, repair events, attention interruptions, costs, latencies.
- Stop-rule log: any trial arm stopped early, with the reason.
- Guardrail compliance record: evidence that no trial task violated the router guardrails.
- Preliminary statistical analysis with Bayesian estimation for the small samples.

**Exit criteria.**
- The trial ran to the pre-registered protocol or to a pre-registered stop rule — not to a post-hoc one.
- No consequential action was randomised; the guardrail compliance record is complete.
- Every trial task has a labelled outcome; there are no unlabelled tasks in the analysis.
- The statistical analysis reports uncertainty honestly: credible intervals, not point claims.

**Dependencies.** Month 9's protocol, labelling infrastructure, and replay baselines. The operator's approval of the eligible task classes — the trial's scope is a consequential decision about the estate's own operation, and it needs the operator's explicit approval.

## Month 11 — Phase 7: Evidence Integration

**Objective.** Assemble the ten-part evidence package and establish the traceability the thesis depends on. Month 11 is arrangement, not new research: the formal specification, the model-checking results, the invariant suites, the consistency and idempotency tests, the threat model, the router experiment report, the operator scorecard, the failure case studies, and the limitations section are gathered into one package, and every sentence of the doctoral claim is traced to the evidence that could refute it. The adversarial integration review from Section 13.6 is conducted here: for each claim, the reviewer confirms the refuting evidence exists and came out in the claim's favour, and any claim that cannot meet this bar is cut or downgraded. The failure case studies are written this month — real failures, narrated honestly, each with the invariant that caught it or the gap that let it through.

**Deliverables.**
- The ten-part evidence package, assembled and versioned.
- Claim-to-evidence traceability matrix: each clause of the doctoral claim linked to its supporting and refuting evidence.
- Adversarial integration review report: claims kept, claims cut, claims downgraded, with reasons.
- Failure case studies (worked, honest, each with a lesson).
- Limitations section, drafted in full.

**Exit criteria.**
- Every clause of the doctoral claim has both supporting and refuting evidence in the package.
- The traceability matrix has no dangling claims and no unclaimed evidence.
- The limitations section is specific: it names failure-model boundaries, measurement thinness, and isolation limits.
- The operator reviews the package and approves the claim as stated — or the claim is restated until he does.

**Dependencies.** All prior months: the package assembles their artifacts. Any month whose exit criteria were not evidenced reopens here — Month 11 is the integration gate, and it fails closed.

## Month 12 — Thesis Write-Up and Defence Preparation

**Objective.** Write the thesis and prepare to defend it. Month 12 follows the ten-chapter structure from Section 13.4: the introduction and literature review, the thesis chapter stating the claim, the architecture chapter, the formal-model chapter, the security-model chapter, the evaluation chapter, the results, the limitations, and the contribution. The month's discipline is the same one the programme has enforced throughout: every assertive sentence traces to the evidence package, and the limitations chapter is written with the same care as the results. Defence preparation is adversarial by design: the known hard questions — the single-operator measurement, the procedural isolation, the attention-cost noise, the small router samples — are answered in writing before they are asked in person, and the answers point at evidence, not at rhetoric.

**Deliverables.**
- Complete thesis draft following the ten-chapter structure.
- Claim-evidence appendix: the traceability matrix in publishable form.
- Defence preparation document: the hard questions with evidence-backed answers.
- Programme retrospective: what the twelve months cost, what they proved, and what remains open — the honest input to any future work.

**Exit criteria.**
- The thesis draft is complete and internally consistent: no chapter contradicts another, no claim lacks its evidence trace.
- The defence preparation covers every limitation the thesis states — the examiner will find them first.
- The operator approves the thesis as the estate's account of itself.
- The programme retrospective is written: the work ends with an honest ledger, not a victory lap.

**Dependencies.** Month 11's integrated evidence package. The thesis cannot be written before the package exists, because the thesis is the package's argument — writing it earlier would be writing the conclusion before the experiment.

## 14.2 Programme Governance

**The operator as principal and final authority.** The operator (HgX) is the principal of this programme in the same sense that he is the principal of the estate: all consequential decisions require his approval, and the programme's consequential decisions are named in advance. They are: the Month 1 vocabulary reconciliation where the papers conflict; the Month 2 modelling-language decision if the chief of staff cannot resolve it on the evidence; the Month 8 isolation-level decision (stop at Level 1 or proceed upward); the Month 9 approval of the live-trial protocol and its eligible task classes; the Month 11 approval of the doctoral claim as stated; and the Month 12 approval of the thesis as the estate's account of itself. Between these gates, the programme runs on delegated authority within the bounds the operator sets — but the bounds are explicit, and anything outside them comes back for approval. This is the approval-at-the-last-safe-moment discipline applied to the programme's own governance: decisions are made when they must be, by the one who bears them, with the evidence on the table.

**Monthly review cadence.** At each month boundary, a review is held with a single question: are this month's exit criteria evidenced? The review is a go/no-go gate, not a status meeting. Go means the exit criteria are met and evidenced, and the next month begins. No-go means the month's work continues until the criteria are met — the schedule slips rather than the standard. A no-go does not require the operator's presence for purely technical shortfalls, but any no-go that changes the programme's end date, scope, or claim comes to the operator as a consequential decision. The review produces a one-page record: the criteria, the evidence, the verdict, and any carry-forward. Twelve months, twelve records, one ledger — the programme is governed the way the estate is governed, because it is the estate's work.

**Jarvis as chief of staff.** Execution runs through the team-deployment pattern: Jarvis acts as chief of staff, issuing one brief per phase to a minimum specialist team — one agent per job, verification mandatory, no agent publishing, sending, spending, or deleting without the operator's approval. The pattern fits this programme exactly: the phases are separable jobs (modelling, test-writing, threat analysis, experiment design, evidence assembly), each needs a specialist's sustained attention, and each needs independent verification before its artifacts enter the package. The chief of staff does not do the specialists' work and does not approve their output on their say-so; verification is a separate job, assigned separately, and "no proof, no done" is enforced by the structure, not by trust.

**No proof, no done — applied to the programme itself.** The estate's rule is the programme's rule. A month is not complete when its artifacts exist but when its exit criteria are evidenced: the model checker output is archived, the test suite runs in CI, the conflict table has its tests, the trial followed its protocol. Month 11's integration gate fails closed: any prior month whose criteria were waived rather than met reopens the gate. This is deliberately strict, because the thesis that emerges from a programme that waived its own standards is a thesis that cannot survive its own limitations section.

**Publishable by construction — applied to the programme's artifacts.** The trilogy's main vision governs the programme's outputs as well as the estate's: every phase's artifacts are produced publishable — the system public, the principal's private life never. The frozen glossary, the formal model, the invariant suite, the consistency contract, the idempotency schema, the threat model, the router's labelled decision history (sanitised), and the evidence package are each releasable without a second production effort. Publication timing remains the operator's consequential decision; publishability is the standing requirement. A phase whose artifacts cannot be published has not finished its work — it has merely finished its writing.

**Dependencies and the critical path.** The programme's critical path runs through Months 1, 2, 3, 11, and 12: the frozen spec, the formal model, the checked results, the integrated evidence, and the written thesis. These months cannot slip without moving the end date, because each is the prerequisite of everything after it. Months 4 through 10 have internal dependencies — the chaos tests assume the contract tests, the idempotency tests assume the consistency contract, the live trials assume the shadow labelling — but they also have some slack against each other: a slow Month 5 can overlap a fast Month 6 without breaking the chain, provided the exit criteria hold. The months with the least slack are Month 2 (the language decision blocks all modelling) and Month 9 (the labelling window cannot be compressed after the fact — outcome labels need calendar time, and no amount of effort creates more of it). The critical-path discipline is therefore: protect Months 1–3 and 9–12 absolutely; use Months 4–8 as the buffer, but never by waiving exit criteria — only by resourcing.

**Pacing: when to switch tracks.** The roadmap's Option A (12-week engineering fix) is the fallback if the full programme cannot be sustained: it keeps the freeze, the property tests, the server-authoritative approvals, the idempotency keys, the threat model, and the shadow evaluation, and it surrenders the model-checked proof, the chaos depth, the live router trials, and the doctoral evidence package. Switch to Option A only on a named constraint — a hard external deadline, a sustained loss of operator availability, or a Month 3 result showing the formal methods are intractable for the estate's complexity — and record the switch as a consequential decision with the operator's approval, because it changes what the thesis can claim. The roadmap's Option C (12–18 month full PhD track) is the extension if the twelve months prove insufficient: it adds the operator study, the attention-cost measurement depth, and the longer router observation windows that a formal doctoral registration might require. Switch to Option C if the Month 9 measurement characterisation shows the attention-cost metric needs a longer baseline, or if the evidence integration of Month 11 reveals gaps that need another experimental cycle. The default is the twelve-month programme as stated. The tracks exist so that changing pace is a decision, not a drift.
