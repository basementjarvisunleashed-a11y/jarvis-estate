#!/bin/bash
# Phase 3, Layer 2 — protocol tests.
# Python 3 stdlib only. No network, no git, no publishing.
#
# Runs the five families (RT revision-token, SM stale-mutation order,
# DA digest-bound approval, OT offline-tap, FV first-valid-decision,
# CT conflict table) and writes:
#   tests/phase3/evidence/<date>-phase3-layer2.log            — full verbose output
#   tests/phase3/evidence/<date>-phase3-layer2-rejections.log — every refusal, with cause
#
# Exact command (from this directory):  ./run.sh
set -uo pipefail
cd "$(dirname "$0")"
OUTDIR="../evidence"
mkdir -p "$OUTDIR"
DATE=$(date +%F)
LOG="$OUTDIR/${DATE}-phase3-layer2.log"
REJ="$OUTDIR/${DATE}-phase3-layer2-rejections.log"
export PHASE3_REJECTION_LOG="$REJ"
: > "$REJ"
: > "$LOG"
python3 -m unittest discover -s . -p "test_*.py" -v > "$LOG" 2>&1
CODE=$?
tail -5 "$LOG"
echo "---"
echo "evidence: $LOG"
echo "rejections: $REJ ($(wc -l < "$REJ") refused requests logged)"
if [ "$CODE" -ne 0 ]; then
  echo "RESULT: FAIL (exit $CODE)"
else
  echo "RESULT: ALL GREEN"
fi
exit "$CODE"
