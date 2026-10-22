#!/usr/bin/env bash
# Phase 6 Layer 2 — run the offline replay harness (deterministic).
# Usage: run.sh [--weighted] [--corpus real|all]
#   --weighted --corpus real   -> weighted EVIDENCE run (102 real entries)
#   --weighted --corpus all    -> weighted sanity check (real + synthetic, NOT evidence)
set -euo pipefail
cd "$(dirname "$0")"
python3 replay.py "$@" | tee ../evidence/2026-10-22-phase6-layer2-run.out
echo "exit=$?"
