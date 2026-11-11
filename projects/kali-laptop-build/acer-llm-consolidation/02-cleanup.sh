#!/usr/bin/env bash
# 02-cleanup.sh — DRAFT. DO NOT RUN until HgX is home AND the 9B abliterated
# model is confirmed loaded inside Ollama (see PLAN.md step 2) AND the voice
# audit (PLAN.md step 3, HgX 2026-11-05 ~16:39 ET) has confirmed which of
# the three models below are actually unused. The three models may be
# voice-related (long dictation / voice-over installs) — a model the audit
# did NOT clear is NOT deleted.
# Removes ONLY the named Ollama models, one by one, each with a
# confirmation prompt. It does NOT touch the 9B, does NOT delete Locally
# Uncensored's model files (separate manual step, after verification), and
# does NOT remove the picture brain (separate decision).
set -u

KEEP="qwen9b-abliterated"
echo "KEEP: $KEEP (must already be in 'ollama list' before this runs)"
ollama list | grep -q "$KEEP" || { echo "STOP: $KEEP is NOT in Ollama yet. Import it first. Aborting."; exit 1; }

echo
echo "AUDIT GATE: the three models below may be voice-related (long dictation /"
echo "voice-over installs). Only delete a model the audit proved unused."
read -r -p "Has the voice audit been completed? Type AUDIT-DONE to proceed: " audit
[ "$audit" = "AUDIT-DONE" ] || { echo "STOP: audit not confirmed. Aborting."; exit 1; }

for model in qwen3:8b qwen2.5:3b agents-a1-4b-heretic:Q4_K_M; do
  if ollama list | grep -q "^${model%%:*}"; then
    read -r -p "Delete Ollama model '$model'? [y/N] " ans
    case "$ans" in
      y|Y) ollama rm "$model" && echo "deleted $model" ;;
      *)   echo "skipped $model" ;;
    esac
  else
    echo "not present, skipping: $model"
  fi
done

echo
echo "Stopping Locally Uncensored's engine (not deleting its files yet)..."
pkill -f -i 'locally' || echo "no LU process found"
echo
echo "Done. Next: verify with 'ollama list' and 'ollama ps', then decide on"
echo "LU model-file deletion and the picture brain (see PLAN.md)."
