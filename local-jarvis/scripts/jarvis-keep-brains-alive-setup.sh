#!/bin/bash
# Keep both brains always loaded — 9B on VRAM + 27B on system RAM.
# HgX order, 2026-11-06: "always load both llms".
# Run once on the Acer:  bash ~/Downloads/jarvis-keep-brains-alive-setup.sh
# What it does:
#  1. Writes ~/Jarvis/autostart/keep-brains-alive.sh — a tiny ping that
#     loads both models with keep_alive 24h (via Ollama native /api/chat).
#  2. Installs a cron job running that ping every 6 hours, so neither
#     brain ever expires — 24h pin, refreshed every 6h.
#  3. Rewrites the router launcher so the hard route also pins 24h
#     (was 1h), and restarts the router to pick that up.
#  4. Runs the ping now, then prints `ollama ps` so you can see both loaded.
# It deletes nothing. Re-running is safe.
set -u
HOME_DIR="$HOME"
LAUNCH_DIR="$HOME_DIR/Jarvis/autostart"
mkdir -p "$LAUNCH_DIR"

cat > "$LAUNCH_DIR/keep-brains-alive.sh" <<'KEEPER'
#!/bin/bash
# Ping both brains, pin each for 24h. Quiet, short prompt, no thinking.
curl -s -m 300 http://127.0.0.1:11434/api/chat -H 'Content-Type: application/json' -d '{"model":"qwen9b-abliterated","messages":[{"role":"user","content":"ping"}],"stream":false,"keep_alive":"24h","think":false}' >/dev/null 2>&1
curl -s -m 600 http://127.0.0.1:11434/api/chat -H 'Content-Type: application/json' -d '{"model":"huihui_ai/Qwen3.8-abliterated:27b","messages":[{"role":"user","content":"ping"}],"stream":false,"keep_alive":"24h","think":false}' >/dev/null 2>&1
echo "$(date '+%F %T') keep-alive ping done"
KEEPER
chmod +x "$LAUNCH_DIR/keep-brains-alive.sh"
echo "keep-alive script: $LAUNCH_DIR/keep-brains-alive.sh"

# Cron: every 6 hours, refresh the 24h pin.
TMP_CRON="$(mktemp)"
crontab -l 2>/dev/null | grep -v "keep-brains-alive" > "$TMP_CRON" || true
echo "0 */6 * * * $LAUNCH_DIR/keep-brains-alive.sh >> $HOME_DIR/Jarvis/keep-alive.log 2>&1" >> "$TMP_CRON"
crontab "$TMP_CRON"
rm -f "$TMP_CRON"
echo "cron installed:"
crontab -l | grep keep-brains-alive

# Router launcher: hard pin 24h (was 1h), restart router to pick it up.
ROUTER_FILE=""
for p in "$HOME_DIR/tonight-scripts/acer-llm-consolidation/04-little-router.py" "$HOME_DIR/workspace/family-bot/acer-llm-consolidation/04-little-router.py" "$HOME_DIR/acer-llm-consolidation/04-little-router.py"; do
  if [ -f "$p" ]; then ROUTER_FILE="$p"; break; fi
done
if [ -n "$ROUTER_FILE" ]; then
  ROUTER_DIR="$(dirname "$ROUTER_FILE")"
  cat > "$LAUNCH_DIR/start-router.sh" <<EOF
#!/bin/bash
cd "$ROUTER_DIR" || exit 1
KEEP_ALIVE_EASY=24h KEEP_ALIVE_HARD=24h exec python3 04-little-router.py >> "$HOME_DIR/Jarvis/router.log" 2>&1
EOF
  chmod +x "$LAUNCH_DIR/start-router.sh"
  echo "router launcher updated (hard pin now 24h)"
  pkill -f "04-little-router.py" 2>/dev/null || true
  sleep 2
  nohup "$LAUNCH_DIR/start-router.sh" >/dev/null 2>&1 &
  sleep 3
  curl -s -m 5 http://127.0.0.1:11435/health && echo "  <- router /health after restart"
else
  echo "router: NOT FOUND — launcher not updated, cron ping still works directly on Ollama"
fi

# Load both brains now.
echo "Loading both brains now — the 27B takes a minute to load into RAM..."
"$LAUNCH_DIR/keep-brains-alive.sh"
sleep 2
echo "--- ollama ps (both should be listed) ---"
ollama ps
echo "Done. Both brains stay loaded; the pin refreshes every 6 hours."
