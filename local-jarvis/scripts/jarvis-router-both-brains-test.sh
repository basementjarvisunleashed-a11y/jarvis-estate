#!/bin/bash
# Router + both brains test.
# Run once:  bash ~/Downloads/jarvis-router-both-brains-test.sh
# Asks the router an easy question (should answer via the 9B) and a hard
# question (should answer via the 27B, CPU-only), prints each answer with
# the model the router reports, then prints ollama ps and the router log.
# The 27B is CPU-only, so the hard answer takes a minute or two — be patient.
# It deletes nothing and changes nothing.
set -u
echo "--- router /health ---"
curl -s -m 5 http://127.0.0.1:11435/health
echo ""
echo "--- ollama ps before ---"
ollama ps
echo ""
echo "--- EASY (expect 9B) ---"
curl -s -m 300 http://127.0.0.1:11435/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"easy","messages":[{"role":"user","content":"Say hello in one short sentence."}],"think":false}' -o /tmp/router-easy.json
python3 -c "import json; d=json.load(open('/tmp/router-easy.json')); print('model:', d.get('model')); print('answer:', d['choices'][0]['message']['content'])" 2>/dev/null || cat /tmp/router-easy.json
echo ""
echo "--- HARD (expect 27B, CPU-only — takes a minute or two) ---"
curl -s -m 600 http://127.0.0.1:11435/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"hard","messages":[{"role":"user","content":"Explain in two sentences what a buffer overflow is."}],"think":false}' -o /tmp/router-hard.json
python3 -c "import json; d=json.load(open('/tmp/router-hard.json')); print('model:', d.get('model')); print('answer:', d['choices'][0]['message']['content'])" 2>/dev/null || cat /tmp/router-hard.json
echo ""
echo "--- ollama ps after ---"
ollama ps
echo "--- router log (last 5 lines) ---"
ROUTER_LOG=""
for p in "$HOME/tonight-scripts/acer-llm-consolidation/router.log" "$HOME/Jarvis/router.log"; do
  if [ -f "$p" ]; then ROUTER_LOG="$p"; break; fi
done
if [ -n "$ROUTER_LOG" ]; then tail -n 5 "$ROUTER_LOG"; else echo "router.log not found in the usual places"; fi
echo "Done."
