#!/bin/sh
# Start the CrackMe v9 Sovereign REA runner (v1) in the background.
# Runs crackme-v9.py: verifies the vault digests, copies the five vault
# files to ~/crackme-v9/work/ (the originals are never modified),
# gunzips core.wasm.gz there, runs the recon (file types, a pure-Python
# WASM parser, wabt if present, a Node export cross-check), writes the
# tool-applicability section, runs five short 27B analysis calls (one
# per task, one section appended per call), verifies at most 3 candidate
# 16-character keys in the working copy, and writes the summary to
# ~/crackme-v9/report.md. Each result is appended immediately after it
# succeeds or fails honestly. Expect roughly 30-90 minutes (five short
# 27B calls at ~5-27 min each, plus the WASM disassembly if wabt is
# present). Never uses elevated privileges. Never touches the dashboard,
# the webcam app, the brains, or the router. Never deletes anything.
# Re-running is safe: completed tasks are skipped (resumable).
DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$DIR/crackme-v9-run.log"
nohup python3 "$DIR/crackme-v9.py" </dev/null >"$LOG" 2>&1 &
sleep 2
PID="$(pgrep -f "python3 $DIR/crackme-v9.py" | head -n 1)"
if [ -n "$PID" ]; then
  echo "Started crackme-v9 v1 (PID $PID)."
else
  echo "crackme-v9 v1 launched (PID not confirmed — it may have finished already; check the run log)."
fi
echo "Run log: $LOG"
echo "Job log: ~/crackme-v9/crackme-v9.log"
echo "Status:  ~/crackme-v9/status.txt"
echo "Report:  ~/crackme-v9/report.md"
echo "Check it: tail -30 ~/crackme-v9/crackme-v9.log"
echo "Stop it:  pkill -f crackme-v9.py"
