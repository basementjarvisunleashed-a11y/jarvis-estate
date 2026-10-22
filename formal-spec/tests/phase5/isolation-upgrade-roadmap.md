# Phase 5 — Isolation Upgrade Roadmap

**Status:** v0.1-draft · **Date:** 2026-10-22
**Sources:** `ROADMAP.md` §8 (the L0–L5 path); `tests/PHASE-5-PLAN.md`
(Layer 1 deliverable: isolation upgrade roadmap); `tests/PHASE-5-OPEN-QUESTIONS.md`
Q3 (answered 2026-10-22 — stay at L0 this phase); `control-matrix.md` §5
(the L0 compensations); `capability-matrix.md` (§2, token reference).

> **Governance.** Draft until HgX ratifies. This phase stays at L0
> (Q3). The roadmap documents the honest path upward — what each level
> would take, and what triggers an advance. **An advance happens only
> on HgX's word.**

---

## 1. Purpose

Isolation is the mechanism that makes trust boundaries real. The
estate currently enforces them procedurally (L0). This roadmap states
where the estate stands, what each higher level would require, and
— honestly sequenced — what would have to be true before an advance.

## 2. Current level: L0 — Procedural (Q3)

**IU-1.** The estate is at L0: doctrine-separated roles (the bot
roster, the custody doctrines), a shared runtime and filesystem, and
human discipline (HgX's word as the change control).

**IU-2.** L0 is stated, not hidden: the exit criterion asks for
"procedural isolation documented and compensated," which is exactly
what `control-matrix.md` §5 documents.

**IU-3.** The L0 compensations are: doctrine as enforcement
(C-31), three-plane enforcement in the deployment build
(`PlaneViolation` on direct cross-plane calls), key custody asserted
in tests (no control/data component holds ceremony key bytes),
sealed logged denials, and the honest threat T-28(L) for what L0
cannot do.

## 3. The path upward — honest sequencing

| Level | Name | What it would take | What triggers considering it |
|---|---|---|---|
| L1 | Filesystem/access discipline | Per-scope directories; path contracts; handoff-only cross-role access; audit logs wired into the estate's runtime | HgX's word + a build order treating this doc's L1 row as the spec. Real work on the live system — it changes how the estate is built and run. |
| L2 | Process/container isolation | Separate containers or OS users for high-risk roles; separate browser profiles; restricted mounts; credential isolation at the process boundary | L1 evidenced + HgX's word. The custody doctrines get their own processes before anything else does. |
| L3 | Capability tokens | Short-lived, scoped, per-task capabilities as tokens; auto-expiry; issuance, storage, and rotation mechanics specified (deferred in this phase — `capability-matrix.md` CM-13) | L2 evidenced + HgX's word. The eight-field vocabulary is already specified; only the mint is missing. |
| L4 | Cryptographic evidence | Signed evidence packets; signed intents; tamper-evident logs; digest attestation | L3 evidenced + HgX's word. Turns "sealed and logged" into "signed and verifiable." |
| L5 | Institutional-grade | Device attestation; hardware-backed keys; multi-party authorization; certification path | L4 evidenced + HgX's word + an external reason (regulatory, institutional, or adversarial pressure). Not a hobby project. |

**IU-4.** The sequencing is load-bearing: no level is skipped.
Tokens without container isolation (L3 before L2) would mint
capabilities the runtime cannot confine; signatures without tokens
(L4 before L3) would sign claims the model cannot scope.

**IU-5.** L1 is implementation depth, not a formalism exercise: it
deserves its own order, its own evidence, and HgX's explicit word —
not a side effect of this phase (Q3's reasoning, adopted).

## 4. What does NOT trigger an advance

**IU-6.** A scare does not advance the level. A single incident
triggers review of the L0 compensations, not a rebuild: the model
distinguishes "the compensation failed" (fix the compensation) from
"the level is insufficient for the estate's risk" (advance the level).

**IU-7.** Convenience does not advance the level. If the estate works
at L0, L0 is where it stays until HgX decides the risk posture
requires more.

## 5. Numbered claims

- **IU-8.** Current level is L0 — procedural — stated with its
  compensations, not as an apology (IU-1…IU-3).
- **IU-9.** Each level L1…L5 states what it would take and what
  triggers considering it (§3); the sequence is ordered and
  unskippable (IU-4).
- **IU-10.** No advance happens without HgX's explicit word — for
  each level, separately (IU-5).
- **IU-11.** Incidents trigger compensation review, not automatic
  rebuilds; convenience never triggers an advance (IU-6, IU-7).

## 6. Open points

- **P5-OP-8 — L1 scoping.** If HgX ever orders L1, whether the first
  per-scope directories cover the custody boundaries (TB-11…TB-15)
  first, or the tool/subagent planes (TB-3/TB-4) first, is a build
  decision for that order. Recorded here so the question is not
  lost. **Needs HgX's word** at that time, not now.

## 7. Cross-references

- `control-matrix.md` §5 — the L0 compensations this roadmap
  defends.
- `threat-catalogue.md` — T-28(L), the named threat for L0's
  ceiling.
- `capability-matrix.md` — CM-13/CM-14: the token vocabulary (L3's
  prerequisite, already specified) and the deferred mint.
- `trust-boundaries.md` — TB-1…TB-15, what higher levels would
  enforce by mechanism.

## 8. Version history

- **v0.1-draft — 2026-10-22.** First draft: L0 current with
  compensations (IU-1…IU-3); L1…L5 honest sequencing with triggers
  (IU-4…IU-7); claims IU-8…IU-11; Q3 baked in; P5-OP-8 recorded.
  Not ratified.
