JARVIS DASHBOARD — FIXED BUILD v11 (2026-11-07, night)
========================================================

v11 is a dual-webcam change on top of v10. Everything from
v2 + v3 + v4 + v5 + v6 + v7 + v8 + v9 + v10 is in here — all 18 v7
fixes, all 7 v8 directives, the v9 polish, and the v10 two-root
media scan, none regressed, plus the 5 playback-fault fixes. One
thing is new: BOTH webcams are in the dashboard at once (HgX's
word, 00:57 ET: "add both webcams in the dashboard").

What is new in v11
-----------------
1. BOTH WEBCAMS AT ONCE — DUAL VIEW, IN THE MEDIA TILE.
   The media tile now shows the Logitech C270 and the laptop
   built-in camera at the same time, beside the video player —
   no Switch camera button any more (that was the single-feed
   v9/v10 control, and it is gone). The C270 is the MAIN feed
   (large, on top); the laptop built-in is secondary, shown as a
   small picture-in-picture over the C270's bottom-right corner
   (120 px wide) — because the laptop lid might be closed. The
   pair costs barely more height than the single feed did in v9,
   so the media controls and the pinned shows stay visible
   without scrolling the tile, and the whole dashboard still fits
   on one 1920x1080 screen with NO scroll.
2. PER-CAMERA STATE. /api/status now reports each camera
   separately under webcam.cams (c270 + laptop: streaming,
   device, label, state) alongside the overall state label
   ("live — C270 + laptop" / "live — C270" / "live — laptop" /
   "standby — live when viewed"). The head pill in the media tile
   reads LIVE when both are up, "1 LIVE" (amber) when only one
   is, and "standby" when neither is streaming. The laptop row
   carries its own state ("laptop · live" / "laptop · standby —
   live when viewed" / "laptop · unavailable").
3. EACH FEED ASKS FOR ITS OWN CAMERA. The two <img> streams
   request their camera with ?nofallback=1, so a failed camera
   reads "unavailable" instead of silently showing the other
   camera in both feeds. The server's two WebcamGrabbers run
   independently — both MJPEG streams at once, no interference.
   (Without nofallback the server still falls back to the other
   camera, as before; the page just never asks it to.)
4. C270 ABSENT → LAPTOP PROMOTED TO MAIN. If the C270 is not
   there, the laptop feed takes the main slot (full width, 4:3,
   no PiP) and the C270 slot is hidden — the dashboard degrades
   to laptop-only instead of crashing or showing a dead frame.
   When the C270 comes back, it takes the main slot again and
   the laptop returns to its PiP. The same promotion happens
   live if the C270 dies mid-stream.
5. A DARK LAPTOP FEED IS LIVE, NOT AN ERROR. If the laptop lid
   is closed, its feed is dark — and it is shown as dark, with
   the state still "live". It is never reported as unavailable
   just for being dark. (Only a camera that cannot be opened at
   all reads "unavailable".)
6. HIDE/SHOW HIDES BOTH. The Hide button collapses the whole
   webcam area (both feeds); a "Show webcams" button appears in
   the media controls; Show restores both feeds. Dropping the
   <img> srcs on Hide closes both streams, so the camera LEDs go
   out.
7. THE WATCHDOG (why a dead feed is noticed at all). An <img>
   does NOT fire an error when a live MJPEG stream simply stops
   — the browser keeps the last frame and stays quiet. So a feed
   that dies mid-stream is caught by a watchdog driven by the
   status poll (every 3 s): a feed that loaded at least once but
   the server now reports as not streaming is failed (message
   shown, laptop promoted, retry in 5 s). A grace period (8 s
   since the feed was last started or loaded a frame) covers the
   status snapshot's staleness (up to ~3 s) plus the poll
   interval (3 s) — without it the watchdog kills a healthy
   feed that has just reconnected and the feed oscillates
   fail/recover every few seconds. The error event (a 503 on
   (re)connect) still fails a feed at once; the grace only gates
   the poll-driven path. Each failed feed retries every 5 s
   until its camera is back.
8. NOTHING ELSE CHANGED. All v10 functionality and visuals are
   carried forward unchanged: two media roots (MP4 folder
   primary, drive secondary), cached scan + ?refresh=1, ffprobe
   probe + needs_vlc, Recent, pinned shows, compact sports,
   honest dots, router from /health, the real router log path,
   media_allowed for both roots. server.py changed (+130 lines:
   per-camera status, the nofallback flag, the snapshot
   preference for the C270 still); index.html changed (the dual
   webcam area, per-feed handlers, the watchdog).

What is new in v10
1. TWO MEDIA ROOTS — THE MP4 FOLDER FIRST, THE DRIVE SECOND.
   The dashboard now scans TWO media roots, in order:
   - PRIMARY: ~/Videos/iPAD PRO MP4/
     (the "iPAD PRO MP4" folder on the laptop's local disk —
     2,785 MP4 files, 239 GB, 24 shows, all H.264 video + AAC
     audio). H.264/AAC plays in the browser AND in VLC, which is
     why these work while the drive's .avi (Sopranos), MPEG-4
     (Dhoom) and AC3 (BBT) files do not.
   - SECONDARY: /mnt/media (the 4 TB drive) — only for shows the
     MP4 folder does not have, so the Sopranos, Dhoom and other
     drive-only content are not lost.
   A show that exists in BOTH places is served from the MP4
   folder only — one entry per show, never duplicated. The
   pinned shows keep working: The Big Bang Theory now comes
   from the MP4 folder (it plays in the tile, with sound), and
   The Sopranos still comes from the drive (it is .avi, so it
   still steers to VLC with the plain-language hint).
   The roots are configurable: IPAD_MP4_DIR (default the path
   above) and MEDIA_DIR (default /mnt/media). /api/media now
   returns "roots" (both paths, primary first) and "sources"
   (per root: path, available, shows contributed) alongside the
   merged shows. The scan is still cached and fast (background
   worker every 120 s, ?refresh=1 for a background refresh,
   never a re-walk per poll) — the MP4 folder is on fast local
   ext4, the drive on slower NTFS, and the shared file cap
   (100,000) still applies across both roots.
2. FALLBACK. The MP4 folder is not assumed to be there. If it
   is missing or unreadable, the drive alone carries the list
   (the tile marks the primary source unavailable) — never an
   empty shows list, never a crash. If neither root is
   walkable, mounted is False and the last good list is kept
   (stale), as before.
3. NOTHING ELSE CHANGED (in v10). index.html is byte-identical to v9
   (same one-screen grid, webcam beside the VLC player,
   pinned-only media + Recent, compact sports, honest dots,
   router from /health, ffprobe probe + needs_vlc). Only
   server.py changed (+104 lines: the two-root scan and the
   per-root fallbacks). (v11 changes index.html too — the dual
   webcam area — and server.py again; see "What is new in v11"
   above.)

What is new in v9
-----------------
1. NICER — A PREMIUM LOOK. The flat navy is gone: the background
   is now near-black with a subtle blue tint and a soft arc-reactor
   glow at the top. Tiles are glassy (a gentle top-to-bottom
   gradient) with soft rounded corners (12px), a faint cyan
   hairline border, and a gentle shadow. Tile titles glow softly
   in cyan. The big numbers (GPU %, temps, scores, the clock) are
   larger, lighter, and brighter, with a soft glow, so they read
   clearly from a few feet away. Buttons are gradient-filled with
   a hover glow; the primary button glows faintly. Status dots
   glow a touch stronger (same colours: green online, amber
   parked, blue installed, red a real fault). Bars are gradient
   filled with a soft glow. Nothing moved, nothing was added, no
   endpoint or behaviour changed — it is the same dashboard,
   dressed better.
2. WEBCAM BESIDE THE MEDIA PLAYER. The webcam is no longer a
   separate floating panel (bottom-right) and no longer its own
   grid tile. The live feed sits in the MEDIA · TV & MOVIES tile,
   directly beside the video player — video on the left, webcam
   on the right. It keeps everything it had: the live MJPEG feed,
   Switch camera, Hide, and the "live — laptop" / "standby — live
   when viewed" state label (now under the feed, in the media
   tile). Hide collapses the webcam column and shows a "Show
   webcam" button in the media controls; the video takes the full
   width while it is hidden. On a narrow screen (phone) the
   webcam wraps below the video instead of overflowing. The grid
   cell the webcam tile used to occupy (row 4, column 5) now
   belongs to Picture Brain, which spans two columns there — no
   hole in the grid, and no other tile changed.

