#!/bin/bash
# keep-brains-alive-v2.sh — patched keep-alive for the GPU orchestrator.
#
# Drop-in replacement for keep-brains-alive.sh. Same log file, same curl
# commands, same order (9B first, then 27B). The one change: it SKIPS the
# 9B ping while the 9B is parked, so the keep-alive never reloads it
# mid-render and steals VRAM from ComfyUI.
#
# How it decides to skip the 9B:
#   1. Read the orchestrator state file (~/Jarvis/gpu-state.json). If
#      mode is "comfy", the 9B is parked: skip it.
#   2. Else, check ComfyUI directly (curl :8188). If it answers, the
#      card is busy even if the state file is stale or missing: skip it.
#   3. Otherwise, ping the 9B as today.
# The 27B is ALWAYS pinged (with num_gpu 0). It lives in system RAM, so
# its ping never touches VRAM and is always safe.
#
# Usage:
#   ./keep-brains-alive-v2.sh            normal run (as the cron calls it)
#   ./keep-brains-alive-v2.sh --dry-run  print what it would do, ping nothing
#
# Cron (unchanged, just the new filename):
#   0 */6 * * * $HOME/Jarvis/autostart/keep-brains-alive-v2.sh >> $HOME/Jarvis/keep-alive.log 2>&1

set -u

STATE_FILE="${GPU_ORCH_STATE_FILE:-$HOME/Jarvis/gpu-state.json}"
LOG_FILE="${GPU_ORCH_LOG_FILE:-$HOME/Jarvis/keep-alive.log}"
OLLAMA_URL="${GPU_ORCH_OLLAMA_URL:-http://127.0.0.1:11434}"
COMFY_URL="${GPU_ORCH_COMFY_URL:-http://127.0.0.1:8188}"
DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
    DRY_RUN=1
fi

# Read the orchestrator mode from the state file. Empty if unreadable.
MODE=""
if [ -f "$STATE_FILE" ]; then
    MODE="$(python3 -c "import json,sys; print(json.load(open('$STATE_FILE')).get('mode',''))" 2>/dev/null || true)"
fi

# Is ComfyUI up (the direct check, in case the state file is stale)?
COMFY_UP=0
if curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$COMFY_URL/" 2>/dev/null | grep -q "^200$"; then
    COMFY_UP=1
fi

SKIP_NINE_B=0
SKIP_REASON=""
if [ "$MODE" = "comfy" ]; then
    SKIP_NINE_B=1
    SKIP_REASON="mode is comfy (9B parked)"
elif [ "$COMFY_UP" = "1" ]; then
    SKIP_NINE_B=1
    SKIP_REASON="ComfyUI is up (card busy)"
fi

ping_nine_b() {
    if [ "$DRY_RUN" = "1" ]; then
        echo "[dry-run] would ping 9B (keep_alive 24h, think false)"
        return 0
    fi
    curl -s --max-time 300 "$OLLAMA_URL/api/chat" -H "Content-Type: application/json" -d '{"model": "qwen9b-abliterated", "messages": [{"role": "user", "content": "Pong"}], "stream": false, "keep_alive": "24h", "think": false}' > /dev/null
}

ping_twenty_seven_b() {
    if [ "$DRY_RUN" = "1" ]; then
        echo "[dry-run] would ping 27B (keep_alive 24h, think false, num_gpu 0)"
        return 0
    fi
    curl -s --max-time 600 "$OLLAMA_URL/api/chat" -H "Content-Type: application/json" -d '{"model": "huihui_ai/Qwen3.8-abliterated:27b", "messages": [{"role": "user", "content": "Pong"}], "stream": false, "keep_alive": "24h", "think": false, "options": {"num_gpu": 0}}' > /dev/null
}

if [ "$SKIP_NINE_B" = "1" ]; then
    echo "keep-alive: skipping 9B ping ($SKIP_REASON)"
else
    ping_nine_b
fi
ping_twenty_seven_b
echo "keep-alive ping done $(date '+%Y-%m-%d %H:%M:%S')"
