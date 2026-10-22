# Phase 3 — Conflict Resolution Table

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §6 (the eight-row table — quoted as the base);
`tests/PHASE-3-OPEN-QUESTIONS.md` (Q1, Q2, Q4); `consistency-model.md`
(this directory); `revision-protocol.md` (this directory).

> **Governance.** Draft until HgX ratifies. Each row carries a stable ID
> (CR-1…CR-8). The Phase 3 plan's Layer 1 gate requires every row to be
> exercised by at least one Layer 2 test — the test mapping is recorded
> at Layer 2, not invented here.

The table's promise: **every conflict resolves deterministically** (Phase
3 exit criterion). "Deterministically" means the resolution is a function
of server-held state and the requests' contents — never of arrival order
beyond what the log records, never of which device the principal happens
to be holding.

---

## CR-1 — Two devices show different status

- **Conflict:** iPhone renders state S₁ at revision r₁; Watch renders
  state S₂ at revision r₂; S₁ ≠ S₂.
- **Resolution:** **Server state wins.** Both surfaces re-pull; the
  orchestrator's current revision is authoritative. There is no
  negotiation between surfaces, no "newer timestamp wins" between
  clients — client clocks are untrusted (see OP-1).
- **Invariant defended:** NT-3 (`consistency-model.md` §6) — no device is
  a source of truth, including against another device.
- **Sequence:** `sequence-diagrams.md` (a).

## CR-2 — Two devices attempt approval

- **Conflict:** iPhone and Watch both transmit an approval decision for
  the same `intent_id`, under adversarial timing.
- **Resolution:** **First valid decision recorded wins.** "Valid" is
  decided by the orchestrator under `revision-protocol.md` §5 (session,
  freshness, intent liveness, revision currency, digest binding). The
  first request to pass all five checks is recorded; the loser's request
  returns the existing decision as a read — it is not recorded, not
  executed, not an error the principal must resolve. If neither passes,
  nothing is recorded.
- **Invariant defended:** consequence is strongly consistent
  (`consistency-model.md` §2); exactly one decision exists per intent.
- **Sequence:** `sequence-diagrams.md` (b). **This is Layer 3's core
  adversarial test** (plan head-start note: specified, not yet
  adversarially tested).

## CR-3 — Client cache says operational, source expired

- **Conflict:** the Watch's cache renders "operational" from a pull whose
  `fresh_until` has passed; the orchestrator's current state is unknown
  or different.
- **Resolution:** **Render unknown / reduced confidence.** The surface
  renders the unknown state — never the expired value as current. See
  `cache-policy.md` §4 and `freshness-policy.md` §4.
- **Invariant defended:** stale data cannot masquerade as current (exit
  criterion).
- **Sequence:** `sequence-diagrams.md` (c).

## CR-4 — Memory says X, live source says Y

- **Conflict:** durable memory (or a cached render) holds X; the live
  source currently says Y.
- **Resolution:** **Live source wins for current facts.** The decision or
  render uses Y, read at decision time (`consistency-model.md` HC-6). X
  is not deleted — it remains in history, flagged as superseded — but it
  is inadmissible as the basis for action.
- **Invariant defended:** decisions bind to current truth, not to
  remembered truth.

## CR-5 — Durable memory contradiction

- **Conflict:** two durable records contradict and neither is a
  superseded revision of the other.
- **Resolution:** **The orchestrator reconciles.** Surfaces never
  reconcile against each other. Reconciliation is a proposed correction
  (HC-5), recorded as an event with both antecedents cited — never a
  silent overwrite.
- **Invariant defended:** single authoritative writer; history is
  append-only.

## CR-6 — Notification arrives after state changed

- **Conflict:** a notification hint describing state S_old arrives after
  the orchestrator has moved to S_new.
- **Resolution:** **The notification is a hint, not truth.** The surface
  discards the hint's content and pulls current state
  (`consistency-model.md` HC-8). Acting on the hint's content is a
  violation.
- **Invariant defended:** notifications carry no authority (substrate
  reference: notifications are at-least-once hints).

## CR-7 — Evidence packet updated

- **Conflict:** a surface holds evidence packet P at `artifact_revision`
  n; the orchestrator seals revision n+1.
- **Resolution:** **New revision; old immutable.** Revision n remains
  sealed and addressable; renders pin to a revision (HC-2). A render that
  cited revision n is not "wrong" — it is historical, and labeled so.
- **Invariant defended:** evidence is append-only; `events.md` v1.1
  `evidence_packet_created` semantics (ratified).

## CR-8 — Artifact changed after approval

- **Conflict:** an approval was recorded against artifact digest D₁; the
  artifact's bytes now digest to D₂ ≠ D₁.
- **Resolution:** **The approval is invalid; a new approval is required.**
  There is no "re-confirm the same approval" — the changed artifact is a
  new intent, proposed and approved afresh. The old approval remains in
  the log, marked superseded-by-artifact-change, never deleted.
- **Invariant defended:** the approval binds the exact intent — digest
  equality is the binding (`revision-protocol.md` §5, step 5).

---

## Test-scope note (not an open decision)

- **CR-2 under partition.** If the two devices are partitioned
  from each other but both reach the orchestrator, CR-2 holds as
  written. If a device is partitioned from the orchestrator, it cannot
  approve at all (`sequence-diagrams.md` (d)). The genuinely adversarial
  case — both devices reaching the orchestrator through different
  network paths with skewed clocks — is Layer 3's work; this table
  states the rule, Layer 3 proves it holds. No decision for HgX here;
  recorded so the test scope is explicit.

## Version history

- **v0.1-draft — 2026-10-21.** First draft: eight roadmap rows
  instantiated with resolutions, defended invariants, and sequence
  pointers. Not ratified.
- **2026-10-21 ~17:49 ET (OP-1 RESOLVED on HgX's word):** keep both — 60 s state/event bound (Phase 0 U-5/D7 ratified), 300 s request-freshness bound (substrate reference).
