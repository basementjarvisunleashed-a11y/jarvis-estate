# Dashboard v8 — the redesign (2026-11-06, night)

The always-on screen, rebuilt on top of v7: one screen, no scroll at
1920×1080, pinned shows + Recent in the media tile, honest health dots,
and the night's big playback fault fixed (none of the shows played on
the live v7 dashboard).

**Status: PUBLISHED here, NOT applied to the Acer.** v8 supersedes v7
as the published dashboard copy. **v7 stays the live dashboard on the
Acer until HgX says to apply v8.** Applying it is the v7 pattern:
back up the current dashboard, unzip, restart, verify — on his word
only.

**What is new over v7:**

1. Router, fixed for real — availability from the router `/health`
   endpoint (cached 5 s), never from a log file; the log tail reads the
   real path `~/tonight-scripts/acer-llm-consolidation/router.log`.
2. Honest health dots — REA and Locally Uncensored read "installed"
   (blue) when present; ComfyUI reads "parked" (amber) when stopped; a
   dot is red only for a real fault.
3. Media tile shows pinned shows + Recent only; the full list sits
   behind a collapsed "All shows" toggle.
4. Recent — server-side `recent.json`, newest first, max 5, survives
   restart; recorded on every play and skip.
5. One screen, no scroll at 1920×1080 (6-col × 4-row grid, tiles scroll
   internally).
6. Sports compact — one line per league, HgX's team only.
7. Playback fault fixed — cached media scan (a slow re-walk no longer
   wipes the shows); ffprobe probe before in-page play (unplayable
   files get a plain-language reason, state untouched); a VLC launch
   failure restores the playback state.

**Verification (build):** `py_compile` clean; API regression 28/28
pass; layout 31/31 pass (1920×1080 no scroll). All 18 v7 fixes carried
forward, none regressed. Full detail in `README-FIRST.txt`.

**Files:**

| File | What it is |
|---|---|
| `server.py` | The dashboard server (scrubbed published copy — see below). |
| `index.html` | The dashboard page. |
| `README-FIRST.txt` | The v8 fix list and the tonight checks. |
| `media-slots.json` | Pinned shows + slots (unchanged from v7). |
| `restart-dashboard-tailnet.sh` | Restart on `0.0.0.0:8899` (unchanged from v7). |
| `dashboard-fixed-2026-11-06-v8-scrubbed.zip` | This folder as a zip (uploaded via the GitHub web UI). |

**Scrub note:** one folder name in `server.py` (`SKIP_DIRS`) was
replaced with the placeholder `ownerlaptop` — rename it to match your
own old laptop backup folder. No credentials, no personal data. The
original zip is untouched (MD5
`bede27503a198777066b4896b22cd430`, 54,711 bytes); the scrubbed zip is
55,068 bytes, MD5 `75d8715395b8689d97e7bbe285204cec`. The media endpoints
have no password by design — the dashboard is meant to be reachable
over the private tailnet only.
