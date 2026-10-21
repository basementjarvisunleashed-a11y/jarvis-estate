#!/bin/bash
# Phase 1 test runner — pull protocol + orchestrator loop + chaos.
# Python 3 stdlib only. No network, no git, no publishing.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 phase1/test_phase1.py
