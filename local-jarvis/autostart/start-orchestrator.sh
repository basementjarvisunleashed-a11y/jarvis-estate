#!/bin/bash
cd "$HOME/Jarvis" || exit 1
exec $HOME/Jarvis/venv/bin/python orchestrator.py >> "$HOME/Jarvis/orchestrator.log" 2>&1
