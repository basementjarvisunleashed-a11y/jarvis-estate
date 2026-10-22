# Phase 5 — Threat Catalogue

**Status:** v0.1-draft · **Date:** 2026-10-22
**Sources:** `ROADMAP.md` §8 (STRIDE + agent-specific rows, named controls);
`tests/PHASE-5-PLAN.md` (head-start note: honest limitations); `tests/PHASE-5-OPEN-QUESTIONS.md`
Q2, Q5, Q6 (answered 2026-10-22); `trust-boundaries.md`; `asset-register.md`;
`capability-matrix.md`; `tests/phase4/ambiguity-protocol.md` (P4-OP-5, Q2 carryover).

> **Governance.** Draft until HgX ratifies. Every threat: an ID, the
> assets and boundary it threatens, the control, and the Layer 2 test
> pointer. **(L)** marks a threat derived from an honest limitation
> (Q5) — a limitation written as a named threat with a compensating
> control, not a footnote.

---

## 1. Purpose

The catalogue is the estate's formal threat model: STRIDE rows plus
the four agent-specific threats, plus Q2's tool-plane truthfulness
(Tampering: false outcome reporting), plus Q5's honest limitations as
named threats. The roadmap's exit criterion demands each consequential
path have a named control; the catalogue is where the naming happens.

## 2. Spoofing

| ID | Threat | Boundary / Assets | Control | Layer 2 test pointer |
|---|---|---|---|---|
| T-1 | Fake approval: an approval decision forged or replayed by a non-HgX actor | TB-1, TB-2 / AR-2 | Device-bound session (`session-lifecycle.md`); intent digest binding; approval objects with digest + timestamp; single-use semantics | `test_session_replay_rejected`, `test_digest_mismatch_rejected` |
| T-2 | Fake source: a live source that is not the claimed authority | TB-6 / AR-6, AR-7, AR-9 | Source validation against allowlist; read-current at decision time | `test_unallowlisted_source_refused` |
| T-3 | Fake completion: a claim of done with no observed outcome | TB-4 / AR-10, AR-11 | Evidence verification: no proof, no done; orchestrator accountable | `test_unevidenced_claim_refused` |

## 3. Tampering

| ID | Threat | Boundary / Assets | Control | Layer 2 test pointer |
|---|---|---|---|---|
| T-4 | Mutated intent: approval granted for X, executed for Y | TB-2 / AR-2 | Digest binding of exact target+effect+scope+revision+expiry; changed scope voids approval (CM-3) | `test_mutated_intent_rejected` |
| T-5 | Artifact tampering: an artifact altered after production | TB-3 / AR-10 | Content digest on artifacts; revision-stable evidence references | `test_artifact_digest_mismatch_flagged` |
| T-6 | Log tampering: records altered to hide or rewrite history | TB-3, TB-7 / AR-12 | Append-only records; tamper-evident logging; one accountable owner per handoff | `test_log_append_only_enforced` |
| T-7 | Memory poisoning: durable memory corrupted by unverified writes | TB-4 / AR-12 | Provenance on memory writes; orchestrator-mediated reconciliation; no subagent writes direct to memory | `test_memory_write_requires_provenance` |
| T-8 | **False outcome reporting (Q2):** the tool plane reports success without executing, or failure after executing | TB-3 / AR-10, AR-11 | Read-after-write verification where the integration supports it; strongest-approval or manual execution where it doesn't (Phase 4 external-system classification) | `test_read_after_write_where_supported`, `test_strongest_approval_where_not` |

## 4. Repudiation

| ID | Threat | Boundary / Assets | Control | Layer 2 test pointer |
|---|---|---|---|---|
| T-9 | Denied authorship: an actor disowns an approval or an execution | TB-2, TB-3 / AR-2, AR-11 | Approval objects with digest + timestamp; evidence packet requirement; one accountable owner per handoff | `test_approval_object_is_non_repudiable` |

## 5. Information disclosure

| ID | Threat | Boundary / Assets | Control | Layer 2 test pointer |
|---|---|---|---|---|
| T-10 | Shared-surface exposure: restricted content rendered where others can see | TB-10 / AR-6, AR-7, AR-8 | States-only rendering on shared surfaces (INV-S5); cross-role least privilege | `test_shared_surface_redaction` |
| T-11 | Notification leakage: a hint that carries payload state | TB-9 / AR-1 | Notification redaction: hint carries pointer + state only, never the record | `test_notification_hint_shape` |
| T-12 | Cross-role leakage: a subject reads beyond its least privilege | TB-3, TB-5 / AR-6, AR-7 | Connector least privilege; the capability matrix (§4) as the enforcement vocabulary | `test_capability_condition_enforced` |
| T-13 | Prompt-injection egress: injected content steering data outward | TB-6 / AR-6, AR-7, AR-9 | Prompt-injection egress discipline: external content is untrusted data, never instructions; no credentials in prompt context | `test_injected_content_never_instruction` |

## 6. Denial of service

