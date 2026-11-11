"""Local Jarvis voice loop: Maono mic -> Whisper -> voice gate -> 8080 orchestrator -> Piper (Alan).
Does NOT auto-start. Usage (venv python):
  jarvis_voice.py loop [seconds]             live loop (only when the operator says so)
  jarvis_voice.py test WAV [--bypass-gate]   offline: one file through the pipeline, reply to out/reply.wav
No delete capability by design."""
import warnings; warnings.filterwarnings("ignore")
import sys, os, re, json, time, subprocess, urllib.request, wave
sys.path.insert(0, os.path.expanduser("~/Jarvis"))
import jarvis as J   # reuse dev(), transcribe(), MIC/SPK, VOICE (same Whisper, same devices)
ORCH = "http://127.0.0.1:8080/jarvis"
# SAF-15: Kali paths. The gate mode is explicit instead of "whatever happens
# when a Windows path fails": off = the 2026-11-05 decision (pass-through,
# the default); on = enforce, and refuse everyone if the gate cannot start.
GATE_PY = os.environ.get("JARVIS_GATE_PY") or sys.executable  # needs SpeechBrain
GATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_gate.py")
GATE_MODE = (os.environ.get("JARVIS_VOICE_GATE") or "off").strip().lower()
OUT = os.path.join(J.BASE, "out")
# jarvis.py tries CUDA first, but cublas64_12.dll is missing on this laptop, so it fails at first use.
# Preload the same Whisper (small.en) on CPU unless JARVIS_WHISPER_DEVICE=cuda.
def _whisper():
    if J._W is None:
        from faster_whisper import WhisperModel
        if os.environ.get("JARVIS_WHISPER_DEVICE") == "cuda":
            J._W = WhisperModel("small.en", device="cuda", compute_type="int8_float16")
        else:
            J._W = WhisperModel("small.en", device="cpu", compute_type="int8")
_whisper()

