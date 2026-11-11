# Dashboard v9 — the published copy

**Status: LIVE on the Acer since 2026-11-07 ~00:18 ET.** Applied from
this folder (v8 backed up to `dashboard.bak-v8` first), confirmed live
by terminal output: `/api/status` 200 with live time, GPU 34°C, media
mounted. v9 supersedes v8 as the live dashboard; v8 stays in the repo
as history (`local-jarvis/dashboard/v8/`).

## What v9 changes (visual polish only — no grid, endpoint, or behaviour change)

- **Palette:** near-black background (`#020509`) with a subtle blue
  tint and a soft arc-reactor glow at the top; tiles are glassy
  gradients with a faint cyan hairline border, 12px rounded corners,
  gentle shadow + inset top highlight.
- **Typography:** refined system sans; tile titles glow softly in cyan;
  big values 32px, weight 300, near-white with a soft cyan glow —
  readable from a few feet away.
- **Breathing room:** tile padding 14px 16px; softer borders and padding.
- **Depth:** gradient-filled bars (cyan, hot amber for heat) with a glow;
  gradient buttons with hover glow; live pill glows green. Dots keep the
  honest colours, glowing a touch stronger.
- **Webcam layout:** the webcam is NO LONGER a separate floating tile.
  It now sits in the MEDIA tile, directly beside the video player
  (video left, webcam right, 270px column, 4:3). Keeps the live feed,
  Switch camera, Hide, and the "live — laptop" / "standby" label (now
  under the feed, in the media tile). Hide collapses the webcam column
  and shows a "Show webcam" button; Show restores it. On a narrow screen
  the webcam wraps below the video. Picture Brain now spans 2 columns in
  the webcam's old cell — no hole in the grid.

## Verification (builder, 2026-11-07)

- `py_compile` clean; `node --check` clean.
- API regression 28/28 pass; layout 35/35 pass (1920×1080 exact
  one-screen fit, webcam beside the player, no floating webcam tile,
  Picture Brain spans 2 columns, Hide/Show round-trip pass, webcam fail
  path pass, mobile wrap pass).
- All v8 + v7 fix markers present; stale webcam refs = 0.

## Scrub note (publishing house)

One hit in `server.py` line 1149: a drive folder name in `SKIP_DIRS`
was replaced with the placeholder `ownerlaptop` (rename it to match your
own drive). Code still compiles after the scrub. The original zip is
untouched at `~/workspace/family-bot/dashboard-fixed-2026-11-06-v9.zip`
(56,634 bytes, MD5 `2c711084f879dba60f2ff43f672fb6b8`). The scrubbed zip
is 56,632 bytes, MD5 `57895981fc8940741d1bee789a668e14`.

## Files

| File | Size (bytes) |
|---|---|
| `server.py` | 102,818 |
| `index.html` | 66,359 |
| `README-FIRST.txt` | 18,367 |
| `media-slots.json` | 74 (unchanged from v8) |
| `restart-dashboard-tailnet.sh` | 1,424 (unchanged from v8) |

See `README-FIRST.txt` for the apply steps and the v9 checks.

---

@basementjarvisu · basementjarvisunleashed@gmail.com
