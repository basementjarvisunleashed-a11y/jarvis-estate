# Phase 5 — Control Matrix

**Status:** v0.1-draft · **Date:** 2026-10-22
**Sources:** `ROADMAP.md` §8 (named controls); `tests/PHASE-5-PLAN.md`
(head-start: lived vs formalized); `tests/PHASE-5-OPEN-QUESTIONS.md` Q2, Q3, Q5, Q6
(answered 2026-10-22); `threat-catalogue.md` (T-1…T-28); `attack-trees.md`
(AT-1…AT-4); `session-lifecycle.md`; `capability-matrix.md`.

> **Governance.** Draft until HgX ratifies. Every control is marked
> **testable** (with its Layer 2 test pointer) or honestly marked
> **non-mechanically-testable** (with its verification method). A
> control without one of those marks does not belong in this matrix.

---

## 1. Purpose

The threat catalogue names threats; this matrix names what stops them
and how we will know. Threat → control → test. The exit criterion
asks for "controls testable" and "posture defensible without
overclaiming" — the testability marks are where that honesty lives.

## 2. The matrix

| Control | Threats | Description | Testability |
|---|---|---|---|
| C-1 | T-1 | Unknown `device_session_id` refused before any other check | Testable — `test_session_replay_rejected` |
| C-2 | T-1 | Revoked session kills authority immediately (SL-14) | Testable — `test_revoked_session_rejected` |
| C-3 | T-1 | Expired session kills authority (SL-15) | Testable — `test_expired_session_rejected` |
| C-4 | T-1, T-4, AT-1, AT-2, AT-4 | Intent digest binds exact target+effect+scope+revision+expiry; any change voids the approval | Testable — `test_digest_mismatch_rejected`, `test_mutated_intent_rejected` |
| C-5 | T-1 | Single-use approval records: duplicate decision returns the existing record, never a second execution | Testable — `test_duplicate_approval_idempotent` |
| C-6 | AT-1 | Approval cards render exact target+effect+scope+expiry from the digest-bound intent | Testable — `test_card_renders_digest_bound_fields` |
| C-7 | T-1, T-21 | Offline taps are gestures, never consent: no authoritative approval without server validation | Testable — `test_offline_tap_not_approval` |
| C-8 | T-4, AT-2 | Approval expiry evaluated at decision time; expired approvals unusable | Testable — `test_expired_approval_rejected` |
| C-9 | T-4, T-23, AT-2 | Server re-validates intent digest + session + expiry at decision time (TB-2) | Testable — `test_decision_time_revalidation` |
| C-10 | T-5 | Artifact content digests; evidence references revision-stable | Testable — `test_artifact_digest_mismatch_flagged` |
| C-11 | T-22, AT-3 | External content is untrusted data, never instructions (TB-6) | Testable — `test_injected_content_never_instruction`, `test_prompt_injection_scenarios` |
| C-12 | T-13, T-22, AT-3 | Tool output is verification input; instructions cannot arrive via the data path (TB-3) | Testable — `test_tool_output_never_instruction` |
| C-13 | T-25, AT-3 | Subagent output is verification input; the orchestrator executes no instructions found in data (TB-4) | Testable — `test_subagent_claim_requires_evidence`, `test_subagent_output_never_instruction` |
| C-14 | T-11, AT-3 | Notification redaction: hints carry pointer + state only, never the record | Testable — `test_notification_hint_shape` |
| C-15 | T-10, AT-3 | States-only rendering on shared surfaces (INV-S5) | Testable — `test_shared_surface_redaction` |
| C-16 | T-13, AT-3 | No credentials in prompt context; vault boundary TB-7 | Testable — `test_no_credential_in_context` |
| C-17 | T-14, AT-4 | Silent-by-default; tiered escalation | Testable — `test_silence_by_default` |
| C-18 | T-14, T-24, AT-4 | No bulk approval: each intent approved singly | Testable — `test_no_bulk_approval` |
| C-19 | T-24, AT-4 | Risk classes; high-risk requires local auth and exact rendering | Testable — `test_high_risk_requires_local_auth` |
| C-20 | T-27, AT-4 | Attention budget monitored with human review; thresholds stated as judgment, not a modeled curve | **Non-mechanically-testable** — verification: periodic human review of the attention-budget log against stated thresholds (procedure documented in Layer 2) |
| C-21 | T-9 | Approval objects with digest + timestamp; one accountable owner per handoff | Testable — `test_approval_object_is_non_repudiable` |
| C-22 | T-6 | Append-only records; tamper-evident logging | Testable — `test_log_append_only_enforced` |
| C-23 | T-7 | Memory writes require provenance; orchestrator-mediated reconciliation | Testable — `test_memory_write_requires_provenance` |
| C-24 | T-8 | Read-after-write verification where supported; strongest-approval or manual execution where not (Q2) | Testable — `test_read_after_write_where_supported`, `test_strongest_approval_where_not` |
| C-25 | T-15, T-16 | Router denial of repeated no-progress action; budgets; no retry on unknown | Testable — `test_router_denies_loops`, `test_budget_enforced` |
| C-26 | T-17, T-23 | Live re-read before consequence; freshness stamps; unknown on observation failure | Testable — `test_stale_state_cannot_consequence`, `test_outage_renders_unknown` |
| C-27 | T-18, T-19, T-20 | Routine scope limits; connector least privilege; router recommends only | Testable — `test_routine_scope_limited`, `test_connector_least_privilege`, `test_router_cannot_approve` |
| C-28 | T-26 | No privacy property asserted in evidence (protocol-shape ZK is not a control) | Testable — `test_no_privacy_property_asserted` (vocabulary-absence assertion over evidence outputs) |
| C-29 | T-2 | Source allowlist validation | Testable — `test_unallowlisted_source_refused` |
| C-30 | T-3 | No proof, no done: unevidenced completion claims refused | Testable — `test_unevidenced_claim_refused` |
| C-31 | TB-11/TB-12/TB-13/TB-14/TB-15 | Custody-boundary enforcement: each doctrine's crossing rules hold as stated; sealed means sealed | Partially testable — crossing-rule unit tests where mechanical (`test_money_custody_exact_approval`); **non-mechanically-testable** where enforcement is doctrinal: verification = HgX's word as change control + review (see §5) |

