#!/bin/bash
export DASHBOARD_HOST=0.0.0.0
cd "$HOME/tonight-scripts/dashboard" || exit 1
exec python3 server.py >> "$HOME/Jarvis/dashboard.log" 2>&1
