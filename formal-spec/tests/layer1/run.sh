#!/bin/sh
# Phase 2, Layer 1 — static contract tests.
# Exact command (from this directory):  python3 -m unittest test_layer1_contracts -v
set -e
cd "$(dirname "$0")"
exec python3 -m unittest test_layer1_contracts -v
