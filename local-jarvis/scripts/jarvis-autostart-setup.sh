#!/bin/bash
# Jarvis autostart setup — router + orchestrator + dashboard, on login.
# Run once on the Acer:  bash ~/jarvis-autostart-setup.sh
# Creates Xfce autostart entries (~/.config/autostart/) and launcher
# scripts in ~/Jarvis/autostart/. Idempotent: re-running is safe.
# It starts the services now too (if not already running) and verifies them.
# It deletes nothing and changes no other settings.
set -u
HOME_DIR="$HOME"
AUTOSTART_DIR="$HOME_DIR/.config/autostart"
LAUNCH_DIR="$HOME_DIR/Jarvis/autostart"
mkdir -p "$AUTOSTART_DIR" "$LAUNCH_DIR"

find_file() {
  for p in "$@"; do
    if [ -f "$p" ]; then echo "$p"; return 0; fi
  done
  return 1
}

PY_ORCH="python3"
if [ -x "$HOME_DIR/Jarvis/venv/bin/python" ]; then PY_ORCH="$HOME_DIR/Jarvis/venv/bin/python"; fi

# --- Router: 04-little-router.py, port 11435 ---
ROUTER_FILE="$(find_file "$HOME_DIR/tonight-scripts/acer-llm-consolidation/04-little-router.py" "$HOME_DIR/workspace/family-bot/acer-llm-consolidation/04-little-router.py" "$HOME_DIR/acer-llm-consolidation/04-little-router.py" || true)"
if [ -n "${ROUTER_FILE:-}" ]; then
  ROUTER_DIR="$(dirname "$ROUTER_FILE")"
  cat > "$LAUNCH_DIR/start-router.sh" <<EOF
#!/bin/bash
cd "$ROUTER_DIR" || exit 1
exec python3 04-little-router.py >> "$HOME_DIR/Jarvis/router.log" 2>&1
EOF
  chmod +x "$LAUNCH_DIR/start-router.sh"
  cat > "$AUTOSTART_DIR/jarvis-router.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Jarvis Router
Comment=Little Router on 127.0.0.1:11435
Exec=$LAUNCH_DIR/start-router.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
  echo "router: $ROUTER_FILE"
else
  echo "router: NOT FOUND — looked in tonight-scripts and workspace; no autostart entry created"
fi

# --- Orchestrator: ~/Jarvis/orchestrator.py, port 8080 ---
if [ -f "$HOME_DIR/Jarvis/orchestrator.py" ]; then
  cat > "$LAUNCH_DIR/start-orchestrator.sh" <<EOF
#!/bin/bash
cd "$HOME_DIR/Jarvis" || exit 1
exec $PY_ORCH orchestrator.py >> "$HOME_DIR/Jarvis/orchestrator.log" 2>&1
EOF
  chmod +x "$LAUNCH_DIR/start-orchestrator.sh"
  cat > "$AUTOSTART_DIR/jarvis-orchestrator.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Jarvis Orchestrator
Comment=Local Jarvis orchestrator on :8080
Exec=$LAUNCH_DIR/start-orchestrator.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
  echo "orchestrator: $HOME_DIR/Jarvis/orchestrator.py (python: $PY_ORCH)"
else
  echo "orchestrator: NOT FOUND at ~/Jarvis/orchestrator.py; no autostart entry created"
fi

# --- Dashboard: server.py, port 8899 ---
DASH_FILE="$(find_file "$HOME_DIR/dashboard/server.py" "$HOME_DIR/workspace/family-bot/dashboard/server.py" "$HOME_DIR/Jarvis/dashboard/server.py" "$HOME_DIR/tonight-scripts/dashboard/server.py" || true)"
if [ -n "${DASH_FILE:-}" ]; then
  DASH_DIR="$(dirname "$DASH_FILE")"
  cat > "$LAUNCH_DIR/start-dashboard.sh" <<EOF
#!/bin/bash
cd "$DASH_DIR" || exit 1
exec python3 server.py >> "$HOME_DIR/Jarvis/dashboard.log" 2>&1
EOF
  chmod +x "$LAUNCH_DIR/start-dashboard.sh"
  cat > "$AUTOSTART_DIR/jarvis-dashboard.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Jarvis Dashboard
Comment=Jarvis dashboard on 127.0.0.1:8899
Exec=$LAUNCH_DIR/start-dashboard.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
  echo "dashboard: $DASH_FILE"
else
  echo "dashboard: NOT FOUND — looked in ~/dashboard and workspace; no autostart entry created"
  echo "dashboard: if it lives elsewhere, tell Jarvis the folder and re-run this script"
fi

# --- Start now, if not already running ---
start_if_down() {
  local name="$1" pattern="$2" launcher="$3"
  if pgrep -f "$pattern" >/dev/null 2>&1; then
    echo "$name: already running"
  elif [ -x "$launcher" ]; then
    nohup "$launcher" >/dev/null 2>&1 &
    echo "$name: started now"
  else
    echo "$name: no launcher, not started"
  fi
}
sleep 1
start_if_down "router" "04-little-router.py" "$LAUNCH_DIR/start-router.sh"
start_if_down "orchestrator" "orchestrator.py" "$LAUNCH_DIR/start-orchestrator.sh"
start_if_down "dashboard" "dashboard/server.py" "$LAUNCH_DIR/start-dashboard.sh"
sleep 3
echo "--- checks ---"
curl -s -m 3 http://127.0.0.1:11435/health && echo "  <- router /health"
curl -s -m 3 -X POST http://127.0.0.1:8080/jarvis -H 'Content-Type: application/json' -d '{"text":"hello"}' && echo "  <- orchestrator"
curl -s -m 3 -o /dev/null -w "dashboard http %{http_code}\n" http://127.0.0.1:8899/
echo "--- autostart files ---"
ls -l "$AUTOSTART_DIR"/jarvis-*.desktop 2>/dev/null || echo "no jarvis autostart files"
echo "Done. After the next reboot + login, these should come back on their own."