## 3. Non-mechanically-testable controls (honest marks)

- **C-20.** The attention budget is an instrumented quantity with
  human-reviewed thresholds. No test can prove a fatigue curve; the
  verification is the review procedure itself. Marked so nobody
  mistakes instrumentation for modeling (T-27).
- **C-31 (doctrinal part).** At L0, custody enforcement is discipline
  plus HgX's word. A test can check that the money-approval shape is
  exact; no test can check that nobody whispered outside the room.
  The verification method is the change-control discipline (§5) and
  periodic review.

## 4. Numbered claims

- **C-1.** Every threat in `threat-catalogue.md` (T-1…T-28) maps to at
  least one control in this matrix.
- **C-2.** Every control is marked testable with a Layer 2 test
  pointer, or honestly marked non-mechanically-testable with its
  verification method — there is no third category.
- **C-3.** The Q5 controls (C-20, C-28, §5) convert the honest
  limitations into the model: unverified privacy claims,
  unmodeled fatigue dynamics, and the L0 ceiling each have a named
  compensating control.
- **C-4.** The Q2 control (C-24) is the Phase 4 external-system
  classification applied as a threat control: verify where supported,
  strongest-approval or manual execution where not.
- **C-5.** Every attack-tree leaf (AT-1…AT-4) resolves to a control
  in this matrix — no dangling leaves.

## 5. The L0 compensations (Q3)

At Level 0 — procedural isolation — the estate cannot enforce
boundaries by mechanism. The model compensates honestly:

1. **Doctrine as enforcement.** The bot roster, the custody
   doctrines (TB-11…TB-15), and HgX's word as change control are the
   L0 boundary enforcers. C-31 names them; the review procedure is
   the verification.
2. **Three-plane enforcement in the deployment build.** Direct
   cross-plane calls raise `PlaneViolation` — the one mechanical
   enforcement L0 has, and it is evidenced in the build's own tests.
3. **Key custody asserted in tests.** No control/data component holds
   ceremony key bytes — asserted, not assumed.
4. **Sealed, logged denials.** Every refusal in the model is a sealed,
   logged denial: the estate's denials are observable, which is what
   makes the Phase 2–4 harnesses the pattern Layer 2 follows.
5. **What L0 cannot do.** It cannot stop a compromised shared runtime,
   a coerced operator, or a side-channel. That ceiling is threat
   T-28(L), and the upgrade path that would raise it is
   `isolation-upgrade-roadmap.md`.

## 6. Open points

None new in this document; P5-OP-3 (custodian naming) and P5-OP-4
(approval-to-session binding) from `capability-matrix.md` apply to
C-31 and C-9 respectively.

## 7. Cross-references

- `threat-catalogue.md` — T-1…T-28, the threats this matrix answers.
- `attack-trees.md` — AT-1…AT-4, whose leaves resolve here.
- `session-lifecycle.md` — the foundation of C-1…C-3.
- `capability-matrix.md` — the enforcement vocabulary (CM-1…CM-9).
- `trust-boundaries.md` — TB-1…TB-15, where each control operates.
- `isolation-upgrade-roadmap.md` — what higher levels would mechanize.

## 8. Version history

- **v0.1-draft — 2026-10-22.** First draft: C-1…C-31 with testability
  marks; Q2/Q3/Q5 baked in; L0 compensations documented; C-20 and
  the doctrinal part of C-31 honestly marked non-mechanically-
  testable. Not ratified.
