# Phase 5 — Capability Matrix

**Status:** v0.1-draft · **Date:** 2026-10-22
**Sources:** `ROADMAP.md` §8 (the eight-field model); `tests/PHASE-5-PLAN.md`
(capability matrix deliverable); `tests/PHASE-5-OPEN-QUESTIONS.md` Q4
(answered 2026-10-22); `trust-boundaries.md` (TB-1…TB-15);
`asset-register.md` (AR-1…AR-15).

> **Governance.** Draft until HgX ratifies. **Reference, not ratification:**
> the contract-freeze paper's macaroon-lineage token shape (intent digest
> + device + expiry + single-use nonce) is used in §2 as a *reference*
> for the vocabulary — it is not a 1.0 contract and nothing here is
> ratified. Issuance, storage, and rotation mechanics are explicitly
> DEFERRED (Q4).

---

## 1. Purpose

The model is capability-based governance: every consequential action
must be expressible in one vocabulary. This document specifies the
eight-field capability format as the matrix's normative vocabulary
(Q4), then applies it: who may do what to which assets, under which
conditions, with which approval and evidence requirements.

## 2. The eight-field capability format (normative vocabulary)

A capability is an eight-tuple:

```text
capability := ( subject, action, object, scope, condition,
                expiry, approval requirement, evidence requirement )
```

| # | Field | Meaning | Example |
|---|---|---|---|
| 1 | `subject` | Who acts (a named role or holder) | `orchestrator`, `HgX`, `money-custodian` |
| 2 | `action` | What is done (a verb from §3) | `execute.consequential` |
| 3 | `object` | What it acts on (an asset ID) | `AR-5` |
| 4 | `scope` | How much of the object | `account:<exact>, amount:<exact>, date:<exact>` |
| 5 | `condition` | Under what circumstances | `session=enrolled-unrevoked AND digest=match` |
| 6 | `expiry` | When the capability lapses | `approval.intent.expiry` |
| 7 | `approval requirement` | Whose approval, of what shape | `HgX explicit, exact target+effect` |
| 8 | `evidence requirement` | What proof must exist after | `evidence packet with execution observation` |

**Field semantics (CM rules):**

- **CM-1.** A capability whose `condition` is false is not a
  capability at all — it cannot be invoked, only re-requested.
- **CM-2.** An `expiry` that has passed voids the capability; expiry
  is evaluated at decision time, not render time.
- **CM-3.** The `approval requirement` binds the exact `action` +
  `object` + `scope` + `condition` + `expiry`; a changed `scope`
  invalidates the approval (mutated-intent rule, `threat-catalogue.md` T-4).
- **CM-4.** The `evidence requirement` names the evidence packet
  content that must exist before the work can be called complete
  (INV-C1, INV-E1 from Phase 2).

**Token-shape reference (Q4).** The contract-freeze work's
macaroon-lineage shape — `intent digest + device + expiry +
single-use nonce` — is cited here as prior art for the *vocabulary*:
it maps onto fields 1/5/6 (`device` ≈ subject+condition,
`intent digest` ≈ condition, `expiry` ≈ expiry,
`single-use nonce` ≈ a condition on one use). It is a reference only.
Whether capabilities are ever minted as tokens is L3 isolation work
(`isolation-upgrade-roadmap.md`), explicitly deferred: issuance,
storage, and rotation mechanics are **not specified in this phase**.

## 3. Action verbs

`read` · `write.memory` · `render.status` · `notify.hint` ·
`request.approval` · `grant.approval` (HgX only) ·
`execute.reversible` · `execute.consequential` · `verify` ·
`compensate` · `delegate` · `attest` (evidence, orchestrator only) ·
`seal` (append to tamper-evident records) · `fetch.external`

## 4. The matrix (subjects × assets)

Each cell: permitted actions, with the eight fields summarized.
"—" means no capability exists for that subject–asset pair.

