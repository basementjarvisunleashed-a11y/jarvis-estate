PUBLISHED COPY — SCRUBBED 2026-11-06
====================================
This is the public copy of dashboard v7 (live on the owner's Acer).
One folder name was scrubbed: "OwnerLaptop" below is a placeholder for
the owner's old laptop backup folder; rename it (in SKIP_DIRS in
server.py) to match your own drive. No other change was made.

JARVIS DASHBOARD — FIXED BUILD v7 (2026-11-06, night)
========================================================

v7 is a thorough audit fix — every issue found in a line-by-line check
of v6 (server + page), listed in 12 below. Everything from v2 + v3 +
v4 + v5 + v6 is in here.

What was wrong, and what this fixes:
1. The media scan grouped everything under "TV SHOWS", so The Sopranos and
   The Big Bang Theory never matched and showed "(not on drive)". Fixed: the
   scan now finds the show folder (the cap is now 100000 — see 7).
2. The status call ran every collector in sequence on every request, so one
   slow piece froze the whole page — the "screenshot". Fixed: a background
   thread refreshes the status every 3s; the page serves the snapshot
   instantly, and the clock now ticks every second on the page itself.
3. The server only listened on the laptop (127.0.0.1), so the iPhone/iPad
   could not reach it even on the tailnet. Fixed: restart with
   DASHBOARD_HOST=0.0.0.0 (the restart script does this).
4. New tiles: Sports (Raptors, Leafs, Blue Jays, Bengals + all NFL scores,
   live from ESPN), Tailscale (this node + online peers), Health & Heat
   (every subsystem as a dot, GPU/CPU temperature bars), and model activity
   (what each model is doing — its last routed job + loaded-until time).
5. One responsive page for the laptop, the iPad and the iPhone.
   Every episode also has a "VLC app" link — tap it on iOS and the episode
   opens in the VLC app (Safari cannot play .mkv in a web page).
   The three blank slots are still there, untouched.
6. NEW in v2 — LIVE webcam, bottom right: a moving feed pinned to the
   bottom-right corner of the dashboard, on the laptop, the iPhone and the
   iPad. The laptop camera (/dev/video0) first, the C270 (/dev/video2) as
   the fallback, with a Switch button between them and a Hide button that
   collapses it to a small "Webcam" pill. The feed is an MJPEG stream at
   /api/webcam-stream (640x480, ~10 fps). The camera runs only while
   someone is watching — it stops about 10 seconds after the last viewer
   leaves, so the camera light goes out.
7. NEW in v3 — the media scan missed the shows entirely: on the real drive
   the scan walked the whole 3.7 TB tree and counted every video file
   toward a 5000-file cap, so it stopped inside the backup folders
   (FileHistory, OwnerLaptop, JarvisBackup, ...) before it ever reached
   TV SHOWS — the tile listed movies and junk folders as "shows" and no
   Sopranos at all. Fixed: the scan now walks only TV SHOWS / MOVIES /
   MUSIC / VIDEOS when those folders exist (otherwise the whole dir), never
   enters backup or system folders (FileHistory, WindowsImageBackup,
   OwnerLaptop, JarvisBackup, $RECYCLE.BIN, System Volume Information,
   Recovery, Program Files, WindowsApps, Back Up, any $-folder), and the
   cap is raised to 100000. No top-level non-media folder appears as a
   show again.
8. NEW in v3 — the dashboard log was empty because Python buffers stdout
   when redirected to a file; the server now launches unbuffered
   (python3 -u) so the log actually gets content. The restart script also
   prints the real tailnet address now (from `tailscale ip -4`) instead of
   a placeholder.
