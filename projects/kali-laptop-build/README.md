# Kali laptop build, 2026-11-10

Snapshot of the Acer Kali build that is actually running on the laptop.

- `local-jarvis/` at the repo root is the voice loop, orchestrator and login launchers.
- `dashboard/` is dashboard v12 (port 8899).
- `webcam-app/` is the webcam app (port 8898).
- `gpu-orchestrator/` parks the 9B model while ComfyUI wants the graphics card.
- `acer-llm-consolidation/` is the little router and the model runbook.

Personal paths and the tailnet address are not in this copy. On the laptop, set:

- `MEDIA_DIR` to the media drive mount
- `IPAD_MP4_DIR` to the iPad-Pro MP4 folder
- home-relative paths under `~/Jarvis`

The live files on the laptop were not moved or edited to make this snapshot.
Logs, voice models, voice profiles, backups and runtime state are not included.
