#!/bin/sh
# Phase 3 — Complete handshake: run the test suite, then write the
# instrumented evidence log. Evidence is written only on a green suite.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TEST_OUT="$(python3 -m unittest phase3.test_phase3 2>&1)"
echo "$TEST_OUT"
TEST_SUMMARY="$(printf '%s\n' "$TEST_OUT" | grep -E '^(Ran [0-9]+ tests|OK|FAILED)' | paste -sd' ' -)"

TEST_SUMMARY="$TEST_SUMMARY" python3 -c "
import os, sys
sys.path.insert(0, '.')
from phase3.handshake import write_evidence_log
write_evidence_log('tests/evidence/phase3-2026-10-21.log',
                   os.environ.get('TEST_SUMMARY', ''))
"
echo "evidence: tests/evidence/phase3-2026-10-21.log"