9. NEW in v4 — the dashboard is the player now. What happened: "Play show
   (VLC)" was the big button, so the Sopranos opened in a separate VLC
   app window floating over the dashboard while the tile sat at "not
   playing" / 0:00 — and closing that VLC window did NOT stop the audio,
   because a VLC process survived the window closing (and a VLC launched
   by hand is invisible to the dashboard, so the old Stop, which only
   killed the one VLC the server itself launched, could not silence it).
   Fixed:
   a. "Watch here" is now the big primary button on every show and every
      episode. It plays the show INSIDE the dashboard tile, in the tile's
      own video player, and the tile says "Now playing: The Sopranos —
      S01E01 (in dashboard · looping · 0:42 / 24:13)" with the time
      counting. The dashboard is the player.
   b. "Play in VLC app" is the separate-window option, labelled as the
      app. Choosing it silences the tile's player first, so the show
      can never play twice at once — and the tile says "Now playing: …
      (in VLC app · looping)" so you always know where the sound is
      coming from.
   c. ONE Stop button stops BOTH. It kills EVERY VLC process on the
      machine by name (pkill vlc), not just the one the server launched
      — so it works even if the VLC window was already closed, and it
      silences a VLC launched by hand too. It also clears the tile's
      player and any queued voice command, so nothing can restart
      playback behind your back. Pause in VLC mode freezes every VLC
      by name the same way.
   d. The server now reports which player is active: /api/play returns
      now_playing {mode: "here"|"vlc", show, episode} and /api/now-playing
      reports the same. (The old mode name "page" still works if an old
      tab sends it — it is reported as "here".)
   e. If this browser cannot play the file in the page (.avi, and .mkv
      whose sound is AC3/DTS), the tile says so plainly instead of
      sitting black — and since v6 it names the right way to watch it
      for the device you are on (see 11). In that case, use the VLC
      app button (VLC understands those files), or open the dashboard
      in Chrome (which does play .mkv in a page).
10. NEW in v5 — closing the VLC window now stops the audio. What
    happened: the server launched VLC through cvlc, the headless
    console player — and cvlc runs vlc with -I dummy, so the VLC
    window that opened was only a video window with no real player
    behind it. Closing it did NOT quit the process, so the audio kept
    playing after the window was gone — the ghost, twice in one night.
    Fixed at the source: the server now launches the normal VLC
    player (windowed, never cvlc), with the same --loop playlist.
    A normal VLC quits when its window is closed, so closing the
    window stops the audio — no button needed. The Stop button is
    unchanged as the safety net: it still kills every VLC process by
    name, and /api/stop still clears now_playing and any queued
    voice-control flag. If only cvlc is installed (no windowed VLC),
    the server answers 503 instead of launching a headless player
    that could ghost again.
11. NEW in v6 — the iPhone/iPad playback confusion is fixed. What
    happened: when the browser could not play a file in the page, the
    tile said "use 'Play in VLC app' below" — but on an iPhone that
    button plays the show on the LAPTOP, not on the phone, so tapping
    it did nothing on the phone. And on a narrow phone screen only two
    of the four show buttons were visible — the "VLC app" link and the
    "Episodes" button were cut off past the right edge, out of reach.
    Fixed:
    a. The hint now names the right path for the device you are on.
       On iPhone/iPad it says: tap the "VLC app" link to play it on
       this device (VLC app required) — "Play in VLC app" plays it on
       the laptop instead. On a laptop/desktop it says: tap the
       "VLC app" link to play it on this device, or "Play in VLC app"
       to play it on the laptop. The hint never again tells an iPhone
       user that the laptop button is the way to watch on the phone.
    b. The four show controls (Watch here / Play in VLC app / VLC app
       / Episodes) are now a wrapping flex row: on a narrow phone
       screen they drop to a second line instead of running off the
       right edge. Verified in a real browser at 390px wide: all four
       buttons visible and reachable on every show row (and the three
       episode-row buttons too), with no sideways scrolling.
    c. What the buttons mean, once and for all: "Watch here" plays in
       the dashboard tile on this device. "VLC app" opens the episode
       in the VLC app ON THIS DEVICE (the VLC app must be installed —
       free from the App Store). "Play in VLC app" plays it on the
       LAPTOP's VLC. If a show is silent in the tile, its sound is in
       a format the browser cannot play (AC3/DTS in a .mkv) — the VLC
       app understands it.
