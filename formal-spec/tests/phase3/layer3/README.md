# Phase 3 — Layer 3: Adversarial Chaos Tests

Adversarial tests of the consistency model (Phase 3 plan, Layer 3 scope).
Python 3 standard library only (`unittest`, fixed virtual clocks — no
randomness, no threads, no network, no git, no publishing).

Adversarial timing is modeled as **explicit, systematically enumerated
delivery permutations** — each case runs against a fresh fixture
(`chaos.py::run_interleavings`, `itertools.permutations`). Partitions are
severable `ChaosLink`s that drop messages the orchestrator never sees.
Clock skew is an explicit per-client offset on request timestamps.

## Run

From this directory:

```sh
./run.sh
```

Writes to `tests/phase3/evidence/`:
- `<date>-phase3-layer3.log` — full verbose unittest output.
- `<date>-phase3-layer3-rejections.log` — every refused request, one row
  per refusal: `(orchestrator:seq)` proving exactly-once, reason, kind,
  intent/work ref, cause. **Every rejection is logged with its cause.**
- `<date>-phase3-layer3-verdicts.log` — one row per adversarial case:
  case id, PASS, the invariants it defended.

## Families (80 adversarial cases)

| File | Family | Cases | What it checks | Draft sections cited |
|---|---|---|---|---|
| `test_adversarial_race.py` | AR (18) | AR-1…AR-6 | CR-2 under every delivery interleaving: two valid racers (2 orders), valid-vs-bad-digest (4), both-invalid (2), three-way with duplicate (6), race at the 300 s bound (2), stale-request-vs-valid (2). Every order: exactly one recorded decision, one execution, identical content, loser on the refuse/name-current/re-pull or already-recorded path | conflict-resolution.md CR-2; revision-protocol.md §5, §6; sequence-diagrams.md (b) |
| `test_partition.py` | PT (7) | PT-1…PT-6 | Dropped decide retried to one record; late arrival refused naming current; both dropped then both re-send (2 orders); stale cache renders unknown while partitioned (CR-3); pre-partition decision stays authoritative (CR-1); flapping partition | conflict-resolution.md CR-1, CR-2, CR-3; sequence-diagrams.md (d); cache-policy.md §4 |
| `test_skew.py` | SK (15) | SK-1…SK-7 | 300 s request bound at ±300/±301; 60 s event bound at 60/61; ±400 s skew cannot mint a decision; in-bound skew bypasses nothing; race under ±250 s skew; skewed pull renders unknown; future-dated event grants no authority | revision-protocol.md §5 (OP-1); freshness-policy.md §4; conflict-resolution.md CR-3 |
| `test_replay.py` | RP (6) | RP-1…RP-6 | Burned slot: 6 replays of a recorded approval change nothing; replays under partition dropped then read-as-recorded; refused request replayed 3× stays refused (3 ledger rows); duplicated pulls idempotent; expired-intent replay stays invalid; burned across reconnect | revision-protocol.md §6; conflict-resolution.md CR-2; sequence-diagrams.md (d) |
| `test_mixed_chaos.py` | MX (34) | MX-1…MX-5 | Partition+skew+race; delayed+skewed+duplicate race (6 orders); both dropped then both re-send fresh (2 orders); skew+partition+offline-tap; **full 24-order fuzz** of two valid racers + duplicate + bad-digest racer | conflict-resolution.md CR-1, CR-2, CR-3; revision-protocol.md §5, §6; sequence-diagrams.md (b), (d) |

## The model

`chaos.py` — the deterministic chaos driver: `fixture()` (identical to
the Layer 2 fixture), `decide()`/`mutate()` request builders, `ChaosLink`
(severable link), `run_interleavings()` (permutation driver),
`assert_single_decision` / `assert_no_decision` / `assert_loser_path`
(the chaos invariants), `record_verdict()`. Reuses the Layer 2 harness
(`../layer2/orchestrator.py`, `clients.py`, `digest.py`) — extended, not
duplicated.

Bounds (OP-1, HgX's word 2026-10-21 ~17:49 ET): 300 s request freshness,
60 s state/event freshness — both probed at their exact boundaries and
one second beyond, in both directions.

## Exit-criterion mapping

| Exit criterion (ROADMAP.md §6) | Covering tests |
|---|---|
| No device can become a source of truth | AR (loser never writes), PT-1/PT-5/PT-6, SK-3/SK-4, RP-1/RP-4, MX (all) |
| Approval conflicts resolve deterministically | AR (all 18 interleavings), PT-2/PT-3, RP-1/RP-2/RP-5, MX (all 34) |
| Stale data cannot masquerade as current | PT-4, SK-1/SK-2/SK-6, MX-4 |
| Offline taps cannot become approvals | PT-1/PT-6, RP-6, MX-4 |
| Behavior tested under clock skew and network loss | SK (15), PT (7), MX (34) |

## Not pinned down here (flagged, not smoothed)

- OP-3 (`device_session_id` lifecycle): only revocation modeled (Layer 2);
  re-enrollment/expiry deferred to Phase 5 per the drafts.
- OP-5 (TTL numbers): tests use the drafts' draft horizons; the rules
  stand regardless of the numbers.
- p99 timing: no wall-clock in the model; bounds tested as arithmetic, as
  the drafts specify.
- True concurrency (threads, two writers racing in the same instant) is
  out of scope for this model: the orchestrator serializes arrivals, and
  the chaos enumerates every serialization. A production orchestrator's
  linearization point is Phase 6 (router) / implementation depth.
