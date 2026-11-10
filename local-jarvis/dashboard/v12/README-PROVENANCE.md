# Dashboard v12 — provenance

**Version:** v12, built 2026-11-08, applied and LIVE on the Acer 2026-11-08 ~17:41 ET (v11 backed up as `dashboard.bak-v11`).
**Live at:** http://100.107.253.109:8899 (port 8899).

## Source

- Original parcel: `dashboard-fixed-2026-11-08-v12.zip`, 58,919 bytes, MD5 `cd1aabacecd2c281988f38ab51842db2` (verified before scrub).
- The parcel and the build dir (`v12-build/`) are byte-identical: all 6 files match by MD5.
- Scrubbed parcel: `dashboard-fixed-2026-11-08-v12-scrubbed.zip`, 58,590 bytes, MD5 `b13de91776d654160860f89100f26148`.

## Files (6 — v12 adds `apply-v12.sh` to the v8–v10 five)

| File | Bytes | MD5 (scrubbed) |
|---|---|---|
| `index.html` | 81,137 | `eafc919eea70af5d17da6a26e5c932af` (unchanged — no leaks) |
| `server.py` | 110,887 | `07cda147611d84653aa6898cca999c7c` (scrubbed; original `ea5ea7b401416bbdfa5a3414dc6d0089`) |
| `media-slots.json` | 74 | `e42033bb9d8d466f05f8195ca15ecb9c` (unchanged) |
| `restart-dashboard-tailnet.sh` | 1,424 | `d6a2fe4f135cbea1414ffdf09f73da13` (unchanged) |
| `README.md` | 5,194 | `7d7b80eef41f3f9adb6869bd63313099` (unchanged — the dashboard's own README) |
| `apply-v12.sh` | 1,276 | `67d713d23c8b145ba455cc140b9b7fdb` (unchanged) |

## What changed in v12 (vs v11; all six are HgX's orders, 2026-11-08 ~17:34 ET)

1. **Laptop camera clearly visible.** In v11 it was a 120 px picture-in-picture over the C270's corner; in v12 the laptop feed is stacked BELOW the C270 at full column width (~270 px). C270 stays main on top. A new amber badge ("dark — lid may be closed?") appears over the laptop feed when mean frame luminance is below 12.
2. **CPU temperature + GPU on top.** A compact top strip directly under the header: CPU temp (big, with 1m load) and GPU (big temp, name, util %, VRAM used/total). Same 3 s status poll, no new endpoint. Amber at 80°C or hotter.
3. **No scroll for the top section.** The top strip is a single ~64 px row (header + strip ≈ 120 px).
4. **The whole dashboard scrolls.** Reverses v8's "one screen, no scroll": the `overflow: hidden` on html/body is gone, the grid is no longer locked to 4 equal rows, tiles no longer scroll inside themselves.
5. **REA tile shows the C270 breakdown.** A highlighted "Latest · 2026-11-08" entry at the top of the REA tile: 15 tools used · 373 functions decompiled (Ghidra, 0 failed) · live USB pcap (6,037 packets, 233 MB, 83.0% isochronous, ~16.7/frame) · Frida trace done · ImHex pattern done · report 31K · verdict: stock, clean UVC device.
6. **Sports much smaller.** Bengals (NFL) only — one compact line — instead of one line per league. Tile ~60 px, roughly a third of v11's. NHL/MLB/NBA are not rendered.

## What did NOT change

- Port 8899, host 0.0.0.0, autostart, server directory layout.
- `server.py` is byte-identical to v11 per the dashboard's own README — **not independently verified here**: the v11 parcel was never sent to the publishing house, so no v11 server.py exists to compare against. The scrubbed server.py does carry v11 markers (`?nofallback=1`, dual view), which is consistent with the claim.
- Media tile (pinned + Recent, VLC + in-tile player, two media roots), Tailscale tile, weather, RAM/drive, conversation tile, model status/activity, health/heat, webcam watchdog, Hide/Show, and the C270→laptop promotion all work as in v11. The webcam app on port 8898 is untouched.
- All 12 API endpoints present (`/api/status`, `/api/voice`, `/api/picture`, `/api/webcam`, `/api/webcam-stream`, `/api/media`, `/api/now-playing`, `/api/media-control`, `/api/fullscreen`, `/api/stream`, `/api/play`, `/api/stop`). Two media roots (`MEDIA_DIRS = [IPAD_MP4_DIR, MEDIA_DIR]`) intact.

## Scrub applied (this build)

Only `server.py` needed scrubbing; the other five files were clean and are byte-identical to the originals.

| # | Location | Was | Now |
|---|---|---|---|
| 1 | `server.py:1209` (SKIP_DIRS) | the owner's laptop name (redacted) | `ownerlaptop` |
| 2 | `server.py:47–48` (docstring, split across two lines) | the local MP4 folder path | `/path/to/ipad-pro-mp4-folder` |
| 3 | `server.py:63` (v10 notes comment) | the local MP4 folder path | `/path/to/ipad-pro-mp4-folder` |
| 4 | `server.py:136` (IPAD_MP4_DIR default) | the local MP4 folder path | `/path/to/ipad-pro-mp4-folder` |

Final identity grep over the scrubbed files: **0 hits** for the owner's real name and **0 hits** for the home-directory path. The originals in `orig/` are untouched.

Deliberate retentions (precedent, not oversights):
- **Tailnet IP `100.107.253.109`** stays in `README.md` (dashboard URL) and in the dashboard's own docs, exactly as in v7/v8/v9/v10. New docs use the `<acer-tailnet-ip>` placeholder; dashboard files retain the literal address.
- **`/mnt/hgx`** (the media-drive mount point) stays — it is the drive label, documented in SETUP.md and STATE, and was kept in v7–v10.
- **`HgX`** (the public handle) stays in comments and UI strings — it is the public identity, not the real name.
- **False positives checked and kept:** `server.py` "two tokens" (code comments about word tokens, not credentials); `/ 100.0` (a percentage calculation, not an IP).

## Verification done

- Original zip MD5 verified before touching anything; all 6 files byte-identical between zip and build dir.
- Scrubbed `server.py` compiles clean (`py_compile`, cfile pointed at /tmp so no `__pycache__` pollutes the staging).
- v9/v10 markers present: two media roots, `/api/media`, webcam in the media tile (27 refs), 12 API endpoints.
- All six v12 changes confirmed present in `index.html`: dark badge ("lid may be closed?"), top strip (9 refs), CPU temp (8 refs), `overflow: hidden` gone from html/body (the 2 remaining occurrences are text-ellipsis on `.top-sub` and a progress `.bar` — not page scroll locks), REA "Latest · 2026-11-08" entry with "373 functions decompiled", sports Bengals-only (3 refs, one compact line).
- `server.py` carries v11 markers (`nofallback` ×8, `v11` ×7) — consistent with the README's "byte-identical to v11" claim, which itself is **unverified** (no v11 parcel on file).

## Honest caveats

- **Laptop camera shows COLOR BARS.** The dashboard is fine — the camera itself outputs bars in all modes (driver reload did not fix it). Camera/firmware issue, not a dashboard bug. Thread closed; no dashboard fix.
- **First media call after restart may be slow, then cached.** The real 2,785-file MP4 folder was tested only on a small copy (carried from the v10 caveat).
- **v11 was never published.** v12 is the first published dashboard after v10; the v11 parcel (applied on the Acer 2026-11-07) never reached the publishing house, so the v10→v12 diff cannot be shown file-by-file. The v12 README documents the v11→v12 delta in words.

## How to apply (from the dashboard's own README)

```bash
bash apply-v12.sh
```

Backs up v11 to `~/tonight-scripts/dashboard.bak-v11` (only if that backup does not already exist), copies the four v12 files in (`index.html`, `server.py`, `media-slots.json`, `restart-dashboard-tailnet.sh`), restarts on 0.0.0.0:8899. No sudo. Then open http://100.107.253.109:8899.

## How to roll back to v11

```bash
cp -r ~/tonight-scripts/dashboard.bak-v11/* ~/tonight-scripts/dashboard/
cd ~/tonight-scripts/dashboard
./restart-dashboard-tailnet.sh
```

---
Footer: @basementjarvisu · basementjarvisunleashed@gmail.com