What is new in v8
-----------------
1. ROUTER, FIXED FOR REAL. /api/status said "Router offline" with
   log_path None and an empty tail, while the router process WAS
   running and its /health endpoint answered OK. Root cause: router
   availability depended on router_log_paths(), which carried a
   hardcoded dev-workspace path (~/workspace/family-bot/...) that
   does not exist on the Acer. Fixed: availability now comes from
   the /health HTTP endpoint (http://127.0.0.1:11435/health, cached
   5 s), never from a log file. The log tail is a nicety only, and
   it now reads the REAL log path: the router writes router.log next
   to its own file, ~/tonight-scripts/acer-llm-consolidation/
   router.log (router source line 56). With no log file anywhere,
   the tile says "router online — no log file" instead of crying
   offline.
2. HONEST HEALTH DOTS. A dot is red only for a real fault now.
   - REA is a skill/tool, not a service: it shows "installed" (blue)
     when its skill directory exists, "running" (green) only while a
     rea process is actually running — never a red "offline" for not
     having a process. The REA tile says "installed — a skill, not a
     service" and the What's Running tile says "installed" too.
   - Locally Uncensored is a desktop app, not a service: "installed"
     (blue) when its directory exists, "running" (green) while open.
   - ComfyUI stopped by design (the 9B has the GPU) shows "parked"
     (amber), not a red "offline". The Picture Brain tile says
     "ComfyUI parked" too.
   - Ollama, Router, Media drive, Wi-Fi, Tailscale, Weather are
     unchanged: online (green) or offline/unmounted (red), with the
     state in words next to every dot.
