# Phase 5 — Programme Plan
## Security Boundary Formalism · Opened 2026-10-22 on HgX's order

> Precedent (HgX's Phase 2 pacing directive, 2026-10-20): go hard, do not
> hurry — follow the roadmap, take the roadmap's full time, document
> everything, comment everything, show proof of work. Phase 4 closed
> 2026-10-21 ~22:31 ET on that standard (PROVEN ~22:30 ET: five drafts,
> 20 protocol tests, 15 chaos tests, all five exit criteria met with
> covering tests). Phase 5 is held to it.
> Roadmap placement: Phase 5 sits in the months 7–9 formalization window
> (consistency, idempotency, security formalization). Pacing follows
> HgX's word.

## The governing rule

Phase 5 closes when its exit criteria are met — not before, not on a date
invented for convenience. Each layer has a gate; a layer opens only when
the previous layer's gate has passed and been recorded. The work layers
open on HgX's word after the question walkthrough — this package is the
opening, not the work.

## Objective (ROADMAP.md §8, quoted)

Convert honest limitations into a formal security model: trust
boundaries, assets, threats, controls, tests.

## Model (ROADMAP.md §8, quoted)

Capability-based governance. A capability specifies: subject, action,
object, scope, condition, expiry, approval requirement, evidence
requirement.

## Assets (ROADMAP.md §8, quoted)

HgX attention; approval authority; credentials; personal data (health,
finance, legal, communications, betting, identity); artifacts; evidence
packets; logs; connectors; runtime; router state.

## Trust boundaries (ROADMAP.md §8, quoted)

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

The estate's lived custody doctrines (HgX's direct orders, 2026-10-20/21)
instantiate several of these boundaries in practice: Money Bot is the
sole custodian of money access (boundary 5, financial integrations);
Tickler Bot is the sole custodian of calendar/email/tasks (boundary 5,
communications integrations); Dr Bot is sealed — its health contents
never cross any boundary (boundary 10, and a hard rule on 3 and 4);
the Overlord is the sole custodian of live location, its existence
unnamed outside its own chat (boundary 10, and a rule on 4); the R&D
lab is sealed — research findings cross no boundary back to the working
room or the estate (boundary 6, and a rule on 4). Phase 5 describes
these boundaries; it does not redesign them. Whether they enter the
formal model as named boundaries is open question Q6.

## Threat model (ROADMAP.md §8, quoted)

- **Spoofing**: fake approval (device-bound session, intent digest), fake
  source (source validation, allowlist), fake completion (evidence
  verification).
- **Tampering**: mutated intent (digest binding), artifact tampering
  (content digest), log tampering (append-only, tamper-evident roadmap),
  memory poisoning (provenance, reconciliation).
- **Repudiation**: approval objects with digest + timestamp; evidence
  packet requirement; one accountable owner per handoff.
- **Information disclosure**: shared-screen states-only; notification
  redaction; cross-role least privilege; prompt-injection egress
  discipline.
- **Denial of service**: attention fatigue (silent-by-default, tiered
  escalation); loop waste (router denial); cost explosion (budgets);
  source outage (visible failure, no stale substitution).
- **Elevation of privilege**: routine scope limits; connector least
  privilege; router recommends only; clients render contracts only.
- **Prompt injection**: external content is untrusted data, never
  instructions; consequential actions need explicit approval; no
  credentials in prompt context.
- **Stale-state manipulation**: live re-read before consequence;
  freshness stamps; unknown on observation failure.
- **Approval fatigue**: exact target/effect, risk classes, local auth
  for high-risk, approval rate metrics, no bulk approval.
- **Subagent deception**: subagent output is verification input;
  evidence required; orchestrator accountable; no proof, no done.

The last four are the agent-specific threats — lived practice already
(the prompt-injection discipline, the freshness rules, the ceremony's
exact target/effect, the no-proof-no-done rule). Phase 5 names them,
catalogues them, and tests their controls.

