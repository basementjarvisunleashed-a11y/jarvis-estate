#!/usr/bin/env bash
# Phase 2 test run: contracts, enrollment, attention budget, plane enforcement.
# Python 3 stdlib only. No network, no git, no publishing.
set -uo pipefail
cd "$(dirname "$0")"
EVIDENCE="../tests/evidence/phase2-2026-10-21.log"
OUT="$(mktemp)"

python3 test_phase2.py >"$OUT" 2>&1
rc=$?
cat "$OUT"
{
  echo "---"
  echo "unittest exit code: $rc"
  tail -n 3 "$OUT"
} >> "$EVIDENCE"
rm -f "$OUT"
echo "evidence: $EVIDENCE"
exit "$rc"
