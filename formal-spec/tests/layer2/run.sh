#!/bin/sh
# Phase 2, Layer 2 — property-based tests.
# Exact command (from this directory):  python3 -m unittest test_layer2_properties -v
set -e
cd "$(dirname "$0")"
exec python3 -m unittest test_layer2_properties -v
