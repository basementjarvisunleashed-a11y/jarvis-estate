#!/bin/bash
# Apply dashboard v12 over the live dashboard (~/tonight-scripts/dashboard/).
# Backs up the current (v11) dashboard to ~/tonight-scripts/dashboard.bak-v11
# (only if that backup does not already exist), copies the v12 files in,
# and restarts the dashboard on 0.0.0.0:8899.
# Run on the Acer from the folder this zip was extracted to:
#   bash apply-v12.sh
# No sudo. No port/host change. Roll back with:
#   cp -r ~/tonight-scripts/dashboard.bak-v11/* ~/tonight-scripts/dashboard/
#   cd ~/tonight-scripts/dashboard && ./restart-dashboard-tailnet.sh
set -e
cd "$(dirname "$0")"
DASH=~/tonight-scripts/dashboard
BAK=~/tonight-scripts/dashboard.bak-v11
if [ -d "$DASH" ]; then
  echo "Dashboard dir found: $DASH"
else
  echo "ERROR: dashboard dir not found at $DASH — nothing to back up or replace."
  exit 1
fi
if [ -d "$BAK" ]; then
  echo "Backup already exists at $BAK — leaving it alone."
else
  echo "Backing up current dashboard to $BAK ..."
  cp -r "$DASH" "$BAK"
  echo "Backup done."
fi
echo "Copying v12 files into $DASH ..."
cp index.html server.py media-slots.json restart-dashboard-tailnet.sh "$DASH/"
chmod +x "$DASH/restart-dashboard-tailnet.sh"
echo "Restarting the dashboard ..."
cd "$DASH"
./restart-dashboard-tailnet.sh
echo "v12 applied."
