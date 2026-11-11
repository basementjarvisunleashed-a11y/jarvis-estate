#!/bin/bash
# Restart the Jarvis webcam app bound to all interfaces (tailnet).
# Kills any server listening on :8898, then relaunches server.py with
# WEBCAM_HOST=0.0.0.0 under nohup, logging to webcam.log.
#
# Run on the Acer from the webcam-app folder:
#   ./restart-webcam.sh
# Then open http://<acer-tailnet-ip>:8898 from the laptop, iPhone or iPad.
set -e
cd "$(dirname "$0")"

if command -v fuser >/dev/null 2>&1; then
    fuser -k 8898/tcp 2>/dev/null || true
else
    pkill -f "python3 server.py" 2>/dev/null || true
fi
sleep 1

WEBCAM_HOST=0.0.0.0 nohup python3 -u server.py > webcam.log 2>&1 &
echo "Webcam app restarting on 0.0.0.0:8898 (log: webcam.log)"
CODE="000"
for i in 1 2 3 4 5 6 7 8 9 10; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:8898/api/status || echo "000")
    if [ "$CODE" = "200" ]; then
        break
    fi
    sleep 1
done
echo "GET /api/status -> HTTP $CODE"
ACER_IP=$(tailscale ip -4 2>/dev/null | head -1)
if [ -n "$ACER_IP" ]; then
    echo "Open it on the tailnet: http://$ACER_IP:8898"
else
    echo "Open it on the tailnet: http://<acer-tailnet-ip>:8898"
fi
