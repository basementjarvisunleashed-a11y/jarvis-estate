#!/usr/bin/env python3
"""Jarvis webcam app server — stdlib only, no dependencies.

A standalone webcam app + dashboard for the Acer: BOTH cameras live at
once, side by side. The Logitech C270 is the MAIN (prominent) feed and
the laptop built-in is #2 (secondary) — because the laptop lid might be
closed, which would block the built-in camera. If the lid is closed its
feed is dark; the page flags that instead of pretending it is fine.
The laptop camera is still the fallback when the C270 is absent (then
only the laptop feed shows). This priority is for THIS app only — it
does not change the dashboard's or the voice loop's camera priority.

Serves the webcam page and a JSON API on 127.0.0.1:8898.

Endpoints:
  GET  /                        webcam page (webcam.html)
  GET  /api/status              cameras (state, fps, uptime, device,
                               resolution, format), recording state,
                               snapshot/recording counts
  GET  /api/stream?cam=c270|laptop
                               live MJPEG multipart stream, one per
                               camera. Each pane is its own camera —
                               NO cross-camera fallback here (unlike
                               the dashboard): if a camera fails, its
                               pane shows "unavailable" while the
                               other keeps going.
  POST /api/snapshot  {cam}     save the latest frame as a dated JPEG
                               in ~/Pictures/webcam/
  POST /api/record/start {cam}  start recording that camera to a dated
                               .mp4 in ~/Pictures/webcam/
  POST /api/record/stop  {cam}  stop recording, return file + duration
  GET  /api/controls?cam=...    current v4l2 control values
  POST /api/controls {cam, values:{...}}
                               apply v4l2 controls
  POST /api/controls/reset {cam}
                               reset v4l2 controls to the known defaults
  GET  /api/gallery            recent snapshots + recordings (newest
                               first), with counts
  GET  /api/file?name=...      serve a snapshot/recording file (Range
                               support for video)

Recording taps the live grabber's frames (one device open, no second
v4l2 open to fight over): a feeder thread pipes the JPEG frames to
ffmpeg image2pipe -> libx264 mp4. The recorder holds a grabber client
so the camera stays live while recording.

Every collector degrades gracefully: a missing camera, a missing
ffmpeg, a missing v4l2-ctl, or a dark lid-closed feed is reported
honestly ("unavailable" / "dark") instead of breaking the page.

Run on the Acer:  python3 server.py
Then open http://127.0.0.1:8898 in a browser.

Env vars (all optional):
  WEBCAM_HOST      interface to bind (default 127.0.0.1; 0.0.0.0 for tailnet)
  WEBCAM_PORT      port to listen on (default 8898)
  WEBCAM_CMD       ffmpeg binary for the live streams (default ffmpeg)
  RECORD_CMD       ffmpeg binary for recording (default ffmpeg)
  V4L2_CMD         v4l2-ctl binary (default v4l2-ctl)
  WEBCAM_PICTURES_DIR  where snapshots + recordings go
                   (default ~/Pictures/webcam)
  WEBCAM_DEV_C270  C270 device (default /dev/video2)
  WEBCAM_DEV_LAPTOP laptop camera device (default /dev/video0)
"""

import json
import os
import re
import shutil
import signal
import socket
import subprocess
import threading
import time
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

try:
    from zoneinfo import ZoneInfo
    TORONTO = ZoneInfo("America/Toronto")
except Exception:  # pragma: no cover - tzdata missing
    TORONTO = None

HOST = os.environ.get("WEBCAM_HOST", "127.0.0.1")
PORT = int(os.environ.get("WEBCAM_PORT", "8898"))
BASE = Path(__file__).resolve().parent
PICTURES_DIR = Path(os.environ.get(
    "WEBCAM_PICTURES_DIR", str(Path.home() / "Pictures" / "webcam")))
WEBCAM_CMD = os.environ.get("WEBCAM_CMD", "ffmpeg")
RECORD_CMD = os.environ.get("RECORD_CMD", "ffmpeg")
V4L2_CMD = os.environ.get("V4L2_CMD", "v4l2-ctl")

