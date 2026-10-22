# Phase 3 — Consistency Model Specification

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §6 (objective, hybrid table, architecture, conflict
table, exit criteria — quoted where noted); `tests/PHASE-3-PLAN.md` (layers,
gates, head-start note); `tests/PHASE-3-OPEN-QUESTIONS.md` (Q1–Q4 answered
2026-10-21 ~17:40–17:44 ET); `~/workspace/jarvis-deploy/phase1/pull.py` and
`phase2/contracts.py` (reference implementation only — the spec is normative);
`contracts/events.md` v1.1; glossary v1.0.0 (normative terms).

> **Governance.** The seven Phase 0/2 artifacts are normative and were not
> touched by this draft. Where this draft and the reference implementation
> disagree, the ratified contracts govern (same discipline as the TLA+ anchor
> in Phase 1). This document is a draft until HgX ratifies it.

---

## 1. Purpose and scope

This document instantiates the ROADMAP.md §6 hybrid consistency model for
HgX's estate under the four answered questions:

- **Q1:** the orchestrator is the deployment build's orchestrator loop
  (SERVE → SENSE → QUEUE → REVIEW → MAINTAIN) as the reference
  implementation; the iPhone is the trusted enrollment/command surface.
- **Q2:** iPhone + Watch are in scope for the consistency model; iPad, TV,
  Vision Pro are pull-only under their surface contracts.
- **Q4:** the deployment substrate is the reference implementation; this
  specification is normative.

The model defines, per operation class, the consistency guarantee each
surface receives — and the invariant this whole phase exists to defend:
**no device can become a source of truth.**

## 2. The governing principle

> **Status may be eventually consistent; consequence must be strongly
> consistent.** (ROADMAP.md §6)

"Status" is anything the estate reports about itself: state flags,
progress, cached reads. "Consequence" is anything the estate does to the
world: approvals recorded, executions fired, evidence sealed. The two are
never confused: a device may hold a slightly stale picture of status and
still be incapable of acting on it, because action requires the
orchestrator's strong, current validation.

## 3. The hybrid table — instantiated

| # | Operation class | Guarantee | In-scope surfaces | Notes |
|---|---|---|---|---|
| HC-1 | Status viewing | Eventual consistency **with freshness stamps** | iPhone, Watch | Every status payload carries its age (§4 of `freshness-policy.md`). A stale render is never presented as current. |
| HC-2 | Evidence viewing | Revision-stable reads | iPhone | Watch never pulls evidence bodies (substrate contract: `never: evidence_bodies`). Reads are pinned to a revision; the revision never mutates under the reader. |
| HC-3 | Approval decision | **Strong authoritative consistency** | iPhone, Watch | The decision is recorded exactly once by the orchestrator, against a live intent (exists, unexpired, digest matches). First valid decision recorded wins (`conflict-resolution.md` CR-2). |
| HC-4 | Consequential execution | **Linearized, single-writer execution** | Orchestrator only | No surface executes. The orchestrator is the single writer; effects are ordered through its event log. |
| HC-5 | Memory correction | Orchestrator-mediated reconciliation | iPhone (submit), orchestrator (reconcile) | Surfaces propose corrections; only the orchestrator reconciles durable contradictions (CR-5). |
| HC-6 | Live-source facts | Read-current at decision time | iPhone, Watch | Any decision citing a live fact re-reads the live source at decision time; cached values are inadmissible for decisions (CR-4). |
| HC-7 | Artifact download | Digest-verified bytes | iPhone | Bytes verify against the sealed manifest digest before use. Watch and pull-only surfaces do not download artifacts. |
| HC-8 | Notification delivery | At-least-once hints, **not authoritative state** | iPhone, Watch | A notification never changes a render. The recipient pulls current state; the hint is discarded after the pull (CR-6). |

### 3.1 Pull-only surfaces (iPad, TV, Vision Pro)

Per Q2, these surfaces are outside the consistency model's obligations and
inside their pull contracts (substrate `phase2/contracts.py`): tablet pulls
`full_evidence_packets`; TV pulls `state` (never `contents`, never
`approvals`); headset pulls `role_artifact_evidence_relationships`. Their
consistency guarantee is exactly HC-1/HC-2 as bounded by their contracts —
nothing more. The day one of them joins his pocket, its scope is decided
by change control, not by drift.

