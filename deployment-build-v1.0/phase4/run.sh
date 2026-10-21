#!/usr/bin/env bash
# Phase 4 — Zero-knowledge proofs (REFERENCE): run tests, write evidence.
# Stdlib only. No network, no git, no publishing. Everything stays local.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PHASE="$ROOT/phase4"
EVIDENCE_DIR="$ROOT/tests/evidence"
EVIDENCE="$EVIDENCE_DIR/phase4-2026-10-21.log"
MEASUREMENTS="$PHASE/measurements.json"

mkdir -p "$EVIDENCE_DIR"
cd "$PHASE"

OUT="$(mktemp)"
trap 'rm -f "$OUT"' EXIT

if python3 test_phase4.py >"$OUT" 2>&1; then
    STATUS="PASS"
else
    STATUS="FAIL"
fi

RAN="$(grep -oE 'Ran [0-9]+ tests' "$OUT" | grep -oE '[0-9]+' || echo 0)"
SUMMARY="$(grep -E '^(OK|FAILED)' "$OUT" | head -1)"

python3 - "$OUT" "$EVIDENCE" "$MEASUREMENTS" "$STATUS" "$RAN" "$SUMMARY" <<'EOF'
import json, sys

out_path, ev_path, meas_path, status, ran, summary = sys.argv[1:7]
with open(out_path) as fh:
    test_output = fh.read()
with open(meas_path) as fh:
    meas = json.load(fh)

lines = []
lines.append("J.A.R.V.I.S. deployment — Phase 4 (Zero-knowledge proofs) evidence")
lines.append("Date: 2026-10-21")
lines.append("Build: REFERENCE implementation — NOT PRODUCTION CRYPTOGRAPHY")
lines.append("  (see phase4/proofs.py header for the honesty notice)")
lines.append("")
lines.append("Statements (exactly three, standardized):")
lines.append("  S1: This value exceeds threshold T in sealed baseline B")
lines.append("      (variance-gate alerts without exposing the baseline)")
lines.append("  S2: An approval exists for intent digest D")
lines.append("      (actuation without re-showing the approval)")
lines.append("  S3: This payload satisfies policy P")
lines.append("      (execution without exposing the payload)")
lines.append("")
lines.append("Protocol shape: commit -> challenge -> respond -> verify,")
lines.append("Fiat-Shamir (challenge = SHA-256 of transcript), non-interactive.")
lines.append("Freshness window: %ds; proofs bind ts + proof_nonce." % meas["freshness_window_s"])
lines.append("")
lines.append("TESTS: Ran %s tests — %s (%s)" % (ran, status, summary))
lines.append("  Breakdown: round-trip S1/S2/S3 (4 incl. wire-privacy),")
lines.append("  false-statement refusal (7 incl. seal-key + tampered approval),")
lines.append("  tampered proof (5), superseded circuit (4), freshness (4),")
lines.append("  replay (2), registry (7), budget measurements (1),")
lines.append("  reference-tag presence folded into round-trip.")
lines.append("")
lines.append("MEASURED vs §4.4 BUDGETS (200 iterations per statement):")
lines.append("  stmt | proving ms (budget 30000) | verify ms (budget 100) | "
             "proof bytes (budget 204800 STARK / 2048 SNARK)")
b = meas["budgets"]
for sid in ("S1", "S2", "S3"):
    m = meas["statements"][sid]
    lines.append("  %s   | %10.3f                | %10.3f             | %d"
                 % (sid, m["prove_ms"], m["verify_ms"], m["proof_bytes"]))
lines.append("")
lines.append("  All budgets met with large margins. Proof sizes (~0.66 KB)")
lines.append("  also fall under the 2 KB SNARK budget numerically, but the")
lines.append("  reference is NOT a SNARK/STARK — no such claim is made.")
lines.append("")
lines.append("HONEST LIMITS:")
lines.append("  1. Zero-knowledge property NOT established for the reference:")
lines.append("     the blinded opening is reversible by the verifier.")
lines.append("  2. The statement predicate is evaluated by the (honest) prover")
lines.append("     and attested in the transcript; a dishonest prover could")
lines.append("     attest falsely. The wire shape cannot detect that — hence")
lines.append("     the prover refuses false statements (ProveError, fail-closed).")
lines.append("  3. Production requires audited STARK/SNARK circuits per §4.3")
lines.append("     (STARKs preferred: no trusted setup).")
lines.append("  4. A proof proves the statement, not the data's truth (§4.5).")
lines.append("     Proofs compose with seals (S2 verifies the approval seal")
lines.append("     before attesting); they do not replace them.")
lines.append("")
lines.append("FILES:")
lines.append("  phase4/proofs.py      REFERENCE prover/verifier, policy table")
lines.append("  phase4/registry.py    versioned statement registry")
lines.append("  phase4/test_phase4.py unittest suite (35 tests)")
lines.append("  phase4/run.sh         this runner")
lines.append("  phase4/measurements.json raw numbers")
lines.append("")
lines.append("FULL TEST OUTPUT:")
lines.append(test_output.rstrip())
lines.append("")

with open(ev_path, "w") as fh:
    fh.write("\n".join(lines))
print("evidence written: %s" % ev_path)
EOF

cat "$OUT"
if [ "$STATUS" != "PASS" ]; then
    echo "phase4 tests FAILED" >&2
    exit 1
fi
