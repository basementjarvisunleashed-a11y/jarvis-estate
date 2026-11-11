# Autostart launchers (2026-11-06)

The launchers that bring Jarvis back on login, exactly as they run on
the Acer. Snapshot from the Acer source parcel of 2026-11-06 23:36 ET
(`jarvis-acer-source-2026-11-06.zip`).

**Files:**

| File | What it starts |
|---|---|
| `start-router.sh` | The model router (`04-little-router.py`, :11435), with 24-hour pins (`KEEP_ALIVE_EASY=24h KEEP_ALIVE_HARD=24h`). |
| `start-orchestrator.sh` | The voice orchestrator (`orchestrator.py`, :8080) under the Jarvis venv Python. |
| `start-dashboard.sh` | The dashboard server (`server.py`, :8899) with `DASHBOARD_HOST=0.0.0.0` so it answers over the tailnet. |
| `keep-brains-alive.sh` | The 6-hour keep-alive ping (9B, then 27B with `num_gpu 0`), each pinned 24h. |

**How they are installed:** `local-jarvis/scripts/jarvis-autostart-setup.sh`
writes these launchers into `~/Jarvis/autostart/` and the matching
`.desktop` entries into `~/.config/autostart/`.

**Post-snapshot change:** `keep-brains-alive.sh` here is the version as
of 23:36. At 23:46 the live file was swapped for
`keep-brains-alive-v2.sh` (in `local-jarvis/gpu-orchestrator/`), which
skips the 9B ping while the 9B is parked so the keep-alive never reloads
it mid-render; the old file was kept as `keep-brains-alive.sh.bak`. The
GPU orchestrator's own launcher (`start-gpu-orchestrator.sh`) was
installed at ~23:45, after this snapshot — it lives in
`local-jarvis/gpu-orchestrator/`.
