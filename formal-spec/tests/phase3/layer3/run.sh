#!/bin/bash
# Phase 3, Layer 3 — adversarial chaos tests.
# Python 3 stdlib only. No randomness, no threads, no network, no git, no publishing.
#
# Runs the five families (AR adversarial race, PT partition, SK skew,
# RP replay, MX mixed chaos) and writes:
#   tests/phase3/evidence/<date>-phase3-layer3.log            — full verbose output
#   tests/phase3/evidence/<date>-phase3-layer3-rejections.log — every refusal, with cause
#   tests/phase3/evidence/<date>-phase3-layer3-verdicts.log   — one row per adversarial case
#
# Exact command (from this directory):  ./run.sh
set -uo pipefail
cd "$(dirname "$0")"
OUTDIR="../evidence"
mkdir -p "$OUTDIR"
DATE=$(date +%F)
LOG="$OUTDIR/${DATE}-phase3-layer3.log"
REJ="$OUTDIR/${DATE}-phase3-layer3-rejections.log"
VER="$OUTDIR/${DATE}-phase3-layer3-verdicts.log"
export PHASE3_REJECTION_LOG="$REJ"
export PHASE3_L3_VERDICTS="$VER"
: > "$REJ"
: > "$LOG"
: > "$VER"
python3 -m unittest discover -s . -p "test_*.py" -v > "$LOG" 2>&1
CODE=$?
tail -5 "$LOG"
echo "---"
echo "evidence: $LOG"
echo "rejections: $REJ ($(wc -l < "$REJ") refused requests logged)"
echo "verdicts: $VER ($(wc -l < "$VER") adversarial cases)"
if [ "$CODE" -ne 0 ]; then
  echo "RESULT: FAIL (exit $CODE)"
else
  echo "RESULT: ALL GREEN"
fi
exit "$CODE"
