#!/bin/bash
# apply-brains-autostart.sh — Install the brains autostart and load them now.
# Copies start-brains.sh to ~/Jarvis/autostart/ and brains.desktop to
# ~/.config/autostart/, then starts a background load of both brains.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/Jarvis/autostart" "$HOME/.config/autostart"
cp "$SRC/start-brains.sh" "$HOME/Jarvis/autostart/start-brains.sh"
chmod +x "$HOME/Jarvis/autostart/start-brains.sh"
cp "$SRC/brains.desktop" "$HOME/.config/autostart/brains.desktop"
echo "Installed start-brains.sh and brains.desktop."
echo "Loading the brains now in the background (log: ~/Jarvis/start-brains.log)..."
nohup "$HOME/Jarvis/autostart/start-brains.sh" >/dev/null 2>&1 < /dev/null &
echo "Started. The 9B loads first, then the 27B (a few minutes)."
echo "Check with: ollama ps"
echo "Brains autostart installed. They will load at every login from now on."
