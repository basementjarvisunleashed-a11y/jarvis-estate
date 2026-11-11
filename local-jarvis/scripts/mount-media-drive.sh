#!/usr/bin/env bash
# mount-media-drive.sh — mount HgX's 4TB external media drive READ-WRITE at /mnt/hgx.
# Finds the drive by its LABEL (HgX), never by a hardcoded /dev name, so it
# cannot grab the wrong disk. The earlier test mount (2026-11-05) was READ-ONLY
# on purpose; tonight we mount read-write so the clean-out can happen.
# Usage: ./mount-media-drive.sh
set -u

LABEL="HgX"
MOUNT="/mnt/hgx"

if mountpoint -q "$MOUNT"; then
  echo "already mounted: $MOUNT"
  mount | grep " $MOUNT "
  df -h "$MOUNT"
  exit 0
fi

DEV=$(lsblk -rno NAME,LABEL | awk -v l="$LABEL" '$2==l {print "/dev/"$1; exit}')
if [ -z "$DEV" ]; then
  echo "STOP: no drive with label '$LABEL' found. Plug it in and try again."
  exit 1
fi
echo "found: $DEV (label $LABEL)"

sudo mkdir -p "$MOUNT"
sudo mount -t ntfs-3g -o rw "$DEV" "$MOUNT" || { echo "mount failed"; exit 1; }
echo "mounted read-write: $DEV -> $MOUNT"
df -h "$MOUNT"
echo "--- top level ---"
ls "$MOUNT" | head -30