# The C270 is the MAIN camera in this app; the laptop built-in is #2.
# (App-only priority — the dashboard and the voice loop keep their own.)
WEBCAM_CAMS = {
    "c270": os.environ.get("WEBCAM_DEV_C270", "/dev/video2"),
    "laptop": os.environ.get("WEBCAM_DEV_LAPTOP", "/dev/video0"),
}
WEBCAM_LABELS = {
    "c270": "Logitech C270",
    "laptop": "Laptop built-in",
}
WEBCAM_ORDER = ("c270", "laptop")  # main first
CAPTURE_SIZE = "640x480"
CAPTURE_FPS = 10
WEBCAM_IDLE_STOP_S = 10   # stop ffmpeg after this long with no clients
WEBCAM_START_WAIT_S = 2.5  # wait this long for the first frame at startup
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"
GALLERY_MAX = 24

# C270 v4l2 controls (from the 2026-11-06 REA read): brightness 128,
# contrast 32, saturation 32, gain 64, sharpness 24, white-balance
# auto on. These are the reset defaults for the C270; the laptop
# camera gets the same reset only for the controls it actually has.
V4L2_DEFAULTS = {
    "brightness": 128,
    "contrast": 32,
    "saturation": 32,
    "gain": 64,
    "sharpness": 24,
    "white_balance_temperature_auto": 1,
}
V4L2_SLIDERS = ("brightness", "contrast", "saturation", "gain", "sharpness")


def now():
    if TORONTO is not None:
        return datetime.now(TORONTO)
    return datetime.now(timezone.utc).astimezone()


def run(cmd, timeout=3):
    """Run a command, return its stdout stripped, or '' on any failure."""
    try:
        out = subprocess.run(cmd, capture_output=True, timeout=timeout)
        if out.returncode != 0:
            return ""
        return out.stdout.decode("utf-8", "replace").strip()
    except Exception:
        return ""


def run_full(cmd, timeout=5):
    """Run a command, return (returncode, stdout, stderr)."""
    try:
        out = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return (out.returncode,
                out.stdout.decode("utf-8", "replace"),
                out.stderr.decode("utf-8", "replace"))
    except Exception as exc:
        return (-1, "", str(exc))


