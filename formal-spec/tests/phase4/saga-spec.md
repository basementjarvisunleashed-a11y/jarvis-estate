# Phase 4 — Governed Saga Specification

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §7 (transaction pattern); `tests/PHASE-4-OPEN-QUESTIONS.md`
(Q1, Q5 — answered by HgX 2026-10-21 ~18:24–18:31 ET);
`tests/phase3/sequence-diagrams.md` (the six-step ceremony);
`idempotency-key-spec.md`; `execution-record-spec.md`.

> **Governance.** Draft until HgX ratifies. Normative over the reference
> implementation where they disagree.

---

## 1. Purpose

The governed saga is the transaction pattern for consequential work in
an estate with no assumed distributed transactions: prepare, approval,
execute, verify, record evidence, compensate. It governs the six-step
ceremony (PROPOSE→RENDER→APPROVE→BIND→EXECUTE→ATTEST) — EXECUTE is the
at-most-once point, and everything in this spec extends outward from it.

## 2. The saga steps

### 2.1 Saga rules

1. **S1.** The saga is: **prepare → approval → execute → verify →
   record evidence → compensate** (if approved and possible). No
   step skipped, no step reordered — the saga is the only path from
   intent to settled effect.
2. **S2.** Preparation needs no approval. Preparation is reversible
   work (drafts, staging, calculation); it carries no consequential
   force.
3. **S3.** Approval binds the exact target and effect. The six-step
   ceremony is the approval path; the approval's digest is the
   eight-field binding (Phase 2 Q3).
4. **S4.** Execution needs a valid approval and fires **at most once
   per idempotency key** (ER2). An execution request without a valid
   approval is refused; a duplicate execution request returns the
   existing record.
5. **S5.** Verification follows the integration class (see
   `ambiguity-protocol.md` §3): execute-then-verify where the
   integration supports it; failed verification → `execution_failed`
   or `execution_unknown`.
6. **S6 (Q5 ruling).** A consequential compensation is a **fresh
   ceremony**: a new intent with its own digest, its own approval, and
   its own idempotency key. The original approval bound a different
   target and a different effect — it cannot authorize the undo.
7. **S7 (Q1 ruling).** For worker-prepared intents, the **orchestrator
   signs after recomputing and validating** the worker-prepared
   digest. The worker's authorship is recorded in the intent's
   provenance fields; the signature is who vouches. One accountable
   signer — the single-writer discipline (Phase 3 Q1).
8. **S8.** **No silent rollback of consequential effects.** Every
   compensation is an intent, proposed, approved, executed, and
   attested — or it does not happen.

### 2.2 Compensation

- Non-consequential compensation (reversible preparation) may ride
  the saga that prepared it — S2's reversibility covers it.
- Consequential compensation (restoring, revoking, undoing a settled
  effect) is a new saga under S6: new intent, new digest, new
  approval, new key, new record.
- A compensation intent whose target is a settled effect names the
  original record as its `approval_ref` antecedent — provenance, not
  authorization.

## 3. Custody

Financial transfers sit under the Money Bot's sole custody (HgX's
direct order, 2026-10-20). The saga names the custodian in the
execution record's provenance; it never routes around custody. The
estate's integrations are not yet inventoried against the
classification (P4-OP-1); until they are, financial transfers are
treated as the highest-risk row: strongest verification, conservative
retry, manual execution where verification is impossible.

## 4. Cross-references

- `idempotency-key-spec.md` — the key the saga executes under.
- `execution-record-spec.md` — the record the saga transitions.
- `retry-policy-matrix.md` — per-class retry posture inside the saga.
- `ambiguity-protocol.md` — verification and unknown-state handling.
- `tests/phase3/sequence-diagrams.md` — the six-step ceremony the
  saga governs.

## 5. Open points

- **P4-OP-1 — External-system inventory.** The roadmap's eight
  classification rows are quoted in the plan; the estate's actual
  integrations are not yet inventoried against them (which support
  native idempotency keys, which support read-after-write, which are
  opaque). Estate work beyond the spec — the saga is written to be
  correct for all eight rows regardless.

## 6. Version history

- **v0.1-draft — 2026-10-21.** First draft: S1–S8 with Q1 (orchestrator
  signs worker-prepared digests) and Q5 (fresh ceremony for
  consequential compensation) baked in; custody note. Not ratified.
