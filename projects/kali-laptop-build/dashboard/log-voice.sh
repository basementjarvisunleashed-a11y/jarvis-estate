#!/usr/bin/env bash
# log-voice.sh — feed the dashboard's live Conversation panel.
#
# The voice loop calls this so the dashboard glows and types out the
# conversation as it happens:
#   - when it hears speech:      ./log-voice.sh state listening
#   - when a phrase is heard:    ./log-voice.sh HgX "VLC on, play the Sopranos"
#   - when Jarvis starts to speak: ./log-voice.sh state speaking
#   - what Jarvis is saying:    ./log-voice.sh Jarvis "Playing The Sopranos, sir."
#   - when the exchange is over: ./log-voice.sh state idle
#
# Usage:
#   ./log-voice.sh <HgX|Jarvis> <text...>
#       append {"time","speaker","text"} to voice-events.jsonl
#   ./log-voice.sh state <listening|speaking|idle>
#       write {"state": "...", "time": ...} to voice-state.json
#
# Env:
#   VOICE_EVENTS — path to the events file (default: voice-events.jsonl next to this script)
#   VOICE_STATE  — path to the state file (default: voice-state.json next to this script)
#
# The state file is written atomically (temp file + rename) so the dashboard
# server never reads a half-written file.
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVENTS="${VOICE_EVENTS:-$SCRIPT_DIR/voice-events.jsonl}"
STATE_FILE="${VOICE_STATE:-$SCRIPT_DIR/voice-state.json}"

usage() {
  echo "usage: $0 <HgX|Jarvis> <text...>" >&2
  echo "       $0 state <listening|speaking|idle>" >&2
  exit 1
}

TIME="$(date -Iseconds)"

if [ "$#" -lt 2 ]; then
  usage
fi

if [ "$1" = "state" ]; then
  STATE="$2"
  case "$STATE" in
    listening|speaking|idle) ;;
    *) echo "error: state must be listening, speaking, or idle (got '$STATE')" >&2; exit 1 ;;
  esac
  python3 - "$STATE_FILE" "$TIME" "$STATE" <<'PYEOF'
import json, sys
state_file, when, state = sys.argv[1:4]
entry = {"state": state, "time": when}
tmp = state_file + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")
import os
os.replace(tmp, state_file)
print(json.dumps(entry))
PYEOF
  exit 0
fi

SPEAKER="$1"
case "$SPEAKER" in
  HgX|Jarvis) ;;
  *) echo "error: speaker must be HgX or Jarvis (got '$SPEAKER')" >&2; exit 1 ;;
esac
shift
TEXT="$*"

python3 - "$EVENTS" "$TIME" "$SPEAKER" "$TEXT" <<'PYEOF'
import json, sys
events, when, speaker, text = sys.argv[1:5]
entry = {"time": when, "speaker": speaker, "text": text}
with open(events, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")
print(json.dumps(entry))
PYEOF
