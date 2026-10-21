# Canonical Work-State Machine — spec/state-machine.md

**DRAFT 0.1 — built 2026-10-21 on HgX's order; awaiting ratification.**
*Normative anchor: `spec/state-machine.tla` (TLA+, Phase 1 proved). Where this document and the TLA+ disagree, the TLA+ governs. Version: 0.1-draft.*

## 1. Purpose

The markdown reading of the twelve-state work-item machine (Paper IV v1.1 §6.1–§6.3; ROADMAP.md §0.4). This is a prose mirror of the formal model — it proves nothing; the TLA+ spec and its TLC proof obligations are the checkable truth.

## 2. The twelve states

| State | Meaning |
|---|---|
| `received` | Brief recorded; orchestrator has not accepted scope. No tools have run, no plan exists. |
| `accepted` | Orchestrator accepted the brief's scope (well-formed, in remit, authorised source). No execution yet. |
| `in_progress` | Bounded plan exists, tools selected, work underway. **All non-consequential execution lives here** (RD-1). Never completes from here. |
| `awaiting_approval` | Next operation is consequential; waiting on an exact approval intent (RD-2). No consequential effect may occur here except via the single guarded exit to `executing`. |
| `executing` | Valid, unexpired, digest-matched approval exists; the approved consequential action is underway. The **only** state from which consequential effects may be produced (RD-1). |
| `verifying` | Work claims completeness: artifact + evidence packet exist; acceptance test applied against **observed** output. The only state from which `completed` is reachable (F1). |
| `completed` | Acceptance passed against observed output, evidence attached. **Terminal.** Optimistic completion unreachable. |
| `blocked` | Stalled on a condition outside the item's control; recovery plausible, plan valid. Cause is provenance only (D6). |
| `failed` | Required source/permission/retry budget unavailable. **Terminal**; failure is visible by doctrine. |
| `paused` | Operator stopped the item by intent. Holds state and revision; resumption re-validates against live sources. |
| `unknown` | State cannot be established through observation — explicit rendered ignorance. Never rendered as operational (INV-S1). |
| `cancelled` | Ended without completion by decision (brief declined, approval denied, operator cancellation). **Terminal** and deliberate. |

Terminal (absorbing, F7): `completed`, `failed`, `cancelled`.

## 3. Transitions T1–T21

Guard (prose) is the Paper IV §6.2 condition; the formal guard is the TLA+ predicate. Effects list what the machine changes; everything else is unchanged.

| # | Source → Target | Firing event | Guard | Effects |
|---|---|---|---|---|
| T1 | `received → accepted` | `brief_accepted` | Brief well-formed, in scope, from an authorised source (operator or authorised routine) | — |
| T2 | `received → cancelled` | `brief_declined` ★ | Brief out of scope or unauthorised; reason recorded | — |
| T3 | `accepted → in_progress` | `plan_created` | Bounded plan exists with identified approval stops; tools selected | — |
| T4 | `in_progress → awaiting_approval` | `approval_requested` | `newIntent` is a well-formed intent, `newIntent.revision = revision`, `newIntent.expiry > now` | `approval_state=requested`; `intent=newIntent`; digests cleared; session authorised |
| T5 | `in_progress → blocked` | `failure_observed` (blocking) | Recovery plausible, plan remains valid | `blocked_cause` recorded |
| T6 | `in_progress → verifying` | `artifact_produced` **and** `evidence_packet_created` (joint) | Work claims completeness; acceptance test stated | `evidence_exists=TRUE`; `verification_method` set (provenance) |
| T7 | `in_progress → failed` | `failure_observed` | — | `failure_observed=TRUE`; `operator_pause=FALSE` |
| T8 | `blocked → in_progress` | `blockage_cleared` ★ | `source_freshness = "fresh"` — source-truth guards need fresh sources (PO-10) | `blocked_cause` cleared |
| T9 | `awaiting_approval → executing` | `approval_granted` | `approval_state="recorded"` ∧ `now < intent.expiry` ∧ digest recomputed = `intent_digest` (at transition time) ∧ `intent.revision = revision` ∧ session authorised ∧ `¬operator_pause` | — |
| T10 | `awaiting_approval → in_progress` | `approval_expired` ★ | `approval_state ∈ {requested, tapped, recorded}` ∧ `now >= intent.expiry` | `approval_state=expired` (item survives; expiry kills the intent, not the work — INV-A4, D5) |
| T11 | `awaiting_approval → cancelled` | `approval_denied` | — | `approval_state=denied` |
| T12 | `awaiting_approval → failed` | `failure_observed` | — | as T7 |
| T13 | `executing → verifying` | `execution_observed` | Observed result ∈ {success, failure} — dispatch without observation is **not** an exit | `execution_observed=result`; `evidence_exists=TRUE` |
| T14 | `executing → failed` | `failure_observed` | — | as T7 |
| T15 | `verifying → completed` | `acceptance_passed` | `evidence_exists` ∧ `acceptance_passed` ∧ `¬failure_observed` — the only road into `completed` (F1, INV-C1/C2/C5) | — |
| T16 | `verifying → failed` | `failure_observed` | Acceptance test failed or required evidence missing | `acceptance_passed=FALSE`; as T7 |
| T17 | any non-terminal → `failed` | `failure_observed` | `observation_status="observed"` (PO-4) — failure interrupts from anywhere, never completes | as T7 |
| T18 | any non-terminal → `paused` | `operator_paused` | `observation_status="observed"` — cannot pause what cannot be observed | `operator_pause=TRUE`. Mid-executing safe-point semantics: in-flight step brought to a safe point; no new consequential step (U-4 glossary; Phase 4 saga spec owns the full formalisation) |
| T19 | `paused → in_progress` | `operator_resumed` ★ | — | `operator_pause=FALSE`; `source_freshness="fresh"` (re-validated against live sources) |
| T20 | any non-terminal → `unknown` | `observation_unavailable` | — | `observation_status="unavailable"`; `operator_pause=FALSE` (PO-5: no asserted pause on an unobservable state) |
| T21 | `unknown → in_progress` | `observation_restored` ★ | `observation_status="unavailable"` — restored by **live re-read, never assumption**; resumes from recorded revision (F6, INV-S1/S4) | `observation_status="observed"`; `source_freshness="fresh"` |