# ---------------------------------------------------------------- grabbers
# One ffmpeg MJPEG grabber per camera (adapted from the dashboard's
# WebcamGrabber, which already runs one grabber per camera — so both
# cameras can stream at the same time, independently). The grabber
# starts on the first client and stops ~10 s after the last client
# leaves, so a camera (and its LED) is not left on when nobody is
# watching. WEBCAM_CMD overrides the ffmpeg binary — a test hook only.
class WebcamGrabber:
    """One ffmpeg MJPEG grabber per camera."""

    def __init__(self, key, device):
        self.key = key
        self.device = device
        self._lock = threading.Lock()          # state: proc/clients/failed
        self._start_lock = threading.Lock()    # serializes (re)starts
        self._cond = threading.Condition()     # new-frame notification
        self._proc = None
        self._reader = None
        self._latest = None                    # (bytes, timestamp)
        self._failed = None                    # error string once both attempts failed
        self._clients = 0
        self._last_use = 0.0
        self._first_start = None               # when this camera first streamed
        self._frame_ts = deque(maxlen=64)      # recent frame timestamps (fps)

    def _spawn(self, with_mjpeg):
        cmd = [WEBCAM_CMD]
        if with_mjpeg:
            cmd += ["-f", "v4l2", "-input_format", "mjpeg"]
        else:
            cmd += ["-f", "v4l2"]
        cmd += ["-video_size", CAPTURE_SIZE, "-framerate", str(CAPTURE_FPS),
                "-i", self.device, "-f", "mjpeg", "-q:v", "5", "-"]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL,
                                stdin=subprocess.DEVNULL)

    def _reader_loop(self, proc):
        buf = bytearray()
        read1 = getattr(proc.stdout, "read1", None)
        try:
            while True:
                chunk = read1(65536) if read1 is not None else proc.stdout.read(65536)
                if not chunk:
                    break
                buf += chunk
                while True:
                    start = buf.find(JPEG_SOI)
                    if start < 0:
                        if len(buf) > 1:
                            del buf[:-1]
                        break
                    end = buf.find(JPEG_EOI, start + 2)
                    if end < 0:
                        if start > 0:
                            del buf[:start]
                        break
                    frame = bytes(buf[start:end + 2])
                    del buf[:end + 2]
                    with self._cond:
                        self._latest = (frame, time.time())
                        self._frame_ts.append(time.time())
                        self._cond.notify_all()
        except Exception:
            pass
        finally:
            with self._cond:
                self._cond.notify_all()

    def _try_start(self):
        """Start ffmpeg; try MJPEG input first, plain v4l2 second.
        Returns (ok, error)."""
        last_err = "webcam failed to start"
        for with_mjpeg in (True, False):
            try:
                proc = self._spawn(with_mjpeg)
            except Exception as exc:
                last_err = "cannot start %s: %s" % (WEBCAM_CMD, exc)
                continue
            self._proc = proc
            self._reader = threading.Thread(target=self._reader_loop,
                                            args=(proc,), daemon=True)
            self._reader.start()
            deadline = time.time() + WEBCAM_START_WAIT_S
            ok = False
            while time.time() < deadline:
                if proc.poll() is not None:
                    break  # exited before producing a frame
                with self._cond:
                    if self._latest is not None:
                        ok = True
                        break
                time.sleep(0.05)
            if ok:
                if self._first_start is None:
                    self._first_start = time.time()
                return True, None
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            self._proc = None
            last_err = "no frames from %s" % self.device
        return False, last_err

    def acquire(self):
        """A client arrived. Returns (ok, error). Starts ffmpeg on first use
        (or restarts it if it died)."""
        with self._start_lock:
            with self._lock:
                self._clients += 1
                self._last_use = time.time()
                if self._proc is not None and self._proc.poll() is None:
                    return True, None
                self._failed = None
                self._latest = None
            ok, err = self._try_start()
            with self._lock:
                if not ok:
                    self._failed = err or "webcam failed to start"
                    self._clients -= 1  # this client never got a stream
                    return False, self._failed
                return True, None

    def release(self):
        with self._lock:
            self._clients = max(0, self._clients - 1)
            self._last_use = time.time()

    def latest(self):
        with self._cond:
            return self._latest

    def wait_frame(self, last_ts, timeout):
        with self._cond:
            return self._cond.wait_for(
                lambda: self._latest is not None and self._latest[1] > last_ts,
                timeout=timeout)

    def is_dead(self):
        with self._lock:
            return self._proc is None or self._proc.poll() is not None

    def is_streaming(self):
        """True when a client is watching this camera right now AND
        frames are actually flowing."""
        with self._lock:
            return (self._clients > 0 and self._proc is not None
                    and self._proc.poll() is None
                    and self._latest is not None)

    def fps(self):
        """Measured frames per second over the last ~2 seconds."""
        now_t = time.time()
        with self._cond:
            recent = [t for t in self._frame_ts if now_t - t <= 2.0]
        return round(len(recent) / 2.0, 1) if recent else 0.0

    def uptime_s(self):
        if self._first_start is None:
            return 0
        return int(time.time() - self._first_start)

    def maybe_stop_idle(self, now):
        with self._lock:
            if self._clients > 0 or self._proc is None:
                return
            if now - self._last_use < WEBCAM_IDLE_STOP_S:
                return
            proc = self._proc
            self._proc = None
            self._latest = None
            self._failed = None
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=2)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


_webcam_grabbers = {}
_webcam_lock = threading.Lock()
_webcam_reaper_started = False


