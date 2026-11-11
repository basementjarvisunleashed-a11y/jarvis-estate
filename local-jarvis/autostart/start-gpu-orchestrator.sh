#!/bin/bash
# start-gpu-orchestrator.sh — launcher for the GPU orchestrator.
# NOT YET INSTALLED. For later deployment on the Acer (see DESIGN.md).
# Place at ~/Jarvis/autostart/start-gpu-orchestrator.sh and point the
# Xfce autostart entry gpu-orchestrator.desktop at it.
set -u
exec python3 "$HOME/tonight-scripts/gpu-orchestrator/gpu_orchestrator.py" --serve >> "$HOME/Jarvis/gpu-orchestrator.log" 2>&1
