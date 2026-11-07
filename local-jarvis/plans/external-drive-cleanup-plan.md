# External Drive Cleanup — Project Brief

**Status 2026-11-07: the drive is mounted read-write at `/mnt/hgx`
(since 2026-11-05 ~18:12 ET) and inventoried (TV SHOWS 911G,
FileHistory 450G, WindowsImageBackup 311G, plus one laptop-backup
folder, 559G). The
item-by-item clean-out is its own project, still to do. Nothing deleted
— that stays his call, item by item.**

**HgX, 2026-11-05 ~17:19 ET: a project of its own, after tonight's dashboard.**

## The drive
- 4TB external, label HgX, /mnt/hgx, NTFS (~3.6TB usable), currently unmounted, ~1TB free.
- Holds the Sopranos plus a lot more shows and everything else — TV shows, movies, music, all of it.

## Phase 1 — Inventory (no deletions)
- Mount read-only first. List everything: shows, movies, music, other — names and sizes. Find out what it all is before touching any of it.

## Phase 2 — Decisions (his call, item by item)
- Go through it together: keep, delete, move. **Nothing is deleted without his word on each item** (house rule).
- Mount note: once mounted read-write, the drive behaves like any other folder — delete, run scripts, play media, write backups, all of it works. (The earlier test mount was read-only on purpose; the cleanup mounts read-write.)

## Phase 3 — Organize
- The media home structure (TV shows / movies / music), so the voice commands can find things by name — "VLC on, play the Sopranos" and everything after it.

## Phase 4 — Backups
- Once cleaned, use the freed space for backups too — the drive does double duty: the media, and the safety net underneath it. What to back up is his call (the estate, the Acer, the course work, the media itself?).

## Sequencing
- **FIRST tonight (HgX, 2026-11-05 ~17:22 ET — change of plan): mount the drive read-write as soon as he is home and clean it out before anything else** — before the brains, the camera, the voice loop, and the dashboard. (Supersedes the earlier "after tonight's dashboard" order.)

## Scripts ready (2026-11-05 ~17:40 ET)
- `mount-media-drive.sh` — finds the drive by its label (HgX), mounts read-write at /mnt/hgx. (The earlier test mount was read-only on purpose.)
- `drive-inventory.sh` — read-only listing (top level + biggest folders + total) for the clean-out. Deletes nothing.