3. THE MEDIA TILE SHOWS ONLY PINNED + SLOTS + RECENT. The full
   43-show library no longer fills the tile: it lives behind a
   collapsed "All shows (N)" toggle, collapsed by default. The tile
   shows the 2 pinned shows, the 3 slots, and Recent.
4. RECENT. The server records every play (show + episode + path +
   mode) in recent.json next to server.py, newest first, kept to
   5, de-duplicated by path, written atomically — so Recent survives
   a restart. The tile shows the most recent few with Watch here /
   Play in VLC buttons. Skipping to the next episode records the new
   episode too.
5. ONE SCREEN, NO SCROLLING, on a 1920x1080 laptop. At desktop
   width (1200px and up) the page is exactly one viewport tall: the
   grid is 6 columns x 4 rows, the media tile spans two rows so its
   video stays watchable, and any tile whose content runs long
   scrolls INSIDE itself instead of pushing the page down. To make
   that fit, the small tiles merged (GPU + CPU + RAM into one System
   tile; Models + Router into one tile; Wi-Fi + Tailscale into one
   Network tile) — every panel is still there, nothing was removed.
   On smaller screens (phone/tablet) the page scrolls as before.
6. SPORTS TILES, SMALLER. One line per league: HgX's team, the
   opponent, the score, the status. The full NFL game list is gone
   (the server now returns only his team game, for every league).
7. NICER. Tighter spacing, smaller headings, consistent tile
   padding, amber/blue health dots, sub-headings inside the merged
   tiles, and the media list scrolls inside its tile instead of
   stretching the page.