def _webcam_reaper():
    while True:
        time.sleep(1)
        now_t = time.time()
        with _webcam_lock:
            grabbers = list(_webcam_grabbers.values())
        for g in grabbers:
            g.maybe_stop_idle(now_t)


def get_webcam_grabber(key):
    global _webcam_reaper_started
    with _webcam_lock:
        g = _webcam_grabbers.get(key)
        if g is None:
            g = WebcamGrabber(key, WEBCAM_CAMS[key])
            _webcam_grabbers[key] = g
            if not _webcam_reaper_started:
                _webcam_reaper_started = True
                threading.Thread(target=_webcam_reaper, daemon=True).start()
        return g


def collect_cameras():
    """Both cameras, C270 main first (this app's priority only)."""
    out = []
    for key in WEBCAM_ORDER:
        dev = WEBCAM_CAMS[key]
        g = _webcam_grabbers.get(key)
        streaming = bool(g and g.is_streaming())
        present = os.path.exists(dev)
        state = "live" if streaming else ("standby" if present else "unavailable")
        out.append({
            "key": key,
            "name": WEBCAM_LABELS[key],
            "device": dev,
            "priority": "main" if key == "c270" else "secondary",
            "present": present,
            "streaming": streaming,
            "state": state,
            "state_label": (("live — " + WEBCAM_LABELS[key]) if streaming
                            else ("standby — live when viewed" if present
                                  else "not connected")),
            "resolution": CAPTURE_SIZE,
            "format": "MJPEG",
            "fps": g.fps() if g else 0.0,
            "uptime_s": g.uptime_s() if g else 0,
        })
    return out


# ---------------------------------------------------------------- recorder
# Records by tapping the live grabber's frames: one device open, no
# second v4l2 open to fight over. A feeder thread pipes the JPEG
# frames to ffmpeg image2pipe -> libx264 mp4. The recorder holds a
# grabber client so the camera stays live while recording.
class Recorder:
    def __init__(self, key):
        self.key = key
        self._lock = threading.Lock()
        self._proc = None
        self._feeder = None
        self._stop = threading.Event()
        self._grabber = None
        self._file = None
        self._started = None
        self._frames = 0

    def is_recording(self):
        with self._lock:
            return self._proc is not None and self._proc.poll() is None

    def info(self):
        with self._lock:
            if self._proc is None:
                return {"recording": False, "file": None, "started": None,
                        "duration_s": 0, "frames": 0}
            return {"recording": self._proc.poll() is None,
                    "file": self._file.name if self._file else None,
                    "started": self._started,
                    "duration_s": int(time.time() - self._started) if self._started else 0,
                    "frames": self._frames}

    def _feeder_loop(self, proc, grabber):
        last_ts = 0.0
        try:
            while not self._stop.is_set():
                grabber.wait_frame(last_ts, timeout=0.2)
                cur = grabber.latest()
                if cur is None:
                    if grabber.is_dead():
                        break
                    continue
                frame, ts = cur
                if ts <= last_ts:
                    continue
                last_ts = ts
                try:
                    proc.stdin.write(frame)
                    proc.stdin.flush()
                except (BrokenPipeError, ValueError):
                    break
                with self._lock:
                    self._frames += 1
        except Exception:
            pass

    def start(self):
        """Start recording. Returns (ok, info-or-error)."""
        with self._lock:
            if self._proc is not None and self._proc.poll() is None:
                return False, "already recording %s" % self.key
        grabber = get_webcam_grabber(self.key)
        ok, err = grabber.acquire()
        if not ok:
            return False, err or "camera unavailable"
        PICTURES_DIR.mkdir(parents=True, exist_ok=True)
        stamp = now().strftime("%Y-%m-%d-%H%M%S")
        fname = "webcam-%s-%s.mp4" % (self.key, stamp)
        out = PICTURES_DIR / fname
        cmd = [RECORD_CMD, "-y", "-f", "image2pipe", "-framerate",
               str(CAPTURE_FPS), "-c:v", "mjpeg", "-i", "-",
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r",
               str(CAPTURE_FPS), str(out)]
        try:
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
        except Exception as exc:
            grabber.release()
            return False, "cannot start %s: %s" % (RECORD_CMD, exc)
        self._stop.clear()
        self._grabber = grabber
        self._proc = proc
        self._file = out
        self._started = time.time()
        self._frames = 0
        self._feeder = threading.Thread(target=self._feeder_loop,
                                        args=(proc, grabber), daemon=True)
        self._feeder.start()
        # Give ffmpeg a moment to fail fast (bad input, no encoder).
        time.sleep(0.5)
        if proc.poll() is not None:
            self._stop.set()
            grabber.release()
            self._proc = None
            return False, "recorder exited immediately (encoder missing?)"
        return True, {"file": fname, "started": self._started}

    def stop(self):
        """Stop recording. Returns (ok, info-or-error)."""
        with self._lock:
            proc = self._proc
            grabber = self._grabber
            fname = self._file.name if self._file else None
            started = self._started
            frames = self._frames
            if proc is None:
                return False, "not recording %s" % self.key
            self._proc = None
            self._file = None
            self._started = None
        self._stop.set()
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.wait(timeout=10)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        if self._feeder is not None:
            self._feeder.join(timeout=3)
        if grabber is not None:
            grabber.release()
        size = 0
        if fname:
            try:
                size = (PICTURES_DIR / fname).stat().st_size
            except Exception:
                size = 0
        return True, {"file": fname, "duration_s": int(time.time() - started) if started else 0,
                      "frames": frames, "size": size}


