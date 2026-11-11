# Jarvis Dashboard — Acer (Kali Linux)

A single-page Jarvis HUD that runs **instead of the screensaver**: GPU, temps,
RAM, models, REA status + history, what's running, weather, Wi-Fi, and the
picture brain — all on one dark screen, refreshing every 3 seconds.

It also carries a **live Conversation panel**: when HgX is talking the
dashboard glows cyan and types out exactly what he is saying; when Jarvis
speaks it glows gold and writes out Jarvis's words as he speaks them. The
voice loop feeds it — see "Live conversation" below.

And a **Media tile**: the Sopranos (and The Big Bang Theory) play right
inside the dashboard — a quarter-screen video area, fullscreen on a button
or a voice command, looping continuously. See "Media" below.

## Run it (on the Acer)

```bash
cd ~/workspace/family-bot/dashboard
python3 server.py
```

Then open **http://127.0.0.1:8899** in a browser and press **F11** for fullscreen.
It only listens on localhost — nothing is exposed to the network.

To run it instead of the screensaver:
1. Disable the screensaver / screen blanking (Xfce: Settings → Power Manager →
   Display → turn off blanking; Settings → Screensaver → disable).
2. Open the browser fullscreen on http://127.0.0.1:8899 and leave it up.
3. Optional — start it on login: add `python3 ~/workspace/family-bot/dashboard/server.py`
   to Xfce's Session and Startup → Application Autostart (only after it works by hand).

Stop it with Ctrl-C in the terminal running `server.py`.

## Files

| File | What it is |
|---|---|
| `index.html` | The dashboard page. Inline CSS/JS only — no external CDNs, works fully offline. Fetches `/api/status` every 3 s, `/api/voice` + `/api/now-playing` every 1 s, `/api/media` every 30 s. |
| `server.py` | Stdlib-only Python 3 server. Serves the page + `GET /api/status`, `GET /api/voice`, `GET /api/media`, `GET /api/now-playing`, `GET /api/stream`, `POST /api/play`, `POST /api/stop`, `POST /api/fullscreen`, `POST /api/media-control` (JSON) on 127.0.0.1:8899. |
| `media-slots.json` | Pinned shows + blank slots for the Media tile. Edit to add shows later. |
| `fullscreen.json` | Created by `POST /api/fullscreen`. `{"fullscreen": true|false}` — the flag the dashboard polls. |
| `media-control.json` | Created by `POST /api/media-control` for the in-page player. One pending action (`{"action", "seq", "ts", ...}`) — the dashboard polls it every 1 s, applies it, then clears it. A flag nobody picks up goes stale after 15 s. |
| `log-rea.sh` | Appends one REA run (time, target, summary) to `rea-history.jsonl` for the history panel. |
| `log-voice.sh` | Feeds the live Conversation panel: appends one spoken line to `voice-events.jsonl`, or sets the current state in `voice-state.json`. |
| `rea-history.jsonl` | Created by `log-rea.sh`. One JSON object per line, newest at the end; the dashboard shows the last 5. |
| `voice-events.jsonl` | Created by `log-voice.sh`. One `{"time","speaker","text"}` per line, newest at the end; the dashboard shows the last 10. |
| `voice-state.json` | Created by `log-voice.sh state ...`. `{"state": "listening"|"speaking"|"idle", "time": ...}` — the current glow. |

## What each panel reads

