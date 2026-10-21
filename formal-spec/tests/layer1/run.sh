#!/bin/sh
# Phase 2, Layer 1 — static contract tests (all modules).
# Exact command (from this directory):
#   python3 -m unittest test_layer1_contracts test_schema_examples test_rendering_invariants -v
# Fixed 2026-10-21 (total verification sweep): run.sh previously ran only
# test_layer1_contracts (39 tests); it now runs all three modules (83 tests).
set -e
cd "$(dirname "$0")"
exec python3 -m unittest test_layer1_contracts test_schema_examples test_rendering_invariants -v
