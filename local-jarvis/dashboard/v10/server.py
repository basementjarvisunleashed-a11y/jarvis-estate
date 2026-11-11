#!/usr/bin/env python3
"""Jarvis dashboard server — stdlib only, no dependencies.

Serves the dashboard page and GET /api/status as JSON on 127.0.0.1:8899,
plus GET /api/voice for the live conversation (state + last 10 events).
Every collector degrades gracefully: if a source is missing on the machine
(no GPU, no ollama, no Wi-Fi, no internet), that panel reports
"available": false and the page shows "unavailable" instead of breaking.

Media: GET /api/media scans the media drive for shows. The dashboard tile
IS the player: POST /api/play with mode "here" streams the show into the
tile's own <video> element (GET /api/stream serves video with Range
support); mode "vlc" plays it in the separate VLC app instead. POST
/api/stop stops both — it kills every VLC process on the machine by name
(a VLC whose window was closed can keep playing audio, and a VLC launched
by hand is invisible to the server, so killing by process is the only way
to guarantee silence) and clears the in-page player. POST /api/fullscreen
toggles the fullscreen flag the dashboard polls. Shows loop continuously.
POST /api/media-control takes voice commands — next / previous / pause /
resume / volume-up / volume-down — and works in both players: for VLC it
acts on the process directly, for the in-page player it writes a flag file
(media-control.json) the dashboard polls every second. Every control
response carries the detail Jarvis needs to confirm the command by voice.

Webcam: GET /api/webcam-stream serves a live MJPEG multipart stream
(laptop /dev/video0 by default, C270 /dev/video2 via ?cam=c270) for the
webcam beside the media player on the dashboard.

Run on the Acer:  python3 server.py
Then open http://127.0.0.1:8899 in a fullscreen browser.

Env vars (all optional):
  DASHBOARD_PORT   port to listen on (default 8899)
  WEBCAM_CMD       ffmpeg binary for the live webcam stream (default ffmpeg)
  PICTURE_DIR      folder to look for the latest ComfyUI picture
                   (default ~/ComfyUI/output)
  ROUTER_LOG       explicit path to router.log
  ROUTER_HEALTH_URL  router /health endpoint (default
                   http://127.0.0.1:11435/health) — router availability
                   comes from this endpoint, NOT from a log file (v8)
  REA_HISTORY      path to rea-history.jsonl (default ./rea-history.jsonl)
  MEDIA_DIR        media drive to scan (default /mnt/hgx)
  IPAD_MP4_DIR     the iPad-Pro MP4 folder, the PRIMARY media source
                   for playback (default /path/to/ipad-pro-mp4-folder) — H.264/AAC MP4s that play in
                   the browser AND in VLC. The drive (MEDIA_DIR)
                   stays as the SECONDARY source, only for shows the
                   MP4 folder does not have (v10)
  DASHBOARD_HOST   interface to bind (default 127.0.0.1; set 0.0.0.0
                   to reach the dashboard over the tailnet)

v8 notes: the media scan is cached and refreshed by a background
thread (see scan_media) so /api/media never re-walks the drive per
request and a failed scan never wipes the shows; /api/play probes a
file's codecs with ffprobe and steers files the browser cannot play
to VLC instead of recording them as "playing" in the tile; recent
plays are kept in recent.json (see record_recent).

v10 notes: two media roots (see MEDIA_DIRS). The iPad-Pro MP4 folder
(IPAD_MP4_DIR, default /path/to/ipad-pro-mp4-folder)
is the PRIMARY source for playback — H.264/AAC MP4s that play in the
browser and in VLC. The drive (MEDIA_DIR) is the SECONDARY source,
only for shows the MP4 folder does not have. A show in both roots is
served from the primary only, never duplicated. If the MP4 folder is
missing, the drive alone carries the list.
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
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

try:
    from zoneinfo import ZoneInfo
    TORONTO = ZoneInfo("America/Toronto")
except Exception:  # pragma: no cover - tzdata missing
    TORONTO = None

HOST = os.environ.get("DASHBOARD_HOST", "127.0.0.1")
PORT = int(os.environ.get("DASHBOARD_PORT", "8899"))
BASE = Path(__file__).resolve().parent
PICTURE_DIR = Path(os.environ.get("PICTURE_DIR", str(Path.home() / "ComfyUI" / "output")))
ROUTER_LOG_ENV = os.environ.get("ROUTER_LOG", "")
# v8: router availability comes from its /health HTTP endpoint, not
# from a log file. The old code depended on router_log_paths(), which
# carried a hardcoded dev-workspace path that does not exist on the
# Acer — so the dashboard said "Router offline" while the router was
# up and answering /health. A log tail is still shown when a real log
# file exists (ROUTER_LOG, or router.log next to server.py); when
# there is none, the tile says so instead of crying offline.
ROUTER_HEALTH_URL = os.environ.get("ROUTER_HEALTH_URL", "http://127.0.0.1:11435/health")
RECENT_FILE = BASE / "recent.json"
RECENT_MAX = 5  # most recent plays kept, newest first
REA_HISTORY = Path(os.environ.get("REA_HISTORY", str(BASE / "rea-history.jsonl")))
VOICE_EVENTS = Path(os.environ.get("VOICE_EVENTS", str(BASE / "voice-events.jsonl")))
VOICE_STATE = Path(os.environ.get("VOICE_STATE", str(BASE / "voice-state.json")))
VOICE_STATES = ("listening", "speaking", "idle")

# ---------------------------------------------------------------- media
MEDIA_DIR = Path(os.environ.get("MEDIA_DIR", "/mnt/hgx"))
# v10: the iPad-Pro MP4 folder is the PRIMARY media source for
# playback. It holds H.264/AAC MP4s (2,785 files, 239 GB on the Acer)
# that play in the browser AND in VLC — which is why these work while
# the drive's .avi (Sopranos), MPEG-4 (Dhoom) and AC3 (BBT) files do
# not. The drive (MEDIA_DIR) stays as the SECONDARY source, only for
# shows the MP4 folder does not have (the Sopranos lives only on the
# drive, as .avi). MEDIA_DIRS is ordered, primary first: a show
# present in both roots is served from the primary only, never
# duplicated. If the MP4 folder is missing/unreadable, the dashboard
# falls back to the drive alone — never an empty list, never a crash.
IPAD_MP4_DIR = Path(os.environ.get(
    "IPAD_MP4_DIR", "/path/to/ipad-pro-mp4-folder"))
MEDIA_DIRS = [IPAD_MP4_DIR, MEDIA_DIR]
VIDEOS_DIR = Path.home() / "Videos"
MEDIA_SLOTS = BASE / "media-slots.json"
FULLSCREEN_FILE = BASE / "fullscreen.json"
MEDIA_CONTROL_FILE = BASE / "media-control.json"
MEDIA_CONTROL_ACTIONS = ("next", "previous", "pause", "resume", "volume-up", "volume-down")
MEDIA_CONTROL_TTL = 15  # seconds; a flag the dashboard never picks up goes stale
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".mpg", ".mpeg", ".ts"}
VIDEO_TYPES = {
    ".mp4": "video/mp4", ".m4v": "video/mp4",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".mpg": "video/mpeg", ".mpeg": "video/mpeg",
    ".ts": "video/mp2t",
}
MEDIA_MAX_FILES = 100000  # cap the scan so a huge drive can't hang the page
DEFAULT_SLOTS = {"pinned": ["The Sopranos", "The Big Bang Theory"],
                 "slots": [None, None, None]}

_play_lock = threading.Lock()
_vlc = {"proc": None}
_playback = {"mode": None, "playing": None, "show": None,
             "playlist": [], "index": 0, "loop": True, "fullscreen": False,
             "paused": False, "volume": 1.0}

WEATHER_URL = "https://wttr.in/Markham?format=j1"
WEATHER_TTL = 600  # seconds

_weather_cache = {"at": 0.0, "data": None}

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


# ---------------------------------------------------------------- helpers
def run(cmd, timeout=3):
    """Run a command, return stdout string or None on any failure."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            return None
        return proc.stdout
    except Exception:
        return None


def now():
    dt = datetime.now(TORONTO) if TORONTO else datetime.now(timezone.utc)
    return dt


def fmt_uptime(seconds):
    seconds = int(seconds)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    if days:
        return "%dd %dh %dm" % (days, hours, minutes)
    if hours:
        return "%dh %dm" % (hours, minutes)
    return "%dm" % minutes


# ---------------------------------------------------------------- collectors
def collect_gpu():
    out = run(["nvidia-smi",
               "--query-gpu=name,utilization.gpu,memory.used,memory.total,"
               "temperature.gpu,power.draw",
               "--format=csv,noheader,nounits"])
    if not out:
        return {"available": False}
    try:
        parts = [p.strip() for p in out.strip().splitlines()[0].split(",")]
        name, util, mem_used, mem_total, temp, power = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
        return {
            "available": True,
            "name": name,
            "utilization_pct": float(util),
            "mem_used_gb": round(float(mem_used) / 1024, 2),
            "mem_total_gb": round(float(mem_total) / 1024, 2),
            "temp_c": float(temp),
            "power_w": float(power),
        }
    except Exception:
        return {"available": False}


def collect_cpu():
    try:
        load1, load5, load15 = os.getloadavg()
    except Exception:
        load1 = load5 = load15 = None
    uptime = None
    try:
        with open("/proc/uptime") as f:
            uptime = fmt_uptime(float(f.read().split()[0]))
    except Exception:
        pass
    temp_c = None
    try:
        # /sys/class/thermal/thermal_zone*/temp is millidegrees C.
        zones = []
        thermal = Path("/sys/class/thermal")
        for zone in sorted(thermal.glob("thermal_zone*")):
            try:
                ztype = (zone / "type").read_text().strip()
                ztemp = int((zone / "temp").read_text().strip()) / 1000.0
                zones.append((ztype, ztemp))
            except Exception:
                continue
        cpu_zones = [t for typ, t in zones
                     if any(k in typ.lower() for k in ("x86_pkg_temp", "coretemp", "k10temp", "cpu", "acpitz"))]
        if cpu_zones:
            temp_c = round(max(cpu_zones), 1)
        elif zones:
            temp_c = round(max(t for _, t in zones), 1)
    except Exception:
        pass
    return {
        "available": True,
        "load_1": load1,
        "load_5": load5,
        "load_15": load15,
        "cores": os.cpu_count(),
        "temp_c": temp_c,
        "uptime": uptime,
    }