| Panel | Source on the Acer |
|---|---|
| Conversation | `/api/voice` — `voice-state.json` + last 10 lines of `voice-events.jsonl`; polled every 1 s. Glows cyan while listening, gold while speaking. |
| Media | `/api/media` — video files on the media drive, grouped by top-level folder (folder name = show), capped at 200 files. The video plays in the tile (one quarter of the dashboard, 16:9). See "Media" below. |
| GPU (RTX 2060) | `nvidia-smi` — utilization %, VRAM used/total GB, temperature, power |
| CPU + temps | `os.getloadavg()`, `/proc/uptime`, `/sys/class/thermal/thermal_zone*/temp` |
| RAM + disk | `/proc/meminfo`, `shutil.disk_usage` on `/` and `/home` |
| Models | `ollama list` (exists) + `ollama ps` (loaded/resident, GPU vs CPU) |
| Router | Tail of `router.log` (last 5 decisions — which brain answered). Searched in: `$ROUTER_LOG`, `./router.log`, `~/workspace/family-bot/acer-llm-consolidation/router.log` |
| REA status + history | `rea-history.jsonl` (last 5 runs); "no REA runs yet" if the file is missing |
| What's running | `pgrep -f` for ollama, the little router, ComfyUI, REA, Locally Uncensored; `ps` for the top 5 CPU processes |
| Weather (Markham) | `https://wttr.in/Markham?format=j1` (no key; cached 10 min; "unavailable" offline) |
| Wi-Fi | `nmcli` (SSID, signal) + local IP from the routing table |
| Picture brain | Latest image in `$PICTURE_DIR` (default `~/ComfyUI/output`); "picture brain idle" when ComfyUI is down |
| Webcam | `webcam.jpg` in this folder, if present (save a C270 frame here to show it) |
| Clock | America/Toronto, from the server |

Every panel degrades gracefully: if its source is missing, the tile shows
"unavailable" and the rest of the page keeps working.

## Config (env vars, all optional)

```bash
DASHBOARD_PORT=8899  python3 server.py   # port (default 8899)
PICTURE_DIR=~/ComfyUI/output python3 server.py   # where to look for pictures
ROUTER_LOG=/path/to/router.log python3 server.py  # explicit router log path
REA_HISTORY=/path/to/rea-history.jsonl python3 server.py
VOICE_EVENTS=/path/to/voice-events.jsonl python3 server.py
VOICE_STATE=/path/to/voice-state.json python3 server.py
MEDIA_DIR=/mnt/media python3 server.py   # media drive to scan (default /mnt/media)
```

## Logging REA runs

```bash
./log-rea.sh ~/firmware.bin "REA: 34 functions named, 2 suspicious strings"
```

The dashboard picks it up on the next refresh. The last 5 runs are shown,
newest first.

## Live conversation — the dashboard glows and types

The Conversation tile is the first tile on the page. It shows the live
transcript — HgX's words in cyan, Jarvis's words in gold, labeled, latest
at the bottom, auto-scrolling — and the whole dashboard frame glows while
anyone is talking: **pulsing cyan while HgX is speaking** (state
`listening`), **gold while Jarvis is speaking** (state `speaking`), calm
otherwise.

The voice loop feeds it with `log-voice.sh`, in this order:

```bash
./log-voice.sh state listening                    # the loop hears speech — dashboard glows cyan
./log-voice.sh HgX "VLC on, play the Sopranos"   # a phrase is recognised — typed out exactly
./log-voice.sh state speaking                     # Jarvis starts to speak — dashboard glows gold
./log-voice.sh Jarvis "Playing The Sopranos, sir."  # Jarvis's words, written out as he speaks
./log-voice.sh state idle                         # exchange over — glow settles
```

Notes for the loop:
- Call `log-voice.sh HgX "<words>"` once per recognised phrase, with the
  exact words transcribed — that is what gets typed out.
- Call `log-voice.sh Jarvis "<reply>"` with the exact reply text as Jarvis
  speaks it (per sentence is fine for long replies).
- Always close with `state idle`, or the glow stays on.
- If the voice loop and the dashboard run from different folders, set
  `VOICE_EVENTS` / `VOICE_STATE` so both point at the same files.
- Missing files are fine: the panel shows "quiet" and state `idle` until
  the first call.

## Media — play the Sopranos in the dashboard

The Media tile is the first tile after Conversation. It shows the video in
one quarter of the dashboard (the tile spans two grid columns, 16:9 video),
with a Now-playing line, Stop, Fullscreen, and Refresh buttons.

