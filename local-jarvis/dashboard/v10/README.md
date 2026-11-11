# Dashboard v10 — provenance

**Applied and LIVE on the Acer 2026-11-07 ~00:45 ET.** v9 backed up on
the Acer as `dashboard.bak-v9`. Original parcel
`dashboard-fixed-2026-11-06-v10.zip`, 59,350 bytes, MD5
`11b4e9ee12b529368aefb0673ec090aa` (5 files). The scrubbed zip on this
page is the same build with the private bits removed (below).

## What changed vs v9

`server.py` only (+104 lines). `index.html`, `media-slots.json`, and
`restart-dashboard-tailnet.sh` are byte-identical to v9 (MD5-verified).

**Two media roots, primary first.** A local folder of 2,785 H.264/AAC
MP4 files (239 GB, 24 shows) is the primary media source for VLC and
in-browser playback. The drive is secondary, only for shows NOT in that
folder — so the Sopranos stays. One entry per show, the MP4 version
wins, no duplicates. `/api/media` now reports the roots and the
per-root sources. Fallback: if the MP4 folder is missing, the drive
alone carries the list — never empty, never a crash. Cached scan +
ffprobe + Recent + pinned + all v9 visuals unchanged.

**Caveat, honestly:** the real 2,785-file folder was tested only on a
small copy. The first media call after restart may be slow, then
cached.

## Verification (REA room, before sending)

MD5, py_compile, markers, **38/38 API, 36/36 layout twice**, fallback
tested, zip verification clean. Publishing house re-verified: parcel
MD5 matches, `index.html` / `media-slots.json` / restart script
byte-identical to v9, scrubbed `server.py` compiles clean.

## Scrub (publishing house)

- The exact local path of the MP4 folder → `/path/to/ipad-pro-mp4-folder`
  (4 spots: docstring, comment, and the `IPAD_MP4_DIR` default in
  `server.py`; 1 spot in `README-FIRST.txt`). Set `IPAD_MP4_DIR` to
  your own folder, or leave the placeholder — the drive fallback means
  the dashboard still runs.
- One laptop name in `SKIP_DIRS` (`server.py`) → `ownerlaptop` (same
  scrub as v7/v8/v9).
- Final identity/path grep over all five files: 0 hits.

## Files

| File | Notes |
|---|---|
| `server.py` | Scrubbed (see above). MD5 `e20e1810d1443174a3111e24bce4edbb`. |
| `index.html` | Byte-identical to v9. |
| `README-FIRST.txt` | Scrubbed (path only). |
| `media-slots.json` | Byte-identical to v9. |
| `restart-dashboard-tailnet.sh` | Byte-identical to v9. |
| `dashboard-fixed-2026-11-06-v10-scrubbed.zip` | All five scrubbed files (uploaded via the GitHub web UI). |

---

@basementjarvisu · basementjarvisunleashed@gmail.com
