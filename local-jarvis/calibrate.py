"""Voice-gate calibration (VG-2b, 2026-10-27). Run with system Python 3.13 (has SpeechBrain):
  py -3.13 C:\\Jarvis\\calibrate.py record me 8       record 8 fresh 4-second clips of HgX
  py -3.13 C:\\Jarvis\\calibrate.py record other 8    record 8 clips of OTHER people / TV / phone
  py -3.13 C:\\Jarvis\\calibrate.py score             score everything, suggest a threshold
Clips are saved in C:\\Jarvis\\voiceprint\\calib\\ and NEVER leave this laptop.
Does not change voice_gate.json -- HgX edits the threshold himself after reading the result."""
import os, sys, glob, json
sys.path.insert(0, r"C:\Jarvis")
import voice_gate as VG
CAL = os.path.join(VG.VOICEPRINT, "calib")

def record(kind, n):
    import sounddevice as sd, soundfile as sf
    os.makedirs(CAL, exist_ok=True)
    start = len(glob.glob(os.path.join(CAL, kind + "_*.wav")))
    for i in range(start + 1, start + n + 1):
        input("[%s %d] press Enter, then speak a normal Jarvis command for 4 s..." % (kind, i))
        a = sd.rec(4 * 16000, samplerate=16000, channels=1, dtype="float32"); sd.wait()
        sf.write(os.path.join(CAL, "%s_%02d.wav" % (kind, i)), a.reshape(-1), 16000)

def score():
    VG._load()
    res = {}
    for kind in ("me", "other"):
        res[kind] = [(os.path.basename(p), round(VG.score(p), 3)) for p in sorted(glob.glob(os.path.join(CAL, kind + "_*.wav")))]
        for name, s in res[kind]: print("%-6s %-14s %.3f %s" % (kind, name, s, "PASS" if s >= VG._thr else "reject"))
    me = [s for _, s in res["me"]]; ot = [s for _, s in res["other"]]
    if not me or not ot: sys.exit("need both 'me' and 'other' clips")
    print("\ncurrent threshold %.2f | HgX min %.3f | others max %.3f" % (VG._thr, min(me), max(ot)))
    if max(ot) < min(me):
        sug = round(max(ot) + 0.4 * (min(me) - max(ot)), 2)
        print("Suggested threshold: %.2f (closer to the impostors, so HgX still passes)" % sug)
    else:
        print("Overlap: some other voice scores as high as HgX. Do not lower security; re-enroll closer to the mic or add clips.")
    print("False accepts at current threshold: %d/%d | false rejects: %d/%d"
          % (sum(s >= VG._thr for s in ot), len(ot), sum(s < VG._thr for s in me), len(me)))

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["record"] and len(a) >= 2 and a[1] in ("me", "other"): record(a[1], int(a[2]) if len(a) > 2 else 8)
    elif a == ["score"]: score()
    else: print(__doc__)