class Gate:
    def __init__(self):
        # Dropped on 2026-11-05. JARVIS_VOICE_GATE=off keeps that pass-through.
        self.p = None
        self.enforce = GATE_MODE != "off"
        if not self.enforce:
            self.info = {"gate": "off", "why": "voice gate off; every speaker is approved"}
            print("Voice gate OFF: every speaker is approved (JARVIS_VOICE_GATE=on to enforce).", file=sys.stderr)
            return
        try:
            self.p = subprocess.Popen([GATE_PY, GATE, "--serve"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL, text=True, bufsize=1)
            self.info = json.loads(self.p.stdout.readline())
        except Exception:
            self.p = None
            self.info = {"gate": "failed", "enforce": True}   # fail closed
            print("Voice gate could not start: refusing every speaker.", file=sys.stderr)
    def check(self, path):
        if self.p is None:
            return (False, 0.0) if self.enforce else (True, 1.0)
        self.p.stdin.write(path + "\n"); self.p.stdin.flush()
        r = json.loads(self.p.stdout.readline()); return r["ok"], r["score"]
    def close(self):
        if self.p is None:
            return
        try: self.p.stdin.close(); self.p.wait(5)
        except Exception: self.p.kill()

def orchestrate(text):
    body = json.dumps({"text": text}).encode()
    r = urllib.request.urlopen(urllib.request.Request(ORCH, body, {"Content-Type": "application/json"}), timeout=120)
    return json.load(r).get("reply", "")

_V = None
def tts(text, path):
    global _V
    from piper import PiperVoice
    if _V is None: _V = PiperVoice.load(J.VOICE)
    with wave.open(path, "wb") as w: _V.synthesize_wav(text, w)
    return path

def play(path):
    import sounddevice as sd, soundfile as sf
    import numpy as np
    d, sr = sf.read(path)
    if sr != 48000:  # Piper speaks at 22050; the speakers only take 48000
        n = int(len(d) * 48000 / sr)
        x = np.linspace(0, len(d) - 1, n)
        if d.ndim > 1:
            d = np.stack([np.interp(x, np.arange(len(d)), d[:, c]) for c in range(d.shape[1])], axis=1).astype("float32")
        else:
            d = np.interp(x, np.arange(len(d)), d).astype("float32")
        sr = 48000
    sd.play(d, sr, device=J.dev(J.SPK, "output")); sd.wait()

def record(seconds, path):
    import sounddevice as sd, soundfile as sf
    sr = 48000  # ALSA hardware rate: the mic refuses 16000 (PortAudio has no resampler)
    try:
        a = sd.rec(int(seconds * sr), samplerate=sr, channels=2, device=J.dev(J.MIC, "input")); sd.wait()
    except Exception:  # mono-only mic (C270): fall back to one channel
        a = sd.rec(int(seconds * sr), samplerate=sr, channels=1, device=J.dev(J.MIC, "input")); sd.wait()
    sf.write(path, a.mean(axis=1) if a.ndim > 1 else a, sr); return path

# --- VG-2c 2026-10-27: replay mitigation -------------------------------------------
# A recording of HgX could pass the speaker gate. For commands that look like they
# change something (file_move, git_commit, VLC control, verdict approve/deny), Jarvis
# asks "Say confirm" and only proceeds on a SECOND, fresh clip that (1) passes the
# gate and (2) Whisper hears as "confirm", within CONFIRM_WINDOW_S. A replayed
# single command clip cannot answer the prompt. Read-only questions skip this.
MUTATING_RE = re.compile(r"\b(move|rename|commit|play|pause|resume|stop|next|skip|previous|"
                         r"volume|louder|quieter|softer|mute|approve|deny|verdict)\b", re.IGNORECASE)
CONFIRM_WINDOW_S = 15

def confirm(gate, speak, secs=4):
    """Return True only for a gated, spoken 'confirm' within the window."""
    if not speak:
        return False  # offline test mode cannot answer the prompt -> refuse
    t0 = time.time()
    play(tts("Say confirm to go ahead.", os.path.join(OUT, "confirm_prompt.wav")))
    wav = record(secs, os.path.join(OUT, "confirm.wav"))
    ok, _ = gate.check(wav)
    if not ok or time.time() - t0 > CONFIRM_WINDOW_S:
        return False
    return "confirm" in J.transcribe(wav).lower()

# --- Patch v5 (rebuilt 2026-11-06): deterministic dispatcher ----------------
# Runs BEFORE the VG-2c confirm gate and BEFORE the model, so commands that
# act (Firefox, terminal, VLC) are no longer killed by "unconfirmed" and no
# longer left to the model to merely talk about. Risky commands (move,
# commit, verdict) are NOT dispatched here, so they still need confirm.
def _vlc_running():
    try:
        return subprocess.run(["pgrep", "-x", "vlc"],
                              capture_output=True).returncode == 0
    except Exception:
        return False

def _sopranos_dir():
    import glob
    import os as _os
    neat = os.path.join(os.environ.get("MEDIA_DIR", "/mnt/media"), "TV SHOWS", "THE SOPRANOS", "The Sopranos")
    if _os.path.isdir(neat):
        return neat
    for cand in glob.glob(os.path.join(os.environ.get("MEDIA_DIR", "/mnt/media"), "TV SHOWS", "**", "The Sopranos"), recursive=True):
        if _os.path.isdir(cand):
            return cand
    return None

def dispatch(text):
    t = (text or "").lower().strip()
    if t.strip(" .!") in ("stop", "exit", "goodbye"):
        return {"action": "stop", "reply": "Goodbye, sir."}
    if "open fire" in t or "open firefox" in t or t.startswith("firefox"):
        subprocess.Popen(["firefox"], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        return {"action": "dispatched", "reply": "Opening Firefox, sir."}
    if ("open a terminal" in t or "open terminal" in t
            or "open the terminal" in t):
        term = None
        for cand in ("xfce4-terminal", "gnome-terminal", "konsole", "xterm"):
            term = shutil.which(cand)
            if term:
                break
        if not term:
            return {"action": "dispatched",
                    "reply": "I could not find a terminal to open, sir."}
        subprocess.Popen([term], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        return {"action": "dispatched", "reply": "Opening a terminal, sir."}
    if "vlc" in t or "sopranos" in t:
        if "play" in t or "vlc on" in t or "sopranos" in t:
            d = _sopranos_dir()
            if d is None:
                return {"action": "dispatched",
                        "reply": "The Sopranos drive is not mounted, sir."}
            if _vlc_running():
                return {"action": "dispatched",
                        "reply": "VLC is already playing, sir."}
            subprocess.Popen(["vlc", "--loop", d],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return {"action": "dispatched",
                    "reply": "Playing the Sopranos, sir."}
    if "list" in t and "file" in t:
        home = os.path.expanduser("~")
        try:
            names = sorted(os.listdir(home))[:12]
        except Exception:
            names = []
        if names:
            return {"action": "dispatched",
                    "reply": "Here are the files in your home folder: "
                             + ", ".join(names) + "."}
        return {"action": "dispatched",
                "reply": "Your home folder is empty, sir."}
    return None

def handle(wav, gate, out_wav, speak, bypass=False):
    t = {}; s = time.time()
    # VG-4 2026-10-27: gate FIRST; other people's speech is never transcribed.
    ok, score = gate.check(wav); t["gate_s"] = time.time() - s
    res = {"text": "", "principal": ok, "score": score}
    if not ok and not bypass:
        res["action"] = "ignored"; res["t"] = t; return res
    s = time.time(); text = J.transcribe(wav); t["whisper_s"] = time.time() - s
    res["text"] = text
    if not text.strip():
        res["action"] = "ignored"; res["t"] = t; return res
    d = dispatch(text)
    if d is not None:
        s = time.time(); tts(d["reply"], out_wav); t["piper_s"] = time.time() - s
        if speak: s = time.time(); play(out_wav); t["play_s"] = time.time() - s
        res.update(action=d.get("action", "dispatched"), reply=d["reply"], wav=out_wav, t=t); return res
    if MUTATING_RE.search(text) and not confirm(gate, speak):  # VG-2c
        res["action"] = "unconfirmed"; res["t"] = t; return res
    s = time.time(); reply = orchestrate(text); t["orchestrator_s"] = time.time() - s
    s = time.time(); tts(reply, out_wav); t["piper_s"] = time.time() - s
    if speak and reply: s = time.time(); play(out_wav); t["play_s"] = time.time() - s
    res.update(reply=reply, wav=out_wav, t=t); return res

def main():
    c, a = (sys.argv[1] if len(sys.argv) > 1 else "help"), sys.argv[2:]
    if c == "test":
        s = time.time(); g = Gate(); J.transcribe(a[0]); warm = time.time() - s   # warm models
        try:
            r = handle(a[0], g, os.path.join(OUT, "reply.wav"), speak=False, bypass="--bypass-gate" in a)
        finally: g.close()
        r["warmup_s"] = warm; r["t"] = {k: round(v, 3) for k, v in r["t"].items()}
        print(json.dumps(r, indent=1))
    elif c == "loop":
        secs = int(a[0]) if a else 5; g = Gate(); print("Voice loop on. Say 'stop' to end.")
        try:
            while True:
                r = handle(record(secs, os.path.join(OUT, "mic.wav")), g, os.path.join(OUT, "reply.wav"), speak=True)
                print(json.dumps({k: r.get(k) for k in ("text", "principal", "score", "reply", "action")}))
                if r["principal"] and r["text"].lower().strip(" .!") in ("stop", "exit", "goodbye"): break
        finally: g.close()
    else: print(__doc__)

if __name__ == "__main__": main()