_recorders = {}


def get_recorder(key):
    with _webcam_lock:
        r = _recorders.get(key)
        if r is None:
            r = Recorder(key)
            _recorders[key] = r
        return r


# ---------------------------------------------------------------- v4l2
def _v4l2_available(device):
    # V4L2_CMD is usually "v4l2-ctl" on PATH; it may also be an
    # explicit script path (tests override it), so accept either.
    if shutil.which(V4L2_CMD) is None and not (
            os.path.isfile(V4L2_CMD) and os.access(V4L2_CMD, os.X_OK)):
        return False, "v4l2-ctl not installed"
    if not os.path.exists(device):
        return False, "camera not connected (%s)" % device
    return True, None


def v4l2_list(device):
    """Current v4l2 controls for a camera. Returns
    {available, device, controls:{name:{min,max,step,default,value,type}}, error}."""
    ok, err = _v4l2_available(device)
    if not ok:
        return {"available": False, "device": device, "controls": {}, "error": err}
    rc, out, _err = run_full([V4L2_CMD, "-d", device, "--list-ctrls"], timeout=5)
    if rc != 0 or not out.strip():
        return {"available": False, "device": device, "controls": {},
                "error": "v4l2-ctl could not list controls for %s" % device}
    controls = {}
    # e.g. "brightness 0x00980900 (int) : min=0 max=255 step=1 default=128 value=128"
    #      "white_balance_temperature_auto 0x0098090c (bool) : default=1 value=1"
    pat = re.compile(r"^(\w+)\s+0x[0-9a-f]+\s+\((\w+)\)\s*:\s*(.*)$")
    for line in out.splitlines():
        line = line.strip()
        m = pat.match(line)
        if not m:
            continue
        name, ctype, rest = m.groups()
        fields = {}
        for kv in re.finditer(r"(\w+)=(-?\d+)", rest):
            fields[kv.group(1)] = int(kv.group(2))
        controls[name] = {
            "type": ctype,
            "min": fields.get("min"),
            "max": fields.get("max"),
            "step": fields.get("step"),
            "default": fields.get("default"),
            "value": fields.get("value", fields.get("default")),
        }
    return {"available": True, "device": device, "controls": controls, "error": None}