def collect_memory():
    mem = {"total_gb": None, "used_gb": None, "available_gb": None,
           "swap_total_gb": None, "swap_used_gb": None}
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                key, _, rest = line.partition(":")
                info[key.strip()] = int(rest.split()[0])  # kB
        total = info.get("MemTotal")
        avail = info.get("MemAvailable")
        swap_total = info.get("SwapTotal", 0)
        swap_free = info.get("SwapFree", 0)
        if total is not None:
            mem["total_gb"] = round(total / 1024 / 1024, 2)
        if total is not None and avail is not None:
            mem["used_gb"] = round((total - avail) / 1024 / 1024, 2)
            mem["available_gb"] = round(avail / 1024 / 1024, 2)
        mem["swap_total_gb"] = round(swap_total / 1024 / 1024, 2)
        mem["swap_used_gb"] = round((swap_total - swap_free) / 1024 / 1024, 2)
    except Exception:
        pass
    disks = []
    for path in ("/", "/home"):
        try:
            usage = shutil.disk_usage(path)
            disks.append({
                "path": path,
                "total_gb": round(usage.total / 1024 ** 3, 1),
                "used_gb": round(usage.used / 1024 ** 3, 1),
                "free_gb": round(usage.free / 1024 ** 3, 1),
            })
        except Exception:
            continue
    # External media drive (HgX's TV shows, movies, music — the Sopranos lives here).
    # Show "unmounted" rather than vanishing when it is not mounted.
    # NOTE: disk_usage() succeeds on an empty mountpoint directory (it
    # returns the root filesystem's numbers), so "is it a directory" is
    # not a mount check — _media_is_mounted() is.
    if _media_is_mounted(Path("/mnt/hgx")):
        try:
            usage = shutil.disk_usage("/mnt/hgx")
            disks.append({
                "path": "/mnt/hgx (media)",
                "total_gb": round(usage.total / 1024 ** 3, 1),
                "used_gb": round(usage.used / 1024 ** 3, 1),
                "free_gb": round(usage.free / 1024 ** 3, 1),
            })
        except Exception:
            disks.append({"path": "/mnt/hgx (media)", "unmounted": True})
    else:
        disks.append({"path": "/mnt/hgx (media)", "unmounted": True})
    mem["disks"] = disks
    return mem


def router_log_paths():
    """Real places a router log could live. The router writes its log
    next to its own file (router source line 56:
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
    "router.log")) — on the Acer that is
    ~/tonight-scripts/acer-llm-consolidation/router.log. The old
    hardcoded dev-workspace path (~/workspace/family-bot/...) was the
    bug: it does not exist on the Acer. Availability no longer
    depends on a log file at all (see router_available); the tail is
    a nicety, shown only when a real log file is found."""
    paths = []
    if ROUTER_LOG_ENV:
        paths.append(Path(ROUTER_LOG_ENV))
    paths.append(Path.home() / "tonight-scripts" / "acer-llm-consolidation" / "router.log")
    paths.append(BASE / "router.log")
    paths.append(Path.cwd() / "router.log")
    return paths


_router_health_cache = {"at": 0.0, "ok": False}


def router_available():
    """Is the little router up? Asked of its /health HTTP endpoint,
    cached for 5 s so the 3 s status snapshot never waits on it
    twice in a row. A router that answers /health is up even when
    no log file exists anywhere on the machine."""
    now_ts = time.time()
    if now_ts - _router_health_cache["at"] < 5:
        return _router_health_cache["ok"]
    ok = False
    try:
        req = Request(ROUTER_HEALTH_URL,
                      headers={"User-Agent": "jarvis-dashboard/1.0"})
        with urlopen(req, timeout=2) as resp:
            ok = resp.status == 200
    except Exception:
        ok = False
    _router_health_cache["at"] = now_ts
    _router_health_cache["ok"] = ok
    return ok


def router_tail():
    """Last few router.log lines, or ([], None) when no real log
    file exists. Never invents a path."""
    for path in router_log_paths():
        try:
            if path.is_file():
                lines = [ln.rstrip("\n") for ln in path.read_text(errors="replace").splitlines() if ln.strip()]
                return lines[-5:], str(path)
        except Exception:
            continue
    return [], None


# ollama ps columns, matched by shape (see collect_models): the
# processor looks like "100% CPU" or "20%/80% CPU/GPU"; the keep-alive
# expiry looks like "24 hours from now" or "58 minutes from now".
_PS_PROC_RE = re.compile(r"(\d+%(?:/\d+%)?\s+(?:CPU|GPU)(?:/(?:CPU|GPU))?)")
_PS_UNTIL_RE = re.compile(r"(\d+\s+(?:second|minute|hour|day)s?\s+from now|never)\s*$", re.I)


def collect_models():
    models = []
    ollama_present = False
    out = run(["ollama", "list"], timeout=5)
    if out:
        ollama_present = True
        lines = [ln for ln in out.strip().splitlines() if ln.strip()]
        for line in lines[1:]:  # skip header
            parts = line.split(None, 3)
            if len(parts) >= 3:
                # SIZE is two tokens ("5.5 GB"); the unit rides in parts[3].
                size = parts[2]
                if len(parts) >= 4:
                    unit = parts[3].split(None, 1)[0]
                    if unit in ("B", "KB", "MB", "GB", "TB"):
                        size = parts[2] + " " + unit
                models.append({"name": parts[0], "size": size, "loaded": False,
                               "processor": None, "location": None,
                               "until": None, "last_task": None})
    ps = run(["ollama", "ps"], timeout=5)
    loaded = {}
    if ps:
        lines = [ln for ln in ps.strip().splitlines() if ln.strip()]
        for line in lines[1:]:  # skip header
            # Columns: NAME ID SIZE PROCESSOR UNTIL — but SIZE is two
            # tokens ("5.5 GB") and PROCESSOR has spaces ("20%/80%
            # CPU/GPU"), so a plain whitespace split lands on the wrong
            # column. Match the processor and the keep-alive expiry
            # ("until") by shape instead.
            name = line.split(None, 1)[0]
            proc_m = _PS_PROC_RE.search(line)
            until_m = _PS_UNTIL_RE.search(line)
            info = {
                "processor": proc_m.group(1) if proc_m else None,
                "until": until_m.group(1) if until_m else None,
            }
            loaded[name] = info
            # Also key by the name without its tag ("qwen9b-abliterated"
            # as well as "qwen9b-abliterated:latest"): ollama list and
            # ollama ps do not always print the same form, and a model
            # must not look offline just because one of them dropped
            # the ":latest".
            if ":" in name:
                loaded.setdefault(name.rsplit(":", 1)[0], info)
    for m in models:
        if m["name"] in loaded:
            info = loaded[m["name"]]
            proc = info["processor"] or ""
            m["loaded"] = True
            m["processor"] = info["processor"]
            m["until"] = info.get("until")
            m["location"] = "VRAM" if "GPU" in proc.upper() else "RAM"
    router_tail_lines, router_log_path = router_tail()
    router = {"available": router_available(),
              "log_path": router_log_path, "tail": router_tail_lines,
              "health_url": ROUTER_HEALTH_URL}
    # What is each model actually doing? Ollama does not expose the live
    # prompt being processed, so the best available signal is the most
    # recent router.log line that mentions the model (the last task the
    # router sent its way) plus its loaded state and keep-alive expiry.
    # When there is no log file there is simply no last-task line.
    for m in models:
        name = m["name"].lower()
        for line in reversed(router.get("tail", [])):
            if name in line.lower():
                m["last_task"] = line
                break
    return {"available": ollama_present, "models": models, "router": router}


REA_SKILL_DIR = Path.home() / ".agents" / "skills" / "reverse-engineer-anything"
LOCALLY_DIR = Path.home() / ".local" / "share" / "Locally Uncensored"


def collect_rea():
    """REA is a skill/tool, not a service: it is "installed" when its
    skill directory exists, and it never shows as "offline" for not
    having a process. Runs are the history log, as before."""
    runs = []
    total = 0
    try:
        if REA_HISTORY.is_file():
            lines = [ln for ln in REA_HISTORY.read_text(errors="replace").splitlines() if ln.strip()]
            total = len(lines)
            for line in lines[-5:]:
                try:
                    runs.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        pass
    return {"available": True, "installed": REA_SKILL_DIR.is_dir(),
            "total": total, "runs": runs}


