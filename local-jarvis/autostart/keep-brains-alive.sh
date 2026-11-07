#!/bin/bash
curl -s -m 300 http://127.0.0.1:11434/api/chat -H 'Content-Type: application/json' -d '{"model":"qwen9b-abliterated","messages":[{"role":"user","content":"ping"}],"stream":false,"keep_alive":"24h","think":false}' >/dev/null 2>&1
curl -s -m 600 http://127.0.0.1:11434/api/chat -H 'Content-Type: application/json' -d '{"model":"huihui_ai/Qwen3.8-abliterated:27b","messages":[{"role":"user","content":"ping"}],"stream":false,"keep_alive":"24h","think":false,"options":{"num_gpu":0}}' >/dev/null 2>&1
echo "$(date '+%F %T') keep-alive ping done"