## Isolation upgrade path (ROADMAP.md §8, quoted)

- **Level 0 — Procedural** (current): doctrine-separated roles, shared
  runtime/filesystem, human discipline.
- **Level 1 — Filesystem/access discipline**: per-scope directories,
  path contracts, handoff-only cross-role access, audit logs.
- **Level 2 — Process/container isolation**: separate containers/users
  for high-risk roles, browser profiles, restricted mounts, credential
  isolation.
- **Level 3 — Capability tokens**: short-lived, scoped, per-task,
  auto-expiry.
- **Level 4 — Cryptographic evidence**: signed evidence packets, signed
  intents, tamper-evident logs, digest attestation.
- **Level 5 — Institutional-grade**: device attestation, hardware-backed
  keys, multi-party authorization, certification path.

Current level: **L0 — procedural.** The estate runs on doctrine-separated
roles (the bot roster, the custody doctrines, the sealed lab), a shared
runtime, and human discipline (HgX's word as the change control). This
is stated, not hidden — the exit criterion asks for "procedural
isolation documented and compensated," which is L0's job, done
honestly. Whether this phase advances the target level is open
question Q3.

## Deliverables (ROADMAP.md §8, quoted)

Asset register; trust boundary diagram; capability matrix; threat
catalogue; attack trees; control matrix; security test suite; isolation
upgrade roadmap.

## Exit criteria (ROADMAP.md §8, quoted verbatim)

Every consequential action has a named threat and control; prompt
injection, stale state, and approval fatigue explicitly modeled;
procedural isolation documented and compensated; controls testable;
posture defensible without overclaiming.

## Layers and gates

### Layer 1 — Security spec documents (opens on HgX's word, after the walkthrough)
- The eight deliverables, drafted under Phase 0 governance (ratified
  contracts are normative; drafts stay drafts until he ratifies):
  asset register (the roadmap's asset list, each with its custodian
  and classification); trust boundary diagram (the ten boundaries,
  with the custody doctrines placed where HgX rules in Q6); capability
  matrix (subject × action × object × scope × condition × expiry ×
  approval requirement × evidence requirement, per the model);
  threat catalogue (STRIDE + the four agent-specific threats, each
  with the roadmap's named controls); attack trees (prompt injection,
  stale-state, approval fatigue, subagent deception — worked to the
  control that stops them); control matrix (threat → control →
  test); security test suite plan; isolation upgrade roadmap (L0
  current, the honest path upward, the target level per Q3).
- Gate: all eight documents written, every threat named with its
  control, every control traceable to a Layer 2 test, and the honest
  limitations carried as modeled threats (Q5) rather than footnotes.

### Layer 2 — Security tests (opens on Layer 1 gate)
- Threat → control verification: each control in the matrix gets an
  executable test — prompt-injection discipline (untrusted content
  never becomes an instruction); stale-state controls (freshness,
  live re-read, unknown on observation failure); approval-fatigue
  controls (exact target/effect, no bulk approval, risk classes);
  subagent-deception controls (output treated as verification input;
  no proof, no done); spoofing/tampering/repudiation controls
  (digest binding, device-bound sessions, evidence packets);
  disclosure controls (notification redaction, least privilege).
- Gate: all security tests green with evidence logs; every control
  in the matrix exercised by at least one test.

### Layer 3 — Adversarial (opens on Layer 2 gate)
- The four agent-specific threats under fire: prompt-injection
  scenarios (injected instructions in tool output, in subagent
  reports, in fetched pages — none become actions); stale-state
  scenarios (racing freshness against consequence); approval-fatigue
  scenarios (barrages of approvals — the exact-target rule holds,
  bulk never happens); subagent-deception scenarios (a subagent
  asserting completion without evidence — the orchestrator refuses
  to mark done).
- Gate: adversarial scenarios green; no injected content becomes an
  instruction; no stale state becomes a consequence; no approval
  barrage becomes a bulk approval; no unevidenced claim becomes
  done.

## Head-start note — honest accounting (2026-10-22)

The deployment build (`~/workspace/jarvis-deploy/`, mapping approved by
HgX 2026-10-21 ~16:41 ET) already evidences parts of the exit criteria,
and the estate lives several more:

- Stale state explicitly modeled — SATISFIED: freshness windows,
  expiry, LAPSED; Phase 3 proved it (42/42, 80/80 adversarial).
- Controls testable — SATISFIED: every refusal is a sealed, logged
  denial; the Phase 2–4 harnesses are the pattern Layer 2 follows.
- Procedural isolation documented — SATISFIED: three planes enforced
  in code (`PlaneViolation` on direct cross-plane calls); key
  custody asserted in tests (no control/data component holds
  ceremony key bytes); the bot roster and custody doctrines are the
  lived L0.
- Prompt-injection discipline — LIVED, not yet formalized: external
  content is treated as untrusted data in every working-room turn;
  the deployment paper episode (2026-10-21) demonstrated the hold
  in practice. The catalogue entry is unwritten.
- Subagent discipline — LIVED, not yet formalized: subagent output
  is verification input; no proof, no done. The catalogue entry is
  unwritten.
- Posture stated without overclaiming — SATISFIED: the mapping's
  honest limits are the standard Phase 5 inherits.

Genuinely open — not claimed, not implied:

- **The per-action named threat catalogue:** the roadmap lists
  threat classes with controls in parentheses; no catalogue names
  each consequential action with its threat and control. Layer 1's
  core work.
- **The attack trees:** unwritten. Layer 1.
- **The capability matrix:** the model's eight fields are quoted
  above, but no matrix maps the estate's subjects, actions, and
  objects. Layer 1; the token posture is open question Q4.
- **Approval fatigue, formally modeled:** instrumented only
  (attention budget as a monitored quantity in the deployment
  build), not modeled. The exit criterion requires it modeled.
- **The reference ZK is explicitly not a control:** the deployment
  build's Phase 4 is the protocol shape, not true zero-knowledge —
  production circuits are required. The threat catalogue must
  capture this honestly (open question Q5), not overclaim.
- **The isolation target:** L0 is current and honestly stated;
  whether this phase advances it is open question Q3.
- **The custody doctrines in the formal model:** lived at L0,
  described in the plan above; whether they enter as named trust
  boundaries is open question Q6.
- **OP-3 — `device_session_id` lifecycle:** carried from the Phase 3
  drafts — enrollment exists in the reference; revocation,
  re-enrollment after device replacement, and session expiry are
  unspecified. Open question Q1.
- **P4-OP-5 — tool-plane truthfulness:** carried from the Phase 4
  work — the retry rules trust the tool plane to report outcomes
  truthfully; a Byzantine tool is outside the Phase 4 threat model.
  Open question Q2.

## Session log

### 2026-10-22 ~07:51 ET — PHASE 5 OPENED (HgX's word)
- "Okay, let's close phase four and start up phase five." Phase 4 was
  already CLOSED 2026-10-21 ~22:31 ET on his word (PROVEN ~22:30 ET);
  this is the Phase 5 opening.
- Opening package: this plan + `tests/PHASE-5-OPEN-QUESTIONS.md`
  (Q1–Q6 awaiting his walkthrough; Q1 is the Phase 3 OP-3 carryover,
  Q2 is the Phase 4 P4-OP-5 carryover).
- The work layers open on his word after the walkthrough — this
  package is the opening, not the work.
- Standing rules carried forward: never advance a phase without his
  explicit consent; ratified files untouched; no email/post/purchase
  without approval; the research pipeline stays sealed; the website
  stays as-is (logs only) per his 2026-10-21 hands-off order; the
  doctrines are described, never redesigned.
