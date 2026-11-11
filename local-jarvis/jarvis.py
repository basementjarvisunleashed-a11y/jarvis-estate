"""Local Jarvis helper. Commands: list, play, pause, ask, say, listen, chat. No delete capability by design."""
import warnings; warnings.filterwarnings("ignore")
import sys, os, json, subprocess, urllib.request, wave
BASE = os.path.expanduser("~/Jarvis")
MODEL = os.environ.get("JARVIS_MODEL", "qwen9b-abliterated")
VOICE = os.path.join(BASE, "voices", "en_GB-alan-medium.onnx")
VLC = "vlc"  # Linux: VLC on PATH (was a Windows path)
# Device priority (HgX, 2026-11-05): laptop built-in FIRST, MaonoCaster
# SECOND, C270 THIRD. Nothing plugged in? The laptop alone still works.
# dev() tries each alias in order and takes the first device that exists.
MIC = ["MAONO", "AUAM200", "HDA Intel PCH", "Built-in Audio", "USB Device 0x46d"]
SPK = ["HDA Intel PCH", "Built-in Audio",
       "MAONO", "AUAM200"]
VLC_HTTP = ("127.0.0.1", 8090, os.environ.get("VLC_HTTP_PASSWORD", "CHANGE_ME"))  # VLC web interface, localhost only

def dev(name, kind):
    """Resolve a device by name, or the first name in a list that exists.

    Linux: host APIs are ALSA / PulseAudio / JACK — never Windows "MME"
    (the old check matched nothing on Kali, so no device was ever found).
    Prefers PulseAudio (PipeWire) when the same hardware appears twice.
    Tries prefix matches first, then substring matches.
    """
    import sounddevice as sd
    names = [name] if isinstance(name, str) else list(name)
    devices = list(sd.query_devices())
    apis = {}
    for i, d in enumerate(devices):
        try:
            apis[i] = sd.query_hostapis(d["hostapi"])["name"]
        except Exception:
            apis[i] = ""
    def _match(prefix):
        for mode in ("prefix", "substring"):
            cands = []
            for i, d in enumerate(devices):
                if d[f"max_{kind}_channels"] <= 0:
                    continue
                hit = (d["name"].startswith(prefix) if mode == "prefix"
                       else prefix.lower() in d["name"].lower())
                if hit:
                    cands.append(i)
            if cands:
                for pref in ("PulseAudio", "ALSA", "JACK"):
                    for i in cands:
                        if apis.get(i) == pref:
                            return i
                return cands[0]
        return None
    for n in names:
        hit = _match(n)
        if hit is not None:
            return hit
    raise SystemExit(f"device not found: {names}")

def list_folder(p="."):
    for e in sorted(os.scandir(p), key=lambda e: (not e.is_dir(), e.name.lower())):
        print(e.name + ("/" if e.is_dir() else ""))

def vlc_cmd(cmd):
    import base64
    h, port, pw = VLC_HTTP
    req = urllib.request.Request(f"http://{h}:{port}/requests/status.json?command={cmd}")
    req.add_header("Authorization", "Basic " + base64.b64encode(f":{pw}".encode()).decode())
    return json.load(urllib.request.urlopen(req, timeout=3)).get("state")

def play(target=None):
    try:
        if target:
            from urllib.parse import quote
            from pathlib import Path
            print(vlc_cmd("in_play&input=" + quote(Path(target).resolve().as_uri() if os.path.exists(target) else target, safe="")))
        else:
            print(vlc_cmd("pl_play"))
    except Exception:
        args = [VLC, "--extraintf", "http", "--http-host", VLC_HTTP[0], "--http-port", str(VLC_HTTP[1]), "--http-password", VLC_HTTP[2]]
        subprocess.Popen(args + ([target] if target else []))
        print("started VLC")

def pause():
    print(vlc_cmd("pl_pause"))

def ask(prompt):
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False,
                       "system": "You are Jarvis, a concise local assistant."}).encode()
    r = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:11434/api/generate", body, {"Content-Type": "application/json"}), timeout=300)
    return json.load(r)["response"].strip()

def tts(text, path=os.path.join(BASE, "out", "say.wav")):
    from piper import PiperVoice
    v = PiperVoice.load(VOICE)
    with wave.open(path, "wb") as w:
        v.synthesize_wav(text, w)
    return path

def say(text, play_it=True):
    p = tts(text)
    if play_it:
        import sounddevice as sd, soundfile as sf
        d, sr = sf.read(p)
        if sr != 48000:
            import numpy as np
            n = int(len(d) * 48000 / sr)
            x = np.linspace(0, len(d) - 1, n)
            d = np.interp(x, np.arange(len(d)), d).astype("float32") if d.ndim == 1 else np.stack([np.interp(x, np.arange(len(d)), d[:, c]) for c in range(d.shape[1])], axis=1).astype("float32")
            sr = 48000
        sd.play(d, sr, device=dev(SPK, "output")); sd.wait()
    return p

_W = None
def transcribe(path):
    global _W
    from faster_whisper import WhisperModel
    if _W is None:
        try: _W = WhisperModel("small.en", device="cuda", compute_type="int8_float16")
        except Exception: _W = WhisperModel("small.en", device="cpu", compute_type="int8")
    import soundfile as sf, numpy as np
    d, sr = sf.read(path, dtype="float32")
    if d.ndim > 1: d = d.mean(axis=1)
    if sr != 16000:
        n = int(len(d) * 16000 / sr); d = np.interp(np.linspace(0, len(d) - 1, n), np.arange(len(d)), d).astype("float32")
    segs, _ = _W.transcribe(d, vad_filter=True)
    return " ".join(s.text.strip() for s in segs)

def listen(seconds=5, path=os.path.join(BASE, "out", "mic.wav")):
    import sounddevice as sd, soundfile as sf
    sr = 48000
    idx = dev(MIC, "input")
    print(f"Listening {seconds}s on {sd.query_devices()[idx]['name']}...")
    a = sd.rec(int(seconds * sr), samplerate=sr, channels=2, device=idx); sd.wait()
    sf.write(path, a.mean(axis=1), sr)  # both mixer channels (2 mics) summed to mono
    return transcribe(path)

def chat(seconds=5):
    while True:
        t = listen(seconds); print("You:", t)
        if not t or t.lower().strip(" .!") in ("stop", "exit", "goodbye"): break
        a = ask(t); print("Jarvis:", a); say(a)

if __name__ == "__main__":
    c, a = (sys.argv[1] if len(sys.argv) > 1 else "help"), sys.argv[2:]
    if c == "list": list_folder(*(a[:1]))
    elif c == "play": play(a[0] if a else None)
    elif c == "pause": pause()
    elif c == "ask": print(ask(" ".join(a)))
    elif c == "say": print(say(" ".join(a)))
    elif c == "tts": print(tts(" ".join(a)))
    elif c == "transcribe": print(transcribe(a[0]))
    elif c == "listen": print(listen(int(a[0]) if a else 5))
    elif c == "chat": chat(int(a[0]) if a else 5)
    else: print(__doc__)

