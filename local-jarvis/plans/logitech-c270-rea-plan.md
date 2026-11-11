# Logitech C270 — REA Teardown Plan (end of tonight)

**Status 2026-11-07: the enumeration, first frame and clip are done —
see `local-jarvis/c270/`. The LED verdict: no software switch, the light
is hardwired to streaming state (blink it by starting/stopping the
stream). The physical teardown, the microscope trick and the party
tricks are still his call.**

**HgX, 2026-11-05 ~16:24 ET: "I want to have REA rip it apart... I want to see it use the VRAM, I want to see it use the RAM, or whatever it needs to do, and I want it to do everything."**

Camera: Logitech C270 HD 720p webcam, USB 2.0, USB ID **046d:0825**, UVC 1.00, driver `uvcvideo` (no proprietary driver). Plug into a **USB 2.0 port** — the C270 is known to prefer USB 2.0 over USB 3.0. It also has a built-in microphone and a recording LED.

## What REA will do to it (the teardown)
1. **Enumerate it.** `lsusb -d 046d:0825 -v` (full descriptors), `v4l2-ctl --all`, `--list-formats-ext`, `--list-ctrls`. REA + the 9B explain every interface, endpoint and control: 4 interfaces (video control, video streaming, audio/mic), formats YUYV + MJPG, up to 1280x960 MJPG, 30fps at 640x480.
2. **Watch it talk.** usbmon + Wireshark USB capture: the UVC probe/commit handshake and the MJPEG stream, live. REA interprets the capture — this is the protocol, naked.
3. **Make it work.** First frame + short clip via ffmpeg. The 9B looks at the frame and describes what the camera sees.
4. **Own the LED.** The recording light is a UVC control — map it with uvcdynctrl (Logitech control mapping) and switch it on/off from the command line. The visible "we own it" moment.
5. **Open it up (his call).** Physical teardown: plastic shell off, photograph the board, identify the sensor + controller chips. Feed the photos to the 27B for chip identification. (The camera is cheap and his — no tears if it never goes back together.)
6. **The microscope trick.** The C270 lens unscrews and flips — turned around it becomes a DIY soldering microscope. Macro view of tiny board components. This one stays: a bench microscope for all the REA work to come.

## What he will SEE (the resource show)
A live watch on screen while REA works, so the brains are visible:
- **VRAM:** `watch -n 1 nvidia-smi` — the 9B resident on the card (~5.5GB of 6GB), spiking as REA calls it.
- **RAM:** `htop` / `free -h` — the 27B holding ~18GB of system RAM, waking when a hard question goes through the router.
- **The router:** `tail -f router.log` — every decision, easy→9B / hard→27B, timestamped.
- **Ollama:** `ollama ps` — both models loaded, one generating at a time.
- The 9B does the fast work (descriptors, controls, first frame); the 27B does the heavy work (protocol interpretation, chip ID from photos). That is the whole dual brain, on show.

## The fun things (after the teardown)
- **Bench camera:** mount it over the workbench — photograph/video every teardown, timelapse the Apple TV work.
- **Stream it:** MJPEG stream over the network, watchable from his phone.
- **Motion detection:** `motion` or a small OpenCV script — the bench watches itself.
- **OpenCV playground:** face detection, frame grabs, fun with the live feed.
- **The microscope:** as above — the camera's second life as a bench tool.

## PARTY TRICKS — the full list (HgX, 2026-11-05 ~16:28 ET: "a lot more party tricks, not just on and off")
The C270 has no motors — pan/tilt is software cropping, not physical movement. Everything below is real on Linux with v4l2 + ffmpeg + OpenCV.
### A. The controls playground (v4l2, scripted)
- **Live photo filters from the command line:** drive brightness, contrast, saturation, hue, white balance, gain, exposure, sharpness, backlight compensation — crank saturation for a vivid look, drop exposure for noir, warm/cool the white balance. Every control is a slider we can script.
- **The LED, properly:** on/off AND blinking patterns via the Logitech UVC mapping (LED mode + LED frequency) — including **Morse code on the recording light**.
### B. Software magic (the frame is ours)
- **Virtual PTZ:** crop into the 1280x960 frame and move the crop window — software pan, tilt and zoom, driven by keys or a script. The camera never moves; the picture does.
- **Face tracking:** OpenCV finds a face, draws the box, and the virtual PTZ keeps it centred — a poor-man's tracking camera.
- **Live video effects:** ffmpeg filters on the stream — grayscale, edge-detect, negative, pixelate, mirror. A fun-house stream.
- **Timelapse:** a frame every N seconds, compiled into a video of the bench work.
- **Motion alerts:** motion triggers a snapshot (or a sound) — the bench watches itself.
### C. The phone remote (camera control panel)
- A tiny web page on the Acer with buttons, open on his phone: **Snap photo, LED on/off, zoom in/out, filter, start/stop recording**. The camera answers to his phone.
- **The dashboard eye:** the live bench feed embedded in the Jarvis dashboard.
### D. REA uses (the camera as a tool)
- **Document scanner:** point it down at a board, photograph it, OCR the chip markings with tesseract, feed the text to the 27B — the chip gets identified from a photo.
- **QR/barcode reader:** point a board's QR code at it, decode it.
- **Teardown recorder:** video every Apple TV step with the bench cam.
### E. Hardware mods (advanced, his call)
- **The microscope:** lens unscrews and flips — macro view of tiny components.
- **Infrared:** removing the IR-cut filter makes it see infrared (delicate hardware mod — later, only if he fancies it).

## Honest limits (stated before we start)
- The C270's firmware lives in the camera controller's ROM — there is no DFU/flash interface to dump it the way we dump a TV board's flash chip. The teardown is descriptors + protocol + driver + physical board, not a firmware dump. Everything else above is real.
- The mic is mono, 16kHz — fine for a bench mic, not a studio.
