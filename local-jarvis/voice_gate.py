"""Local Jarvis voice gate. Run with Python 3.13 (has SpeechBrain).
is_principal(wav_path) -> (bool, score). Uses the EXISTING enrolled profile; never re-enrolls.
CLI:  python voice_gate.py file.wav      -> prints JSON
      python voice_gate.py --serve       -> reads wav paths on stdin, writes one JSON line each
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, json
DL = r"C:\Users\<user>\Downloads"
MODEL_DIR = os.path.join(DL, "pretrained_models", "spkrec-ecapa-voxceleb")
PROFILE = os.path.join(DL, "profiles.json")
CONFIG = r"C:\Jarvis\voice_gate.json"
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
        except Exception: _thr = DEFAULT_THRESHOLD
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
        _load(); print(json.dumps({"ready": True, "threshold": _thr}), flush=True)
        for line in sys.stdin:
            try: ok, s = is_principal(line.strip()); print(json.dumps({"ok": ok, "score": s}), flush=True)
            except Exception as ex: print(json.dumps({"ok": False, "score": None, "error": str(ex)}), flush=True)
    else:
        import time; t = time.time(); _load(); t1 = time.time()
        ok, s = is_principal(sys.argv[1])
        print(json.dumps({"ok": ok, "score": round(s, 4), "threshold": _thr, "load_s": round(t1 - t, 2), "score_s": round(time.time() - t1, 3)}))
