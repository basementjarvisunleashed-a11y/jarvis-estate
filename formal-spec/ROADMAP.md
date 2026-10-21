# Roadmap to Fix the Missing Formalisms

*Doctoral-level remediation roadmap for J.A.R.V.I.S. — recorded 2026-10-08.
Declared by HgX as the focus of his life. Source: HgX's own directive.*

Below is a doctoral-level remediation roadmap. Its purpose is to move J.A.R.V.I.S. from **strong architectural specification** to **formally defensible engineering and research contribution**.

The roadmap is organized around the six gaps:

1. Formal state machine proof
2. Invariant verification
3. Consistency model
4. Idempotency guarantees
5. Security boundary formalism
6. Router optimality

The end goal is not to make the system more complicated. The goal is to make the existing doctrine provable, testable, and measurable.

---

# 1. Target End-State

After this roadmap, J.A.R.V.I.S. should be able to demonstrate the following:

| Gap | Target State |
|---|---|
| Formal state machine | A canonical state machine specification with model-checked proof that illegal transitions cannot occur under defined failure conditions. |
| Invariant verification | A suite of executable tests and formal properties proving that core invariants hold. |
| Consistency model | A documented consistency contract for multi-device observation, approval, caching, and recovery. |
| Idempotency guarantees | Explicit transactional semantics for preparation, approval, execution, verification, and retry. |
| Security boundary formalism | A formal threat model, capability matrix, trust-boundary map, and upgraded isolation roadmap. |
| Router optimality | Empirical comparison of routing policies using accepted work, cost, repair, latency, loops, and attention cost. |

The final output should be:

> **A formally specified, empirically validated, human-governed agent control plane.**

That is a much stronger doctoral claim than:

> "We built a personal AI assistant."

---

# 2. High-Level Roadmap Summary

| Phase | Objective | Main Output | Exit Criterion |
|---:|---|---|---|
| 0 | Freeze contracts | Canonical specification repository | All papers reconciled into one normative spec |
| 1 | Formalize state machine | State machine model and proof obligations | Illegal transitions are provably unreachable |
| 2 | Verify invariants | Invariant test suite and property tests | Core invariants pass in CI and chaos tests |
| 3 | Define consistency model | Multi-device consistency contract | Approval and status conflicts resolve deterministically |
| 4 | Specify idempotency | Transaction and retry semantics | Duplicate taps, retries, and ambiguous executions cannot create double consequences |
| 5 | Formalize security boundaries | Threat model and capability matrix | Each consequential path has named controls and tests |
| 6 | Evaluate router optimality | Routing experiment report | Router policy is justified by measured outcomes, not intuition |
| 7 | Integrate into doctoral evidence | PhD validation package | Architecture, proofs, tests, and metrics form one defensible thesis |

---

# 3. Phase 0 — Freeze the Contracts

## Purpose

Before proving anything, the system must have one canonical specification. The three white papers are consistent in philosophy, but they use slightly different vocabularies.

Examples:

- The operating paper describes the doctrine as:

  `Role → Live Source → Tool → Artifact → Evidence → Approval → Routine`

- The backend paper describes a request lifecycle:

  `Brief → Route → Plan → Execute → Verify → Approve → Handoff`

- The front-end paper describes an operator loop:

  `Brief → Work → Evidence → Approval → Decision`

These are compatible, but a formal system needs one normative model.

## Deliverables

### 0.1 Canonical Glossary

Define every term once.

| Term | Normative Meaning |
|---|---|
| Work item | One bounded unit of requested estate work |
| Artifact | Inspectable output produced by work |
| Evidence packet | Structured proof bundle attached to work |
| Approval intent | Exact consequential action awaiting HgX |
| Routine | Scheduled skill that has earned repetition |
| Live source | Authoritative current-state system |
| Durable memory | Identity, preferences, principles, commitments |
| Unknown state | Insufficient observation, not failure |
| Paused state | Operator-intent stop, not outage |
| Degraded state | Observed impairment threatening outcome |
| Completed state | Acceptance test passed with evidence |

### 0.2 Canonical Work-State Machine

Proposed canonical states:

```text
received
accepted
in_progress
awaiting_approval
executing
verifying
completed
blocked
failed
paused
unknown
cancelled
```

Proposed transition skeleton:

