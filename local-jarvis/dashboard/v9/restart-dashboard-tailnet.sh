#!/bin/bash
# Restart the Jarvis dashboard bound to all interfaces (tailnet).
# Kills any server listening on :8899, then relaunches server.py with
# DASHBOARD_HOST=0.0.0.0 under nohup, logging to dashboard.log.
#
# Run on the Acer from the dashboard folder:
#   ./restart-dashboard-tailnet.sh
# Then open http://<acer-tailnet-ip>:8899 from the iPhone or iPad.
set -e
cd "$(dirname "$0")"

if command -v fuser >/dev/null 2>&1; then
    fuser -k 8899/tcp 2>/dev/null || true
else
    pkill -f "python3 server.py" 2>/dev/null || true
fi
sleep 1

DASHBOARD_HOST=0.0.0.0 nohup python3 -u server.py > dashboard.log 2>&1 &
echo "Dashboard restarting on 0.0.0.0:8899 (log: dashboard.log)"
# The first status collection can take a few seconds (it walks the
# media drive and calls ollama), so wait for the server to answer
# instead of failing the script on the first curl. set -e would exit
# here on a connection-refused curl, before the tailnet address below.
CODE="000"
for i in 1 2 3 4 5 6 7 8 9 10; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:8899/api/status || echo "000")
    if [ "$CODE" = "200" ]; then
        break
    fi
    sleep 1
done
echo "GET /api/status -> HTTP $CODE"
ACER_IP=$(tailscale ip -4 2>/dev/null | head -1)
if [ -n "$ACER_IP" ]; then
    echo "Open it on the tailnet: http://$ACER_IP:8899"
else
    echo "Open it on the tailnet: http://<acer-tailnet-ip>:8899"
fi