| Subject / Asset | AR-1 attention | AR-2 approval authority | AR-3 credentials | AR-4 health | AR-5 finance | AR-6/AR-7 legal/comms | AR-8 betting | AR-9 identity | AR-10/11/12 artifacts/evidence/logs | AR-13 connectors | AR-14/15 runtime/router |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **HgX** | — | `grant.approval` (any exact intent; expiry=rendered) | — | — | — | — | — | — | `read` | — | — |
| **Orchestrator** | `notify.hint` (conditions: TB-9 rules; silent-by-default) | `request.approval` (exact target+effect; no bulk) | — | — | — | — | — | `read` (condition: decision-time need) | `attest`, `seal`, `read` | `execute.reversible` (least privilege) | `read` |
| **Money custodian** (TB-11) | — | — | — | — | `execute.consequential` (condition: HgX explicit approval of exact amount+account+date; evidence: packet with observation) | — | — | — | `attest` (own packets) | `execute.reversible` (financial integrations) | — |
| **Calendar/comms custodian** (TB-12) | — | — | — | — | — | `read`, `write.memory` (condition: estate routing via custodian) | — | — | `attest` (own packets) | `execute.reversible` (comms integrations) | — |
| **Health service** (TB-13) | `notify.hint` (condition: its own sealed channel) | — | — | `read`, `attest` (condition: sealed; no content crosses) | — | — | — | — | `attest` (own packets) | `execute.reversible` (health integrations) | — |
| **Research lab** (TB-15) | — | — | — | — | — | — | — | — | `attest` (own archive) | — | — |
| **Subagents** (TB-4) | — | — | — | — | — | — | — | — | `attest` (own evidence to orchestrator) | `execute.reversible` (task-scoped, orchestrator-delegated) | — |
| **Usage router** (TB-8) | — | — | — | — | — | — | — | — | `read` (decision-time facts only) | — | `read` (AR-15) |

**Notes on the matrix:**

- **CM-5.** No subject holds `execute.consequential` except the money
  custodian, and then only under TB-11's exact-approval condition.
  The orchestrator delegates but does not itself execute
  consequential actions outside custody boundaries — every
  consequential execution names its approver (HgX) and its executor.
- **CM-6.** No subject holds `grant.approval` except HgX. The
  orchestrator and custodians may `request.approval`; they may never
  self-approve.
- **CM-7.** The live-location custody boundary (TB-14) has no row in
  this matrix: its custodian is never named (Q6 secrecy constraint).
  The model records the boundary's existence and crossing rules in
  `trust-boundaries.md`; it does not record who holds it.
- **CM-8.** The health service's `attest` capability is confined to
  its own packets; TB-13's seal means its evidence never appears in
  another room's packet or report.
- **CM-9.** `notify.hint` is the only attention action in the model;
  there is no capability for bulk, rich, or state-carrying
  notification to HgX.

## 5. Numbered claims

- **CM-10.** The eight-field format (§2) is the matrix's normative
  vocabulary; every capability in this model is stated in those
  eight fields.
- **CM-11.** Every consequential action in the matrix names an
  `approval requirement` and an `evidence requirement`; neither is
  ever "none" for a consequential action.
- **CM-12.** Capabilities are conditions, not possessions: a false
  condition or a passed expiry means the action may not be taken
  (CM-1, CM-2).
- **CM-13.** Issuance, storage, and rotation mechanics for
  capabilities-as-tokens are explicitly deferred to L3 isolation
  work on HgX's word — this document specifies the vocabulary, not
  the mint (Q4).
- **CM-14.** The macaroon-lineage token shape from the contract-freeze
  work is cited as a reference for the vocabulary only; it is not
  adopted as a 1.0 contract and nothing in it is ratified by this
  document.

## 6. Open points

- **P5-OP-3 — Custodian subject names.** The matrix uses the role
  names "money custodian" and "calendar/comms custodian" because
  HgX's custody orders name Money Bot and Tickler Bot; it uses
  "health service" and "research lab" for TB-13/TB-15. **Needs
  HgX's word** on whether the operational bot names should appear
  verbatim in the formal model.
- **P5-OP-4 — Approval-to-session binding.** Whether `grant.approval`
  binds to the presenting `device_session_id` (so a stolen approval
  hint cannot be tapped from another session) is unspecified here.
  Recommendation: yes, as a `condition` field entry. **Needs HgX's
  word** before it becomes CM law.

## 7. Cross-references

- `asset-register.md` — AR-1…AR-15, the objects.
- `trust-boundaries.md` — TB-1…TB-15, where each capability operates.
- `session-lifecycle.md` — the `condition: session=enrolled-unrevoked`
  foundation (Q1).
- `threat-catalogue.md` — the threats each row is meant to defeat.
- `control-matrix.md` — every control marked testable against these
  capability rows.
- `isolation-upgrade-roadmap.md` — L3, where tokens would be minted.

## 8. Version history

- **v0.1-draft — 2026-10-22.** First draft: eight-field vocabulary
  (CM-1…CM-4), action verbs, the matrix, claims CM-10…CM-14; Q4
  baked in (reference cited, issuance/storage/rotation deferred);
  P5-OP-3, P5-OP-4 recorded. Not ratified.