```text
received → accepted
accepted → in_progress
in_progress → awaiting_approval
in_progress → blocked
in_progress → verifying
awaiting_approval → executing
awaiting_approval → cancelled
executing → verifying
executing → failed
verifying → completed
verifying → failed
any state + evidence_of_failure → failed
operator intent → paused
insufficient observation → unknown
```

### 0.3 Canonical Event Vocabulary

| Event | Meaning |
|---|---|
| `brief_received` | HgX or authorized routine submits work |
| `brief_accepted` | Orchestrator accepts scope |
| `plan_created` | Bounded plan exists |
| `artifact_produced` | Inspectable output exists |
| `evidence_packet_created` | Proof bundle exists |
| `approval_requested` | Consequence boundary reached |
| `approval_granted` | Exact intent approved |
| `approval_denied` | Intent denied |
| `approval_expired` | Intent expired |
| `execution_started` | Approved action began |
| `execution_observed` | Result observed |
| `acceptance_passed` | Acceptance test passed |
| `failure_observed` | Failure condition observed |
| `operator_paused` | HgX paused service or work |
| `observation_unavailable` | State cannot be established |

### 0.4 Specification Repository

Versioned repository containing:

- `spec/state-machine.md`
- `spec/invariants.md`
- `spec/consistency.md`
- `spec/idempotency.md`
- `spec/security-threat-model.md`
- `spec/router-policy.md`
- `contracts/watchtower.schema.json`
- `contracts/evidence-packet.schema.json`
- `contracts/approval-intent.schema.json`
- `contracts/decision-packet.schema.json`
- `contracts/artifact-manifest.schema.json`
- `tests/`
- `proofs/`
- `experiments/`

## Exit Criteria

Phase 0 is complete when all three white papers are reconciled into one normative spec; every state, event, contract, and invariant has one owner; no two documents define the same concept differently; the specification is versioned and reviewable.

---

# 4. Phase 1 — Formal State Machine Proof

## Objective

Prove that the work-state machine cannot enter illegal or unsafe states under the defined assumptions.

## What "Fixed" Means

1. A completed state cannot be reached without acceptance evidence.
2. An executing state cannot be reached without a valid approval for consequential actions.
3. A mutated or expired approval cannot lead to execution.
4. Unknown cannot be rendered as operational.
5. Paused cannot be confused with failed.
6. Failure events can interrupt normal flow but cannot silently become completion.
7. Optimistic completion is unreachable.
8. Offline approval cannot create a valid approval.
9. Duplicate approval taps cannot create duplicate execution.
10. Stale state cannot masquerade as current state.

## Method

**1.1 Create a formal model** — TLA+ or Alloy recommended (best balance for a doctoral engineering thesis); Coq/Lean for stronger proof; property-based state-machine testing if formal tools are too heavy.

**1.2 State variables** (minimum): `work_state`, `approval_state`, `intent_digest`, `intent_expiry`, `evidence_exists`, `acceptance_passed`, `execution_observed`, `source_freshness`, `operator_pause`, `observation_status`.

**1.3 Transition guards** — e.g. `can_enter_completed = evidence_exists AND acceptance_passed AND NOT failure_observed`; `can_enter_executing` requires valid, unexpired, digest-matched approval for consequential actions; `can_render_operational` requires observed operational state with valid freshness.

**1.4 Illegal states** — completed without evidence packet; executing without valid approval; approved intent with changed target/effect; unknown rendered as operational; paused rendered as failed; optimistic completion from delegated claim; offline approval becoming authoritative.

**1.5 Failure model** — network interruption, expired approval, mutated intent, duplicate tap, stale live source, missing evidence, subagent completion without proof, router failure, device clock skew, out-of-order events, missing permissions, credential challenge, operator pause.

## Deliverables

Formal state machine model; guard table; failure model; proof obligations; model checker results; counterexample report.

## Exit Criteria

Model checker finds no reachable illegal state under the assumed failure model; any weakened guard permitting an illegal state produces a counterexample; proof obligations documented.

---

# 5. Phase 2 — Invariant Verification

## Objective

Convert architectural promises into executable invariants.

## Core Invariant Set

**A. Completion** — INV-C1: no completion without evidence packet. INV-C2: no completion if required tests failed. INV-C3: no delegated claim produces completion without verification. INV-C4: no optimistic UI state overrides authoritative backend state. INV-C5: completion supported by observed output, not fluent text.

