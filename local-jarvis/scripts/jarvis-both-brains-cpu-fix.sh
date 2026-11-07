#!/bin/bash
# Fix: both brains loaded at once.
# Why only one was loaded: the graphics card has only 6 GB. The 9B alone
# nearly fills it, and the 27B was taking 22% of the GPU as well, so Ollama
# evicted the 9B to make room. System RAM was only 10% used — RAM is NOT
# the problem. The fix: pin the 27B to CPU/system RAM only (num_gpu 0),
# leaving the whole GPU free for the 9B.
# Run once:  bash ~/Downloads/jarvis-both-brains-cpu-fix.sh
# It: backs up the router, patches it so the hard route sends num_gpu 0,
# updates the keep-alive ping the same way, unloads the 27B, restarts the
# router, reloads both brains, and prints ollama ps + free + nvidia-smi.
# It deletes nothing except the old router backup is kept as .bak.
set -u
HOME_DIR="$HOME"
LAUNCH_DIR="$HOME_DIR/Jarvis/autostart"
mkdir -p "$LAUNCH_DIR"

# 1. Patch the router: hard model -> CPU only.
ROUTER_FILE=""
for p in "$HOME_DIR/tonight-scripts/acer-llm-consolidation/04-little-router.py" "$HOME_DIR/workspace/family-bot/acer-llm-consolidation/04-little-router.py" "$HOME_DIR/acer-llm-consolidation/04-little-router.py"; do
  if [ -f "$p" ]; then ROUTER_FILE="$p"; break; fi
done
if [ -z "$ROUTER_FILE" ]; then
  echo "router: NOT FOUND — cannot patch; stopping here"
  exit 1
fi
echo "router: $ROUTER_FILE"
cp -n "$ROUTER_FILE" "$ROUTER_FILE.bak" 2>/dev/null || true
python3 - "$ROUTER_FILE" <<'PYEOF'
import sys
path = sys.argv[1]
src = open(path).read()
if "num_gpu" in src:
    print("router: num_gpu already present, no change")
    sys.exit(0)
old = '''    if "max_tokens" in body:
        options["num_predict"] = body["max_tokens"]
    if options:
'''
new = '''    if "max_tokens" in body:
        options["num_predict"] = body["max_tokens"]
    if model == HEAVY_MODEL:
        options["num_gpu"] = 0
    if options:
'''
assert old in src, "router: expected to_native block not found — aborting, no change"
open(path, "w").write(src.replace(old, new, 1))
print("router: patched — hard model now num_gpu 0 (CPU only)")
PYEOF
python3 -m py_compile "$ROUTER_FILE" && echo "router: compiles OK"

# 2. Update the keep-alive ping: 27B with num_gpu 0.
cat > "$LAUNCH_DIR/keep-brains-alive.sh" <<'KEEPER'
#!/bin/bash
curl -s -m 300 http://127.0.0.1:11434/api/chat -H 'Content-Type: application/json' -d '{"model":"qwen9b-abliterated","messages":[{"role":"user","content":"ping"}],"stream":false,"keep_alive":"24h","think":false}' >/dev/null 2>&1
curl -s -m 600 http://127.0.0.1:11434/api/chat -H 'Content-Type: application/json' -d '{"model":"huihui_ai/Qwen3.8-abliterated:27b","messages":[{"role":"user","content":"ping"}],"stream":false,"keep_alive":"24h","think":false,"options":{"num_gpu":0}}' >/dev/null 2>&1
echo "$(date '+%F %T') keep-alive ping done"
KEEPER
chmod +x "$LAUNCH_DIR/keep-brains-alive.sh"
echo "keep-alive script updated (27B CPU-only)"

# 3. Restart the router with the patched file.
pkill -f "04-little-router.py" 2>/dev/null || true
sleep 2
nohup "$LAUNCH_DIR/start-router.sh" >/dev/null 2>&1 &
sleep 3
curl -s -m 5 http://127.0.0.1:11435/health && echo "  <- router /health after restart"

# 4. Unload the 27B (it was GPU-loaded), then reload both brains.
ollama stop huihui_ai/Qwen3.8-abliterated:27b 2>/dev/null || true
sleep 2
echo "Loading both brains now — 27B CPU-only this time..."
"$LAUNCH_DIR/keep-brains-alive.sh"
sleep 2
echo "--- ollama ps (both should be listed now) ---"
ollama ps
echo "--- memory ---"
free -h
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
echo "Done. If both are listed, the fix worked: 9B on GPU, 27B on CPU/RAM."