12. NEW in v7 — a line-by-line audit of v6, checked "100 times". What
    was found and fixed (server = server.py, page = index.html):
    a. The media drive looked "mounted" when it was not. The disk tile
       and the media scan only checked that /mnt/hgx was a directory —
       but an empty mountpoint IS a directory, and disk_usage() happily
       reports the laptop's own drive for it. So with the drive
       unplugged the tile showed the NVMe's numbers as the media drive
       and the scan claimed "mounted: true" with no shows. Fixed: the
       server now only counts the drive as mounted when it is a mount
       point or actually holds media (a category folder or a video
       file). Unplugged, the tile says "unmounted" and the Health dot
       goes red.
    b. Episodes sorted wrong: "Episode 10" came before "Episode 2"
       (plain alphabetical order). Fixed: natural sort — Episode 2
       before Episode 10, in the episode lists and the show list.
    c. Toggling fullscreen in VLC mode restarted the show from
       episode 1. The fullscreen relaunch played the whole playlist
       from the start, ignoring the episode you were on. Fixed: it now
       relaunches from the current episode (the episode itself still
       restarts from its beginning — VLC cannot resume mid-episode).
    d. Skipping to the next episode while VLC failed to launch left
       the tile claiming the new episode was playing when nothing was.
       Fixed: the old episode is restored if the launch fails.
    e. The media stream endpoint would serve ANY file under the media
       drive — documents, photos, backups — to anyone on the tailnet.
       Fixed: /api/stream and the /api/play path branch now answer 415
       for anything that is not a video file.
    f. A Wi-Fi name with a colon in it broke the Wi-Fi tile (the
       signal was read as the name). Fixed: the name and the signal are
       split off the two ends, so a colon in the middle is kept.
    g. The status snapshot walked /proc twice (once for the processes
       tile, once for the picture tile) and the two could disagree.
       Fixed: one walk per snapshot, shared by both.
    h. The webcam snapshot tile was dead: nothing ever wrote
       webcam.jpg, so it always said "no snapshot yet" even while the
       live feed worked. Fixed: while a live stream is running, the
       server saves its latest frame as webcam.jpg (at most once every
       30 s), so the tile shows a still.
    i. The webcam label could lie: if the laptop camera failed, the
       server silently fell back to the C270, but the label still said
       "laptop". Fixed: the server reports which camera is actually
       streaming, and the page corrects the label from it.
    j. The picture and webcam images were re-downloaded on EVERY 3 s
       poll (the cache-buster always differed) — a needless download
       every 3 s, worst on the phone over the tailnet. Fixed: each
       image is re-fetched only when it actually changes (a new
       picture name, a new snapshot time).
    k. The status bar could look live while the server was dead: the
       clock kept ticking on its own forever, and the footer kept
       showing the last good update as if it were current. Fixed: the
       clock freezes when no poll has succeeded for 10 s; the footer
       says "server unreachable — last update …" on a failed poll; and
       when the server answers but its data is over 15 s old, the LIVE
       pill reads "● STALE" in amber.
    l. The "can't play this file" hint vanished after one second: the
       1 s now-playing poll overwrote it with "Now playing" (the server
       still recorded the file as playing). Fixed: the hint stays up
       until you pick another episode or press Stop.
    m. That hint was wrong for some files: it told you to use the VLC
       app for ANY load failure — including a down server or a moved
       file, where VLC would not help. Fixed: .avi/.mkv get the VLC
       hint; other files get "could not load — the server may be
       unreachable, or the file may have moved".
    n. A show or episode name with a quote in it could break its row
       (the name goes into data-* attributes). Fixed: quotes are
       escaped now, like the other characters.
    o. The Fullscreen button ignored the player mode: in VLC mode it
       fullscreened the tile's empty video (a black screen) while VLC
       also went fullscreen. Fixed: in VLC mode the button only tells
       the server; it does not touch the tile's video.
    p. The Pause/Resume button went out of step if you paused from the
       video's own controls (the tile has native controls too).
       Fixed: the button now follows the video's own pause/play.
    q. A model could look offline just because ollama list and ollama
       ps print its name differently ("qwen9b-abliterated" vs
       "qwen9b-abliterated:latest"). Fixed: both spellings match.
    r. The restart script could exit before printing the tailnet
       address: its one health-check curl ran under set -e, so if the
       server was slow to start the script died on the first curl.
       Fixed: it now retries the health check for up to 10 s.
    Deliberately NOT changed: the POST endpoints (/api/play, /api/stop,
    /api/media-control, /api/fullscreen) have no password — the
    dashboard is meant to be reachable over the private tailnet (the
    iPhone/iPad and the voice loop use them), and a password would
    break that. The build-log and milestone buttons are NOT in this
    dashboard — they belong to the website, which is hands-off by
    HgX's order; nothing was invented for them here.

