#!/usr/bin/env bash
# 01-check.sh — READ-ONLY diagnosis for the Acer LLM consolidation.
# Run when HgX is home. Changes nothing. Shows: what is running, what is
# loaded on VRAM, where the 9B GGUF lives, and how much disk the models use.
set -u
echo "=== Ollama ==="
command -v ollama >/dev/null && { ollama list; echo "--- loaded now:"; ollama ps; } || echo "ollama not on PATH"
echo
echo "=== GPU / VRAM ==="
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv 2>/dev/null || echo "nvidia-smi unavailable"
echo
echo "=== Inference processes ==="
ps aux | grep -Ei 'ollama|locally|freellm|comfy|openjutsu|ai-memory' | grep -v grep || echo "none found"
echo
echo "=== Large GGUF model files on disk (the 9B lives somewhere here) ==="
find "$HOME" /opt /usr/local -name '*.gguf' -size +1G 2>/dev/null -exec ls -lh {} \;
echo
echo "=== Model disk use ==="
du -sh "$HOME/.ollama" "$HOME/.cache" 2>/dev/null; df -h "$HOME" | tail -1
echo
echo "=== Listening local LLM services ==="
ss -ltnp 2>/dev/null | grep -E '11434|3001|8188|8189|49374' || echo "none of the usual ports listening"
