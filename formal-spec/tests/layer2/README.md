# Layer 2 — Property-Based Tests (Phase 2)

Runnable Python 3 standard-library suite (`unittest` + `random`, fixed
seeds). Generated inputs, asserted invariants, over a work-item
simulator built on the Layer 1 guard reference model
(`tests/layer1/spec_model.py`): the legal-transition table is the one
cross-built from the ratified artifacts, and both gates are the spec's
own guard semantics.

## Run

From this directory:

```sh
python3 -m unittest test_layer2_properties -v
```

or simply:

```sh
./run.sh
```

The suite writes its **rejection log** — every generator-attempted
action the machine refused, counted by guard — to
`tests/evidence/2026-10-20-layer2-rejections.log` at teardown.

## What it covers (Paper IV §8.2)

- **PT-1 — Approval mutation fuzz** (INV-A2, A3, A7): 900 mutated
  intents (450 between tap and record, 450 between record and grant)
  across three fixed seeds; every mutation refused on digest mismatch;
  zero executions. Plus an unmutated positive control.
- **PT-2 — Expiry sweep** (INV-A4): 3,000 (expiry, attempt-time)
  samples spanning ±1 year around the boundary, one fixed seed; every
  late attempt refused at record and at grant; every live attempt
  honoured; the exact boundary (`now == expiry`) refused.
- **PT-3 — Duplicate decision storm** (INV-A6, PO-9): 120 intents,
  1–50 duplicate grants each, ×1–3 network duplication, interleaved
  duplicate taps and record retries; exactly one recorded decision and
  exactly one execution per intent.
- **PT-4 — Random event sequences** (INV-C1–C5, A1, E1; PO-1, PO-2,
  PO-11): 2,000 sequences (five fixed seeds; half driven to the
  approval gate first, half raw; state-aware draws in
  executing/verifying) over the 19-event vocabulary plus environment
  actions; invariants asserted after every step from the
  transition-entry snapshots.
- **PT-5 — Stale source injection** (INV-S1, S4, E5; PO-10): 2,000
  renderer readings (stale never renders `operational`), plus 200
  blocked items whose source-dependent guard (`blockage_cleared`, T8)
  fails closed on stale data and passes on fresh.

## Files

| File | Role |
|---|---|
| `work_item_sim.py` | Work-item simulator over the Layer 1 model; rejection ledger |
| `test_layer2_properties.py` | The PT-1…PT-5 suite; writes the rejection log |
| `run.sh` | Runner (the exact command above) |