def v4l2_set(device, values):
    """Apply {name: value} via v4l2-ctl. Returns (ok, applied-or-error)."""
    ok, err = _v4l2_available(device)
    if not ok:
        return False, err
    # Only set integer-valued controls we can name; reject anything else.
    pairs = []
    for name, val in values.items():
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name or ""):
            return False, "bad control name: %r" % (name,)
        try:
            pairs.append("%s=%d" % (name, int(val)))
        except Exception:
            return False, "bad value for %s: %r" % (name, val)
    if not pairs:
        return False, "no controls given"
    rc, _out, err_txt = run_full([V4L2_CMD, "-d", device, "--set-ctrl",
                                  ",".join(pairs)], timeout=5)
    if rc != 0:
        return False, (err_txt.strip() or "v4l2-ctl --set-ctrl failed")
    return True, {p.split("=", 1)[0]: int(p.split("=", 1)[1]) for p in pairs}


# ---------------------------------------------------------------- snapshots / gallery
def take_snapshot(key):
    """Save the camera's latest frame as a dated JPEG.
    Returns (ok, info-or-error)."""
    grabber = get_webcam_grabber(key)
    ok, err = grabber.acquire()
    if not ok:
        return False, err or "camera unavailable"
    try:
        # Wait briefly for a fresh frame (the grabber may have just started).
        grabber.wait_frame(0.0, timeout=2.0)
        cur = grabber.latest()
        if cur is None:
            return False, "no frame from %s" % WEBCAM_LABELS[key]
        frame, _ts = cur
        PICTURES_DIR.mkdir(parents=True, exist_ok=True)
        stamp = now().strftime("%Y-%m-%d-%H%M%S")
        fname = "webcam-%s-%s.jpg" % (key, stamp)
        out = PICTURES_DIR / fname
        tmp = out.with_suffix(".jpg.tmp")
        tmp.write_bytes(frame)
        os.replace(tmp, out)
        return True, {"file": fname, "url": "/api/file?name=" + fname,
                      "size": out.stat().st_size}
    finally:
        grabber.release()


def list_gallery():
    """Recent snapshots + recordings in ~/Pictures/webcam/, newest first."""
    files = []
    try:
        PICTURES_DIR.mkdir(parents=True, exist_ok=True)
        entries = list(PICTURES_DIR.iterdir())
    except Exception:
        entries = []
    for p in entries:
        name = p.name
        if not (name.startswith("webcam-") and
                (name.endswith(".jpg") or name.endswith(".mp4"))):
            continue
        try:
            st = p.stat()
        except Exception:
            continue
        kind = "snapshot" if name.endswith(".jpg") else "recording"
        cam = "c270" if "-c270-" in name else ("laptop" if "-laptop-" in name else None)
        files.append({"name": name, "kind": kind, "cam": cam,
                      "size": st.st_size, "mtime": st.st_mtime,
                      "url": "/api/file?name=" + name})
    files.sort(key=lambda f: f["mtime"], reverse=True)
    snaps = sum(1 for f in files if f["kind"] == "snapshot")
    recs = sum(1 for f in files if f["kind"] == "recording")
    return {"files": files[:GALLERY_MAX], "total": len(files),
            "snapshots": snaps, "recordings": recs}


