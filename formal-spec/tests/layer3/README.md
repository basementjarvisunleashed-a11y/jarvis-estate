# Layer 3 — Chaos Tests (Phase 2)

Runnable Python 3 standard-library suite (`unittest`). Fault injection
into running work items — the ten canonical scenarios of ROADMAP.md §5
/ Paper IV §8.2 (CH-1…CH-10) — against the Layer 2 work-item simulator
plus the contract models in `chaos_model.py`.

## Run

From this directory:

```sh
python3 -m unittest test_layer3_chaos -v
```

or simply:

```sh
./run.sh
```

## Honest scope

Faults are injected at the **contract level** — replayed decisions,
expired intents, mutated digests, duplicate deliveries, stale readings,
malformed packets — because the estate's devices, clients, and router
are runtimes outside this repository. Where a scenario's full form
needs that runtime, the test asserts the closest contract-level
equivalent and the gap is on record (suite docstring; run report):

- **CH-5** — no Paper III client / revision-token protocol artifact
  exists yet (INV-C4 pending); asserted: authoritative-state rendering
  rule + packet revision binding (INV-E2).
- **CH-6** — the usage router is estate runtime (INV-R1/R5 pending;
  `spec/router-policy.md` is a planned Phase 6 artifact); asserted:
  the router contract — named-policy fallback with the fallback logged,
  recommendations never crossing the consequence boundary.

## Files

| File | Role |
|---|---|
| `chaos_model.py` | Completion writer (packet contract), router reference, client rendering rule |
| `test_layer3_chaos.py` | The CH-1…CH-10 scenario suite |
| `run.sh` | Runner (the exact command above) |
