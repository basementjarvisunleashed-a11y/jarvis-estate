# Jarvis Stability Scoring

A stable (unchanging) rubric measuring Jarvis's maturity week over week, so the
year's growth is visible as a curve, not a feeling.

## The three parts

1. `corrections.md` — every correction HgX issues: date, what was wrong, the fix.
   Corrections are data, not demerits; they train the stability.
2. `concepts.md` — the operating concepts with stable definitions and sources.
3. `STABILITY.md` — the score (0–100) plus its full history.

## Rubric v1.0 (stable — weights change only on HgX's word)

Score = 100 × (0.25×audit_pass + 0.25×evidence_complete + 0.20×identity_clean
                + 0.15×publish_health + 0.15×correction_stability)

- `audit_pass` — weekly audits passed / audits run that week.
- `evidence_complete` — PROVEN claims with evidence / PROVEN claims.
- `identity_clean` — 1 if the real-name grep is 0 hits, else 0.
- `publish_health` — 1 if the public site URL is live, else 0.
- `correction_stability` — max(0, 1 − corrections_this_week / 10).

Recomputed every weekly audit; history appended, never rewritten.
