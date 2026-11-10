#!/bin/bash
# start-brains.sh — Load both LLM brains at login (9B first, then 27B).
# 9B first, then 27B (load-order rule: reloading 9B after 27B evicts the 27B).
# Both pinned with keep_alive 24h. Logs to ~/Jarvis/start-brains.log.
# Run by Xfce autostart via ~/.config/autostart/brains.desktop.
# Also safe to run by hand any time to (re)load the brains.
LOG="$HOME/Jarvis/start-brains.log"
{
echo "=== $(date '+%Y-%m-%d %H:%M:%S') start-brains: waiting for ollama ==="
# Wait for ollama serve to answer (up to 60s).
for i in $(seq 1 30); do
  if curl -s -m 2 http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    break
  fi
  sleep 2
done
echo "=== $(date '+%Y-%m-%d %H:%M:%S') start-brains: ollama up, loading 9B (GPU) ==="
curl -s -m 180 http://127.0.0.1:11434/api/chat -d '{"model":"qwen9b-abliterated-32k","messages":[{"role":"user","content":"Hello"}],"stream":false,"think":false,"keep_alive":"24h","options":{"num_ctx":32768}}'
echo ""
echo "=== $(date '+%Y-%m-%d %H:%M:%S') start-brains: 9B done, loading 27B (RAM) ==="
curl -s -m 900 http://127.0.0.1:11434/api/chat -d '{"model":"huihui_ai/Qwen3.8-abliterated:27b","messages":[{"role":"user","content":"Hello"}],"stream":false,"think":false,"keep_alive":"24h","options":{"num_ctx":4096,"num_gpu":0}}'
echo ""
echo "=== $(date '+%Y-%m-%d %H:%M:%S') start-brains: done ==="
ollama ps
} >> "$LOG" 2>&1
