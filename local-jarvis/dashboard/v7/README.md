# Jarvis dashboard — v7 (2026-11-06)

Always-on dashboard for the Acer (Kali) — GPU, temperatures, RAM, what's
running, what each model is doing, local weather, Wi-Fi, REA status, models
online/offline, last things REA did, plus a media tile (one quarter of the
screen; voice or button takes it fullscreen) and a live two-way conversation
feed. Serves on port **8899**; iPhone/iPad reach it over the tailnet.

**Status:** v7 is applied and live on the Acer (current dashboard).
18 issues fixed over v6 — cached media scan, background status refresh,
tailnet listening, sports/Tailscale/health/model tiles, live webcam,
one-screen layout groundwork. v8 (redesign) is being built separately.

**Published copy — scrubbed:** one folder name was replaced with the
placeholder `ownerlaptop` / `OwnerLaptop` (in `SKIP_DIRS` in `server.py`
and in `README-FIRST.txt`); rename it to match your own old laptop backup
folder. No other change was made. Original zip MD5
`3565de1ca53f82f0e8cdd274410d5983`; scrubbed zip MD5
`94a1ab2a1f07a26350db1e3e02394be6`.

**Files:** `server.py` (stdlib + Flask-free, port 8899),
`index.html` (single page), `media-slots.json` (pinned shows + 3 blank
slots), `restart-dashboard-tailnet.sh` (serves on `0.0.0.0`), `README-FIRST.txt`
(full fix list). No password on the media endpoints by design — tailnet only.
