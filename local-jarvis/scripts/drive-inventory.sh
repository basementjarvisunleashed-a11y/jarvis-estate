#!/usr/bin/env bash
# drive-inventory.sh — READ-ONLY listing of what's on the media drive, for the clean-out.
# Nothing is deleted by this script. It only looks.
# Usage: ./drive-inventory.sh [/mnt/hgx]
set -u

ROOT="${1:-/mnt/hgx}"
[ -d "$ROOT" ] || { echo "not mounted: $ROOT"; exit 1; }

echo "== top level =="
ls -la "$ROOT"
echo
echo "== biggest top-level folders =="
du -sh "$ROOT"/*/ 2>/dev/null | sort -rh | head -20
echo
echo "== total =="
df -h "$ROOT"