**B. Approval** — INV-A1: consequential action cannot execute without approved intent. INV-A2: approval binds to action, target, effect, scope, revision, expiry. INV-A3: changed target/effect invalidates prior approval. INV-A4: expired approval unusable. INV-A5: offline approval cannot create authoritative consent. INV-A6: duplicate taps must not duplicate execution. INV-A7: approval cannot authorize adjacent or future actions.

**C. Evidence** — INV-E1: every completed consequential run has an evidence packet. INV-E2: evidence packet revision matches artifact revision. INV-E3: missing evidence renders as missing. INV-E4: gaps stay visible. INV-E5: sources current where live truth is required.

**D. State rendering** — INV-S1: unknown never renders as operational. INV-S2: paused never renders as failed. INV-S3: degraded requires observed impairment. INV-S4: stale data shows reduced confidence or unknown. INV-S5: shared surfaces never render restricted content.

**E. Router** — INV-R1: router recommends path only, never approves consequence. INV-R2: repeated identical error triggers escalation or path change. INV-R3: repeated no-progress action denied. INV-R4: fresh cache may suppress refetch when sufficient. INV-R5: router fallback preserves safety if external backend fails.

## Verification Strategy

- **Layer 1: Static contract tests** — schema validation; unknown enums fail closed; missing fields fail; expired approvals fail; mutated digests fail; incomplete evidence cannot produce completion.
- **Layer 2: Property-based tests** — random event sequences asserting invariants (approval mutations, expiry times, duplicates, network loss, subagent claims, stale sources).
- **Layer 3: Chaos tests** — device offline during approval, approval expiry mid-review, intent change after card render, duplicate tap, backend change before client refresh, router backend down, stale live source, subagent completion without evidence, digest mismatch, missing tests in evidence packet.

## Deliverables

Invariant catalogue; contract test suite; property-based test suite; chaos test suite; invariant traceability matrix (invariant → doctrine → code → test).

## Exit Criteria

Every major doctrine statement has a testable invariant; all tests automated; mutated/expired approval cannot pass; optimistic completion fails tests; suite citable as empirical validation.

---

# 6. Phase 3 — Consistency Model

## Objective

Define how iPhone, Watch, iPad, TV, and Vision Pro observe and interact with estate state without becoming independent sources of truth.

## Recommended Model

Hybrid consistency:

| Operation Class | Guarantee |
|---|---|
| Status viewing | Eventual consistency with freshness stamps |
| Evidence viewing | Revision-stable reads |
| Approval decision | Strong authoritative consistency |
| Consequential execution | Linearized, single-writer execution |
| Memory correction | Orchestrator-mediated reconciliation |
| Live-source facts | Read-current at decision time |
| Artifact download | Digest-verified bytes |
| Notification delivery | At-least-once hints, not authoritative state |

Core principle: **status may be eventually consistent; consequence must be strongly consistent.**

## Architecture

**Single authoritative writer** — the orchestrator (or authorized execution layer). Clients may submit briefs, request evidence, render status, present approval, transmit approval decisions, open artifacts. Clients may NOT approve locally without server validation, infer completion, mutate evidence, reinterpret intent, bypass approval, or become a second orchestrator.

**Event-sourced work state** — each work item carries `work_id`, `revision`, `state`, `history`, `evidence_refs`, `approval_refs`, `last_observed_at`, `fresh_until`; every meaningful transition appends an event.

**Revision tokens** — every client request includes `work_id`, `revision`, `intent_id`, `intent_digest`, `device_session_id`, `timestamp`; the server rejects stale mutations.

**Approval flow** — client renders card from hint → operator taps → client sends decision with intent_id + digest → server validates (intent exists, unexpired, digest matches, action permissible, session authorized) → server records once → returns authoritative result → client renders. Changed intent → reject and present new intent. Expired → disable and refresh. Offline → no local approval; pending gesture only, not consent.

## Conflict Resolution

| Conflict | Resolution |
|---|---|
| Two devices show different status | Server state wins |
| Two devices attempt approval | First valid decision recorded wins |
| Client cache says operational, source expired | Render unknown / reduced confidence |
| Memory says X, live source says Y | Live source wins for current facts |
| Durable memory contradiction | Orchestrator reconciles |
| Notification arrives after state changed | Notification is a hint, not truth |
| Evidence packet updated | New revision; old immutable |
| Artifact changed after approval | Approval invalid; new approval required |

