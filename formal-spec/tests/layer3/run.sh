#!/bin/sh
# Phase 2, Layer 3 — chaos tests.
# Exact command (from this directory):  python3 -m unittest test_layer3_chaos -v
set -e
cd "$(dirname "$0")"
exec python3 -m unittest test_layer3_chaos -v
