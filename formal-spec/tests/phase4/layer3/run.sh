#!/bin/bash
# Phase 4, Layer 3 — adversarial chaos tests.
# Python 3 stdlib only. No network, no git, no publishing.
#
# Runs the three families (NL network-loss, AD adversarial-duplicates,
# AX ambiguous-chaos) and writes:
#   tests/phase4/evidence/<date>-phase4-layer3.log            — full verbose output
#   tests/phase4/evidence/<date>-phase4-layer3-rejections.log — every refusal, with cause
#
# Exact command (from this directory):  ./run.sh
set -uo pipefail
cd "$(dirname "$0")"
OUTDIR="../evidence"
mkdir -p "$OUTDIR"
DATE=$(date +%F)
LOG="$OUTDIR/${DATE}-phase4-layer3.log"
REJ="$OUTDIR/${DATE}-phase4-layer3-rejections.log"
export PHASE4_REJECTION_LOG="$REJ"
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
