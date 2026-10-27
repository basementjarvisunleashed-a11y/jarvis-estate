"""Local Jarvis voice loop: Maono mic -> Whisper -> voice gate -> 8080 orchestrator -> Piper (Alan).
Does NOT auto-start. Usage (venv python):
  jarvis_voice.py loop [seconds]             live loop (only when the operator says so)
  jarvis_voice.py test WAV [--bypass-gate]   offline: one file through the pipeline, reply to out\\reply.wav
No delete capability by design."""
import warnings; warnings.filterwarnings("ignore")
import sys, os, re, json, time, subprocess, urllib.request, wave
sys.path.insert(0, r"C:\Jarvis")
import jarvis as J   # reuse dev(), transcribe(), MIC/SPK, VOICE (same Whisper, same devices)
ORCH = "http://127.0.0.1:8080/jarvis"
GATE_PY = r"C:\Users\<user>\AppData\Local\Programs\Python\Python313\python.exe"  # has SpeechBrain
GATE = r"C:\Jarvis\voice_gate.py"
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
        self.p = subprocess.Popen([GATE_PY, GATE, "--serve"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.info = json.loads(self.p.stdout.readline())
    def check(self, path):
        self.p.stdin.write(path + "\n"); self.p.stdin.flush()
        r = json.loads(self.p.stdout.readline()); return r["ok"], r["score"]
    def close(self):
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
    d, sr = sf.read(path); sd.play(d, sr, device=J.dev(J.SPK, "output")); sd.wait()

def record(seconds, path):
    import sounddevice as sd, soundfile as sf
    sr = 16000
    a = sd.rec(int(seconds * sr), samplerate=sr, channels=2, device=J.dev(J.MIC, "input")); sd.wait()
    sf.write(path, a.mean(axis=1), sr); return path

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
    if MUTATING_RE.search(text) and not confirm(gate, speak):  # VG-2c
        res["action"] = "unconfirmed"; res["t"] = t; return res
    s = time.time(); reply = orchestrate(text); t["orchestrator_s"] = time.time() - s
    s = time.time(); tts(reply, out_wav); t["piper_s"] = time.time() - s
    if speak: s = time.time(); play(out_wav); t["play_s"] = time.time() - s
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
