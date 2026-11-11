#!/usr/bin/env bash
# log-rea.sh — append one REA run to rea-history.jsonl (read by the dashboard).
#
# Usage:
#   ./log-rea.sh <target> <summary...>
#
#   target   — the file/app REA analysed (path or name)
#   summary  — one-line result, e.g. "12 functions named, looks like ARMv7 firmware"
#
# Example:
#   ./log-rea.sh $HOME/firmware.bin "REA: 34 functions named, 2 suspicious strings, Ghidra project saved"
#
# Env:
#   REA_HISTORY — path to the .jsonl file (default: rea-history.jsonl next to this script)
#
# Tip: call it right after an `npx rea-agents analyze` run, or wrap it in a
# small shell function so every REA run is logged automatically.
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HISTORY="${REA_HISTORY:-$SCRIPT_DIR/rea-history.jsonl}"

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <target> <summary...>" >&2
  exit 1
fi

TARGET="$1"
shift
SUMMARY="$*"
TIME="$(date -Iseconds)"

python3 - "$HISTORY" "$TIME" "$TARGET" "$SUMMARY" <<'PYEOF'
import json, sys
history, when, target, summary = sys.argv[1:5]
entry = {"time": when, "target": target, "summary": summary}
with open(history, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")
print(json.dumps(entry))
PYEOF
