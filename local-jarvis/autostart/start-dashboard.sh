#!/bin/bash
export DASHBOARD_HOST=0.0.0.0
cd "/home/hgx/tonight-scripts/dashboard" || exit 1
exec python3 server.py >> "/home/hgx/Jarvis/dashboard.log" 2>&1
