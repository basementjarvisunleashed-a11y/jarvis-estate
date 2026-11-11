#!/bin/bash
# Back up every LLM/model on the machine to the HgX drive.
# COPY ONLY — nothing is moved, nothing is deleted.
# Run on the Acer:  bash ~/tonight-scripts/llm-backup.sh
# Target: /mnt/hgx/JarvisBackup/llm-2026-11-06/
# Send the whole output to Jarvis.
set -u
DEST="/mnt/hgx/JarvisBackup/llm-2026-11-06"

if [ ! -d /mnt/hgx ]; then
  echo "STOP: /mnt/hgx is not mounted. Mount the drive first (runbook step 0), then run this again."
  exit 1
fi

echo "--- free space on the drive ---"
df -h /mnt/hgx

echo "--- sizes to copy ---"
du -sh ~/.ollama/models ~/.cache/huggingface 2>/dev/null || true
echo "loose GGUFs (outside the two trees above):"
find "$HOME" -name "*.gguf" 2>/dev/null | grep -v "$HOME/.ollama/" | grep -v "$HOME/.cache/huggingface/" | while read -r f; do du -h "$f"; done

echo "--- space check (need < free, with headroom) ---"
NEED=$( (du -sb ~/.ollama/models ~/.cache/huggingface 2>/dev/null | awk '{s+=$1} END {print s+0}'; find "$HOME" -name "*.gguf" 2>/dev/null | grep -v "$HOME/.ollama/" | grep -v "$HOME/.cache/huggingface/" | xargs -r du -sb 2>/dev/null | awk '{s+=$1} END {print s+0}') | awk '{s+=$1} END {print s+0}' )
FREE=$(df --output=avail -B1 /mnt/hgx 2>/dev/null | tail -1)
echo "need ~$NEED bytes, free $FREE bytes"
if [ -n "$NEED" ] && [ -n "$FREE" ] && [ "$NEED" -gt 0 ] && [ "$FREE" -gt 0 ] && [ "$NEED" -gt "$FREE" ]; then
  echo "STOP: not enough free space on the drive. Nothing was copied."
  exit 1
fi

mkdir -p "$DEST"

copy_tree() {
  src="$1"; name="$2"
  if [ ! -e "$src" ]; then echo "skip (not found): $src"; return 0; fi
  echo "copying $name ..."
  if command -v rsync >/dev/null 2>&1; then
    rsync -a "$src" "$DEST/$name/"
  else
    mkdir -p "$DEST/$name" && cp -a "$src/." "$DEST/$name/"
  fi
}

copy_tree ~/.ollama/models ollama-models
copy_tree ~/.cache/huggingface huggingface-cache

echo "copying loose GGUFs ..."
mkdir -p "$DEST/loose-gguf"
find "$HOME" -name "*.gguf" 2>/dev/null | grep -v "$HOME/.ollama/" | grep -v "$HOME/.cache/huggingface/" | while read -r f; do
  echo "  $f"
  cp -a "$f" "$DEST/loose-gguf/"
done

echo "--- verify ---"
du -sh "$DEST"
echo "files in backup: $(find "$DEST" -type f | wc -l)"
echo "GGUFs in backup: $(find "$DEST" -name "*.gguf" | wc -l)  (source: $(find "$HOME" -name "*.gguf" 2>/dev/null | wc -l))"
echo "Backup done. Nothing was moved or deleted."
