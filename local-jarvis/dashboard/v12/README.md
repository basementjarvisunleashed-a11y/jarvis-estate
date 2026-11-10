# JARVIS DASHBOARD — v12 (2026-11-08)

v12 is a fix release on top of v11. Everything from v2–v11 is in here,
none regressed. Six things are new — all six are HgX's orders
(2026-11-08 ~17:34 ET, voice).

## What changed in v12

1. **Laptop camera — clearly visible.** In v11 the laptop built-in
   camera was a 120 px picture-in-picture over the C270's lower-right
   corner — too small to see, and when it was dark (lid closed / dark
   ceiling) it was a black box on a dark page, invisible. In v12 the
   laptop feed is stacked BELOW the C270 at full column width
   (~270 px), so it is clearly visible. The C270 stays main (large,
   on top). If the C270 is absent, the laptop is still promoted to
   main and the C270 feed is hidden, as in v11. A new amber badge
   ("dark — lid may be closed?") appears over the laptop feed when
   its mean frame luminance is below 12 — the same threshold the
   standalone webcam app uses — so a dark feed reads as "live but
   dark" instead of looking missing. The badge is measured by
   sampling the live frame to a small offscreen canvas every 5 s
   (same-origin, so readback is allowed); any failure just hides
   the badge, never breaks the page.

2. **CPU temperature + GPU on top.** A new compact top strip sits
   directly under the header, above everything else: CPU temp (big,
   with 1m load) and GPU (big temp, name, util %, VRAM used/total).
   It is filled by the same 3 s status poll as the System tile
   (same `/api/status` data — no new endpoint). It turns amber at
   80°C or hotter.

3. **No scroll for the top section.** The top strip is a single row,
   ~64 px tall (header + strip ≈ 120 px), so it fits in any viewport
   without scrolling. On a phone it stacks vertically instead of
   squeezing side by side.

4. **The whole dashboard scrolls.** This reverses v8's "one screen,
   no scroll": the `overflow: hidden` on html/body is gone, the grid
   is no longer locked to 4 equal rows, and tiles no longer scroll
   inside themselves. Rows size to their content and the page grows
   + scrolls naturally. The grid keeps its 6-column desktop
   placement. Below 1200 px nothing changes (it scrolled there
   already).

5. **REA status/history shows the C270 breakdown.** A highlighted
   "Latest · 2026-11-08" entry sits at the top of the REA tile:
   Logitech C270 breakdown — 15 tools used · 373 functions
   decompiled (Ghidra, all OK, 0 failed) · live USB pcap captured
   (6,037 packets, 233 MB, 83.0% isochronous, ~16.7/frame) · Frida
   trace done · ImHex pattern done · report 31K · verdict: stock,
   clean UVC device, no hidden tricks. It is static HTML, outside
   `#rea-body`, so the 3 s status poll (which rewrites `#rea-body`)
   never wipes it. Existing REA history entries are untouched.

6. **Sports much smaller.** The sports tile now shows the Bengals
   (NFL) only — one compact line (score + status) — instead of one
   line per league. The tile is ~60 px tall, roughly a third of
   v11's. The other leagues (NHL/MLB/NBA) are not rendered. To
   bring them back, render every league again in the sports block
   of index.html (the comment there says how).

## What did NOT change

- Port 8899, host 0.0.0.0, autostart, server directory layout.
- server.py is byte-identical to v11. No endpoint changed
  (`/api/status`, `/api/media`, `/api/webcam-stream`,
  `/api/voice`, `/api/play`, `/api/stream`, etc.) and no JSON
  field changed (including `webcam.cams`).
- Media tile (pinned + Recent, VLC + in-tile player, two roots),
  Tailscale tile, weather, RAM/drive, conversation tile, model
  status/activity, health/heat, the webcam watchdog (3 s poll,
  8 s grace, 5 s retry), Hide/Show, and the C270→laptop promotion
  all work as in v11.
- The webcam app on port 8898 is untouched.

## How to apply

On the Acer, from the folder this zip was extracted to:

```bash
bash apply-v12.sh
```

That backs up the current (v11) dashboard to
`~/tonight-scripts/dashboard.bak-v11` (only if that backup does
not already exist), copies the four v12 files in
(`index.html`, `server.py`, `media-slots.json`,
`restart-dashboard-tailnet.sh`), and restarts the dashboard on
0.0.0.0:8899. No sudo. Then open http://100.107.253.109:8899
(or the tailnet IP the restart script prints).

## How to verify

1. `curl -s http://127.0.0.1:8899/api/status | head -c 200` → HTTP 200.
2. Open the dashboard. The top strip (CPU temp + GPU) is the first
   thing under the header. Scroll down — the whole page scrolls.
3. In the media tile, the laptop camera is a full-width feed below
   the C270 (not a tiny PiP). If it is dark, an amber "dark — lid
   may be closed?" badge shows over it.
4. The REA tile has the "Latest · 2026-11-08 — Logitech C270
   breakdown" entry at the top.
5. The sports tile is one short line (Bengals only).

## How to roll back to v11

```bash
cp -r ~/tonight-scripts/dashboard.bak-v11/* ~/tonight-scripts/dashboard/
cd ~/tonight-scripts/dashboard
./restart-dashboard-tailnet.sh
```

If `dashboard.bak-v11` does not exist (apply-v12.sh never ran),
re-extract `dashboard-fixed-2026-11-06-v11.zip` over
`~/tonight-scripts/dashboard/` and restart the same way.
