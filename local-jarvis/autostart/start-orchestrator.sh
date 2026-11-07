#!/bin/bash
cd "/home/hgx/Jarvis" || exit 1
exec /home/hgx/Jarvis/venv/bin/python orchestrator.py >> "/home/hgx/Jarvis/orchestrator.log" 2>&1