THE SHOWS-NOT-PLAYING FAULT — root causes and fixes
----------------------------------------------------
HgX reported NONE of the shows played on live v7 — clicking a show
or episode did nothing, including .mp4s that played before, while
the dashboard's own state said a Dhoom 2004 .mp4 was "playing"
(mode "here") and nothing played. Four defects, each fixed:

a. THE SCAN WAS SLOW AND ITS FAILURE WIPED THE SHOWS. The scan
   re-walked the whole drive on every /api/media poll (every 30 s)
   and concurrent polls could each start a walk. On a slow NTFS
   drive the walk outlasted the browser's patience, the client
   disconnected (the log's only errors: ConnectionResetError and
   BrokenPipeError — there was NO scan exception), and the error
   path answered mounted:false with an empty show list — so the
   tile showed "unmounted" with no shows, and a click found no show
   to play, while the drive was fine. Fixed: the scan is cached and
   refreshed by a background thread (every 120 s, or on
   ?refresh=1); /api/media serves the last good scan instantly; a
   failed scan NEVER wipes the shows — it keeps the last good list
   and marks it stale. The walk is also single-flight now, and one
   unreadable file or directory is skipped instead of killing the
   whole scan. A client disconnect while sending a reply no longer
   raises out of the handler either.
b. A FAILED VLC LAUNCH WIPED THE PLAYBACK. v7's save/restore
   covered skipping only: a failed Play in VLC app (no vlc on PATH,
   launch error) cleared the previous playback and left "not
   playing" — or a stale "playing" — behind it. Fixed: play_request
   saves the whole playback first and restores it exactly on a
   failed VLC launch (503 still answers, with the restored state).
