# Logitech C270 — REA capture (2026-11-05/06)

The C270 webcam, enumerated and captured on the Acer. The camera is the
dashboard's secondary camera (the laptop built-in is primary) and one of
the voice loop's four mics.

**Camera facts (from the captures):** USB `046d:0825`, `/dev/video2`
(+ `/dev/video3` metadata, `/dev/media1`); laptop built-in is
`/dev/video0`. MJPG 1280×720 and 1280×960 both at 30 fps; YUYV 7.5 fps
at 720p/960p, 30 fps only at 640×480 and below. LED: no software switch
— hardwired to streaming state.

**Files:**

| File | What it is |
|---|---|
| `c270-descriptors.txt` | USB descriptors (1,456 lines). |
| `c270-usbmon.txt` | usbmon capture of the camera traffic. |
| `c270-9b-summary.txt` | The 9B model's summary of the descriptor chunks (interfaces, endpoints, formats, resolutions, frame rates, controls). |
| `c270-rainbow.mp4` | 3-second 720p test clip — pure colour bars, no room, no people. (Binary: uploaded via the GitHub web UI, same as the dashboard zip.) |

**Also on record (in the dashboard):** while a live stream is running,
the server saves its latest frame as `webcam.jpg` (at most once every
30 s); the webcam label reports which camera is actually streaming.