**Pinned shows.** The tile shows two main options at the top — **The
Sopranos** and **The Big Bang Theory** — then three blank slots. The slots
live in `media-slots.json` in this folder:

```json
{"pinned": ["The Sopranos", "The Big Bang Theory"], "slots": [null, null, null]}
```

To add a show later, put its folder name in a slot (e.g. `"slots":
["Breaking Bad", null, null]`) and hit Refresh — a blank slot renders as
"+ add show". Any other show folder found on the drive is listed under
"All shows on the drive" below the pinned ones.

**Two ways to watch.** Each episode has **Play (VLC)** — launches VLC on
the Acer (the path that works for everything, including mkv) — and **Watch
here** — plays it in the dashboard's own `<video>` element via
`/api/stream` (best effort: mp4/H.264 plays in-page; mkv and others fall
back to VLC). **Play show (VLC)** / **Watch show** play the whole show.

**Loop.** Playing a show plays it continuously in a loop — episodes in
order, then repeat from the start. VLC gets `--loop`; the in-page player
advances to the next episode on `ended` and wraps to the first.

**Fullscreen.** The Fullscreen button on the tile calls
`requestFullscreen()` on the video element. The voice command
**"Hey Jarvis, go full screen"** works the same way: the voice loop calls

```bash
curl -s -X POST http://127.0.0.1:8899/api/fullscreen \
  -H 'Content-Type: application/json' -d '{"on": true}'
```

and the dashboard (polling every 1 s) fullscreens the video. If VLC is the
active player, the server relaunches VLC with `--fullscreen` on the same
playlist instead. One honest browser limit: `requestFullscreen()` needs a
user gesture, so a voice-triggered fullscreen on the in-page player falls
back to a CSS "theater" mode (the player covers the whole screen) when the
browser blocks the real fullscreen. Leaving fullscreen with Esc settles the
flag so it can be turned on again.

**Endpoints.**

| Endpoint | What it does |
|---|---|
| `GET /api/media` | `{mounted, root, shows: [{name, episodes: [{name, path}]} ], pinned, slots}`. `mounted: false` + empty shows when the drive is unmounted/missing. |
| `POST /api/play` | `{"show": "The Sopranos"}` or `{"path": "..."}`, optional `"mode": "vlc"` (default) or `"page"`, `"loop": true` (default), `"fullscreen": bool`. Launches VLC detached (prefers `cvlc`, falls back to `vlc`); stops whatever is already playing first. Returns `{"playing", "mode", "show", "loop", "fullscreen"}`. |
| `POST /api/stop` | Terminates VLC if running, clears the now-playing state and the fullscreen flag. Returns `{"playing": null}`. |
| `GET /api/now-playing` | `{"playing", "mode", "show", "loop", "fullscreen"}`. |
| `POST /api/fullscreen` | `{"on": true\|false}` — writes the flag to `fullscreen.json` (the dashboard polls it every 1 s); relaunches VLC with `--fullscreen` if VLC is the active player. |
| `GET /api/fullscreen` | `{"fullscreen": bool}`. |
| `GET /api/stream?path=...` | Serves a video file with HTTP Range support (206 Partial Content) for the embedded player. |

**Path whitelist (security).** `/api/play` and `/api/stream` only accept
paths under the media dir (`$MEDIA_DIR`, default `/mnt/media`) or `~/Videos`.
Anything else — including `../` escapes and symlinks out of the media tree
— is rejected with 403. The dashboard only listens on localhost, so these
endpoints are only reachable from the Acer itself.

**Voice loop reuse.** The voice command "VLC on, play the Sopranos" calls
the same playback path as the dashboard — one remote in the voice, one on
the screen:

```bash
curl -s -X POST http://127.0.0.1:8899/api/play \
  -H 'Content-Type: application/json' -d '{"show": "The Sopranos", "loop": true}'
```

