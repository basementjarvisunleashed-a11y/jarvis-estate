# Layer 2 — Offline Replay Harness

Deterministic, Python 3 stdlib only. Implements stage 2 of the
experiment protocol (`../experiment-protocol.md` EP-3…EP-5).

## What it does

1. Loads the corpus: the real router log (`~/workspace/usage-router/logs/`,
   1 entry today) plus the labeled synthetic fixtures (`fixtures.json`,
   12 entries, every one marked `synthetic:true`).
2. Replays each entry through three policies: `unconstrained` (RP-8a),
   `cache-only` (RP-8b), `local` (RP-8c — the seven rules).
3. Compares each policy's recommendation against the LOGGED `action_taken`.
   Outcome metrics are computed only over entries where the policy AGREED
   with what was actually done (measured outcomes). Where the policy would
   have done something else, the outcome is `counterfactual_unknown` — the
   harness makes no claim about what would have happened.
4. Runs the INV-R5 fallback check (failing backend → local, logged) and
   the Q2 Jev-refusal check (instantiating the Jev backend without his
   approval raises `JevNotApproved`; nothing is sent).

## What it does NOT do

- No Jev calls — the interface exists, the approval does not.
- No synthetic entry is presented as measured evidence. The fixtures
  verify the machinery (all seven rules fire; the guardrail check trips
  on the unconstrained baseline by design).

## Weighted mode (gate OPEN — weights signed 2026-10-22)

```sh
./run.sh --weighted --corpus real   # weighted EVIDENCE run (102 real entries, 0 synthetic)
./run.sh --weighted --corpus all    # weighted sanity check (real + synthetic; NOT evidence)
```

`--weighted` computes WT-9 per policy with the signed weights parsed
from `../weight-table.md` (never hardcoded; the run fails loudly if any
weight is unsigned). Per DL-4, entries with unknown outcome labels are
excluded from outcome metrics; unknown numeric labels contribute 0 and
are counted. `accepted_work` counts `outcome == "accepted"` only; loops
are detected in state (`action_repeat_count >= 3`).

Weighted evidence: `../evidence/2026-10-22-phase6-layer2-weighted.log`,
`../evidence/2026-10-22-phase6-layer2-weighted-metrics.json`.

## Run

```sh
./run.sh
```

Evidence: `../evidence/2026-10-22-phase6-layer2.log`,
`../evidence/2026-10-22-phase6-layer2-metrics.json`,
`../evidence/2026-10-22-phase6-layer2-run.out`.
