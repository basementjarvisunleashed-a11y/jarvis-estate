#!/bin/bash
cd "/home/hgx/tonight-scripts/acer-llm-consolidation" || exit 1
KEEP_ALIVE_EASY=24h KEEP_ALIVE_HARD=24h exec python3 04-little-router.py >> "/home/hgx/Jarvis/router.log" 2>&1
