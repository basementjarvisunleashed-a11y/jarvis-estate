"""Local Jarvis voice gate. Run with Python 3.13 (has SpeechBrain).
is_principal(wav_path) -> (bool, score). Uses the EXISTING enrolled profile; never re-enrolls.
CLI:  python voice_gate.py file.wav      -> prints JSON
      python voice_gate.py --serve       -> reads wav paths on stdin, writes one JSON line each
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, json
# VG-1 2026-10-27: voice-profile data moved OUT of Downloads (which the orchestrator's file
# tools can read/move) into C:\Jarvis\voiceprint (ACL: owner, SYSTEM, Administrators only).
# profiles.json, take*.wav and pretrained_models must never leave this laptop.
VOICEPRINT = r"C:\Jarvis\voiceprint"
MODEL_DIR = os.path.join(VOICEPRINT, "pretrained_models", "spkrec-ecapa-voxceleb")
PROFILE = os.path.join(VOICEPRINT, "profiles.json")
CONFIG = r"C:\Jarvis\voice_gate.json"
LOG = r"C:\Jarvis\voice_gate.log"
_warn = None  # VG-2a: set when voice_gate.json is missing/corrupt; also reported in the "ready" line

def _log_warning(msg):
    """VG-2a 2026-10-27: never fall back silently -- write to voice_gate.log and stderr."""
    global _warn
    _warn = msg
    try:
        import datetime
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("%s WARNING %s\n" % (datetime.datetime.now().isoformat(timespec="seconds"), msg))
    except Exception:
        pass
    print("voice_gate WARNING: " + msg, file=sys.stderr, flush=True)
DEFAULT_THRESHOLD = 0.45  # provisional, UNCALIBRATED — pending calibration
_m = _ref = _thr = None

def _load():
    global _m, _ref, _thr
    if _m is None:
        import numpy as np
        from speechbrain.inference.speaker import EncoderClassifier
        _m = EncoderClassifier.from_hparams(source=MODEL_DIR, savedir=MODEL_DIR)
        p = json.load(open(PROFILE))["primary"]
        _ref = np.asarray(p["embedding"], dtype="float32"); _ref /= np.linalg.norm(_ref)
        try: _thr = float(json.load(open(CONFIG))["threshold"])
        except Exception as ex:  # VG-2a: missing/corrupt config -> default, but LOUDLY
            _thr = DEFAULT_THRESHOLD
            _log_warning("voice_gate.json unreadable (%s: %s); using default threshold %.2f"
                         % (type(ex).__name__, ex, DEFAULT_THRESHOLD))
    return _m

def score(wav_path):
    import numpy as np, soundfile as sf, torch
    m = _load()
    d, sr = sf.read(wav_path, dtype="float32")
    if d.ndim > 1: d = d.mean(axis=1)
    if sr != 16000:
        n = int(len(d) * 16000 / sr); d = np.interp(np.linspace(0, len(d) - 1, n), np.arange(len(d)), d).astype("float32")
    e = m.encode_batch(torch.from_numpy(d).unsqueeze(0)).squeeze().detach().cpu().numpy()
    return float(np.dot(e, _ref) / np.linalg.norm(e))

def is_principal(wav_path):
    s = score(wav_path)
    return s >= _thr, s

if __name__ == "__main__":
    if sys.argv[1:] == ["--serve"]:
        _load(); print(json.dumps({"ready": True, "threshold": _thr, "warning": _warn}), flush=True)
        for line in sys.stdin:
            try: ok, s = is_principal(line.strip()); print(json.dumps({"ok": ok, "score": s}), flush=True)
            except Exception as ex: print(json.dumps({"ok": False, "score": None, "error": str(ex)}), flush=True)
    else:
        import time; t = time.time(); _load(); t1 = time.time()
        ok, s = is_principal(sys.argv[1])
        print(json.dumps({"ok": ok, "score": round(s, 4), "threshold": _thr, "load_s": round(t1 - t, 2), "score_s": round(time.time() - t1, 3)}))
