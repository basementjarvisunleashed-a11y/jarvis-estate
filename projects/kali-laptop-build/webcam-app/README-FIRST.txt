J.A.R.V.I.S. WEBCAM APP — README FIRST
=====================================
A standalone webcam app + dashboard for the Acer: BOTH cameras live at
once. The Logitech C270 is the MAIN (prominent) feed; the laptop
built-in is #2 (secondary), because the laptop lid might be closed.
If the lid is closed its feed is dark — the app flags that instead of
pretending it is fine. The laptop camera is the fallback when the C270
is absent (then only the laptop feed shows). This priority is for THIS
app only — it does not change the dashboard's or the voice loop's
camera priority.

WHAT IT DOES
------------
- Dual live MJPEG feeds, side by side: C270 main (large), laptop #2
  (smaller). Click Focus on either pane to make it the main one.
- Snapshot per camera (dated JPEG in ~/Pictures/webcam/).
- Record per camera (start/stop, dated .mp4 in ~/Pictures/webcam/).
- v4l2 picture controls (brightness, contrast, saturation, gain,
  sharpness, white-balance auto) with a Reset to defaults button.
- Camera status dashboard: live/standby/dark/unavailable, resolution,
  format, measured fps, uptime, recording state, snapshot/recording
  counts, and a recent-captures gallery (thumbnails — click to view).
- One screen at 1920x1080; stacked and scrollable on a phone.
- Graceful degradation: a missing camera, a missing ffmpeg, or a
  missing v4l2-ctl is reported honestly ("unavailable") — never a crash.

FILES (4)
----------
  webcam.html            the app + dashboard page (dark, cyan glow)
  server.py              the server (stdlib only, port 8898)
  restart-webcam.sh      restart it bound to all interfaces (tailnet)
  README-FIRST.txt       this file

INSTALL ON THE ACER (run the apply paste below)
------------------------------------------------
The app needs ffmpeg and v4l2-ctl on the Acer (both are already
there: ffmpeg was used for the C270 rainbow video, v4l2-ctl for the
filter test). No other dependency. Port 8898 must be free.

AFTER INSTALL, OPEN IT
----------------------
  On the laptop:  http://127.0.0.1:8898
  On the tailnet (iPhone/iPad):  http://<acer-tailnet-ip>:8898
  (the restart script prints the tailnet URL)

WHERE THINGS GO
---------------
  Snapshots:   ~/Pictures/webcam/webcam-<cam>-YYYY-MM-DD-HHMMSS.jpg
  Recordings:  ~/Pictures/webcam/webcam-<cam>-YYYY-MM-DD-HHMMSS.mp4
  Server log:  <app-dir>/webcam.log
  (Snapshots and recordings are the same dated naming the dashboard
  and the C270 work already use in ~/Pictures/webcam/.)

API (for the curious)
--------------------
  GET  /api/status              cameras, recording, counts
  GET  /api/stream?cam=c270|laptop   live MJPEG (one per camera)
  POST /api/snapshot  {cam}     save a dated JPEG
  POST /api/record/start {cam}  start recording
  POST /api/record/stop  {cam}  stop recording
  GET  /api/controls?cam=...    v4l2 values
  POST /api/controls {cam, values:{...}}   apply v4l2 controls
  POST /api/controls/reset {cam}           reset to defaults
  GET  /api/gallery            recent snapshots + recordings
  GET  /api/file?name=...      serve a snapshot/recording

VERIFIED (before shipping)
--------------------------
  py_compile clean; page JS clean (node --check).
  API regression (fake cameras): both streams serving at once,
  snapshot + record per camera, controls get/set/reset, gallery,
  no-camera degradation (503 + honest "unavailable", page still loads).
  Layout (headless Chromium): 1920x1080 one screen, dual feeds
  visible, C270 main larger than laptop, no horizontal scroll,
  no page errors; 390 px stacked, no horizontal scroll.
  Still unverified without the Acer: real cameras, real v4l2
  controls, real snapshot/record files, the dark-lid flag on a
  genuinely closed lid.