**Media voice controls.** "Hey Jarvis, next episode", "volume up",
"pause" (plus previous, volume down, resume) all work inside the
dashboard **and** in fullscreen/theater mode — the controls run on 1 s
polls, which keep running whatever the screen is doing. The voice loop
calls one endpoint, and the on-screen buttons (Previous, Pause/Resume,
Next, Vol −, Vol +) call the same one, so voice and touch can never
disagree. In theater mode the buttons float over the bottom of the screen;
in true fullscreen the video's own native controls appear.

```bash
curl -s -X POST http://127.0.0.1:8899/api/media-control \
  -H 'Content-Type: application/json' -d '{"action": "next"}'
curl -s -X POST http://127.0.0.1:8899/api/media-control \
  -H 'Content-Type: application/json' -d '{"action": "previous"}'
curl -s -X POST http://127.0.0.1:8899/api/media-control \
  -H 'Content-Type: application/json' -d '{"action": "pause"}'
curl -s -X POST http://127.0.0.1:8899/api/media-control \
  -H 'Content-Type: application/json' -d '{"action": "resume"}'
curl -s -X POST http://127.0.0.1:8899/api/media-control \
  -H 'Content-Type: application/json' -d '{"action": "volume-up"}'
curl -s -X POST http://127.0.0.1:8899/api/media-control \
  -H 'Content-Type: application/json' -d '{"action": "volume-down"}'
```

`POST /api/media-control` returns the resulting state — and an unknown
action returns 400. `GET /api/media-control` returns
`{"pending": <action or null>, "state": {...}}` (the pending flag the
dashboard is about to apply).

**Jarvis confirms every voice command by voice.** Nothing happens
silently: the response carries the detail the loop needs to speak the
confirmation, and the confirmation also lands on the Conversation panel.

| Voice command | Action | Response fields the loop speaks from | Jarvis says |
|---|---|---|---|
| "Play the Sopranos" | `POST /api/play` `{"show": "The Sopranos"}` | `"playing": "The Sopranos"`, `"episode": "S01E01…"` | "Playing the Sopranos" |
| "Play S01E02" / an episode | `POST /api/play` `{"path": "…"}` | `"playing"` / `"episode"` = the episode name | "Playing \<episode name\>" |
| "Next episode" | `{"action": "next"}` | `"action": "next"`, `"playing": "<episode name>"` | "Playing next episode" |
| "Previous episode" | `{"action": "previous"}` | `"action": "previous"`, `"playing": "<episode name>"` | "Playing previous episode" |
| "Pause" | `{"action": "pause"}` | `"paused": true` | "Paused" |
| "Resume" / "Play" | `{"action": "resume"}` | `"paused": false` | "Resuming" |
| "Volume up" | `{"action": "volume-up"}` | `"volume": 0–1`, `"volume_pct": %` | "Volume up" (or "Volume \<pct\> percent") |
| "Volume down" | `{"action": "volume-down"}` | `"volume": 0–1`, `"volume_pct": %` | "Volume down" |
| (nothing playing) | any of the above | `"playing": null`, `"error": "nothing playing"` | "Nothing is playing right now" |
| (end of a non-looping list) | `{"action": "next"}` | `"playing": null`, `"error": "end of playlist"` | "That was the last episode" |

**How each action works, by player.**

