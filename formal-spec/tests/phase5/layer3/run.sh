#!/bin/bash
# Phase 5, Layer 3 -- adversarial test suite: the four agent-specific
# threats under fire (T-22 prompt injection, T-23 stale-state
# manipulation, T-24 approval fatigue, T-25 subagent deception).
# Python 3 stdlib only. No network, no git, no publishing.
# Deterministic: fixed virtual clocks, hand-built adversarial cases,
# systematic permutation enumeration (itertools) -- no randomness.
#
# Runs the four families (PI prompt injection, SS stale state, AF
# approval fatigue, SD subagent deception) and writes:
#   tests/phase5/evidence/<date>-phase5-layer3.log             -- full verbose output
#   tests/phase5/evidence/<date>-phase5-layer3-rejections.log  -- every refusal/flag, with cause
#   tests/phase5/evidence/<date>-phase5-layer3-verdicts.jsonl  -- one machine-checkable
#                                                                verdict per adversarial case
#   tests/phase5/evidence/<date>-phase5-layer3-summary.txt     -- pass/fail per family + verdict tally
#
# Exact command (from this directory):  ./run.sh
set -uo pipefail
cd "$(dirname "$0")"
OUTDIR="../evidence"
mkdir -p "$OUTDIR"
DATE=$(date +%F)
LOG="$OUTDIR/${DATE}-phase5-layer3.log"
REJ="$OUTDIR/${DATE}-phase5-layer3-rejections.log"
VER="$OUTDIR/${DATE}-phase5-layer3-verdicts.jsonl"
SUM="$OUTDIR/${DATE}-phase5-layer3-summary.txt"
export PHASE5_REJECTION_LOG="$REJ"
export PHASE5_VERDICTS_FILE="$VER"
: > "$REJ"
: > "$LOG"
: > "$VER"
python3 -m unittest discover -s . -p "test_*.py" -v > "$LOG" 2>&1
CODE=$?
python3 - "$LOG" "$VER" <<'EOF' > "$SUM"
import json, os, re, sys
text = open(sys.argv[1], encoding="utf-8").read()
verdicts = [json.loads(l) for l in
            open(sys.argv[2], encoding="utf-8") if l.strip()]
families = {"test_prompt_injection": "PI",
            "test_stale_state": "SS",
            "test_approval_fatigue": "AF",
            "test_subagent_deception": "SD"}
passed = failed = 0
fam_stats = {}
current_mod = None
for line in text.splitlines():
    m = re.match(r"^\S+ \((test_\w+)\.", line)
    if m:
        current_mod = m.group(1)  # test id line names the module
    m2 = re.match(r".* \.\.\. (ok|FAIL|ERROR)$", line)
    if m2:
        if m2.group(1) == "ok":
            passed += 1
        else:
            failed += 1
        tag = families.get(current_mod, "??")
        key = (tag, m2.group(1))
        fam_stats[key] = fam_stats.get(key, 0) + 1
        current_mod = None
refusals = len(open(os.environ["PHASE5_REJECTION_LOG"],
                    encoding="utf-8").readlines())
print(f"phase5-layer3: {passed} passed, {failed} failed, "
      f"{refusals} refusals/flags logged")
for mod, tag in families.items():
    p = fam_stats.get((tag, "ok"), 0)
    f = (fam_stats.get((tag, "FAIL"), 0) +
         fam_stats.get((tag, "ERROR"), 0))
    print(f"  {tag} {mod}.py: {p} passed, {f} failed")
print(f"adversarial cases: {len(verdicts)}")
cats = {}
for v in verdicts:
    key = (v["case"][:2], v["verdict"])
    cats[key] = cats.get(key, 0) + 1
for (fam, cat), n in sorted(cats.items()):
    print(f"  {fam} {cat}: {n}")
# every verdict must name a threat and a control, and case IDs must be unique
unnamed = [v["case"] for v in verdicts
           if not v.get("threat") or not v.get("control")]
cases = [v["case"] for v in verdicts]
dupes = sorted({c for c in cases if cases.count(c) > 1})
print(f"verdicts missing threat/control IDs: {len(unnamed)} {unnamed}")
print(f"duplicate case IDs: {len(dupes)} {dupes}")
findings = [v for v in verdicts if v["verdict"] == "finding"]
print(f"findings (broken controls): {len(findings)}")
for f in findings:
    print(f"  FINDING {f['case']} [{f['threat']}/{f['control']}]: "
          f"{f['detail']}")
EOF
cat "$SUM"
echo "---"
echo "evidence: $LOG"
echo "rejections: $REJ ($(wc -l < "$REJ") refused/flagged events logged)"
echo "verdicts: $VER ($(wc -l < "$VER") case verdicts)"
echo "summary: $SUM"
if [ "$CODE" -ne 0 ]; then
  echo "RESULT: FAIL (exit $CODE)"
else
  echo "RESULT: ALL GREEN"
fi
exit "$CODE"