def collect_voice():
    """Live conversation state + last 10 events for the Conversation panel.

    Fed by log-voice.sh from the voice loop. Missing files mean the loop
    hasn't spoken yet: state "idle", empty events — never an error.
    """
    state = "idle"
    try:
        if VOICE_STATE.is_file():
            data = json.loads(VOICE_STATE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("state") in VOICE_STATES:
                state = data["state"]
    except Exception:
        pass
    events = []
    try:
        if VOICE_EVENTS.is_file():
            lines = [ln for ln in VOICE_EVENTS.read_text(errors="replace").splitlines() if ln.strip()]
            for line in lines[-10:]:
                try:
                    ev = json.loads(line)
                    if isinstance(ev, dict) and "speaker" in ev and "text" in ev:
                        events.append(ev)
                except Exception:
                    continue
    except Exception:
        pass
    return {"state": state, "events": events}


# ---------------------------------------------------------------- audio
MIC_PRIORITY = [
    ("primary", ("HDA Intel PCH", "ALC295", "Built-in Audio")),
    ("secondary", ("MAONO", "AUAM200")),
    ("tertiary", ("046d", "C270", "USB Device 0x46d")),
]
MIC_LABELS = {"primary": "Laptop built-in mic (ALC295)",
              "secondary": "MaonoCaster AU-AM200",
              "tertiary": "Logitech C270 mic"}


def _mic_priority(name, desc):
    hay = ((name or "") + " " + (desc or "")).lower()
    for prio, keys in MIC_PRIORITY:
        if any(k.lower() in hay for k in keys):
            return prio
    return None


def collect_audio():
    """Microphones + speaker, live from PipeWire (pactl).

    Every known mic is listed whether it is plugged in or not: a plugged-in
    mic reports its live state (active = capturing right now, ready =
    present and available but not capturing — the voice loop is parked,
    so nothing is capturing, and that is normal, not a fault); an
    unplugged one reports present: false.
    Priority (HgX, 2026-11-05): laptop built-in primary, MaonoCaster
    secondary, C270 tertiary. Nothing plugged in? The laptop alone is
    primary, so the panel still shows a working mic.
    """
    result = {"available": False, "mics": [], "speaker": None}
    out = run(["pactl", "list", "sources"], timeout=5)
    if out is None:
        return result
    # Which sources currently have something capturing from them.
    active_ids = set()
    outs = run(["pactl", "list", "source-outputs"], timeout=5) or ""
    for m in re.finditer(r"Source:\s*(\d+)", outs):
        active_ids.add(int(m.group(1)))
    # Parse sources: blocks starting "Source #N".
    sources = {}
    cur = None
    for line in out.splitlines():
        m = re.match(r"Source #(\d+)", line)
        if m:
            cur = {"id": int(m.group(1)), "name": "", "desc": "", "state": ""}
            sources[cur["id"]] = cur
            continue
        if cur is None:
            continue
        s = line.strip()
        if s.startswith("Name:"):
            cur["name"] = s.split(":", 1)[1].strip()
        elif s.startswith("Description:"):
            cur["desc"] = s.split(":", 1)[1].strip()
        elif s.startswith("State:"):
            cur["state"] = s.split(":", 1)[1].strip()
    seen = set()
    for src in sources.values():
        prio = _mic_priority(src["name"], src["desc"])
        if prio is None:
            continue
        seen.add(prio)
        active = src["state"] == "RUNNING" or src["id"] in active_ids
        result["mics"].append({
            "priority": prio,
            "name": src["desc"] or src["name"],
            "device": src["name"],
            "present": True,
            # "ready", not "idle": a present mic that is not capturing
            # right now is available and waiting — "idle" read like a
            # fault, and nothing is capturing because the voice loop
            # is parked, not because the mic is broken.
            "state": "active" if active else "ready",
            "pipewire_state": src["state"],
        })
    # Mics not plugged in right now still show, as not connected.
    for prio, label in MIC_LABELS.items():
        if prio not in seen:
            result["mics"].append({"priority": prio, "name": label,
                                  "device": None, "present": False,
                                  "state": "not connected",
                                  "pipewire_state": None})
    order = {"primary": 0, "secondary": 1, "tertiary": 2}
    result["mics"].sort(key=lambda m: order.get(m["priority"], 9))
    # Default speaker.
    sink = run(["pactl", "get-default-sink"], timeout=3)
    if sink:
        result["speaker"] = {"name": sink.strip(),
                             "volume": get_sink_volume()}
    result["available"] = True
    return result


def collect_cameras():
    """Cameras, by HgX's priority: laptop built-in primary, C270 secondary."""
    cams = []
    for dev, prio, label in (("/dev/video0", "primary", "Laptop built-in webcam"),
                             ("/dev/video2", "secondary", "Logitech C270")):
        cams.append({"device": dev, "priority": prio, "name": label,
                     "present": os.path.exists(dev)})
    return {"cameras": cams}


def iter_proc_args():
    """Yield (pid, argv list) for readable processes, skipping ourselves.

    Reads /proc directly instead of pgrep -f: pgrep -f matches any command
    line that merely *mentions* a name (a shell running a command with the
    word in it counts as "running"). Matching on the actual argv below
    avoids that.
    """
    me = os.getpid()
    try:
        pids = [p for p in os.listdir("/proc") if p.isdigit()]
    except Exception:
        return
    for pid_s in pids:
        pid = int(pid_s)
        if pid == me:
            continue
        try:
            with open("/proc/%d/cmdline" % pid, "rb") as f:
                raw = f.read()
            if not raw:
                continue
            args = [a.decode("utf-8", "replace") for a in raw.split(b"\0") if a]
            if args:
                yield pid, args
        except Exception:
            continue


def proc_cwd(pid):
    try:
        return os.readlink("/proc/%d/cwd" % pid)
    except Exception:
        return ""


def service_counts():
    """Count real service processes by argv shape, not by bare-word match."""
    counts = {"ollama": 0, "router": 0, "comfyui": 0, "rea": 0, "locally_uncensored": 0}
    for pid, args in iter_proc_args():
        basenames = [os.path.basename(a) for a in args]
        if "ollama" in basenames:
            counts["ollama"] += 1
        if any(a.endswith("04-little-router.py") or a.endswith("little-router.py") for a in args):
            counts["router"] += 1
        if any("rea-agents" in a for a in args):
            counts["rea"] += 1
        if any("ocally" in b.lower() for b in basenames):
            counts["locally_uncensored"] += 1
        # ComfyUI runs as `python3 main.py` from inside its own directory.
        if any(a.endswith("main.py") for a in args) and "ComfyUI" in proc_cwd(pid):
            counts["comfyui"] += 1
        elif any("/ComfyUI/" in a for a in args):
            counts["comfyui"] += 1
    return counts


def collect_processes(counts=None):
    counts = counts if counts is not None else service_counts()
    # Honest states, not just running/down: ComfyUI is "parked" when
    # stopped by design (the 9B has the GPU), and REA / Locally
    # Uncensored are tools that live installed on disk, not services
    # — "installed", never a red "down" for not having a process.
    services = {}
    for k, v in counts.items():
        running = v > 0
        if k == "comfyui":
            state, tone = ("running", "green") if running else ("parked", "amber")
        elif k == "rea":
            if running:
                state, tone = "running", "green"
            elif REA_SKILL_DIR.is_dir():
                state, tone = "installed", "blue"
            else:
                state, tone = "not installed", "red"
        elif k == "locally_uncensored":
            if running:
                state, tone = "running", "green"
            elif LOCALLY_DIR.is_dir():
                state, tone = "installed", "blue"
            else:
                state, tone = "not installed", "red"
        else:
            state, tone = ("running", "green") if running else ("down", "red")
        services[k] = {"running": running, "count": v,
                       "state": state, "tone": tone}
    top = []
    out = run(["ps", "-eo", "pid,comm,%cpu,%mem", "--sort=-%cpu"], timeout=3)
    if out:
        for line in out.strip().splitlines()[1:6]:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    top.append({"pid": int(parts[0]), "comm": parts[1],
                                "cpu_pct": float(parts[2]), "mem_pct": float(parts[3])})
                except Exception:
                    continue
    return {"services": services, "top_cpu": top}


def collect_weather():
    now_ts = time.time()
    if _weather_cache["data"] is not None and now_ts - _weather_cache["at"] < WEATHER_TTL:
        return _weather_cache["data"]
    try:
        req = Request(WEATHER_URL, headers={"User-Agent": "jarvis-dashboard/1.0"})
        with urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        cur = data["current_condition"][0]
        result = {
            "available": True,
            "temp_c": cur.get("temp_C"),
            "feels_like_c": cur.get("FeelsLikeC"),
            "desc": (cur.get("weatherDesc") or [{}])[0].get("value"),
            "humidity": cur.get("humidity"),
            "wind_kmph": cur.get("windspeedKmph"),
        }
    except Exception:
        result = {"available": False}
    _weather_cache["at"] = now_ts
    _weather_cache["data"] = result
    return result


def collect_wifi():
    ssid = None
    signal = None
    out = run(["nmcli", "-t", "-f", "ACTIVE,SSID,SIGNAL", "dev", "wifi"], timeout=3)
    if out:
        for line in out.splitlines():
            # ACTIVE:SSID:SIGNAL — but the SSID itself may contain ":",
            # so split the active flag off the front and the signal off
            # the back; whatever is left in the middle is the SSID.
            try:
                active, rest = line.split(":", 1)
                ssid_raw, signal_s = rest.rsplit(":", 1)
            except ValueError:
                continue
            if active.strip().lower() == "yes":
                ssid = ssid_raw.strip()
                try:
                    signal = int(signal_s.strip())
                except Exception:
                    signal = None
                break
    ip = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.connect(("8.8.8.8", 80))  # no packets sent; just resolves the local route
        ip = sock.getsockname()[0]
        sock.close()
    except Exception:
        ip = None
    available = bool(ssid or ip)
    return {"available": available, "ssid": ssid, "signal": signal, "ip": ip}


def latest_image(directory):
    try:
        if not directory.is_dir():
            return None
        files = [p for p in directory.iterdir()
                 if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
        if not files:
            return None
        return max(files, key=lambda p: p.stat().st_mtime)
    except Exception:
        return None


def collect_picture(counts=None):
    comfy_running = (counts or service_counts()).get("comfyui", 0) > 0
    img = latest_image(PICTURE_DIR)
    result = {
        "comfyui_running": comfy_running,
        # "parked", not "idle": ComfyUI is stopped by design while the
        # 9B holds the GPU — a parked picture brain, not a fault.
        "status": "running" if comfy_running else "parked",
        "available": img is not None,
        "name": img.name if img else None,
        "url": "/api/picture" if img else None,
        "dir": str(PICTURE_DIR),
    }
    return result


def collect_webcam():
    # Snapshot still: saved from the live stream when one is running
    # (see _maybe_save_webcam_snapshot in the webcam section below —
    # nothing ever wrote webcam.jpg before, so this tile always said
    # "no snapshot yet" even while the live feed worked).
    _maybe_save_webcam_snapshot()
    snap = BASE / "webcam.jpg"
    streaming, streaming_device = webcam_streaming()
    mtime = None
    try:
        if snap.is_file():
            mtime = snap.stat().st_mtime
    except Exception:
        mtime = None
    return {"available": snap.is_file(),
            "url": "/api/webcam" if snap.is_file() else None,
            "mtime": mtime,
            # Which camera is actually streaming right now (a grabber
            # with a live client). The page label is corrected from
            # this when the server falls back to the other camera —
            # the <img> tag cannot read the X-Webcam-Device header.
            "streaming": streaming,
            "streaming_device": streaming_device,
            # Honest state, not a bare "idle": the camera is live
            # while someone is viewing it, and on standby — ready,
            # stream starts on first viewer — the rest of the time.
            # The camera is never "off" for being unwatched.
            "state": "live" if streaming else "standby",
            "state_label": ("live — " + streaming) if streaming
                           else "standby — live when viewed"}


# ---------------------------------------------------------------- status snapshot
# /api/status used to run every collector inline, so one slow collector
# (a hung NTFS mount, a weather fetch, ollama) froze the whole page and
# the clock looked dead. Now a background thread refreshes the snapshot
# every 3 s and /api/status serves the stored snapshot instantly, with a
# fresh server timestamp stamped on at request time.
_status_cache = {"at": 0.0, "data": None}
_status_lock = threading.Lock()


def time_block(dt=None):
    dt = dt or now()
    return {
        "iso": dt.isoformat(),
        "display": dt.strftime("%H:%M:%S"),
        "date": dt.strftime("%a %Y-%m-%d"),
        "tz": "America/Toronto",
    }


def _status_worker():
    while True:
        try:
            snap = collect_status()
        except Exception:
            snap = None
        if snap is not None:
            with _status_lock:
                _status_cache["at"] = time.time()
                _status_cache["data"] = snap
        time.sleep(3)


def get_status_snapshot():
    """Serve the stored status snapshot with a fresh timestamp.

    The page must never wait on a collector: the snapshot is at most ~3 s
    old, and the clock is always stamped fresh at request time.
    """
    with _status_lock:
        snap = _status_cache["data"]
        age = time.time() - _status_cache["at"] if snap is not None else None
    if snap is None:
        try:
            snap = collect_status()
        except Exception as exc:
            return {"error": str(exc)}
        with _status_lock:
            _status_cache["at"] = time.time()
            _status_cache["data"] = snap
        age = 0.0
    payload = dict(snap)
    payload["time"] = time_block()
    payload["snapshot_age_s"] = round(age, 1) if age is not None else None
    return payload


# ---------------------------------------------------------------- sports
ESPN_SCOREBOARDS = {
    "nfl": ("NFL", "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"),
    "nba": ("NBA", "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"),
    "nhl": ("NHL", "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"),
    "mlb": ("MLB", "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"),
}
MY_TEAMS = {
    "nfl": "Cincinnati Bengals",
    "nba": "Toronto Raptors",
    "nhl": "Toronto Maple Leafs",
    "mlb": "Toronto Blue Jays",
}
_sports_cache = {"at": 0.0, "data": None}
SPORTS_TTL = 60  # seconds


def _fetch_json(url, timeout=5):
    try:
        req = Request(url, headers={"User-Agent": "jarvis-dashboard/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _parse_game(event):
    try:
        comp = event["competitions"][0]
        comps = comp["competitors"]
        away = next(c for c in comps if c.get("homeAway") == "away")
        home = next(c for c in comps if c.get("homeAway") == "home")
        status = (comp.get("status") or {}).get("type") or {}
        state = status.get("state") or ""
        # Pre-game events carry "0" scores from ESPN — a 0-0 that never
        # happened. Null them out so the tile never shows a fake score.
        away_score = away.get("score")
        home_score = home.get("score")
        if state == "pre":
            away_score = home_score = None
        return {
            "away": (away.get("team") or {}).get("abbreviation") or (away.get("team") or {}).get("shortDisplayName"),
            "home": (home.get("team") or {}).get("abbreviation") or (home.get("team") or {}).get("shortDisplayName"),
            "away_score": away_score,
            "home_score": home_score,
            "status": status.get("shortDetail") or status.get("detail") or "",
            "state": state,
            "away_name": (away.get("team") or {}).get("displayName"),
            "home_name": (home.get("team") or {}).get("displayName"),
        }
    except Exception:
        return None


def _parse_league(key, label, data):
    """One league's slice of the scoreboard. Any unexpected shape
    degrades to unavailable instead of killing the whole sports tile."""
    try:
        events = data.get("events") or []
        games = [g for g in (_parse_game(e) for e in events) if g]
        my_name = MY_TEAMS[key]
        my_game = None
        for g in games:
            if (my_name.lower() in (g.get("away_name") or "").lower()
                    or my_name.lower() in (g.get("home_name") or "").lower()):
                my_game = g
                break
        if my_game:
            mine_is_away = my_name.lower() in (my_game.get("away_name") or "").lower()
            my_team = {
                "name": my_name,
                "opponent": my_game["home_name"] if mine_is_away else my_game["away_name"],
                "my_score": my_game["away_score"] if mine_is_away else my_game["home_score"],
                "opp_score": my_game["home_score"] if mine_is_away else my_game["away_score"],
                "status": my_game["status"],
                "state": my_game["state"],
                "has_game": True,
            }
        else:
            my_team = {"name": my_name, "has_game": False}
        # Season type lives on leagues[0].season.type.name ("Regular
        # Season", "Off Season", ...); the top-level "season" is just
        # {"type": 2, "year": 2026}.
        season_type = ""
        try:
            lg_info = (data.get("leagues") or [{}])[0]
            season_type = ((lg_info.get("season") or {}).get("type") or {}).get("name", "") or ""
        except Exception:
            season_type = ""
        if not events and "off" in season_type.lower():
            note = "offseason"
        elif not my_game:
            note = "no game today"
        else:
            note = None
        return {
            "key": key, "label": label, "available": True,
            "my_team": my_team,
            # v8: only HgX's team game, for every league — the full
            # NFL game list made the sports tile a wall of scores.
            # The tile is his team, the opponent, the score, the
            # status; nothing else.
            "games": [my_game] if my_game else [],
            "note": note,
        }
    except Exception:
        return {"key": key, "label": label, "available": False,
                "my_team": None, "games": [], "note": None}


def collect_sports():
    """Scores from ESPN's public scoreboard API (no key needed).
    HgX's teams first, then every NFL game. Never invents a score: a
    team with no game shows 'no game today', an out-of-season league
    shows 'offseason'."""
    now_ts = time.time()
    if _sports_cache["data"] is not None and now_ts - _sports_cache["at"] < SPORTS_TTL:
        return _sports_cache["data"]
    leagues = []
    any_ok = False
    for key, (label, url) in ESPN_SCOREBOARDS.items():
        data = _fetch_json(url, timeout=5)
        if data is None:
            leagues.append({"key": key, "label": label, "available": False,
                            "my_team": None, "games": [], "note": None})
            continue
        league = _parse_league(key, label, data)
        if league.get("available"):
            any_ok = True
        leagues.append(league)
    result = {"available": any_ok, "leagues": leagues}
    _sports_cache["at"] = now_ts
    _sports_cache["data"] = result
    return result


# ---------------------------------------------------------------- tailscale
def collect_tailscale():
    """This node's tailnet identity + online peers. Unavailable when
    tailscale is not installed or the daemon is not up."""
    out = run(["tailscale", "status", "--json"], timeout=5)
    if out is None:
        return {"available": False}
    try:
        data = json.loads(out)
    except Exception:
        return {"available": False}
    self_node = data.get("Self") or {}
    peers = []
    for p in (data.get("Peer") or {}).values():
        ips = p.get("TailscaleIPs") or []
        peers.append({
            "name": (p.get("DNSName") or "").rstrip("."),
            "ip": ips[0] if ips else None,
            "os": p.get("OS"),
            "online": bool(p.get("Online")),
        })
    peers.sort(key=lambda p: (p["name"] or ""))
    self_ips = self_node.get("TailscaleIPs") or []
    return {
        "available": True,
        "self": {
            "name": (self_node.get("DNSName") or "").rstrip("."),
            "ip": self_ips[0] if self_ips else None,
            "os": self_node.get("OS"),
            "online": bool(self_node.get("Online", True)),
        },
        "peers": peers,
    }


def collect_status():
    # One /proc walk per snapshot: collect_processes() and
    # collect_picture() used to each call service_counts() themselves,
    # so the snapshot walked /proc twice and the two could disagree
    # if a service started or stopped between the two walks.
    counts = service_counts()
    status = {
        "time": time_block(),
        "gpu": collect_gpu(),
        "cpu": collect_cpu(),
        "memory": collect_memory(),
        "models": collect_models(),
        "rea": collect_rea(),
        "processes": collect_processes(counts),
        "weather": collect_weather(),
        "wifi": collect_wifi(),
        "picture": collect_picture(counts),
        "webcam": collect_webcam(),
        "audio": collect_audio(),
        "cameras": collect_cameras(),
        "sports": collect_sports(),
        "tailscale": collect_tailscale(),
    }
    status["health"] = collect_health(status)
    return status


def collect_health(s):
    """One rollup for the Health & Heat tile: a dot per subsystem plus
    the two temperatures that get heat bars.

    Honest states (v8): a dot is red only for a real fault. REA and
    Locally Uncensored are installed tools, not services — "installed"
    (blue), never a red "offline" for not having a process. ComfyUI
    stopped by design is "parked" (amber), not a red "offline".
    Each item carries {"name", "state", "tone"}; "ok" stays for
    back-compat and means "no fault" (green, blue and amber are all ok).
    """
    disks = s.get("memory", {}).get("disks", [])
    media_ok = any("media" in str(d.get("path", "")) and not d.get("unmounted")
                   for d in disks)
    procs = s.get("processes", {}).get("services", {})

    def item(name, state, tone):
        return {"name": name, "state": state, "tone": tone,
                "ok": tone != "red"}

    items = [
        item("Ollama", "online" if s.get("models", {}).get("available") else "offline",
             "green" if s.get("models", {}).get("available") else "red"),
        item("Router", "online" if s.get("models", {}).get("router", {}).get("available") else "offline",
             "green" if s.get("models", {}).get("router", {}).get("available") else "red"),
        item("ComfyUI", procs.get("comfyui", {}).get("state", "parked"),
             procs.get("comfyui", {}).get("tone", "amber")),
        item("REA", procs.get("rea", {}).get("state", "installed"),
             procs.get("rea", {}).get("tone", "blue")),
        item("Locally Uncensored", procs.get("locally_uncensored", {}).get("state", "installed"),
             procs.get("locally_uncensored", {}).get("tone", "blue")),
        item("Media drive", "online" if media_ok else "unmounted",
             "green" if media_ok else "red"),
        item("Wi-Fi", "online" if s.get("wifi", {}).get("available") else "offline",
             "green" if s.get("wifi", {}).get("available") else "red"),
        item("Tailscale", "online" if s.get("tailscale", {}).get("available") else "offline",
             "green" if s.get("tailscale", {}).get("available") else "red"),
        item("Weather", "online" if s.get("weather", {}).get("available") else "offline",
             "green" if s.get("weather", {}).get("available") else "red"),
    ]
    return {
        "items": items,
        "gpu_temp_c": s.get("gpu", {}).get("temp_c"),
        "cpu_temp_c": s.get("cpu", {}).get("temp_c"),
    }


# ---------------------------------------------------------------- media
def _is_within(path, root):
    try:
        return path.is_relative_to(root)
    except AttributeError:  # Python < 3.9
        try:
            return os.path.commonpath([str(path), str(root)]) == str(root)
        except ValueError:
            return False


def media_allowed(path):
    """Resolve a requested path; return it only if it lives under one
    of the media roots (v10: the MP4 folder first, then the drive) or
    ~/Videos. Anything else (including ../ escapes and symlinks out
    of the media tree) is rejected."""
    try:
        resolved = Path(path).expanduser().resolve()
    except Exception:
        return None
    for root in list(MEDIA_DIRS) + [VIDEOS_DIR]:
        try:
            if _is_within(resolved, root.resolve()):
                return resolved
        except Exception:
            continue
    return None


def load_slots():
    """Pinned shows + blank slots, from media-slots.json (editable later)."""
    try:
        if MEDIA_SLOTS.is_file():
            data = json.loads(MEDIA_SLOTS.read_text(encoding="utf-8"))
            pinned = [str(p) for p in (data.get("pinned") or [])][:2]
            slots = [(str(s) if s else None) for s in (data.get("slots") or [])]
            slots = (slots + [None, None, None])[:3]
            return {"pinned": pinned or list(DEFAULT_SLOTS["pinned"]), "slots": slots}
    except Exception:
        pass
    return {"pinned": list(DEFAULT_SLOTS["pinned"]), "slots": list(DEFAULT_SLOTS["slots"])}


CATEGORY_FOLDERS = {"tv shows", "movies", "music", "tv", "shows"}
# Folders the media walk never enters, at any level (case-insensitive):
# backups, system folders and other non-media trees. A directory whose
# name starts with "$" is also skipped (e.g. $RECYCLE.BIN).
SKIP_DIRS = {"filehistory", "windowsimagebackup", "ownerlaptop",
             "jarvisbackup", "$recycle.bin", "system volume information",
             "recovery", "config.msi", "found.000", "program files",
             "windowsapps", "back up"}
# The media categories we actually scan when they exist under MEDIA_DIR.
MEDIA_CATEGORY_DIRS = {"tv shows", "movies", "music", "videos"}


def _is_skipped_dir(name):
    low = name.lower()
    return low in SKIP_DIRS or low.startswith("$")
SEASON_RE = re.compile(r"^(season|s\d{1,2})", re.I)
# v8: the media scan is cached and refreshed by a background thread.
# The old code re-walked the whole drive on every /api/media poll
# (the page polls every 30 s) and concurrent polls could each start
# a walk — on a slow NTFS drive the walk outlasted the client's
# patience, the client disconnected, and the error path answered
# mounted:false with an empty show list, so the tile looked broken
# (and a click found no show to play) while the drive was fine.
# Now /api/media serves the last good scan instantly; a background
# thread re-walks on a timer, ?refresh=1 asks for a background
# refresh, and a failed scan NEVER wipes the shows — it keeps the
# last good list and says so (stale: true).
_media_cache = {"at": 0.0, "data": None, "refreshing": False, "error": None}
_media_lock = threading.Lock()
MEDIA_REFRESH_S = 120  # seconds between background re-walks


def _root_walkable(root):
    """Should this media root be walked? The drive (MEDIA_DIR) only
    when it is really the drive (see _media_is_mounted) — an empty
    mountpoint must not be walked as if it were the drive. Any other
    root (the local MP4 folder) when the directory exists."""
    if root == MEDIA_DIR:
        return _media_is_mounted(root)
    try:
        return root.is_dir()
    except OSError:
        return False


def _any_root_walkable():
    """True when at least one media root can be walked — the dashboard
    has a media source, even if the drive is unmounted."""
    return any(_root_walkable(r) for r in MEDIA_DIRS)


def _sources_snapshot():
    """Per-root availability without walking (for error fallbacks)."""
    return [{"path": str(r), "available": _root_walkable(r), "shows": 0}
            for r in MEDIA_DIRS]


def _walk_root(root, count, skipped):
    """Walk one media root; return (shows, count, skipped) where shows
    maps show name -> episode list. count/skipped are carried in so
    the file cap is shared across roots."""
    shows = {}
    # Scope the walk: when the media dir holds the usual category folders
    # (TV SHOWS / MOVIES / MUSIC / VIDEOS), walk only those — the rest of
    # the drive is backups and system folders, and walking all of it let
    # the file cap cut the scan off before TV SHOWS was ever reached.
    # Otherwise fall back to walking the whole dir (skip-list still applies).
    # The MP4 folder has no category folders at the top (its top level
    # IS show folders), so it takes the whole-dir path — which is right
    # and fast (local ext4, 2,785 files).
    walk_roots = []
    try:
        for child in sorted(root.iterdir()):
            if child.is_dir() and child.name.lower() in MEDIA_CATEGORY_DIRS:
                walk_roots.append(child)
    except OSError:
        walk_roots = []
    if not walk_roots:
        walk_roots = [root]
    for walk_root in walk_roots:
        for dirpath, dirnames, filenames in os.walk(walk_root, onerror=lambda e: None):
            # Never descend into backup/system folders, at any level.
            dirnames[:] = [d for d in dirnames if not _is_skipped_dir(d)]
            dirnames.sort()
            for name in sorted(filenames):
                if count >= MEDIA_MAX_FILES:
                    break
                p = Path(dirpath) / name
                if p.suffix.lower() not in VIDEO_EXTS:
                    continue
                try:
                    rel = p.relative_to(root)
                    show, ep_name = _show_and_episode(rel)
                except Exception:
                    skipped += 1
                    continue
                shows.setdefault(show, []).append({"name": ep_name, "path": str(p)})
                count += 1
            if count >= MEDIA_MAX_FILES:
                break
        if count >= MEDIA_MAX_FILES:
            break
    return shows, count, skipped


def _do_scan():
    """The actual walk of the media roots. Returns the result dict.
    One unreadable file or directory is skipped, never fatal: the
    walk reports what it could read instead of raising and wiping
    the whole list.

    v10: two roots, in order — the iPad-Pro MP4 folder first (the
    primary source for playback), the drive second (only for shows
    the MP4 folder does not have). A show present in both is served
    from the primary only: one entry per show, never duplicated.
    If the MP4 folder is missing/unreadable, the drive alone carries
    the list; if neither root is walkable, mounted is False and the
    shows are empty (the caller keeps the last good list, stale)."""
    slots = load_slots()
    sources = []
    per_root = []
    count = 0
    skipped = 0
    for root in MEDIA_DIRS:
        if not _root_walkable(root):
            sources.append({"path": str(root), "available": False, "shows": 0})
            continue
        root_shows, count, skipped = _walk_root(root, count, skipped)
        per_root.append((root, root_shows))
        sources.append({"path": str(root), "available": True,
                        "shows": len(root_shows)})
    if not per_root:
        return {"mounted": False, "root": str(MEDIA_DIR), "shows": [],
                "pinned": slots["pinned"], "slots": slots["slots"],
                "roots": [str(r) for r in MEDIA_DIRS], "sources": sources}
    # Merge, primary first: a show already collected from a
    # higher-priority root blocks the same show (case-insensitive)
    # from a lower root — the MP4 version wins, no duplicates.
    shows = {}
    seen = set()
    contributed = {}
    for root, root_shows in per_root:
        n = 0
        for show in sorted(root_shows, key=_natural_key):
            if show.lower() in seen:
                continue
            seen.add(show.lower())
            shows[show] = root_shows[show]
            n += 1
        contributed[str(root)] = n
    for src in sources:
        if src["available"]:
            src["shows"] = contributed.get(src["path"], 0)
    out = [{"name": k, "episodes": sorted(v, key=lambda e: _natural_key(e["name"]))}
           for k, v in sorted(shows.items(), key=lambda kv: _natural_key(kv[0]))]
    result = {"mounted": True, "root": str(MEDIA_DIR), "shows": out,
              "pinned": slots["pinned"], "slots": slots["slots"],
              "roots": [str(r) for r in MEDIA_DIRS], "sources": sources}
    if skipped:
        result["skipped"] = skipped
    return result


def _refresh_media_background():
    """Re-walk the drive in the background and swap in the new list.
    Single-flight: a refresh already running is not started twice.
    On failure the last good list stays in place and the error is
    recorded — a failed scan never wipes the shows."""
    with _media_lock:
        if _media_cache["refreshing"]:
            return
        _media_cache["refreshing"] = True
    try:
        result = _do_scan()
    except Exception as exc:
        with _media_lock:
            _media_cache["error"] = str(exc)
        return
    finally:
        with _media_lock:
            _media_cache["refreshing"] = False
    with _media_lock:
        _media_cache["data"] = result
        _media_cache["at"] = time.time()
        _media_cache["error"] = None


def _media_worker():
    """Background re-walk on a timer, forever."""
    while True:
        time.sleep(MEDIA_REFRESH_S)
        try:
            _refresh_media_background()
        except Exception:
            pass


def scan_media(force=False):
    """Scan the media drive for video files, grouped by show folder.
    Serves the cached scan instantly; the walk runs in the background
    (every MEDIA_REFRESH_S, or on ?refresh=1). The first ever call
    scans synchronously so the first page load still gets a list.
    Never returns an empty shows list because a scan failed — a failed
    scan keeps the last good list and marks it stale."""
    slots = load_slots()
    if force:
        threading.Thread(target=_refresh_media_background, daemon=True).start()
    with _media_lock:
        cached = _media_cache["data"]
        age = time.time() - _media_cache["at"] if cached is not None else None
        refreshing = _media_cache["refreshing"]
        error = _media_cache["error"]
    if cached is not None:
        out = dict(cached)
        out["pinned"] = slots["pinned"]
        out["slots"] = slots["slots"]
        out["stale"] = bool(error) or (age is not None and age > MEDIA_REFRESH_S * 2)
        out["refreshing"] = refreshing
        if error:
            out["error"] = error
        return out
    try:
        result = _do_scan()
    except Exception as exc:
        # No good scan has ever completed: say so honestly, and say
        # whether any media source is even there.
        return {"mounted": _any_root_walkable(), "root": str(MEDIA_DIR),
                "shows": [], "pinned": slots["pinned"], "slots": slots["slots"],
                "roots": [str(r) for r in MEDIA_DIRS],
                "sources": _sources_snapshot(),
                "error": str(exc), "stale": True, "refreshing": False}
    with _media_lock:
        _media_cache["data"] = result
        _media_cache["at"] = time.time()
        _media_cache["error"] = None
    out = dict(result)
    out["stale"] = False
    out["refreshing"] = False
    return out


# ---------------------------------------------------------------- codecs
# v8: why "playing" could mean nothing on screen. The server recorded
# any file as playing in "here" mode, but the browser's <video> can
# only decode some of them — a DivX-era MPEG-4 video, AC3/DTS sound,
# or any .avi sits black (or silent) while the tile claims it is
# playing. So /api/play probes the file first (ffprobe, cached) and
# steers files the browser cannot play to VLC instead of pretending.
_codec_cache = {}
_CODEC_CACHE_MAX = 200
# Codecs a browser <video> element can actually play. Conservative
# on purpose: Chromium plays MPEG-4 Part 2 in an .mp4, Firefox does
# not — and a file that plays video with no sound (AC3) is not
# "playing" either. VLC plays all of these, with sound.
BROWSER_VIDEO_CODECS = {"h264", "vp8", "vp9", "av1"}
BROWSER_AUDIO_CODECS = {"aac", "mp3", "opus", "vorbis"}


def probe_codecs(path):
    """(video_codec, audio_codec) for a file via ffprobe, cached by
    path+size+mtime. Returns (None, None) when ffprobe is missing or
    the file cannot be probed — the caller then fails open (old
    behaviour) instead of refusing to play a file it knows nothing
    about."""
    try:
        st = Path(path).stat()
        key = (str(path), st.st_size, st.st_mtime)
    except Exception:
        return None, None
    if key in _codec_cache:
        return _codec_cache[key]
    vcodec = acodec = None
    for stream, which in (("v:0", "v"), ("a:0", "a")):
        try:
            proc = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", stream,
                 "-show_entries", "stream=codec_name", "-of", "csv=p=0",
                 str(path)],
                capture_output=True, text=True, timeout=5)
            if proc.returncode == 0 and proc.stdout.strip():
                # ffprobe's csv writer can trail a comma (e.g. "ac3,");
                # the codec name is the first field.
                name = proc.stdout.strip().splitlines()[0].strip().lower()
                name = name.split(",")[0].strip() or None
                if which == "v":
                    vcodec = name
                else:
                    acodec = name
        except Exception:
            pass
    if len(_codec_cache) > _CODEC_CACHE_MAX:
        _codec_cache.clear()
    _codec_cache[key] = (vcodec, acodec)
    return vcodec, acodec


def playable_here(path):
    """Can this file play in the dashboard tile's <video> element?
    Returns (playable, reason). reason is None when playable, else a
    short plain-language explanation for the VLC hint."""
    ext = Path(path).suffix.lower()
    if ext == ".avi":
        return False, "browsers can't play .avi files in a page"
    vcodec, acodec = probe_codecs(path)
    if vcodec is None and acodec is None:
        return True, None  # unprobed: fail open, let the browser try
    if vcodec and vcodec not in BROWSER_VIDEO_CODECS:
        return False, "this file's video (%s) can't play in a browser page" % vcodec
    if acodec and acodec not in BROWSER_AUDIO_CODECS:
        return False, "this file's sound (%s) can't play in a browser page" % acodec
    return True, None


def vlc_hint(reason):
    """Plain-language steer for a file the browser cannot play."""
    base = reason or "this browser can't play this file in the page"
    return base + " — tap the \u201cVLC app\u201d link to play it on this device, or \u201cPlay in VLC app\u201d to play it on the laptop."


# ---------------------------------------------------------------- recent
def load_recent():
    """Last plays, newest first, persisted in recent.json so they
    survive a restart. [] when nothing has played yet."""
    try:
        if RECENT_FILE.is_file():
            data = json.loads(RECENT_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [r for r in data if isinstance(r, dict)][:RECENT_MAX]
    except Exception:
        pass
    return []


def record_recent(show, episode, path, mode):
    """Remember a play: show + episode name + path + mode, newest
    first, de-duplicated by path, kept to RECENT_MAX. Atomic write
    (tmp + replace) so a crash mid-write cannot corrupt the file."""
    try:
        recent = load_recent()
        recent = [r for r in recent if r.get("path") != str(path)]
        recent.insert(0, {"show": show, "episode": episode,
                          "path": str(path), "mode": mode,
                          "time": now().strftime("%H:%M")})
        recent = recent[:RECENT_MAX]
        tmp = RECENT_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(recent), encoding="utf-8")
        os.replace(tmp, RECENT_FILE)
        return recent
    except Exception:
        return load_recent()


def _show_and_episode(rel):
    """Map a file under the media dir to (show name, episode display name).

    Real layout: TV SHOWS/THE SOPRANOS/The Sopranos/The Sopranos - Season 01/S01E01.mkv
    -> show "THE SOPRANOS", episode "The Sopranos - Season 01/S01E01.mkv".
    Category folders (TV SHOWS, MOVIES, ...) are stripped; a redundant
    subfolder that repeats the show name is skipped the same way.
    """
    parts = list(rel.parts)
    i = 0
    while i < len(parts) - 1 and parts[i].lower() in CATEGORY_FOLDERS:
        i += 1
    while i < len(parts) - 1 and SEASON_RE.match(parts[i]):
        i += 1
    if len(parts) - i <= 1:
        return "Unsorted", parts[-1]
    show = parts[i]
    j = i + 1
    while j < len(parts) - 1 and parts[j].lower() == show.lower():
        j += 1
    return show, "/".join(parts[j:])


def _media_is_mounted(root):
    """Is the media dir really the drive, not an empty mountpoint?

    os.path.isdir() and shutil.disk_usage() both succeed on an empty
    mountpoint directory (they report the root filesystem), so neither
    proves the drive is attached. A directory counts as the media
    drive when it is a mount point, or when it actually holds media
    (a category folder or a video file) — the second leg covers a
    MEDIA_DIR override pointing at a real (non-mount) media tree.
    """
    try:
        if not root.is_dir():
            return False
        if os.path.ismount(root):
            return True
        for child in root.iterdir():
            if child.is_dir() and child.name.lower() in MEDIA_CATEGORY_DIRS:
                return True
            if child.is_file() and child.suffix.lower() in VIDEO_EXTS:
                return True
    except OSError:
        return False
    return False


def _natural_key(s):
    """Sort key that orders Episode 2 before Episode 10 (a plain
    lexicographic sort puts 10 before 2)."""
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", str(s))]


def find_show(name):
    shows = scan_media()["shows"]
    for show in shows:
        if show["name"] == name:
            return show
    for show in shows:
        if show["name"].lower() == name.lower():
            return show
    return None


def locate_in_library(path):
    """If path is an episode of a scanned show, return
    (show_name, [episode paths], index). Otherwise None.

    Used so a single-episode play still knows the show it belongs to —
    the server can then skip next/previous across the whole show.
    """
    try:
        resolved = str(Path(path).expanduser().resolve())
    except Exception:
        return None
    for show in scan_media()["shows"]:
        paths = [ep["path"] for ep in show["episodes"]]
        if resolved in paths:
            return show["name"], paths, paths.index(resolved)
    return None


def get_fullscreen():
    try:
        if FULLSCREEN_FILE.is_file():
            data = json.loads(FULLSCREEN_FILE.read_text(encoding="utf-8"))
            return bool(data.get("fullscreen"))
    except Exception:
        pass
    return bool(_playback.get("fullscreen", False))


def set_fullscreen(on):
    _playback["fullscreen"] = bool(on)
    try:
        tmp = FULLSCREEN_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps({"fullscreen": bool(on)}), encoding="utf-8")
        os.replace(tmp, FULLSCREEN_FILE)
    except Exception:
        pass


def vlc_binary():
    """The normal VLC player — the one with a window. Never cvlc.
    cvlc is the headless console player: it runs vlc with -I dummy, so
    closing its video window does NOT quit the process and the audio
    keeps playing after the window is gone. A normal VLC quits when its
    window is closed, which is what closing the window is supposed to
    mean. If only cvlc is installed, there is no safe player to launch,
    so this returns None and the caller answers 503."""
    return shutil.which("vlc")


def stop_vlc():
    """Stop every VLC on this machine, not just the one this server
    launched. The server now launches the normal VLC player, which
    quits when its window is closed — so closing the window already
    stops the audio, and this is only the safety net: a VLC launched
    by hand (or a headless cvlc launched by hand) is invisible to the
    tracked Popen, so Stop kills by process name to guarantee silence.
    pkill matches this user's processes only; it returns non-zero
    (None from run()) when nothing is running, which is fine."""
    proc = _vlc["proc"]
    _vlc["proc"] = None
    if proc is not None:
        try:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
        except Exception:
            pass
    run(["pkill", "-x", "vlc"], timeout=3)


def start_vlc(paths, loop, fullscreen):
    """Launch the normal VLC player (windowed, never cvlc) detached
    with the playlist. Returns the Popen object, or None if no VLC
    binary is on PATH or the launch failed. Closing the VLC window
    quits the player, so the audio stops with it."""
    binary = vlc_binary()
    if binary is None:
        return None
    args = [binary]
    args.append("--loop" if loop else "--play-and-exit")
    if fullscreen:
        args.append("--fullscreen")
    args.extend(str(p) for p in paths)
    try:
        return subprocess.Popen(args, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
    except Exception:
        return None


def play_request(body):
    """POST /api/play. Returns (http_status, payload)."""
    if not isinstance(body, dict):
        return 400, {"error": "JSON object expected"}
    # "here" = the dashboard tile's own <video> (the player). "page" is
    # the old name for the same thing — still accepted, always reported
    # as "here". Anything else falls back to "vlc" (the separate app).
    mode = body.get("mode", "vlc")
    if mode == "page":
        mode = "here"
    if mode not in ("here", "vlc"):
        mode = "vlc"
    loop = bool(body.get("loop", True))
    fullscreen = bool(body["fullscreen"]) if "fullscreen" in body else get_fullscreen()
    # Resolve what to play before touching the current playback.
    index = 0
    if body.get("show"):
        show = find_show(str(body["show"]))
        if show is None:
            return 404, {"error": "show not found: %s" % body["show"]}
        paths = [ep["path"] for ep in show["episodes"]]
        if not paths:
            return 404, {"error": "show has no episodes"}
        display = show["name"]
        episode = show["episodes"][0]["name"]  # first episode of the show
        show_name = show["name"]
    elif body.get("path"):
        resolved = media_allowed(str(body["path"]))
        if resolved is None:
            return 403, {"error": "path not under the media dir or ~/Videos"}
        if not resolved.is_file():
            return 404, {"error": "file not found"}
        if resolved.suffix.lower() not in VIDEO_EXTS:
            return 415, {"error": "not a video file: %s" % resolved.suffix}
        display = resolved.name
        episode = resolved.name
        show_name = None
        located = locate_in_library(resolved)
        if located is not None:
            # The episode belongs to a scanned show: keep the whole show
            # as the playlist so next/previous can skip across it.
            show_name, paths, index = located
        else:
            paths = [str(resolved)]
    else:
        return 400, {"error": "need 'path' or 'show'"}
    with _play_lock:
        # Save the current playback BEFORE touching it: a failed VLC
        # launch must put it back exactly (v7's S3 save/restore
        # covered skip only — a failed Play in VLC app wiped a good
        # in-page playback and left "not playing" behind it).
        prev = dict(_playback)
        prev["playlist"] = list(_playback.get("playlist") or [])
        prev_fullscreen = get_fullscreen()
        if mode == "here":
            # Probe the file FIRST: a file the browser cannot decode
            # (DivX-era MPEG-4 video, AC3/DTS sound, any .avi) used
            # to be recorded as "playing" here while the tile sat
            # black or silent — the Dhoom symptom. Steer those to
            # VLC before touching any state, so nothing claims to be
            # playing when nothing is.
            first_path = paths[index]
            ok, reason = playable_here(first_path)
            if not ok:
                vcodec, acodec = probe_codecs(first_path)
                return 200, {"action": "play", "needs_vlc": True,
                             "playable_here": False, "reason": reason,
                             "hint": vlc_hint(reason),
                             "codecs": {"video": vcodec, "audio": acodec},
                             "playing": display, "episode": episode,
                             "mode": "here", "show": show_name,
                             "loop": loop, "fullscreen": fullscreen,
                             "now_playing": control_state()}
            stop_vlc()
            set_fullscreen(fullscreen)
            _playback.update({"mode": None, "playing": None, "show": None,
                              "playlist": [], "loop": loop, "fullscreen": fullscreen,
                              "index": 0, "paused": False})
            _playback.update({"mode": "here", "playing": display,
                              "show": show_name, "playlist": paths, "index": index})
            record_recent(show_name or "Unsorted", episode, first_path, "here")
            vcodec, acodec = probe_codecs(first_path)
            return 200, {"action": "play", "playing": display, "episode": episode,
                         "mode": "here", "show": show_name, "loop": loop,
                         "fullscreen": fullscreen, "paused": False,
                         "playable_here": True,
                         "codecs": {"video": vcodec, "audio": acodec},
                         "volume": _playback.get("volume"),
                         "now_playing": control_state()}
        # VLC plays from the chosen episode: rotate the playlist so the
        # picked episode is first, then loop the whole show from there.
        stop_vlc()
        set_fullscreen(fullscreen)
        _playback.update({"mode": None, "playing": None, "show": None,
                          "playlist": [], "loop": loop, "fullscreen": fullscreen,
                          "index": 0, "paused": False})
        launch = paths[index:] + paths[:index] if index else list(paths)
        proc = start_vlc(launch, loop, fullscreen)
        if proc is None:
            # Launch failed: put the old playback back exactly, so the
            # tile does not claim the new episode is playing when
            # nothing is — and does not lose the old one either.
            _playback.update(prev)
            set_fullscreen(prev_fullscreen)
            state = control_state()
            state["error"] = "VLC not installed (no vlc on PATH)"
            return 503, state
        _vlc["proc"] = proc
        _playback.update({"mode": "vlc", "playing": display,
                          "show": show_name, "playlist": paths, "index": index})
        record_recent(show_name or "Unsorted", episode, paths[index], "vlc")
        return 200, {"action": "play", "playing": display, "episode": episode,
                     "mode": "vlc", "show": show_name, "loop": loop,
                     "fullscreen": fullscreen, "paused": False,
                     "volume": _playback.get("volume"),
                     "now_playing": control_state()}


def stop_playback():
    """Stop BOTH players: every VLC process by name (stop_vlc) and the
    in-page player (state cleared here; the page also pauses and clears
    its <video> on the next now-playing poll). Any queued voice-control
    flag is cleared too, so a pending "next episode" cannot restart
    playback after Stop."""
    with _play_lock:
        stop_vlc()
        clear_control_flag()
        set_fullscreen(False)
        _playback.update({"mode": None, "playing": None, "show": None,
                          "playlist": [], "index": 0, "fullscreen": False,
                          "paused": False})
        state = control_state()
    state["stopped"] = True
    return state


def _refresh_vlc_state():
    """If VLC exited on its own (playlist finished without loop, user
    closed the window), drop the stale playback state. Caller holds
    _play_lock, or is a single read path that tolerates it."""
    proc = _vlc["proc"]
    if _playback.get("mode") == "vlc" and proc is not None and proc.poll() is not None:
        _vlc["proc"] = None
        _playback.update({"mode": None, "playing": None, "show": None,
                          "playlist": [], "index": 0, "paused": False})


def current_episode_name():
    """Display name of the episode at the current playlist index."""
    playlist = _playback.get("playlist") or []
    idx = _playback.get("index", 0)
    if playlist and 0 <= idx < len(playlist):
        return Path(playlist[idx]).name
    return _playback.get("playing")


def control_state():
    """The playback state the voice loop confirms from: playing, paused,
    volume — as best known. For the in-page player, volume is the target
    the dashboard was last told to use; for VLC it is the system sink
    volume (see _do_volume)."""
    _refresh_vlc_state()
    vol = _playback.get("volume")
    return {
        "playing": _playback.get("playing"),
        "episode": current_episode_name(),
        "show": _playback.get("show"),
        "mode": _playback.get("mode"),
        "paused": bool(_playback.get("paused", False)),
        "volume": vol,
        "volume_pct": (round(vol * 100) if isinstance(vol, (int, float)) else None),
        "loop": bool(_playback.get("loop", True)),
        "fullscreen": get_fullscreen(),
        "index": _playback.get("index", 0),
    }


def now_playing():
    with _play_lock:
        return control_state()


# ---------------------------------------------------------------- media control
def get_sink_volume():
    """System sink volume as 0–1, via pactl. None if pactl is missing."""
    out = run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], timeout=3)
    if not out:
        return None
    m = re.search(r"(\d+)%", out)
    if not m:
        return None
    return int(m.group(1)) / 100.0


