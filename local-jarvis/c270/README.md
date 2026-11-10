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

## The 15-tool breakdown — CLOSED 2026-11-08

All 15 REA tools were run against the C270 (rounds 2–5, 2026-11-07–08).
Ghidra: 373 functions decompiled (373 `.c` files, 0 failed). Live pcap:
6,037 packets / 233 MB, 83.0% isochronous (~16.7 per MJPEG frame),
17.0% interrupt. Frida trace done. ImHex `.hexpat` done. **Verdict:
stock, clean UVC device, no hidden tricks.** (The "98.7% isochronous"
figure from the 2026-11-06 text capture was NOT confirmed by the pcap
— the pcap shows 83.0%.) The consolidated report (31,367 bytes) lives
on the Acer at `~/webcam-15tool-breakdown/consolidated-report.md` — it
was not sent to the publishing house, so it is recorded here and in
`STATE-2026-11-10.md`, not published as a file. The laptop built-in
camera shows color bars in all modes — a camera/firmware fault, not a
dashboard issue; the thread is closed.

**Also on record (in the dashboard):** while a live stream is running,
the server saves its latest frame as `webcam.jpg` (at most once every
30 s); the webcam label reports which camera is actually streaming.