- **VLC player.** `next` / `previous` stop VLC and relaunch it with the
  playlist rotated to the new episode, same loop/fullscreen flags, so the
  show keeps looping from there. `pause` / `resume` send **SIGSTOP /
  SIGCONT** to the VLC process — the picture and sound freeze exactly
  where they are and pick up from the same frame. `volume-up` / `volume-down`
  run `pactl set-sink-volume @DEFAULT_SINK@ +5%` / `-5%` — this is the
  **system** sink volume, not VLC-only: it turns down everything on that
  sink (including Jarvis's voice) until it is turned back up.
- **In-page player.** The server writes the action to
  `media-control.json`; the dashboard polls it every 1 s and applies it
  to the `<video>` element: `next`/`previous` jump to the server's episode
  index (wrapping at the ends, so the loop never stops), `pause` calls
  `video.pause()`, `resume` calls `video.play()`, `volume-up`/`volume-down`
  set `video.volume` ±0.1, clamped 0–1. The dashboard clears the flag
  after applying it (and ignores flags older than 15 s, so a stale
  command never fires late). The server's `paused` / `volume` in the
  response are best-known values — if the dashboard isn't open, the flag
  just goes stale and nothing happens.

**Requirements.** VLC must be installed (it is: 3.0.24 on the Acer). The
media drive must be mounted (`/mnt/media`) or the tile says "Media drive
unmounted — mount it first".

## Troubleshooting

- **GPU tile says unavailable** — `nvidia-smi` isn't on PATH or the NVIDIA driver
  isn't loaded. The tile stays quiet; everything else works.
- **Models tile says "Ollama not responding"** — Ollama isn't running. Start it,
  then refresh.
- **Weather unavailable** — no internet, or wttr.in is down. The tile recovers
  on its own when the network is back (cached, retried every 10 min).
- **Picture brain idle** — ComfyUI isn't running, or `~/ComfyUI/output` has no
  images yet. Start ComfyUI and generate something, or point `PICTURE_DIR`
  somewhere with images.
- **Port in use** — another copy is already running, or something else holds
  8899. Run `DASHBOARD_PORT=8898 python3 server.py` and open that port instead.
- **Conversation stays idle / "quiet"** — the voice loop hasn't called
  `log-voice.sh` yet, or it wrote to different files. Check that
  `voice-events.jsonl` and `voice-state.json` exist next to `server.py`
  (or that `VOICE_EVENTS` / `VOICE_STATE` match on both sides), and that
  `GET /api/voice` returns the state and events.
- **Glow stays on** — the loop never sent `state idle`. Send
  `./log-voice.sh state idle` to settle it.
- **Media tile says "Media drive unmounted"** — `/mnt/media` isn't mounted.
  Mount the external drive (read-write for the clean-out, read-only is
  enough for playback) and hit Refresh shows.
- **Play (VLC) does nothing / "VLC not installed"** — no `cvlc` or `vlc`
  on PATH. VLC 3.0.24 is installed on the Acer; check `which cvlc vlc`.
- **In-page video won't play (mkv)** — the browser can't decode it. Use
  Play (VLC) for mkv and other non-browser formats; mp4/H.264 plays
  in-page.
- **Fullscreen doesn't trigger from voice** — the browser blocked
  `requestFullscreen()` without a click, so the player fell back to the
  CSS theater mode (full-screen overlay). Click the tile's Fullscreen
  button for real fullscreen, or watch via VLC, where the server passes
  `--fullscreen` directly.
- **Media control does nothing / "nothing playing"** — no show or episode
  is playing yet. Start one first (Play show / Watch here, or the voice
  command "play the Sopranos"). Volume still works with nothing playing.
- **Volume up does nothing in VLC ("pactl unavailable")** — `pactl`
  isn't on PATH (PipeWire/PulseAudio tools missing). Install
  `pulseaudio-utils`, or use the in-page player, whose volume is the
  video element's own.
- **Pause doesn't resume in VLC** — VLC was SIGSTOPped; resume sends
  SIGCONT to the same process. If VLC was closed by hand instead, start
  the show again — the server treats a dead VLC as "nothing playing".

## Audio tile — microphones (HgX, 2026-11-05 ~19:34 ET)
- The Audio tile lists every mic by priority — **laptop built-in (ALC295) primary,
  MaonoCaster AU-AM200 secondary, C270 tertiary** — with a live state: **ACTIVE**
  (capturing right now), **idle** (present, not capturing), or **not connected**
  (unplugged — still shown). It also shows the default speaker (+ volume) and
  both cameras (laptop built-in primary, C270 secondary, present or not).
- States come live from PipeWire (`pactl list sources` + `pactl list
  source-outputs`): a mic is ACTIVE when its PipeWire state is RUNNING or
  something is capturing from it. If pactl is missing, the tile says so.
