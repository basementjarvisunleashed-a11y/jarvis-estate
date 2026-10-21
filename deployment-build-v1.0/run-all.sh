#!/bin/sh
# J.A.R.V.I.S. deployment build — full test run, all phases.
# Usage: sh run-all.sh
# Private working-room build. Nothing here leaves the workspace.
set -e
cd "$(dirname "$0")"
echo "=== Phase 0: Ground ==="
python3 -m unittest phase0.test_phase0 2>&1 | tail -3
echo "=== Phase 1: Pull ==="
python3 -m unittest phase1.test_phase1 2>&1 | tail -3
echo "=== Phase 2: Orchestra ==="
python3 -m unittest phase2.test_phase2 2>&1 | tail -3
echo "=== Phase 3: Handshake ==="
python3 -m unittest phase3.test_phase3 2>&1 | tail -3
echo "=== Phase 4: Proofs ==="
python3 -m unittest phase4.test_phase4 2>&1 | tail -3
echo "=== DONE ==="