TONIGHT, ON THE ACER (from the dashboard folder):
  1. Unzip this parcel over ~/tonight-scripts/dashboard/
     (replaces server.py + index.html; keeps log-rea.sh, log-voice.sh).
  2. chmod +x restart-dashboard-tailnet.sh
  3. ./restart-dashboard-tailnet.sh
     (kills the old server, relaunches on 0.0.0.0:8899, checks itself)
  4. On the laptop: http://127.0.0.1:8899
     On the iPhone/iPad (on the tailnet): http://100.107.253.109:8899
  5. Check: the clock ticks every second; the Sopranos and Big Bang Theory
     show episodes in the media tile; the Sports, Tailscale and Health &
     Heat tiles are filled; the webcam panel bottom-right shows a LIVE
     moving feed (laptop camera first — Switch to the C270 to check it).
  6. Stream check (it streams, so cap the wait):
     curl -s -o /dev/null -w "%{http_code}\n" --max-time 15 \
       http://127.0.0.1:8899/api/webcam-stream
     Expect 200 with a camera live. 503 means no camera was found.
  7. Player check — the v5 test, in order:
     a. Click "Watch here" on The Sopranos. The show plays INSIDE the
        tile and the line reads "Now playing: … (in dashboard · looping
        · <time> / <length>)" with the time counting.
     b. Click "Play in VLC app" on The Big Bang Theory. The tile's
        player goes silent, the show opens in the VLC app window, and
        the line reads "(in VLC app · looping)".
     c. Close the VLC window. The audio MUST stop — this is the v5
        fix, no Stop button needed. The tile line returns to
        "not playing" on the next poll, and in the terminal
        pgrep -a vlc shows nothing. If the audio keeps playing after
        the window is closed, that is a stray VLC launched by hand;
        press Stop on the tile and check pgrep again — expect nothing.
     d. Press Stop on the tile with something playing. Everything goes
        silent, the line reads "not playing", and pgrep -a vlc shows
        nothing.
  8. Terminal check for the ghost-audio fix (optional, proves it):
     vlc --loop "/mnt/hgx/TV SHOWS/THE SOPRANOS/The Sopranos/The Sopranos - Season 01" &
     (a VLC launched by hand, like the old one)
     curl -s -X POST http://127.0.0.1:8899/api/stop -H 'Content-Type: application/json' -d '{}'
     pgrep -a vlc
     Expect nothing — Stop kills the hand-launched VLC too.
  9. iPhone/iPad check — the v6 test, on the phone (on the tailnet):
     a. Open http://100.107.253.109:8899 in Safari. All four buttons
        must be visible on every show row — "Watch here", "Play in VLC
        app", "VLC app", "Episodes" — the last two on a second line if
        needed, none cut off past the right edge.
     b. Tap "Watch here" on The Sopranos (.avi). The tile must say,
        in plain words, to tap the "VLC app" link to play it on this
        device, and that "Play in VLC app" plays it on the laptop.
     c. With the VLC app installed (free from the App Store), tap the
        "VLC app" link on a Sopranos episode — the episode opens in
        the VLC app ON THE PHONE and plays there.
  10. v7 checks (on the laptop, after the v5/v6 checks above):
     a. Unplug the media drive (or unmount /mnt/hgx) and reload. The
        Memory tile must say the media drive is "unmounted" (not the
        laptop's own numbers), and the media tile must say it is not
        mounted — not "mounted" with no shows.
     b. In the media tile, the episodes of a show with more than nine
        episodes must run 1, 2, … 9, 10 — not 1, 10, 2.
     c. Play a show in VLC app, skip to episode 3, then press
        Fullscreen. It must resume from episode 3, not episode 1.
     d. Leave the dashboard open and stop the server. Within 10 s the
        clock must freeze, the LIVE pill must read OFFLINE, and the
        footer must say "server unreachable — last update …".
     e. Click "Watch here" on a Sopranos .avi. The "can't play this
        file" hint must stay up (not be replaced by "Now playing"
        after a second).

To make the tailnet bind survive a reboot, add this line to
~/Jarvis/autostart/start-dashboard.sh before the python3 line:
  export DASHBOARD_HOST=0.0.0.0

Still unverified without the Acer: real GPU/Ollama/Tailscale values, the
real Sopranos files on /mnt/hgx, the iPhone actually opening the page, the
vlc:// link opening the VLC app on iOS, the real laptop and C270 cameras
on the live feed, and the panel rendering on a real phone screen. The
in-tile player was verified here against a fake media tree (Sopranos .mkv
+ Big Bang Theory .mp4) — whether the real Sopranos .mkv files play
in-tile depends on the browser (see 9e): Chrome yes, Firefox no.
