# Layer 1 — Static Contract Tests (Phase 2)

Runnable Python 3 standard-library suite (`unittest` only; no third-party
packages). It tests the **real ratified artifacts** — it parses
`contracts/events.md` and `spec/state-machine.tla` at run time and fails
closed on any drift — plus a Python reference implementation of the
spec's guard semantics (`can_enter_executing`, `ServerRecordsApproval`,
`can_enter_completed`) in `spec_model.py`.

## Run

From this directory:

```sh
python3 -m unittest test_layer1_contracts -v
```

or simply:

```sh
./run.sh
```

## What it covers

- **ST-01…ST-10** — structural checks: the 12-state set, the 19-event
  vocabulary, T1–T21 completeness in both artifacts, events.md ↔ .tla
  transition-table agreement, canonical endpoints, single roads into
  `completed` (F1) and `executing` (F2), forbidden pairs absent (F3/F7/F8),
  single keyed exit from `unknown` (F6).
- **CT-A1…A7** — the approval gate: missing approval refused; expired
  approval refused at record and at grant; mutation of any of the six
  bound intent fields changes the SHA-256 digest (ratified rule U-1) and
  is refused; tap ≠ authority (INV-A5); unauthorised session refused;
  pause blocks the gate; an approval for one intent does not authorise
  another (INV-A7); a duplicate grant is not a second transition (INV-A6).
- **CT-C1/C2/C3/C5, CT-E1** — the completion gate: no completion without
  evidence, without a passed acceptance test, or with a failure observed;
  a delegated claim is not an input to the guard; completion only from
  `verifying`.
- **CT-E5 / CT-S4 (structural)** — freshness guards in the spec text:
  `BlockageCleared` requires `source_freshness = "fresh"`; resumption and
  observation-restoration set freshness by re-validation/re-read.
- **Fail-closed validation** — unknown event names, unknown states, and
  illegal transitions (including `failed → completed`) are rejected.

## Schema example tests (new 2026-10-21)

`test_schema_examples.py` + `schema_validator.py` + `fixtures/` — tests the
five v0.1 contract schemas (`contracts/approval-intent.schema.json`,
`decision-packet.schema.json`, `evidence-packet.schema.json`,
`artifact-manifest.schema.json`, `watchtower.schema.json`) with one valid
worked example and at least two failing cases each. Every failing case
asserts the rejection (fail closed): mutated digest, missing required
field, unknown enum value, expired approval, missing `gaps` (INV-E4),
revision mismatch (INV-E2), stale reading at full confidence,
degraded-without-note (INV-S3). Run: `python3 -m unittest test_schema_examples -v`
— 23/23 passing (evidence `tests/evidence/2026-10-21-schema-tests.log`).

## Files

| File | Role |
|---|---|
| `spec_model.py` | Parsers for the two artifacts + guard reference implementation |
| `test_layer1_contracts.py` | The unittest suite |
| `run.sh` | Runner (the exact command above) |