c. THE BROWSER COULD NOT PLAY THE FILE, AND THE SERVER SAID IT WAS
   PLAYING ANYWAY. The server recorded any file as "playing" in
   "here" mode, but a browser <video> can only decode some of them:
   a DivX-era MPEG-4 video, AC3/DTS sound, or any .avi sits black
   (or silent) while the tile claims it is playing — exactly the
   Dhoom symptom (state "playing", nothing on screen). Fixed: the
   server probes each file with ffprobe (video + audio codec,
   cached) before playing it in the tile. A file the browser cannot
   play comes back needs_vlc with a plain-language reason ("this
   file's video (mpeg4) can't play in a browser page") and a VLC
   hint — and the playback state is left untouched, so nothing
   claims to be playing when nothing is. The page asks the server
   FIRST now and only loads the <video> element for a playable
   file. Unprobed files (no ffprobe, or an unreadable file) fail
   open: the browser tries, and its existing "can't play this file"
   hint still applies. The probe is conservative on purpose:
   Chromium plays MPEG-4 Part 2 in an .mp4, Firefox does not — and
   a file that plays video with no sound (AC3) is not "playing".
   VLC plays all of these, with sound.
d. AUTO-ADVANCE NEVER TOLD THE SERVER. When a video ended, the
   tile advanced to the next episode on its own and the server's
   now-playing went stale (old episode name, old index). Fixed by
   (c)'s reorder: every in-page play now goes through /api/play, so
   the server stays in step — and Recent records the advance too.
e. THE QUEUE COULD BE POISONED BY AN UNPLAYABLE PICK (found while
   testing v8 itself). The click replaced the tile's playlist with
   the new show's episodes BEFORE the probe answered — so when the
   previous video ended, the tile auto-advanced into the unplayable
   show's first episode and showed ITS hint for a file nobody
   picked (in the test: a Dhoom click ended up showing the AC3
   hint). Fixed: the offered playlist is adopted only once the
   server says the file plays here; on a needs_vlc answer the tile
   is silenced and the hint stands on its own, and the previous
   playlist is never touched.

Also in v8, the small print:
- The webcam no longer says a bare "idle": it reads
  "standby — live when viewed" when nobody is watching, and
  "live — laptop/c270" while streaming — and "live" now means
  frames are actually flowing, not just that the camera is still
  starting up. (In v9 that label sits under the feed, in the media
  tile beside the player, instead of in its own tile.) The mic no
  longer says "idle" either: a present mic that is not capturing
  reads "READY — available, not capturing" (the voice loop is
  parked, so nothing is capturing, and that is normal, not a
  fault). Labels only — nothing records or captures anything new.
- The "All shows" toggle state survives the 30 s media re-render.
- A Recent entry whose show has left the scan still plays: it
  falls back to a single-episode queue instead of doing nothing.
- Rapid double-clicks on Watch here cannot cross their answers:
  only the latest play sets the video source.

Everything from v2–v7 is still in here (media scan scope and
skip-list, background status snapshot, tailnet bind, VLC windowed
player with the pkill safety net, per-device playback hints,
wrapping show buttons, natural episode sort, fullscreen from the
current episode, skip-failure restore, /api/stream 415 for
non-video, Wi-Fi colon fix, single /proc walk, webcam snapshot,
label correction after camera fallback, images reloaded only on
change, stale-snapshot pill and frozen clock, the "can't play"
hint surviving the 1 s poll, quote escaping, fullscreen mode
awareness, pause-button sync, model name matching, restart-script
health retry). Deliberately NOT changed: the POST endpoints have no
password (the dashboard is meant to be reachable over the private
tailnet, and the iPhone/iPad and the voice loop use them); the
build-log and milestone buttons are NOT in this dashboard — they
belong to the website, which is hands-off by HgX's order; nothing
was invented for them.

TONIGHT, ON THE ACER (from the dashboard folder):
  1. Back up the current dashboard first:
     cp -r ~/tonight-scripts/dashboard ~/tonight-scripts/dashboard.bak-v10
  2. Unzip this parcel over ~/tonight-scripts/dashboard/
     (replaces server.py + index.html; keeps log-rea.sh, log-voice.sh).
     recent.json is created by the server on first play — there is
     nothing to copy for it.
  3. chmod +x restart-dashboard-tailnet.sh
  4. ./restart-dashboard-tailnet.sh
     (kills the old server, relaunches on 0.0.0.0:8899, checks itself)
  5. On the laptop: http://127.0.0.1:8899
     On the iPhone/iPad (on the tailnet): http://<tailnet-ipv4>:8899
  6. Check: the clock ticks every second; the Sopranos and Big Bang Theory
     show episodes in the media tile; the Sports, Tailscale and Health &
     Heat tiles are filled; BOTH webcams show LIVE moving feeds BESIDE
     the video player in the media tile — the Logitech C270 large on
     top, the laptop built-in small over its bottom-right corner.
     There is no floating webcam panel any more, no separate webcam
     tile, and no Switch camera button — Picture Brain is wider
     (it spans the webcam's old cell in row 4).
  7. Stream check (it streams, so cap the wait): check BOTH feeds:
     curl -s -o /dev/null -w "%{http_code}\n" --max-time 15 \
       "http://127.0.0.1:8899/api/webcam-stream?cam=c270&nofallback=1"
     curl -s -o /dev/null -w "%{http_code}\n" --max-time 15 \
       "http://127.0.0.1:8899/api/webcam-stream?cam=laptop&nofallback=1"
     Expect 200 for each with a camera live. 503 means that camera
     was not found (with nofallback there is no silent fallback —
     without it, the server falls back to the other camera).
  8. Player check — the v5 test, in order:
     a. Click "Watch here" on The Sopranos. The tile must say, in
        plain words, to use the VLC app (the Sopranos are .avi) —
        it must NOT sit black claiming to play.
     b. Click "Watch here" on The Big Bang Theory. The show plays
        INSIDE the tile and the line reads "Now playing: … (in
        dashboard · looping · <time> / <length>)" with the time
        counting.
     c. Click "Play in VLC app" on The Big Bang Theory. The tile's
        player goes silent, the show opens in the VLC app window, and
        the line reads "(in VLC app · looping)".
     d. Close the VLC window. The audio MUST stop — this is the v5
        fix, no Stop button needed. The tile line returns to
        "not playing" on the next poll, and in the terminal
        pgrep -a vlc shows nothing. If the audio keeps playing after
        the window is closed, that is a stray VLC launched by hand;
        press Stop on the tile and check pgrep again — expect nothing.
     e. Press Stop on the tile with something playing. Everything goes
        silent, the line reads "not playing", and pgrep -a vlc shows
        nothing.
  9. iPhone/iPad check — the v6 test, on the phone (on the tailnet):
     a. Open http://<tailnet-ipv4>:8899 in Safari. All four buttons
        must be visible on every show row — "Watch here", "Play in VLC
        app", "VLC app", "Episodes" — the last two on a second line if
        needed, none cut off past the right edge.
     b. Tap "Watch here" on a Sopranos .avi. The tile must say, in
        plain words, to tap the "VLC app" link to play it on this
        device, and that "Play in VLC app" plays it on the laptop.
     c. With the VLC app installed (free from the App Store), tap the
        "VLC app" link on a Sopranos episode — the episode opens in
        the VLC app ON THE PHONE and plays there.
  10. v8 checks (on the laptop):
     a. The whole dashboard fits on one 1920x1080 screen with NO
        vertical scrollbar. The media tile shows only the 2 pinned
        shows, the 3 slots and Recent — not all 43 shows. The "All
        shows (N)" toggle is collapsed by default; clicking it opens
        the full list.
     b. Play something, then reload the page: it is still in Recent.
        Play something else, then press Stop and reload: both are in
        Recent, newest first.
     c. The Router tile says "online" (the router is up) and the
        Health dots read: Router online (green), REA installed
        (blue), Locally Uncensored installed (blue), ComfyUI parked
        (amber) — no red "offline" on any of those four.
     d. The mic reads READY and the webcam label under the feed (in
        the media tile, beside the video player) reads "standby —
        live when viewed" while nobody is watching the feed.
     e. Sports shows one compact line per league (Bengals, Raptors,
        Leafs, Jays) — no full NFL game list.
     f. Click "Watch here" on a Dhoom .mp4 (or any file whose sound
        is AC3): the tile says plainly that the browser cannot play
        it and names the VLC path — it does not sit black claiming
        to play.
     g. Terminal check for the scan fix (optional): with the
        dashboard open, curl the media endpoint twice, 5 s apart —
        both must answer in well under a second:
        time curl -s http://127.0.0.1:8899/api/media -o /dev/null
        (The first call after a restart may take a few seconds: it
        is the one synchronous walk. Every call after that is the
        cache.)
  11. v9 checks (on the laptop):
     a. The webcam sits BESIDE the video player in the media tile
        (video left, webcam right) — no floating panel, no
        separate webcam tile. (In v9 it was ONE switchable feed
        with a Switch camera button; v11 shows BOTH at once and
        the Switch button is gone — see the v11 checks below.)
        Hide collapses the webcam column and a "Show webcam"
        button appears in the media controls; Show brings it back.
     b. Picture Brain is wider (it spans the webcam's old cell in
        row 4). The whole dashboard still fits on one 1920x1080
        screen with NO vertical scrollbar.
     c. It looks nicer: near-black background with a soft glow at
        the top, glowing cyan tile titles, larger brighter numbers,
        rounded tiles with a faint cyan hairline and a gentle
        shadow. Same tiles, same data, same behaviour.
  12. v10 checks (on the laptop):
     a. The Big Bang Theory plays INSIDE the tile (Watch here)
        with sound — it now comes from the MP4 folder (H.264/AAC),
        not the drive's AC3 copy. The line reads "Now playing: …
        (in dashboard · looping · <time> / <length>)" with the
        time counting.
     b. The Sopranos still shows in the media tile (pinned) and
        "Watch here" still steers it to VLC in plain words (it is
        .avi, on the drive only) — it must NOT sit black claiming
        to play.
     c. "All shows" opens the merged library: the MP4 folder's
        shows (OZARK, Seinfeld, Silicon Valley, …) plus the
        drive-only shows (Sopranos, Dhoom, …) — no show listed
        twice. A show in both places (Big Bang Theory, Seinfeld,
        Silicon Valley) appears once, and its episodes are the
        MP4-folder versions.
     d. Play something from the MP4 folder, then reload the page:
        it is still in Recent. Play a drive-only show too: both
        are in Recent, newest first.
     e. Terminal check: curl the media endpoint and look at the
        sources — the MP4 folder must read available: true with
        its show count, the drive available: true with its count:
        curl -s http://127.0.0.1:8899/api/media | python3 -m json.tool | grep -A3 sources
        (Both media calls answer in well under a second; the
        first call after a restart may take a few seconds — it
        is the one synchronous walk of both roots.)
  13. v11 checks (on the laptop):
     a. BOTH webcams show in the media tile at once, beside the
        video player: the Logitech C270 large on top (tagged
        "C270 · main"), the laptop built-in small over its
        bottom-right corner (tagged "laptop"). The head pill
        reads LIVE and the laptop line reads "laptop · live".
        There is no Switch camera button any more.
     b. The media controls (Stop / Prev / Pause / Next / Vol /
        Fullscreen / Refresh shows) and the first pinned show are
        fully visible in the media tile — the two feeds did not
        push them below the fold. The whole dashboard still fits
        on one 1920x1080 screen with NO vertical scrollbar.
     c. Hide collapses the whole webcam area (both feeds); a
        "Show webcams" button appears in the media controls;
        Show brings both feeds back, live.
     d. Unplug the C270 (or cover it so the camera cannot open):
        the laptop feed takes the main slot (full width) and the
        head pill reads "1 LIVE". Plug it back: the C270 returns
        to main and the laptop to its corner, and the pill reads
        LIVE again. (A dark laptop feed — lid closed — still
        reads live; it is shown dark, not "unavailable".)
     e. Terminal check: curl /api/status and look at webcam.cams
        — c270 and laptop each report streaming true with their
        device and label:
        curl -s http://127.0.0.1:8899/api/status | python3 -m json.tool | grep -A8 '"webcam"'

To make the tailnet bind survive a reboot, add this line to
~/Jarvis/autostart/start-dashboard.sh before the python3 line:
  export DASHBOARD_HOST=0.0.0.0

Still unverified without the Acer: real GPU/Ollama/Tailscale values,
the real Sopranos files on /mnt/media, the iPhone actually opening the
page, the vlc:// link opening the VLC app on iOS, the real laptop and
C270 cameras on the live feed (both at once now, C270 main + laptop
PiP — verified here only against a fake two-camera ffmpeg that emits
a red frame for the C270 and a blue frame for the laptop, including
the C270-missing fallback, the laptop promotion, the dark-laptop
feed, and Hide/Show; the real closed-lid behaviour — a genuinely
dark laptop feed, as opposed to the fake near-black frame — has not
been seen), the PiP rendering on a real phone screen (on a phone the
webcams wrap below the video — verified here at 390px for no
sideways scroll and both feeds visible), and the real router.log tail
(the test machine had no router log file — on the Acer it lives at
~/tonight-scripts/acer-llm-consolidation/router.log). The in-tile
player was verified here against a fake two-root media tree (the
MP4 folder's H.264+AAC plays in-tile and is preferred over the
drive's copy; the drive's MPEG-4+AAC and H.264+AC3 steer to VLC;
the drive-only .avi steers to VLC) — whether a given real file
plays in-tile depends on its actual codecs, which the probe now
reports in the /api/play answer. The real MP4 folder itself (2,785
files, 239 GB, 24 shows on the Acer) was NOT walked here — only a
fake 4-show copy of it. The fallback (MP4 folder missing, drive
alone carries the list) was verified here against a fake missing
folder; on the Acer it has not been exercised. The full 2,785-file
scan speed on the real machine is also unmeasured — the scan is
cached (background worker, 120 s) so the first call after a
restart may take a few seconds, and every call after that is the
cache.