| ID | Threat | Boundary / Assets | Control | Layer 2 test pointer |
|---|---|---|---|---|
| T-14 | Attention exhaustion: HgX flooded by noise | TB-9 / AR-1 | Silent-by-default; tiered escalation; no bulk approval | `test_silence_by_default`, `test_no_bulk_approval` |
| T-15 | Loop waste: the router or an agent burns cycles without progress | TB-8 / AR-14 | Router denial of repeated no-progress action (INV-R2/R3) | `test_router_denies_loops` |
| T-16 | Cost explosion: unbounded spend on compute or connectors | TB-8, TB-5 / AR-13 | Budgets; conservative retry (no retry on unknown) | `test_budget_enforced` |
| T-17 | Source outage: a dead source rendered as current | TB-6 / AR-6, AR-7 | Visible failure; unknown on observation failure; no stale substitution | `test_outage_renders_unknown` |

## 7. Elevation of privilege

| ID | Threat | Boundary / Assets | Control | Layer 2 test pointer |
|---|---|---|---|---|
| T-18 | Routine scope creep: a routine doing what it was never granted | TB-3 / AR-10, AR-13 | Routine scope limits; capabilities expire; no standing consequential authority | `test_routine_scope_limited` |
| T-19 | Connector overreach: an integration touched outside its grant | TB-5 / AR-13 | Connector least privilege; custody boundaries TB-11/TB-12 for finance and comms | `test_connector_least_privilege` |
| T-20 | Router as approver: the usage router authorizing consequence | TB-8 / AR-2 | Router recommends only; the guardrails list from Phase 6's plan is adopted as a control here | `test_router_cannot_approve` |
| T-21 | Client as orchestrator: a device approving locally or inferring state | TB-1, TB-2 / AR-2, AR-10 | Clients render contracts only; no local approval; offline taps are gestures, not consent | `test_offline_tap_not_approval` |

## 8. Agent-specific threats

| ID | Threat | Boundary / Assets | Control | Layer 2 test pointer |
|---|---|---|---|---|
| T-22 | Prompt injection: external content treated as instructions | TB-6, TB-3, TB-4 / AR-2 | Untrusted-data discipline in every turn; consequential actions require explicit approval; no injected content becomes an instruction | `test_prompt_injection_scenarios` |
| T-23 | Stale-state manipulation: a raced or cached state becoming a consequence | TB-2 / AR-2 | Live re-read before consequence; freshness stamps; unknown on observation failure | `test_stale_state_cannot_consequence` |
| T-24 | Approval fatigue (attack): barrage of approvals degrading HgX's judgment | TB-2 / AR-1, AR-2 | Exact target+effect; risk classes; local auth for high-risk; approval rate metrics; no bulk approval | `test_approval_barrage_holds` |
| T-25 | Subagent deception: a subagent asserting completion without evidence | TB-4 / AR-11 | Subagent output is verification input; evidence required; orchestrator accountable; no proof, no done | `test_subagent_claim_requires_evidence` |

## 9. Honest limitations as named threats (Q5)

These threats exist *because* the estate is honest about its limits.
Each has a compensating control — the conversion Q5 ordered.

| ID | Threat | What it names | Control | Layer 2 test pointer |
|---|---|---|---|---|
| T-26 (L) | Unverified privacy claim: the deployment build's ZK work is protocol-shape only, not true zero-knowledge | / AR-4, AR-5 | **No privacy property is asserted in evidence.** No evidence packet, log, or report claims a privacy guarantee the build does not provide; production circuits are required before any such claim. | `test_no_privacy_property_asserted` — asserts the vocabulary is absent from all evidence outputs |
| T-27 (L) | Unmodeled fatigue dynamics: approval fatigue is instrumented (attention budget monitored) but not formally modeled — the controls' thresholds rest on judgment, not proof | TB-9, TB-2 / AR-1 | Instrumentation with human review: the attention budget is monitored and reviewed; thresholds are stated as operational judgment; no claim of a modeled fatigue curve. | Manual review procedure — marked non-mechanically-testable in `control-matrix.md` |
| T-28 (L) | Procedural isolation's ceiling: L0 cannot do what containers do — a compromised shared runtime defeats doctrine | all boundaries / all assets | Documented compensations (`control-matrix.md` §5): three-plane enforcement in the deployment build, key custody asserted in tests, sealed logged denials; plus the honest upgrade roadmap (`isolation-upgrade-roadmap.md`) | `test_plane_violation_blocked`, `test_key_custody_asserted` |

## 10. Cross-references

- `attack-trees.md` — AT-1…AT-4 work T-1, T-4, T-13/T-22, T-24 to the
  leaf control that stops them.
- `control-matrix.md` — every control here marked testable, with its
  verification method.
- `asset-register.md` — the assets each row threatens.
- `capability-matrix.md` — the control vocabulary (CM-1…CM-9).
- `session-lifecycle.md` — the foundation of T-1's control.

## 11. Version history

- **v0.1-draft — 2026-10-22.** First draft: T-1…T-25 STRIDE + agent-
  specific rows; T-8 false-outcome reporting (Q2); T-26(L)…T-28(L)
  honest limitations as named threats (Q5); every row with assets,
  boundary, control, and Layer 2 test pointer. Not ratified.
