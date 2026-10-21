# Phase 3 — Layer 2: Protocol Tests

Executable tests of the revision protocol and the conflict table
(Phase 3 plan, Layer 2 scope). Python 3 standard library only
(`unittest`, fixed virtual clocks — no randomness, no network, no git,
no publishing).

## Run

From this directory:

```sh
./run.sh
```

Writes to `tests/phase3/evidence/`:
- `<date>-phase3-layer2.log` — full verbose unittest output.
- `<date>-phase3-layer2-rejections.log` — every refused request, one
  row per refusal: `(orchestrator:seq)` proving exactly-once, reason,
  request kind, intent/work ref, cause. **Every rejection is logged
  with its cause.**

## Families (42 tests)

| File | Family | What it checks | Draft sections cited |
|---|---|---|---|
| `test_revision_token.py` | RT (11) | Token refuses stale action; monotonicity R1–R5; both bounds (60 s state/event, 300 s request) honored at their boundaries | revision-protocol.md §3, §5; consistency-model.md NT-1 |
| `test_stale_mutation.py` | SM (8) | Five-step rejection order verified in sequence; refused mutations change nothing; mutated intents re-proposed, never updated in place | revision-protocol.md §5 |
| `test_digest_approval.py` | DA (6) | D_seen == D binds; mismatch lapses with attested lapse; independent digest recomputation; CR-8 artifact-change invalidation | revision-protocol.md §5 step 5; conflict-resolution.md CR-8; spec/approval-digest.md |
| `test_offline_tap.py` | OT (5) | Offline tap records a local gesture only — never a decision; reconnect discards it; expired cards disable the tap; long-offline holds no authority | sequence-diagrams.md (d); consistency-model.md NT-4, NT-5; cache-policy.md §4 |
| `test_first_valid_decision.py` | FV (6) | First valid decision recorded wins; loser gets refuse/name-current/re-pull (sequence (b)); duplicates return the record, never a second execution | conflict-resolution.md CR-2; revision-protocol.md §6 |
| `test_conflict_table.py` | CT (6) | CR-1 server wins; CR-3 unknown render; CR-4 live source wins; CR-5 orchestrator reconciles append-only; CR-6 hint discarded; CR-7 new revision, old immutable | conflict-resolution.md CR-1,3,4,5,6,7 |

Every CR-1…CR-8 row is exercised by at least one test (the plan's
Layer 1 gate).

## The model

`orchestrator.py` — the estate's single authoritative writer as a
minimal in-memory model enforcing the draft rules (six-field token,
five-step gate, digest binding, first-valid-decision-wins, CR-8
invalidation). `clients.py` — iPhone/Watch surfaces with age-honest
rendering and the offline-tap gesture path. `digest.py` — the ratified
eight-field approval digest (Phase 2 Q3/Q4), recomputed independently.

Bounds (OP-1, HgX's word 2026-10-21 ~17:49 ET): 300 s request freshness,
60 s state/event freshness — both tested at their exact boundaries.

## Refusal categories (current run)

stale-revision 13 · intent-invalid 8 · stale-request 4 ·
unknown-session 4 · digest-lapse 3 · stale-event 1 — 33 refused
requests, each logged exactly once.

## Not pinned down here (flagged, not smoothed)

- OP-3 (`device_session_id` lifecycle): revocation is modeled; re-enrollment
  and session expiry are unspecified in the drafts — deferred to Phase 5
  per the draft.
- OP-5 (TTL numbers): cache/freshness tests use the drafts' draft
  horizons; the rules stand regardless of the numbers.
- CR-2 under partition / adversarial skew: specified, not adversarially
  tested — Layer 3's core work (plan head-start note).
- p99 timing expectations: no wall-clock in the model; bounds tested as
  arithmetic, which is what the drafts specify.