# ---------------------------------------------------------------- HTTP
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # keep the console quiet
        pass

    def _send(self, status, body, content_type):
        if isinstance(body, str):
            body = body.encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_json(self, status, obj):
        try:
            payload = json.dumps(obj).encode("utf-8")
        except Exception:
            payload = b"{}"
        self._send(status, payload, "application/json")

    def _send_file(self, path):
        """Serve a file, with HTTP Range support (206) for video."""
        try:
            size = path.stat().st_size
        except Exception:
            self._send(404, "file not found", "text/plain")
            return
        ctype = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                 ".png": "image/png", ".mp4": "video/mp4"}.get(
                     path.suffix.lower(), "application/octet-stream")
        range_hdr = (self.headers.get("Range") or "").strip()
        start, end = 0, size - 1
        status = 200
        if range_hdr:
            m = re.match(r"bytes=(\d*)-(\d*)$", range_hdr)
            if not m:
                self.send_response(416)
                self.send_header("Content-Range", "bytes */%d" % size)
                self.end_headers()
                return
            start_s, end_s = m.groups()
            if start_s == "" and end_s == "":
                self.send_response(416)
                self.send_header("Content-Range", "bytes */%d" % size)
                self.end_headers()
                return
            if start_s == "":
                start = max(size - int(end_s), 0)
            else:
                start = int(start_s)
                end = int(end_s) if end_s != "" else size - 1
            if start >= size or end < start:
                self.send_response(416)
                self.send_header("Content-Range", "bytes */%d" % size)
                self.end_headers()
                return
            end = min(end, size - 1)
            status = 206
        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(length))
        self.end_headers()
        try:
            with open(path, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except Exception:
            return None
        try:
            raw = self.rfile.read(length) if length > 0 else b""
            return json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            return None

    def _serve_stream(self, cam):
        """GET /api/stream — live MJPEG multipart for ONE camera.
        No cross-camera fallback: each pane is its own camera. If
        this camera fails, its pane shows "unavailable" while the
        other keeps going."""
        if cam not in WEBCAM_CAMS:
            cam = "c270"
        grabber = get_webcam_grabber(cam)
        ok, err = grabber.acquire()
        if not ok:
            self._send_json(503, {"error": err or "webcam unavailable",
                                  "cam": cam})
            return
        try:
            self.send_response(200)
            self.send_header("Content-Type",
                             "multipart/x-mixed-replace; boundary=frame")
            self.send_header("X-Webcam-Device", WEBCAM_CAMS[cam])
            self.send_header("X-Webcam-Cam", cam)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            last_ts = 0.0
            last_sent_at = 0.0
            have_frame = False
            while True:
                grabber.wait_frame(last_ts, timeout=0.1)
                cur = grabber.latest()
                if cur is None:
                    break
                frame, ts = cur
                now_t = time.time()
                if ts > last_ts or (have_frame and now_t - last_sent_at > 2.0):
                    part = (b"--frame\r\nContent-Type: image/jpeg\r\n"
                            b"Content-Length: %d\r\n\r\n" % len(frame)) + frame + b"\r\n"
                    try:
                        self.wfile.write(part)
                        self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        break
                    last_ts = ts
                    have_frame = True
                    last_sent_at = now_t
                if grabber.is_dead():
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            grabber.release()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        try:
            if path in ("/", "/index.html", "/webcam.html"):
                page = BASE / "webcam.html"
                if page.is_file():
                    self._send(200, page.read_bytes(), "text/html; charset=utf-8")
                else:
                    self._send(500, "webcam.html not found next to server.py",
                               "text/plain")
            elif path == "/api/status":
                cams = collect_cameras()
                rec = {k: get_recorder(k).info() for k in WEBCAM_ORDER}
                gal = list_gallery()
                any_live = any(c["streaming"] for c in cams)
                self._send_json(200, {
                    "time": now().isoformat(),
                    "cameras": cams,
                    "recording": rec,
                    "counts": {"snapshots": gal["snapshots"],
                               "recordings": gal["recordings"],
                               "total": gal["total"]},
                    "any_live": any_live,
                    "pictures_dir": str(PICTURES_DIR),
                })
            elif path == "/api/stream":
                cam = (query.get("cam") or ["c270"])[0]
                self._serve_stream(cam)
            elif path == "/api/controls":
                cam = (query.get("cam") or ["c270"])[0]
                if cam not in WEBCAM_CAMS:
                    cam = "c270"
                self._send_json(200, v4l2_list(WEBCAM_CAMS[cam]))
            elif path == "/api/gallery":
                self._send_json(200, list_gallery())
            elif path == "/api/file":
                name = (query.get("name") or [""])[0]
                # Only plain filenames from the pictures dir — no paths.
                if (not name or "/" in name or "\\" in name or ".." in name
                        or not (name.startswith("webcam-") and
                                (name.endswith(".jpg") or name.endswith(".mp4")))):
                    self._send(400, "bad file name", "text/plain")
                    return
                self._send_file(PICTURES_DIR / name)
            else:
                self._send(404, "not found", "text/plain")
        except Exception as exc:  # never crash the app
            try:
                self._send_json(500, {"error": str(exc)})
            except Exception:
                pass

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()
        if body is None:
            self._send_json(400, {"error": "bad JSON body"})
            return
        try:
            if path == "/api/snapshot":
                cam = body.get("cam") or "c270"
                if cam not in WEBCAM_CAMS:
                    self._send_json(400, {"error": "unknown camera: %s" % cam})
                    return
                ok, info = take_snapshot(cam)
                if ok:
                    self._send_json(200, {"ok": True, "cam": cam, **info})
                else:
                    self._send_json(503, {"ok": False, "error": info, "cam": cam})
            elif path == "/api/record/start":
                cam = body.get("cam") or "c270"
                if cam not in WEBCAM_CAMS:
                    self._send_json(400, {"error": "unknown camera: %s" % cam})
                    return
                rec = get_recorder(cam)
                if rec.is_recording():
                    self._send_json(409, {"ok": False,
                                          "error": "already recording %s" % cam})
                    return
                ok, info = rec.start()
                if ok:
                    self._send_json(200, {"ok": True, "cam": cam, **info})
                else:
                    self._send_json(503, {"ok": False, "error": info, "cam": cam})
            elif path == "/api/record/stop":
                cam = body.get("cam") or "c270"
                if cam not in WEBCAM_CAMS:
                    self._send_json(400, {"error": "unknown camera: %s" % cam})
                    return
                rec = get_recorder(cam)
                if not rec.is_recording():
                    self._send_json(409, {"ok": False,
                                          "error": "not recording %s" % cam})
                    return
                ok, info = rec.stop()
                if ok:
                    self._send_json(200, {"ok": True, "cam": cam, **info})
                else:
                    self._send_json(503, {"ok": False, "error": info, "cam": cam})
            elif path == "/api/controls":
                cam = body.get("cam") or "c270"
                if cam not in WEBCAM_CAMS:
                    self._send_json(400, {"error": "unknown camera: %s" % cam})
                    return
                values = body.get("values") or {}
                if not isinstance(values, dict) or not values:
                    self._send_json(400, {"error": "no values given"})
                    return
                ok, applied = v4l2_set(WEBCAM_CAMS[cam], values)
                if ok:
                    self._send_json(200, {"ok": True, "cam": cam, "applied": applied})
                else:
                    self._send_json(503, {"ok": False, "error": applied, "cam": cam})
            elif path == "/api/controls/reset":
                cam = body.get("cam") or "c270"
                if cam not in WEBCAM_CAMS:
                    self._send_json(400, {"error": "unknown camera: %s" % cam})
                    return
                listed = v4l2_list(WEBCAM_CAMS[cam])
                if not listed.get("available"):
                    self._send_json(503, {"ok": False,
                                          "error": listed.get("error"), "cam": cam})
                    return
                have = listed["controls"]
                values = {n: v for n, v in V4L2_DEFAULTS.items() if n in have}
                if not values:
                    self._send_json(503, {"ok": False,
                                          "error": "no known controls on this camera",
                                          "cam": cam})
                    return
                ok, applied = v4l2_set(WEBCAM_CAMS[cam], values)
                if ok:
                    self._send_json(200, {"ok": True, "cam": cam, "applied": applied})
                else:
                    self._send_json(503, {"ok": False, "error": applied, "cam": cam})
            else:
                self._send_json(404, {"error": "not found"})
        except Exception as exc:  # never crash the app
            try:
                self._send_json(500, {"error": str(exc)})
            except Exception:
                pass


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("webcam app on http://%s:%d  (C270 main, laptop secondary)" % (HOST, PORT),
          flush=True)
    print("pictures: %s" % PICTURES_DIR, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
