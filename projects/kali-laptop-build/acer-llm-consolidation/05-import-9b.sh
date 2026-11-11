#!/usr/bin/env bash
# 05-import-9b.sh — Move the Qwen 3.5 9B Abliterated out of Locally
# Uncensored and into Ollama as "qwen9b-abliterated".
# Run when HgX is home, BEFORE 02-cleanup.sh (deleting first would destroy
# the model we are keeping). It finds the GGUF, lets HgX pick it, builds a
# Modelfile, imports it, and proves it answers on the GPU.
set -u
cd "$(dirname "$0")"

echo "=== Hunting for the 9B GGUF (Locally Uncensored's model files) ==="
mapfile -t CANDIDATES < <(find "$HOME" -iname '*9b*.gguf' -o -iname '*qwen3.5*.gguf' 2>/dev/null | grep -iv '7b' | head -20)
if [ "${#CANDIDATES[@]}" -eq 0 ]; then
  echo "No 9B GGUF found by name. Broader hunt (any GGUF over 1GB):"
  find "$HOME" -name '*.gguf' -size +1G 2>/dev/null -exec ls -lh {} \;
  echo "Pick the file and re-run with its path: $0 /path/to/model.gguf"
  exit 1
fi
if [ "${#CANDIDATES[@]}" -eq 1 ]; then
  GGUF="${CANDIDATES[0]}"
else
  echo "Candidates:"
  i=1; for c in "${CANDIDATES[@]}"; do echo "  $i) $c"; i=$((i+1)); done
  read -r -p "Pick a number: " n
  GGUF="${CANDIDATES[$((n-1))]}"
fi
echo "Using: $GGUF"
ls -lh "$GGUF"

echo
echo "=== Building Modelfile (Ollama uses the GGUF's own chat template) ==="
cat > Modelfile.qwen9b <<EOF
FROM $GGUF
PARAMETER num_ctx 8192
PARAMETER temperature 0.7
EOF
cat Modelfile.qwen9b

echo
read -r -p "Import as 'qwen9b-abliterated' in Ollama? [y/N] " ans
case "$ans" in
  y|Y) ;;
  *) echo "Aborted — nothing imported."; exit 0 ;;
esac
ollama create qwen9b-abliterated -f Modelfile.qwen9b || { echo "IMPORT FAILED"; exit 1; }

echo
echo "=== Proving it: one short prompt, thinking OFF (simple prompts) ==="
ollama run qwen9b-abliterated --think=false "Say hello in one sentence."
echo
echo "=== Is it on the GPU? ==="
ollama ps
nvidia-smi --query-gpu=memory.used,memory.total --format=csv 2>/dev/null
echo
echo "If the answer above is clean and the GPU shows the model loaded,"
echo "the 9B is safe inside Ollama — only then run 02-cleanup.sh."
