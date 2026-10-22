# Phase 5, Layer 3 — Adversarial Test Suite: the four agent-specific threats under fire

**Status:** v0.1 · **Date:** 2026-10-22
**Authorized:** HgX's explicit word, 2026-10-22 ~08:01 ET (all three
Phase 5 work layers, sequentially).

Layer 2 verified that the controls hold against their named threats.
Layer 3 attacks: hand-built adversarial cases against the four
agent-specific threats (T-22 prompt injection, T-23 stale-state
manipulation, T-24 approval fatigue, T-25 subagent deception),
working along the leaves of `attack-trees.md` (AT-2, AT-3, AT-4).
Where orderings matter, every ordering is enumerated
deterministically (itertools permutations — no randomness).

## Layout

| File | Family | Threats | Controls |
|---|---|---|---|
| `adversary.py` | The adversarial harness (extends Layer 2's `estate.py`: credential quarantine, external-content ingestion, freshness gate, risk classifier, TB-4 orchestrator, verdict recorder) | — | — |
| `test_prompt_injection.py` | Prompt-injection scenarios (PI-01…PI-10) | T-22, T-13 | C-11, C-12, C-13, C-16, C-6, C-4 (backstop) |
| `test_stale_state.py` | Stale-state scenarios (SS-01…SS-08) | T-23, T-4 | C-26, C-9, C-4, C-8, C-2 |
| `test_approval_fatigue.py` | Approval-fatigue scenarios (AF-01…AF-08) | T-24, T-14, T-27 | C-17, C-18, C-19, C-20 (honest mark) |
| `test_subagent_deception.py` | Subagent-deception scenarios (SD-01…SD-08) | T-25, T-3, T-22 | C-13, C-30, C-10, C-22, C-23 |
| `run.sh` | Runner: runs everything, writes dated evidence logs + per-case verdicts | — | — |

Every test file documents what it checks, the threat ID (T-n) and
control ID (C-n) it attacks/defends, and the attack-tree leaf it
walks. Every case logs a machine-checkable verdict (case ID, threat
ID, control ID, verdict category, detail) to the JSONL verdict file.

## How to run

From this directory:

```bash
./run.sh
```

Writes to `tests/phase5/evidence/`:

- `<date>-phase5-layer3.log` — full verbose unittest output
- `<date>-phase5-layer3-rejections.log` — every refusal and flag, with cause
- `<date>-phase5-layer3-verdicts.jsonl` — one verdict per adversarial case
- `<date>-phase5-layer3-summary.txt` — pass/fail per family + verdict tally

Python 3 stdlib only. Deterministic: fixed virtual clocks, hand-built
cases, systematic permutation enumeration, no randomness, no network,
no git, no publishing. The suite touches nothing under `spec/` or
`contracts/` — the ratified files stay read-only — and it does not
modify Layer 2's files; it imports and extends them.

## Verdict vocabulary

- `held-refused` — the attack was refused with a named cause.
- `held-flagged` — the attack was neutralized and logged as a flagged
  event (no raise): credential quarantine (PI-08), card-tail drop
  (PI-05), risk-class escalation (AF-06).
- `held-backstop` — the primary heuristic missed, but a deeper
  control held (PI-07: paraphrase evasion meets the digest-bound
  approval backstop).
- `clean-pass` — a benign control case behaved correctly.
- `finding` — a control broke under adversarial pressure. A finding
  is reported, never hidden; the suite currently records none.

## Honesty marks (what this suite does NOT claim)

- **The instruction-marker vocabulary is heuristic.** Paraphrased
  instructions outside the vocabulary are not caught by the scan
  (PI-07 documents this openly). What the model guarantees is
  defense in depth: uncaught content stays data, and no
  consequential action fires without a digest-bound approval (C-4).
- **The risk classifier is operational judgment.** High-risk is
  derived from the digest-bound intent's effect+scope hints
  (AF-06); synonym-disguised effects outside the hint list are a
  known gap, mitigated by the same exact-approval backstop.
- **The freshness TTL (300s) is stated, not derived.** The boundary
  tests pin the behavior at the stated limit; they do not prove the
  limit is the right one.
- **The attention budget counts per hour.** A barrage deliberately
  spread across a window boundary is not stopped by the counter;
  C-20's human-review procedure is the compensating control
  (documented in `layer2/review-procedure.md`, exercised in AF-08).
- **Credential patterns are shape-prefixes.** Novel exfiltration
  encodings outside the modeled shapes are outside the harness.
- **The canonical order re-read → validate → execute is a harness
  choice**, stated in `adversary.py` and tested as stated.
- **The model is a test-side reimplementation, not the build.**
  These tests verify that the *specification as written* refuses the
  threats as named, under adversarial pressure. They do not audit
  the deployment build's code, and they do not re-litigate the v0.1
  drafts' open points (P5-OP-1…P5-OP-7), which await HgX's word.

## Refusal / flag causes exercised

`injected-instruction-in-data`, `credential-quarantined` (flagged),
`injected-instruction-in-card-display` (flagged),
`risk-class-escalated` (flagged), `stale-state-cannot-consequence`,
`superseded-revision`, `approval-expired`, `revoked-session`,
`digest-mismatch`, `approval-replay`, `fake-approval`,
`attention-budget-exceeded`, `bulk-approval-refused`,
`high-risk-not-exact`, `high-risk-requires-local-auth` (Layer 2),
`silent-by-default` (logged, not raised), `no-proof-no-done`,
`unknown-artifact`, `artifact-digest-mismatch`,
`log-contradicts-claim`, `memory-write-not-orchestrator`,
`memory-write-no-provenance`.