## 4. The single authoritative writer

The orchestrator (reference: the deployment build's loop — SERVE answers
pulls; SENSE ingests and updates baselines; QUEUE briefs engines; REVIEW
checks returns with provenance; MAINTAIN renews leases) is the estate's
only writer. Surfaces **may**: submit briefs, request evidence, render
status, present approval cards, transmit approval decisions, open
artifacts. Surfaces **may NOT**: approve locally without server
validation, infer completion, mutate evidence, reinterpret intent, bypass
approval, or become a second orchestrator. (ROADMAP.md §6, quoted.)

The iPhone's trusted-surface status is enrollment and presentation — it is
the root of device identity and the surface the approval card is presented
on — **not** write authority. The roadmap's own rule ("clients may NOT
become a second orchestrator") applies to the iPhone exactly as it applies
to the Watch.

## 5. Event-sourced work state

Each work item carries `work_id`, `revision`, `state`, `history`,
`evidence_refs`, `approval_refs`, `last_observed_at`, `fresh_until`;
every meaningful transition appends an event. (ROADMAP.md §6.) The event
log is the estate's memory of what happened; surfaces hold copies of
renders, never the log. `revision` is an integer, monotonically increasing
per `work_id` (see `revision-protocol.md`). `artifact_revision` remains
integer per the Phase 2 Q2 ruling; `expires_at` remains integer epoch
seconds per the Phase 2 Q1 ruling.

## 6. "No device can become a source of truth" — operationalized

The exit criterion is not a slogan. It is these five testable assertions
(the Layer 2/3 targets):

1. **NT-1.** No surface holds write authority: every state transition in
   the event log names the orchestrator as writer.
2. **NT-2.** A surface render is always labeled with provenance (the
   revision and age it was rendered from) — a render without provenance
   is a defect, not a feature.
3. **NT-3.** Two surfaces disagreeing resolve to the server's state, never
   by negotiation between surfaces (`conflict-resolution.md` CR-1).
4. **NT-4.** A surface that has been offline for any duration holds no
   authority on reconnect: it pulls, it does not assert
   (`sequence-diagrams.md` (d)).
5. **NT-5.** Approval authority lives in the recorded decision, not in the
   tap: the tap is a gesture; the orchestrator's record is the decision
   (`revision-protocol.md` §6).

## 7. Relation to the reference implementation

The deployment substrate (`~/workspace/jarvis-deploy/`) implements the
pull discipline, the per-surface contracts, sealed denials, replay
handling, and a ±300 s request-freshness bound (see **OP-1** below). This
specification is normative over it: where the substrate's behavior and
this spec disagree, the spec governs and the substrate is corrected by
change control. The substrate is evidence, not law.

## 8. Open points

- **OP-1 — Clock-skew bound.** Phase 0 U-5/D7 (ratified) sets the
  clock-skew Δ at **60 s**. The reference implementation refuses pull
  requests beyond **±300 s** of the server clock. These are different
  numbers governing adjacent checks (event freshness vs. request
  freshness), but Layer 2/3 need one stated bound for the freshness
  tests. **Needs HgX's word:** keep both (60 s for event/state freshness,
  300 s for request freshness), or unify.
- **OP-2 — The basement laptop.** Q2's context names the laptop as a home
  node; the answer names only iPhone + Watch. **Needs HgX's word:**
  explicitly out of scope for the model, or pull-only under a contract.
- **OP-6 — Formal proof of the hybrid table (recorded, not a decision).** Per the
  plan's head-start note, proving the table (beyond testing it) is beyond
  this phase's exit criteria. Recorded here so it is not mistaken for an
  omission.

## 9. Version history

- **v0.1-draft — 2026-10-21.** First draft: hybrid table instantiated for
  iPhone + Watch scope; NT-1..NT-5 operationalization; Q1–Q4 answers
  baked in. Not ratified.
- **2026-10-21 ~17:49 ET (OP-1 RESOLVED on HgX's word):** keep both — 60 s state/event bound (Phase 0 U-5/D7 ratified), 300 s request-freshness bound (substrate reference).