def set_sink_volume(step):
    """Adjust the system sink volume by step ('+5%' / '-5%').
    Returns the resulting volume 0–1, or None if pactl is missing."""
    out = run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", step], timeout=3)
    if out is None:
        return None
    return get_sink_volume()


def write_control_flag(flag):
    """Write a control action for the in-page player (same atomic pattern
    as the fullscreen flag). Returns the flag with seq + timestamp."""
    flag = dict(flag)
    flag["seq"] = int(time.time() * 1000)
    flag["ts"] = time.time()
    try:
        tmp = MEDIA_CONTROL_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(flag), encoding="utf-8")
        os.replace(tmp, MEDIA_CONTROL_FILE)
    except Exception:
        pass
    return flag


def read_control_flag():
    """Pending control action for the in-page player, or None. A flag the
    dashboard never picks up goes stale after MEDIA_CONTROL_TTL seconds."""
    try:
        if not MEDIA_CONTROL_FILE.is_file():
            return None
        data = json.loads(MEDIA_CONTROL_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "action" not in data:
            return None
        if time.time() - float(data.get("ts", 0)) > MEDIA_CONTROL_TTL:
            clear_control_flag()
            return None
        return data
    except Exception:
        return None


def clear_control_flag():
    try:
        MEDIA_CONTROL_FILE.unlink()
    except FileNotFoundError:
        pass
    except Exception:
        pass


def _do_volume(action):
    """volume-up / volume-down. VLC: the SYSTEM sink volume via pactl
    (±5%) — this is not VLC-only, it turns down everything on that sink
    until turned back up. In-page: the video element's volume ±0.1,
    tracked server-side and applied by the dashboard from the flag."""
    delta = 0.1 if action == "volume-up" else -0.1
    if _playback.get("mode") == "vlc":
        step = "+5%" if action == "volume-up" else "-5%"
        new = set_sink_volume(step)
        if new is None:
            state = control_state()
            state.update({"action": action, "error": "pactl unavailable"})
            return state
        _playback["volume"] = new
        state = control_state()
        state["action"] = action
        return state
    cur = _playback.get("volume")
    if not isinstance(cur, (int, float)):
        cur = 1.0
    target = round(max(0.0, min(1.0, cur + delta)), 2)
    _playback["volume"] = target
    flag = write_control_flag({"action": action, "volume": target})
    state = control_state()
    state.update({"action": action, "control": flag})
    return state


def _do_skip(action):
    """next / previous. VLC: stop and relaunch with the playlist rotated
    to the new episode, same loop/fullscreen flags. In-page: write a flag
    (index + path + episode) for the dashboard to apply to its <video>."""
    playlist = _playback["playlist"]
    idx = _playback.get("index", 0)
    loop = bool(_playback.get("loop", True))
    if action == "next":
        if idx + 1 >= len(playlist) and not loop:
            # End of a non-looping playlist: stop.
            stop_vlc()
            _playback.update({"mode": None, "playing": None, "show": None,
                              "playlist": [], "index": 0, "paused": False})
            state = control_state()
            state.update({"action": action, "error": "end of playlist"})
            return state
        idx = (idx + 1) % len(playlist)
    else:  # previous
        if idx == 0 and not loop:
            idx = 0
        else:
            idx = (idx - 1) % len(playlist)
    ep_path = playlist[idx]
    ep_name = Path(ep_path).name
    prev_index = _playback.get("index", 0)
    prev_playing = _playback.get("playing")
    prev_paused = _playback.get("paused", False)
    _playback["index"] = idx
    _playback["playing"] = ep_name
    _playback["paused"] = False
    if _playback.get("mode") == "vlc":
        launch = playlist[idx:] + playlist[:idx]
        stop_vlc()
        proc = start_vlc(launch, loop, bool(_playback.get("fullscreen", False)))
        if proc is None:
            # Launch failed: put the old episode back, so the state
            # does not claim the new one is playing when nothing is.
            _playback["index"] = prev_index
            _playback["playing"] = prev_playing
            _playback["paused"] = prev_paused
            state = control_state()
            state.update({"action": action, "error": "VLC not installed (no vlc on PATH)"})
            return state
        _vlc["proc"] = proc
        record_recent(_playback.get("show") or "Unsorted", ep_name, ep_path, "vlc")
        state = control_state()
        state["action"] = action
        return state
    flag = write_control_flag({"action": action, "index": idx, "path": ep_path,
                               "episode": ep_name, "show": _playback.get("show")})
    record_recent(_playback.get("show") or "Unsorted", ep_name, ep_path, "here")
    state = control_state()
    state.update({"action": action, "control": flag})
    return state


def _do_pause(action):
    """pause / resume. VLC: SIGSTOP freezes the process in place (video +
    audio stop exactly where they are); SIGCONT resumes it. In-page:
    write a flag for the dashboard to apply to its <video>."""
    paused = action == "pause"
    if _playback.get("mode") == "vlc":
        proc = _vlc["proc"]
        if proc is not None and proc.poll() is None:
            try:
                proc.send_signal(signal.SIGSTOP if paused else signal.SIGCONT)
            except Exception:
                pass
        # Same ghost-audio rule as Stop: freeze/resume every VLC by
        # name, not just the tracked one, so a stray copy cannot keep
        # playing while the dashboard says paused.
        run(["pkill", "-STOP" if paused else "-CONT", "-x", "vlc"], timeout=3)
        _playback["paused"] = paused
        state = control_state()
        state["action"] = action
        return state
    flag = write_control_flag({"action": action})
    _playback["paused"] = paused
    state = control_state()
    state.update({"action": action, "control": flag})
    return state


def media_control_request(body):
    """POST /api/media-control. Returns (http_status, payload).

    The payload always carries the detail Jarvis needs to confirm the
    command by voice: next/previous -> {"playing": "<episode name>",
    "action": "next"}; pause -> {"paused": true}; resume ->
    {"paused": false}; volume-up/down -> {"volume": 0-1, "volume_pct": %}
    Volume works even with nothing playing (it is the system volume in
    VLC mode, the tracked video volume in here mode). Everything else
    needs something playing, or it answers {"error": "nothing playing"}.
    """
    if not isinstance(body, dict):
        return 400, {"error": "JSON object expected"}
    action = body.get("action")
    if action == "clear":
        clear_control_flag()
        state = control_state()
        state["action"] = "clear"
        return 200, state
    if action not in MEDIA_CONTROL_ACTIONS:
        return 400, {"error": "unknown action: %s (want one of %s)"
                     % (action, ", ".join(MEDIA_CONTROL_ACTIONS))}
    with _play_lock:
        _refresh_vlc_state()
        if action in ("volume-up", "volume-down"):
            return 200, _do_volume(action)
        if _playback.get("mode") is None or not _playback.get("playlist"):
            state = control_state()
            state.update({"action": action, "error": "nothing playing"})
            return 200, state
        if action in ("next", "previous"):
            return 200, _do_skip(action)
        return 200, _do_pause(action)


def apply_fullscreen(on):
    """POST /api/fullscreen. Stores the flag; if VLC is the active player,
    relaunches it with (or without) --fullscreen on the same playlist.
    Relaunches from the CURRENT episode, not the first one: the old code
    restarted the whole show from episode 1 every time fullscreen was
    toggled. (The episode itself still restarts from its beginning —
    VLC cannot resume mid-episode on a relaunch.)"""
    on = bool(on)
    with _play_lock:
        set_fullscreen(on)
        if _playback.get("mode") == "vlc" and _playback.get("playlist"):
            paths = list(_playback["playlist"])
            idx = _playback.get("index", 0)
            if 0 < idx < len(paths):
                paths = paths[idx:] + paths[:idx]
            loop = bool(_playback.get("loop", True))
            stop_vlc()
            proc = start_vlc(paths, loop, on)
            if proc is not None:
                _vlc["proc"] = proc
    return {"fullscreen": on}


# ---------------------------------------------------------------- webcam stream
# LIVE MJPEG stream for the dashboard's webcam (beside the media player).
# GET /api/webcam-stream?cam=laptop|c270 serves multipart/x-mixed-replace,
# the format a plain <img> tag plays on iOS Safari — so the feed works on
# the laptop, the iPhone and the iPad. One ffmpeg subprocess per camera
# captures MJPEG at 640x480, ~10 fps; a reader thread keeps only the latest
# frame in memory. The grabber starts on the first client and stops ~10 s
# after the last client leaves, so the camera (and its LED) is not left on
# when nobody is watching. WEBCAM_CMD overrides the ffmpeg binary — a test
# hook only, so the stream can be exercised on a machine with no camera.
WEBCAM_CMD = os.environ.get("WEBCAM_CMD", "ffmpeg")
WEBCAM_CAMS = {
    "laptop": "/dev/video0",
    "c270": "/dev/video2",
}
WEBCAM_IDLE_STOP_S = 10   # stop ffmpeg after this long with no clients
WEBCAM_START_WAIT_S = 2.5  # wait this long for the first frame at startup
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"


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

    def _spawn(self, with_mjpeg):
        cmd = [WEBCAM_CMD]
        if with_mjpeg:
            cmd += ["-f", "v4l2", "-input_format", "mjpeg"]
        else:
            cmd += ["-f", "v4l2"]
        cmd += ["-video_size", "640x480", "-framerate", "10",
                "-i", self.device, "-f", "mjpeg", "-q:v", "5", "-"]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL,
                                stdin=subprocess.DEVNULL)

    def _reader_loop(self, proc):
        buf = bytearray()
        # read1() returns as soon as any data is available; a plain read()
        # would block until its buffer fills, which would throttle the
        # stream to one burst every second or so instead of ~10 fps.
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
                            del buf[:-1]  # keep a possible split SOI at the tail
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
        frames are actually flowing. A grabber that is still starting
        (or failing to start) has a live process but no frames yet —
        calling that "live" put "live — laptop" on the tile for a
        camera that was never going to produce a picture."""
        with self._lock:
            return (self._clients > 0 and self._proc is not None
                    and self._proc.poll() is None
                    and self._latest is not None)

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
        now = time.time()
        with _webcam_lock:
            grabbers = list(_webcam_grabbers.values())
        for g in grabbers:
            g.maybe_stop_idle(now)


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


def webcam_streaming():
    """Which camera (if any) is streaming right now. Used by
    collect_webcam so the page label tells the truth after the server
    falls back to the other camera."""
    with _webcam_lock:
        grabbers = list(_webcam_grabbers.values())
    for g in grabbers:
        try:
            if g.is_streaming():
                return g.key, g.device
        except Exception:
            continue
    return None, None


_webcam_snap_at = 0.0


def _maybe_save_webcam_snapshot():
    """Keep the Webcam tile's still alive: when a live stream is
    running, save its latest frame as webcam.jpg (throttled to once
    every 30 s). Nothing ever wrote webcam.jpg before, so the tile
    always said 'no snapshot yet' even while the live feed worked."""
    global _webcam_snap_at
    now = time.time()
    if now - _webcam_snap_at < 30:
        return
    with _webcam_lock:
        grabbers = list(_webcam_grabbers.values())
    for g in grabbers:
        cur = g.latest()
        if cur is None:
            continue
        frame, _ts = cur
        snap = BASE / "webcam.jpg"
        try:
            tmp = snap.with_suffix(".jpg.tmp")
            tmp.write_bytes(frame)
            os.replace(tmp, snap)
            _webcam_snap_at = now
        except Exception:
            pass
        return


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
            # The client went away mid-reply (a slow media scan used to
            # make this routine). That is not a server error and must
            # not raise out of the handler — there is nobody left to
            # tell, and the error path must never wipe the shows.
            pass

    def _send_json(self, status, obj):
        try:
            payload = json.dumps(obj).encode("utf-8")
        except Exception:
            payload = b"{}"
        self._send(status, payload, "application/json")

    def _send_file(self, path):
        """Serve a video file, with HTTP Range support (206 Partial Content)
        so the browser's <video> element can seek and stream it."""
        try:
            size = path.stat().st_size
        except Exception:
            self._send(404, "file not found", "text/plain")
            return
        ctype = VIDEO_TYPES.get(path.suffix.lower(), "application/octet-stream")
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

    def _serve_webcam_stream(self, cam):
        """GET /api/webcam-stream — live MJPEG multipart stream for the
        dashboard's webcam beside the media player. Falls back to the other
        camera if the requested one fails to start."""
        if cam not in WEBCAM_CAMS:
            cam = "laptop"
        grabber = get_webcam_grabber(cam)
        ok, err = grabber.acquire()
        device = WEBCAM_CAMS[cam]
        if not ok:
            other = "c270" if cam == "laptop" else "laptop"
            grabber = get_webcam_grabber(other)
            ok, err = grabber.acquire()
            device = WEBCAM_CAMS[other]
            cam = other
        if not ok:
            self._send_json(503, {"error": err or "webcam unavailable"})
            return
        try:
            self.send_response(200)
            self.send_header("Content-Type",
                             "multipart/x-mixed-replace; boundary=frame")
            self.send_header("X-Webcam-Device", device)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            last_ts = 0.0
            last_sent_at = 0.0
            have_frame = False
            while True:
                grabber.wait_frame(last_ts, timeout=0.1)
                cur = grabber.latest()
                if cur is None:
                    break  # grabber died before any frame: end, client retries
                frame, ts = cur
                now = time.time()
                if ts > last_ts or (have_frame and now - last_sent_at > 2.0):
                    part = (b"--frame\r\nContent-Type: image/jpeg\r\n"
                            b"Content-Length: %d\r\n\r\n" % len(frame)) + frame + b"\r\n"
                    try:
                        self.wfile.write(part)
                        self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        break
                    last_ts = ts
                    have_frame = True
                    last_sent_at = now
                if grabber.is_dead():
                    break  # ffmpeg died: end the stream so the client retries
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            grabber.release()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        if path in ("/", "/index.html"):
            index = BASE / "index.html"
            if index.is_file():
                self._send(200, index.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send(500, "index.html not found next to server.py", "text/plain")
        elif path == "/api/status":
            try:
                payload = json.dumps(get_status_snapshot()).encode("utf-8")
                self._send(200, payload, "application/json")
            except Exception as exc:  # never crash the dashboard
                self._send(500, json.dumps({"error": str(exc)}), "application/json")
        elif path == "/api/voice":
            try:
                payload = json.dumps(collect_voice()).encode("utf-8")
                self._send(200, payload, "application/json")
            except Exception as exc:  # never crash the dashboard
                self._send(200, json.dumps({"state": "idle", "events": []}), "application/json")
        elif path == "/api/picture":
            img = latest_image(PICTURE_DIR)
            if img is None:
                self._send(404, "no picture yet", "text/plain")
            else:
                self._send(200, img.read_bytes(), IMAGE_TYPES.get(img.suffix.lower(), "image/png"))
        elif path == "/api/webcam":
            snap = BASE / "webcam.jpg"
            if not snap.is_file():
                self._send(404, "no webcam snapshot yet", "text/plain")
            else:
                self._send(200, snap.read_bytes(), "image/jpeg")
        elif path == "/api/webcam-stream":
            cam = (query.get("cam") or ["laptop"])[0]
            self._serve_webcam_stream(cam)
        elif path == "/api/media":
            try:
                force = (query.get("refresh") or ["0"])[0] == "1"
                data = scan_media(force=force)
                data["recent"] = load_recent()
                self._send_json(200, data)
            except Exception as exc:  # never crash the dashboard
                # A failed scan never wipes the shows: answer with the
                # last good list if there is one, marked stale.
                with _media_lock:
                    cached = _media_cache["data"]
                if cached is not None:
                    data = dict(cached)
                    data["pinned"] = load_slots()["pinned"]
                    data["slots"] = load_slots()["slots"]
                    data["recent"] = load_recent()
                    data["stale"] = True
                    data["error"] = str(exc)
                    self._send_json(200, data)
                else:
                    self._send_json(200, {"mounted": _any_root_walkable(),
                                          "root": str(MEDIA_DIR),
                                          "shows": [], "pinned": list(DEFAULT_SLOTS["pinned"]),
                                          "slots": list(DEFAULT_SLOTS["slots"]),
                                          "roots": [str(r) for r in MEDIA_DIRS],
                                          "sources": _sources_snapshot(),
                                          "recent": load_recent(),
                                          "error": str(exc), "stale": True})
        elif path == "/api/now-playing":
            self._send_json(200, now_playing())
        elif path == "/api/media-control":
            # control_state() refreshes (and can clear) the VLC state,
            # so read it under the play lock like every other path that
            # touches playback state.
            with _play_lock:
                self._send_json(200, {"pending": read_control_flag(),
                                      "state": control_state()})
        elif path == "/api/fullscreen":
            self._send_json(200, {"fullscreen": get_fullscreen()})
        elif path == "/api/stream":
            raw = (query.get("path") or [None])[0]
            if not raw:
                self._send(400, "missing ?path=", "text/plain")
                return
            resolved = media_allowed(raw)
            if resolved is None:
                self._send(403, "path not under the media dir or ~/Videos", "text/plain")
                return
            if not resolved.is_file():
                self._send(404, "file not found", "text/plain")
                return
            # The stream endpoint is for video. Without this it would
            # serve any file under the media drive (documents, photos,
            # backups) to anyone on the tailnet.
            if resolved.suffix.lower() not in VIDEO_EXTS:
                self._send(415, "not a video file", "text/plain")
                return
            self._send_file(resolved)
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/play":
            body = self._read_json_body()
            if body is None:
                self._send_json(400, {"error": "invalid JSON body"})
                return
            status, payload = play_request(body)
            self._send_json(status, payload)
        elif path == "/api/stop":
            self._send_json(200, stop_playback())
        elif path == "/api/media-control":
            body = self._read_json_body()
            if body is None:
                self._send_json(400, {"error": "invalid JSON body"})
                return
            status, payload = media_control_request(body)
            self._send_json(status, payload)
        elif path == "/api/fullscreen":
            body = self._read_json_body()
            if body is None or "on" not in body:
                self._send_json(400, {"error": 'need {"on": true|false}'})
                return
            self._send_json(200, apply_fullscreen(body["on"]))
        else:
            self._send(404, "not found", "text/plain")


def main():
    threading.Thread(target=_status_worker, daemon=True).start()
    threading.Thread(target=_media_worker, daemon=True).start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.daemon_threads = True
    print("Jarvis dashboard on http://%s:%d  (Ctrl-C to stop)" % (HOST, PORT))
    print("Serving from %s ; pictures from %s ; media from %s" % (BASE, PICTURE_DIR, ", ".join(str(r) for r in MEDIA_DIRS)))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