## Deliverables

Consistency model specification; revision protocol; conflict resolution table; multi-device sequence diagrams; device cache policy; freshness policy.

## Exit Criteria

No device can become a source of truth; approval conflicts resolve deterministically; stale data cannot masquerade as current; offline taps cannot become approvals; behavior tested under clock skew and network loss.

---

# 7. Phase 4 — Idempotency Guarantees

## Objective

Prevent duplicate consequential effects from retries, duplicate taps, network failures, or ambiguous execution.

## Core Principle

> Consequential actions must be at-most-once unless the system has observed that they did not occur or are safely repeatable.

## Operation Classes

| Class | Examples | Retry Policy |
|---|---|---|
| Read | Fetch calendar, price, document, status | Freely repeatable |
| Prepare | Draft, stage, calculate, reconcile | Repeatable if reversible |
| Approve | HgX grants exact intent | Record once; duplicate returns same decision |
| Execute | Send, publish, purchase, delete, transfer | At-most-once unless verified safe |
| Verify | Observe result after execution | Freely repeatable |
| Compensate | Restore, revoke, undo if possible | Only if supported and approved |
| Memory write | Update durable memory | Reconcile, do not duplicate contradictions |

## Idempotency Model

Idempotency key = `hash(work_id, intent_id, intent_digest, action, target, scope, revision, operation_class)`.

Server stores: key, status, created/updated timestamps, approval ref, execution state, observed result, attempt count, last error, safe-to-retry flag.

Execution record states: `prepared → approved → execution_requested → execution_started → execution_observed / execution_failed / execution_unknown → completed / cancelled`.

**Duplicate taps**: first tap validates and records; second tap returns existing decision and state — never a second execution.

**Ambiguous outcome**: do not mark completed; do not auto-retry if consequential; verify externally if possible; else mark `execution_unknown` and escalate with the next safe option.

## Transaction Pattern

Governed saga (no assumed distributed transactions): prepare → approval → execute → verify → record evidence → compensate if approved and possible. Preparation needs no approval; approval binds exact target/effect; execution needs valid approval; execution must be idempotent or verified; failed verification → unknown/failed; compensation needs its own approval if consequential; no silent rollback of consequential effects.

## External System Classification

| Integration Class | Handling |
|---|---|
| Supports idempotency key | Use native idempotency |
| Supports read-after-write verification | Execute then verify |
| No idempotency, no verification | High-risk; strongest approval or manual execution |
| Reversible action | Prefer reversible preparation |
| Irreversible action | Exact approval and evidence |
| Financial transfer | Strongest verification, conservative retry |
| Publication | Digest-bound artifact and expiry |
| Deletion | Recoverable change preferred; require recovery path |

## Deliverables

Idempotency key specification; execution record schema; saga specification; retry policy matrix; ambiguity handling protocol; duplicate-tap and offline-approval test suites.

## Exit Criteria

Duplicate taps cannot duplicate effects; network loss cannot silently complete; ambiguous consequential actions become visible unknown/failed; retries only when safe; at-most-once demonstrable under test.

---

# 8. Phase 5 — Security Boundary Formalism

## Objective

Convert honest limitations into a formal security model: trust boundaries, assets, threats, controls, tests.

## Model

Capability-based governance. A capability specifies: subject, action, object, scope, condition, expiry, approval requirement, evidence requirement.

## Assets

HgX attention; approval authority; credentials; personal data (health, finance, legal, communications, betting, identity); artifacts; evidence packets; logs; connectors; runtime; router state.

## Trust Boundaries

1. HgX devices ↔ estate edge
2. Estate edge ↔ orchestrator
3. Orchestrator ↔ tools
4. Orchestrator ↔ subagents
5. Orchestrator ↔ connectors
6. Orchestrator ↔ external web
7. Orchestrator ↔ Secure Vault
8. Orchestrator ↔ external router
9. Client ↔ notification system
10. Personal surfaces ↔ shared surfaces

## Threat Model (STRIDE + agent-specific)

