#!/bin/bash
cd ~/tonight-scripts/webcam-app-build
nohup ./restart-webcam.sh </dev/null >/tmp/webcam-app-start.log 2>&1 &