★ = Phase 0 addition adopted under the §5.4 reconciliation decisions.

### Non-transition actions (approval machinery — not numbered transitions)

- **Operator taps approve (gesture):** `requested → tapped`, records `tap_digest` = what the operator actually saw. Not authority — the server must record (INV-A5).
- **Duplicate tap:** stutters — the recorded decision and execution state are returned as-is (INV-A6).
- **Server records approval:** the only path to `recorded`. Requires server validation of intent existence, expiry, digest match (`DigestOf(intent) = tap_digest` — a mutation between tap and record forces rejection, PO-3), permissibility, and session.
- **Time advance (Tick):** server clock only; bounded by `MaxNow` in the finite instance. `now < intent.expiry` is enforced for time to advance while `executing` (PO-2, fail closed).
- **Chain advance:** the seven custody links complete strictly in order (§5 below).

## 4. Idempotency and expiry rules

- **Idempotency key** (glossary, Paper IV §5.6): `hash(work_id, intent_id, intent_digest, action, target, scope, revision, operation_class)`. The server records the key's execution state and returns the recorded outcome on repeat — duplicate taps, duplicate grants, and network retries never create a second execution.
- **Tap ≠ authority:** a client tap is a gesture until the server records the decision (INV-A5). Offline taps can never record (PO-8).
- **Expiry (INV-A4):** intent expiry is a property of the intent, not a verdict on the work. An expired intent cannot authorise: T9's guard `now < intent.expiry` fails, and T10 returns the item to `in_progress` where a fresh intent may be issued. A recorded-but-expired approval is dead.
- **Expiry is expressed in server time** (Nat in the formal model; see the open interpretation note in `approval-digest.md` re: epoch-seconds vs ISO-8601).

## 5. Chain of custody

Paper I doctrine chain, Paper IV §3.1: Role → Live Source → Tool → Artifact → Evidence → Approval → Routine. Links complete strictly in order; skipping a stage is unreachable by construction. `paused`/`unknown` suspend custody (no link may be claimed while control is suspended or observation unavailable). Routine (link 7) is earned through evidenced completed transitions; repetition counting lives in the scheduler (U2/U4 interpretive anchors — see TLA+ notes).

## 6. Clock skew

**Δ = 60 seconds**, ratified by HgX 2026-10-19 (glossary U-5, decision D7, Paper IV §7.5#9; PO-2 fails at Δ = 300s). `now` is server time; all guards compare against it. A client-observed time may differ by at most Δ; any decision inside the skew window must be re-validated, never trusted. Instantiate `Delta <- 60` for model checking.

## 7. Forbidden transitions (Paper IV §6.3)

F1: →`completed` except via `verifying` · F2: `awaiting_approval→executing` without valid recorded approval · F3: `executing→completed` · F4: `in_progress→executing` · F5: `paused→executing` · F6: `unknown→any` except via `observation_restored` · F7: terminal states are absorbing · F8: `failed→completed` · F9: `verifying→executing`. Enforced by construction in the TLA+; TLC checks the temporal properties.

## 8. Liveness exclusion

**PO-12 (liveness: every approval request resolves; no item waits past `intent_expiry`) is explicitly out of scope for Phase 1 safety checking** (Paper IV §7.6, §7.8; TLA+ note). It requires fairness assumptions beyond the checked properties. T10 guarantees no item waits in `awaiting_approval` past expiry with no transition, but the positive liveness claim (grants eventually execute, observations eventually arrive) is not proved here.

## 9. Cross-reference

- Events vocabulary: `contracts/events.md` (19 events, envelope fields, naming resolutions).
- Terms: `contracts/glossary.md` (69 terms, 25 conflicts resolved).
- Contract schemas (DRAFT 0.1, this package): `contracts/approval-intent.schema.json`, `contracts/decision-packet.schema.json`, `contracts/evidence-packet.schema.json`, `contracts/artifact-manifest.schema.json`, `contracts/watchtower.schema.json`.
- Digest rule: `spec/approval-digest.md` (DRAFT 0.1, this package).
- Proof: `proofs/phase1-tlc-report.md` v1.1 (3,266,929 states, zero violations, six counterexample fixes).

> Promotion note (2026-10-21, on HgX's order "push all of it"): promoted to canonical placement as v0.1 draft. Formal ratification to v1.0.0 remains HgX's call. Open questions OQ-1..OQ-6 recorded in tests/staging/prescribed-files/BUILD-NOTES.md.
