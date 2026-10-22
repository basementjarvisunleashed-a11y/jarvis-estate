#!/bin/bash
# Phase 5, Layer 2 -- security test suite: threat -> control verification.
# Python 3 stdlib only. No network, no git, no publishing. Deterministic:
# fixed virtual clocks, hand-built cases, no randomness.
#
# Runs the seven families (SP spoofing, TM tampering, RP repudiation,
# DC disclosure, DF DoS/fatigue, HL honest limitations, EL elevation)
# and writes:
#   tests/phase5/evidence/<date>-phase5-layer2.log            -- full verbose output
#   tests/phase5/evidence/<date>-phase5-layer2-rejections.log -- every refusal, with cause
#
# Exact command (from this directory):  ./run.sh
set -uo pipefail
cd "$(dirname "$0")"
OUTDIR="../evidence"
mkdir -p "$OUTDIR"
DATE=$(date +%F)
LOG="$OUTDIR/${DATE}-phase5-layer2.log"
REJ="$OUTDIR/${DATE}-phase5-layer2-rejections.log"
SUM="$OUTDIR/${DATE}-phase5-layer2-summary.txt"
export PHASE5_REJECTION_LOG="$REJ"
: > "$REJ"
: > "$LOG"
python3 -m unittest discover -s . -p "test_*.py" -v > "$LOG" 2>&1
CODE=$?
python3 - "$LOG" <<'EOF' > "$SUM"
import re, sys
text = open(sys.argv[1]).read()
families = {"test_spoofing.py": "SP", "test_tampering.py": "TM",
            "test_repudiation.py": "RP", "test_disclosure.py": "DC",
            "test_dos_fatigue.py": "DF", "test_honest_limits.py": "HL",
            "test_elevation.py": "EL"}
flags = re.M  # $ must match every line end, not just end of string
passed = len(re.findall(r" \.\.\. ok$", text, flags))
failed = len(re.findall(r" \.\.\. (FAIL|ERROR)$", text, flags))
refusals = len(open(__import__("os").environ["PHASE5_REJECTION_LOG"]).readlines())
print(f"phase5-layer2: {passed} passed, {failed} failed, "
      f"{refusals} refusals logged")
for fname, tag in families.items():
    mod = fname[:-3].replace(".", r"\.")  # module name, no .py
    p = len(re.findall(rf"\({mod}\..*\) \.\.\. ok$", text, flags))
    f = len(re.findall(rf"\({mod}\..*\) \.\.\. (FAIL|ERROR)$", text, flags))
    print(f"  {tag} {fname}: {p} passed, {f} failed")
EOF
cat "$SUM"
echo "---"
echo "evidence: $LOG"
echo "rejections: $REJ ($(wc -l < "$REJ") refused requests logged)"
echo "summary: $SUM"
if [ "$CODE" -ne 0 ]; then
  echo "RESULT: FAIL (exit $CODE)"
else
  echo "RESULT: ALL GREEN"
fi
exit "$CODE"
