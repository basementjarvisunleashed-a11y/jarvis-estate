#!/bin/sh
# Start the overnight BLA + 27B runner (v1) in the background.
# HgX starts this before bed; it runs while he sleeps and leaves a
# morning report. It does two jobs, in order:
#   1. Resume the CrackMe v9 Sovereign runner to completion (it was
#      killed at 08:25 ET 2026-11-10 to free the CPU for Claude Code;
#      it resumes from the WASM task). It may take hours — the runner
#      waits for it (up to 12 hours) and never kills it.
#   2. A BLA red-vs-blue test: `bla harden` on a tiny test license-check
#      file (created by the runner in its own work dir — NOT a real
#      artifact), then ONE short 27B call analyses the hardened output
#      and reports whether the 27B can still recover the secret key.
# Before it starts, it checks that no other 27B runner is running (the
# HARD RULE — never two 27B runners at once) and that the 27B is loaded
# and resident (it loads it if needed; the 9B is untouched, it lives on
# the GPU). Re-running is safe: completed work is skipped (resumable).
# Never uses elevated privileges. Never deletes anything. Never touches
# the BLA vault originals, the dashboard, the webcam app, the brains,
# or the router.
DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$DIR/overnight-run.log"
nohup python3 "$DIR/overnight-27b.py" </dev/null >"$LOG" 2>&1 &
sleep 2
PID="$(pgrep -f "python3 $DIR/overnight-27b.py" | head -n 1)"
if [ -n "$PID" ]; then
  echo "Started overnight-27b v1 (PID $PID)."
else
  echo "overnight-27b v1 launched (PID not confirmed — it may have finished already or been blocked by the duplicate guard; check the run log)."
fi
echo "Run log: $LOG"
echo "Job log: ~/overnight-27b/overnight.log"
echo "Status:  ~/overnight-27b/status.txt"
echo "Report:  ~/overnight-27b/report.md"
echo "Check it: tail -30 ~/overnight-27b/overnight.log"
echo "Stop it:  pkill -f overnight-27b.py"