- **Spoofing**: fake approval (device-bound session, intent digest), fake source (source validation, allowlist), fake completion (evidence verification).
- **Tampering**: mutated intent (digest binding), artifact tampering (content digest), log tampering (append-only, tamper-evident roadmap), memory poisoning (provenance, reconciliation).
- **Repudiation**: approval objects with digest + timestamp; evidence packet requirement; one accountable owner per handoff.
- **Information disclosure**: shared-screen states-only; notification redaction; cross-role least privilege; prompt-injection egress discipline.
- **Denial of service**: attention fatigue (silent-by-default, tiered escalation); loop waste (router denial); cost explosion (budgets); source outage (visible failure, no stale substitution).
- **Elevation of privilege**: routine scope limits; connector least privilege; router recommends only; clients render contracts only.
- **Prompt injection**: external content is untrusted data, never instructions; consequential actions need explicit approval; no credentials in prompt context.
- **Stale-state manipulation**: live re-read before consequence; freshness stamps; unknown on observation failure.
- **Approval fatigue**: exact target/effect, risk classes, local auth for high-risk, approval rate metrics, no bulk approval.
- **Subagent deception**: subagent output is verification input; evidence required; orchestrator accountable; no proof, no done.

## Isolation Upgrade Path

- **Level 0 — Procedural** (current): doctrine-separated roles, shared runtime/filesystem, human discipline.
- **Level 1 — Filesystem/access discipline**: per-scope directories, path contracts, handoff-only cross-role access, audit logs.
- **Level 2 — Process/container isolation**: separate containers/users for high-risk roles, browser profiles, restricted mounts, credential isolation.
- **Level 3 — Capability tokens**: short-lived, scoped, per-task, auto-expiry.
- **Level 4 — Cryptographic evidence**: signed evidence packets, signed intents, tamper-evident logs, digest attestation.
- **Level 5 — Institutional-grade**: device attestation, hardware-backed keys, multi-party authorization, certification path.

## Deliverables

Asset register; trust boundary diagram; capability matrix; threat catalogue; attack trees; control matrix; security test suite; isolation upgrade roadmap.

## Exit Criteria

Every consequential action has a named threat and control; prompt injection, stale state, and approval fatigue explicitly modeled; procedural isolation documented and compensated; controls testable; posture defensible without overclaiming.

---

# 9. Phase 6 — Router Optimality

## Objective

Turn the router from plausible heuristic into empirically justified control policy.

## Research Question

> Under what conditions does the usage router improve accepted work while reducing cost, loops, repair, and attention cost?

## Policies to Compare

Unconstrained orchestration; cache-only; local heuristic policy; TypeSafe Jev backend; hybrid policy; learned policy (later).

## Objective Function

Maximize `accepted_work − human_repair_cost − attention_cost − financial_cost − loop_penalty − latency_penalty`, subject to: no unauthorized consequential action, no stale-state substitution, no hidden failure, no evidence omission. (A cheap wrong answer is not optimal.)

## Metrics

Accepted work rate; human repair cost; cost per accepted artifact; latency; loop rate; escalation precision/recall; false denial rate; stale-source error rate; attention cost; evidence completeness.

## Experimental Design

- **Stage 1 — Shadow logging** (current state supports this): extend router logs with outcome labels (outcome, human_repair, repair_time_minutes, cost_units, latency_seconds, attention_interruptions, evidence_complete).
- **Stage 2 — Offline replay**: replay historical decisions through alternate policies.
- **Stage 3 — Controlled live trials**: low-risk tasks under different policies; random assignment for eligible tasks only; never randomize consequential actions.
- **Stage 4 — Statistical evaluation**: acceptance rate, cost per artifact, repair rate, loop rate, latency, attention interruptions; Bayesian estimation for small samples.

## Router Guardrails

The router must never: approve consequential action; override approval boundaries; authorize spending/sending/deletion; hide failures; suppress evidence; substitute stale data; become a second orchestrator.

## Deliverables

Router policy specification; decision log schema; outcome label schema; experiment protocol; policy comparison report; cost-attention-acceptance dashboard; doctoral analysis chapter.

## Exit Criteria

Router decisions linked to outcomes; local, cache-only, and unconstrained baselines compared; Jev evaluated if approved; value supported by measured evidence.

---

# 10. Phase 7 — Integration into Doctoral Evidence

## Purpose

Convert engineering artifacts into a defensible thesis contribution.

## Doctoral Claim

> A doctrine-governed agent control plane, using formal state constraints, evidence packets, approval binding, consistency rules, and usage routing, can increase accepted work while reducing human repair, attention cost, and unsafe consequential action.

## Required Evidence Package

