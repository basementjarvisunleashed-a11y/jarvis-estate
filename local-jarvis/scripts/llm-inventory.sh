#!/bin/bash
# LLM inventory — every model on the machine, in order. Read-only.
# Nothing is changed, nothing is deleted.
# Run on the Acer:  bash ~/tonight-scripts/llm-inventory.sh
# Send the whole output to Jarvis.
set -u
echo "=== 1. Ollama models (ollama list) ==="
ollama list 2>/dev/null || echo "ollama not answering"
echo
echo "=== 2. Ollama loaded right now (ollama ps) ==="
ollama ps 2>/dev/null || echo "ollama ps failed"
echo
echo "=== 3. GGUF files on disk (all of them) ==="
find "$HOME" -name "*.gguf" -exec du -h {} \; 2>/dev/null | sort -k2
echo
echo "=== 4. Hugging Face cache (the ears) ==="
ls ~/.cache/huggingface/hub 2>/dev/null || echo "no HF cache dir"
du -sh ~/.cache/huggingface 2>/dev/null || true
echo
echo "=== 5. Ollama store size ==="
du -sh ~/.ollama/models 2>/dev/null || echo "no ~/.ollama/models dir"
echo
echo "=== 6. What each one is for (from the 2026-11-05 audit) ==="
echo "qwen9b-abliterated                 THE brain — Local Jarvis + orchestrator default, resident VRAM"
echo "huihui_ai/Qwen3.8-abliterated:27b  heavy brain — hard reasoning, system RAM, never GPU"
echo "qwen3:8b                          old orchestrator default (re-pointed) — fallback only"
echo "qwen2.5:3b                        old Local Jarvis default (re-pointed) — fallback only"
echo "agents-a1-4b-heretic              in NO live code — does nothing"
echo "Qwen2.5-7B GGUF                   unused — dead weight"
echo "nomic-embed-text                  embedding model"
echo "cohere-transcribe GGUF            Hex speech model — untouched"
echo "HF cache (Whisper/Parakeet/OmniVoice/nllb)  the ears — speech models"
echo "Done. Send me the whole output."
