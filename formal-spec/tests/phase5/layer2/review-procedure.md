# Attention-budget review procedure (C-20 verification method)

**Status:** v0.1-draft · **Date:** 2026-10-22

**Control:** C-20 (control-matrix.md section 2) — the attention budget
is monitored with human review. Honestly marked **non-mechanically-
testable** (control-matrix.md section 3): the attention budget is an
instrumented quantity with human-reviewed thresholds. **No test can
prove a fatigue curve.** This document is the verification method
itself: the procedure is the verification.

**Threat:** T-27 (L) — unmodeled fatigue dynamics (threat-catalogue.md
section 9). The thresholds rest on judgment, not proof; they are
stated here as **operational judgment**, not a modeled fatigue curve.

## The procedure (periodic human review)

1. Export the attention-budget log (`Attention.export_budget_log` in
   `estate.py`; exercised by `test_budget_log_exportable`).
2. For the review window, count high-risk approval requests per hour
   against the stated threshold (default: 3 per hour).
3. Any window at or above threshold is a review item: the human
   reviewer (HgX, or a reviewer he names) reads the intents, checks
   that each carried exact target+effect rendering (C-19), and records
   a finding.
4. The threshold may be adjusted on the reviewer's word only, with the
   adjustment logged and dated. It is never claimed as a modeled
   fatigue curve.
5. Findings land in the evidence log; three consecutive windows at
   threshold trigger a control review of C-17/C-18/C-19.

## What this procedure does NOT claim

- It does not model approval fatigue.
- It does not prove any threshold prevents degraded judgment.
- It converts the honest limitation (T-27) into a named compensating
  control (C-20): instrumentation with human review, thresholds
  stated as operational judgment.

**Governance.** Draft until HgX ratifies. The review cadence and the
threshold values are HgX's word, not the model's.
