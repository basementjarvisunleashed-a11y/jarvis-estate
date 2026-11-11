# Jarvis Dashboard — the screen instead of the screensaver

**Status 2026-11-07: the original design plan (2026-11-05). The dashboard
is built and v8 is live on the Acer — see `local-jarvis/dashboard/v8/`.
This plan is the design record, not the current state.**

**HgX's order, 2026-11-05 ~17:04–17:06 ET: a dashboard visualization running instead of the screensaver, showing everything. Ready by bedtime tonight (past midnight).**

## What it shows
- GPU (utilization, VRAM used/total, temperature, power) — RTX 2060 6GB
- Temperatures (CPU + GPU), CPU load, uptime
- RAM (used/total, swap), disk (512GB NVMe)
- What each model is thinking/doing — router log (last decisions), Ollama ps (loaded models)
- Models online/offline — which are loaded (awake) vs available but not loaded (asleep)
- REA status + history — the last 3–5 things REA did (from rea-history.jsonl)
- Everything running on Kali — key services (Ollama, router, ComfyUI, REA, LU) + top processes
- Local weather (Markham), Wi-Fi (SSID, signal, IP)
- Picture-brain visuals — latest ComfyUI image, webcam snapshot
- Clock (America/Toronto), date

## Media tile — play the Sopranos inside the dashboard (HgX, 2026-11-05 ~17:26 ET)
- **The dashboard becomes the remote control:** a Media tile lists the shows on the drive (the Sopranos first), each episode with a Play button.
- **Play launches VLC** (cvlc) on the Acer — the path that works for every file — with Stop and a Now-playing line. Browser-playable files (mp4/H.264) can also play embedded in the dashboard via a Range-supporting stream endpoint; anything else falls back to VLC.
- **One playback path, two remotes:** the voice command ("VLC on, play the Sopranos") and the dashboard Play button do the same thing (the voice loop can call the same /api/play endpoint).
- **Security:** the play/stream endpoints only allow paths under the media drive (/mnt/hgx) or ~/Videos — localhost only, nothing else.
- **Honest note:** the drive must be mounted and cleaned first — the dashboard cannot play what it cannot see.
- **Quarter screen + fullscreen (HgX, 2026-11-05 ~17:26 ET):** the video plays in ONE QUARTER of the dashboard — Sopranos, Big Bang Theory, anything else. Say "Hey Jarvis, go full screen" and it goes fullscreen (voice loop calls POST /api/fullscreen; a Fullscreen button on the tile does the same).
- **Two main options + three blanks:** the tile shows The Sopranos and The Big Bang Theory at the top, then three blank slots to add shows later (media-slots.json).
- **Loop:** a show plays continuously in a loop (episodes in order, then repeat from the start).
- **Media voice controls (HgX, 2026-11-05 ~17:32 ET):** "Hey Jarvis, next episode", "Hey Jarvis, volume up", "Hey Jarvis, pause" (plus previous, volume down, resume) — all work inside the dashboard AND in fullscreen. Endpoint: POST /api/media-control. In-page player: control flag polled every second. VLC: next/previous relaunches the next episode; pause/resume via SIGSTOP/SIGCONT; volume via pactl (system volume, documented). On-screen buttons too (Previous, Pause/Resume, Next, Volume up/down). Theater mode for fullscreen is fine (accepted).

## Live conversation feed (HgX, 2026-11-05 ~17:13 ET)
- **When he talks / gives orders, the dashboard GLOWS** — a pulsing cyan glow around the frame while listening.
- **It types out exactly what he is saying** — his words appear in the Conversation panel as they are recognized.
- **When Jarvis speaks, the dashboard shows it** — Jarvis's words written out as he speaks them (gold/amber glow while speaking), so you can read what you hear.
- Feed: the voice loop writes events via `log-voice.sh` (speaker HgX/Jarvis + text) and state (`listening` / `speaking` / `idle`); the dashboard polls `/api/voice` every second.
- Honest note: word-by-word typing as he speaks depends on the loop's streaming transcription; the robust version shows each recognized phrase as it lands, with the glow showing live that he is being heard.

## How it runs
- Files: `~/workspace/family-bot/dashboard/` (index.html + server.py, stdlib-only, no dependencies; port 8899).
- On the Acer: `python3 server.py`, open http://127.0.0.1:8899 in a fullscreen browser — instead of the screensaver. The screensaver blanking stays off while it's up (standing order: never signs out, never asks password — the dashboard replaces the blank screen).
- Every panel degrades to "unavailable" if its source is missing — never breaks the page.

## Picture brain — KEPT (HgX, 2026-11-05 ~17:05–17:06 ET)
- ComfyUI + comfy-api-proxy + OpenJutsu STAY. Reversal of the conditional-delete: needed for the dashboard visuals, for explaining REA teardowns with images, and for the webcam work. He was right initially.
- Whether it stays ACTIVE all the time is decided later. It is not deleted.

## Tonight's order (change of plan, HgX 2026-11-05 ~17:22 ET)
0. **Drive cleanup FIRST** — mount read-write, clean it out, before anything else. Then: 1. The two brains (consolidation). 2. The camera. 3. The voice loop. 4. The dashboard — ready by bedtime.

## Screensaver fix — NEEDED, later (HgX, 2026-11-05 ~18:07 ET)
- **Failure reported:** the screensaver did not work — the monitor turned off and it signed him out.
- **Fix (later, on the Acer):** while the dashboard is up, the screen must stay on — disable Xfce screensaver blanking/lock and power-manager display sleep and any idle auto-logout, so the dashboard runs instead of the screensaver without the monitor turning off or the session signing out. **All via terminal script (xfconf-query) — no GUI settings, per his standing order.** Verify by leaving the dashboard up and watching that it never blanks or locks.