Formal specification; model checking/proof; invariant tests; consistency tests; idempotency tests; threat model; router experiment; operator scorecard; failure case studies; limitations section.

## Suggested Thesis Structure

1. Introduction: attention and authority in personal agent systems
2. Literature review: AI agents, human-AI interaction, safety, calm technology
3. Thesis: contracts around the model, not model intelligence alone
4. Architecture: operating, backend, and front-end control planes
5. Formal model: state machine, invariants, consistency, idempotency
6. Security model: threat boundaries and procedural isolation limits
7. Evaluation: routing, accepted work, repair, attention cost
8. Results
9. Limitations
10. Contribution and future work

---

# 11. Timeline Options

## Option A — 12-Week Engineering Fix

| Weeks | Phase |
|---:|---|
| 1 | Phase 0: Freeze contracts |
| 2–3 | Phase 1: Formal state machine |
| 3–4 | Phase 2: Invariant verification |
| 4–5 | Phase 3: Consistency model |
| 5–6 | Phase 4: Idempotency guarantees |
| 6–8 | Phase 5: Security threat model |
| 8–10 | Phase 6: Router shadow/replay evaluation |
| 11–12 | Phase 7: Integration and final report |

## Option B — 6-Month Doctoral Validation

Months 1–6: freeze contracts and glossary; state machine proof and invariant suite; consistency, idempotency, chaos testing; security threat model and boundary tests; router experiment with live low-risk tasks; doctoral write-up and evidence integration.

## Option C — 12–18 Month Full PhD Track

Months 1–3: specification, formal model, literature review. Months 4–6: state machine proofs, invariant tests. Months 7–9: consistency, idempotency, security formalization. Months 10–12: router experiments and operational metrics. Months 13–15: operator study, attention-cost measurement. Months 16–18: thesis writing, limitations, defense preparation.

---

# 12. Minimum Viable Fix vs Full PhD Fix

| Gap | Minimum Viable Fix | Full PhD Fix |
|---|---|---|
| State machine | Documented transition table and property tests | Model-checked proof with failure model |
| Invariants | CI tests for major invariants | Formal property suite plus chaos validation |
| Consistency | Server authoritative for approvals; eventual status | Formal consistency contract with multi-device fault injection |
| Idempotency | Idempotency keys for consequential actions | Full saga model with ambiguous-outcome verification tests |
| Security | Threat model and control matrix | Attack trees, capability formalism, isolation upgrade evaluation |
| Router | Shadow logs and heuristic review | Controlled comparison of policies with outcome metrics |

---

# 13. Immediate Next Actions

1. Create a `jarvis-formal-spec` repository.
2. Freeze the canonical state machine.
3. Write the canonical glossary.
4. Convert the doctrine into an invariant list.
5. Define the approval intent digest rule.
6. Define the consistency guarantee matrix.
7. Define the idempotency key schema.
8. Create the threat model document.
9. Extend router logs with outcome labels.
10. Build a test harness for mutated/expired approvals.
11. Build a chaos test for duplicate approval taps.
12. Build a stale-source test.
13. Build a delegation-without-proof test.
14. Build a shared-surface redaction test.
15. Produce the first router shadow report.

---

# 14. Definition of Done

1. The state machine has a formal specification.
2. Illegal transitions are shown to be unreachable under the defined failure model.
3. Core invariants are tested automatically.
4. Mutated or expired approvals cannot execute.
5. Multi-device state conflicts resolve deterministically.
6. Offline taps cannot become approvals.
7. Duplicate taps cannot create duplicate consequences.
8. Ambiguous execution becomes visible unknown or failed, not false completion.
9. Security boundaries and limitations are explicitly modeled.
10. Prompt injection, stale state, and approval fatigue are addressed.
11. The usage router is evaluated against baselines.
12. The evaluation measures accepted work, repair, cost, latency, loops, and attention cost.
13. The limitations remain honest.
14. The evidence supports the thesis.

---

# Final Recommendation

The fastest way to fix the gaps is not to add more features. The correct sequence is:

```text
Freeze the doctrine
→ Formalize the state machine
→ Turn doctrine into invariants
→ Define consistency and idempotency
→ Formalize security boundaries
→ Measure router performance
→ Integrate into doctoral evidence
```

That sequence turns J.A.R.V.I.S. from a strong architectural white paper series into a defensible doctoral-grade contribution.
