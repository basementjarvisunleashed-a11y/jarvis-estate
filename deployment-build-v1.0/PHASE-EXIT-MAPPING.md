# Phase-exit mapping — deployment build v1.0 vs doctoral phases 2–7

**HgX's verdict (2026-10-21 ~16:41 ET): reviewed, approved — "I like it."** No phase is closed by signature alone; the mapping stands as the official assessment. Closures, if any, on his further word.

For each doctoral phase: the roadmap's exit criterion, what this build
satisfies **with evidence**, and what remains open. **No phase is closed
by this build — HgX closes phases on evidence.** (Phase 0/1 mapping is
covered by the estate's existing records; this build reuses their
contracts.)

Test totals: Phase 0: 18 · Phase 1: 27 · Phase 2: 33 · Phase 3: 19 ·
Phase 4: 35 — **132 tests, all passing.** Evidence logs in
`tests/evidence/`.

## Phase 2 — Invariant Verification

Exit: *"Every major doctrine statement has a testable invariant; all
tests automated; mutated/expired approval cannot pass; optimistic
completion fails tests; suite citable as empirical validation."*

- SATISFIED (implementation evidence): mutated approval cannot pass —
  phase3 binding test (target 4→5 changes D; edge and mint refuse);
  expired approval cannot pass — card expiry → LAPSED, re-presentation
  required; optimistic completion fails — offline tap records nothing
  (device outbox empty, log unchanged); completion requires a sealed
  EVIDENCE entry. All 132 tests automated via `run-all.sh`.
- REMAINS OPEN: this build does not execute the formal Phase 2
  invariant catalogue (C1–C5/A1–A7/E1–E5/S1–S5/R1–R5) — that catalogue
  lives in `~/workspace/jarvis-formal-spec/tests/`. The suites here are
  citable as empirical validation of the deployment cut, not as the
  Phase 2 proof.

## Phase 3 — Consistency Model

Exit: *"No device can become a source of truth; approval conflicts
resolve deterministically; stale data cannot masquerade as current;
offline taps cannot become approvals; behavior tested under clock skew
and network loss."*

- SATISFIED: no device is a source of truth — the data plane owns
  sealed state; every surface pulls within its contract (phase2, 9
  refusals + 9 allowances); stale data cannot masquerade — ±301s skew
  → sealed `stale-request` denial (phase1 chaos); offline taps never
  become approvals (phase3, asserted zero recording); clock skew and
  partition covered by chaos tests.
- REMAINS OPEN: concurrent conflicting approvals from two devices are
  not exercised — deterministic conflict resolution is specified
  (digest equality) but not adversarially tested; the roadmap's hybrid
  consistency table is not formally proven here.

## Phase 4 — Idempotency Guarantees

Exit: *"Duplicate taps cannot duplicate effects; network loss cannot
silently complete; ambiguous consequential actions become visible
unknown/failed; retries only when safe; at-most-once demonstrable under
test."*

- SATISFIED: duplicate taps cannot duplicate effects — token nonce
  burns on first successful use; replay refused + incident logged
  (phase3); identical pull replay → byte-identical sealed response,
  exactly one data read + one log entry (phase1); network loss cannot
  silently complete — partition → client-side `PartitionError`, server
  never chases, journal untouched; at-most-once demonstrable — 19
  phase3 tests + replay/nonce-burn tests.
- REMAINS OPEN: "ambiguous consequential actions become visible
  unknown/failed" is partially covered (LAPSED states, sealed
  denials); the Phase 4 idempotency spec's open item (who signs the
  digest for worker-prepared intents — Q6, deferred) is untouched.

## Phase 5 — Security Boundary Formalism

Exit: *"Every consequential action has a named threat and control;
prompt injection, stale state, and approval fatigue explicitly modeled;
procedural isolation documented and compensated; controls testable;
posture defensible without overclaiming."*

- SATISFIED (partial): stale state explicitly modeled — freshness
  windows (300s proofs, request staleness), expiry, LAPSED; controls
  testable — every refusal is a sealed, logged denial; procedural
  isolation documented — three planes enforced in code
  (`PlaneViolation` on direct cross-plane calls), key custody asserted
  in tests (no control/data component holds ceremony key bytes);
  posture stated without overclaiming (see README honest limits).
- REMAINS OPEN: no per-action named threat catalogue; prompt injection
  is not modeled; approval fatigue is only instrumented (attention
  budget as a monitored quantity), not formally modeled; the reference
  ZK is explicitly not a control — production circuits required.

## Phase 6 — Router Optimality

Exit: *"Router decisions linked to outcomes; local, cache-only, and
unconstrained baselines compared; Jev evaluated if approved; value
supported by measured evidence."*

- REMAINS OPEN, entirely: this build contains no router. (Consistent
  with the estate record: INV-R2/R3/R4 deferred to Phase 6 by design.)
  Nothing here satisfies Phase 6.

## Phase 7 — Integration into Doctoral Evidence

Required package: *"Formal specification; model checking/proof;
invariant tests; consistency tests; idempotency tests; threat model;
router experiment; operator scorecard; failure case studies;
limitations section."*

- CONTRIBUTES: invariant tests (132, automated); consistency tests
  (phase1 chaos, phase2 contracts, phase3 binding); idempotency tests
  (phase3 nonce/replay, phase4 freshness/replay); failure case studies
  (all five §5.4 behaviors as tests); limitations section (README +
  per-phase evidence logs).
- REMAINS OPEN: formal specification of this build, model checking,
  threat model, router experiment, operator scorecard — and HgX's
  verdict on the whole.

## Deployment paper's own acceptance criteria (§6.4)

- Pull protocol under chaos: DONE (phase1, 27 tests).
- Orchestra contracts + sealed denials: DONE (phase2, 33 tests).
- Handshake §5.5 reproduces + §5.4 refusals: DONE (phase3, 19 tests;
  digest D computed = d0f1d967…f78).
- Proofs S1/S2/S3 within budgets: DONE as REFERENCE (phase4, 35
  tests; budgets met; ZK property not established).
- Attention, one quiet week: NOT DONE — requires live operation time;
  not satisfiable by tests.
