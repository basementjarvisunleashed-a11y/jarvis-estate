"""enroll.py — Local Jarvis voice enrollment (primary profile).

Records N takes of "hey local jarvis" through the laptop's default input
(Maono mic, directly or via the VoiceMeeter B1 mix — either captures the
real acoustic path), embeds each take with SpeechBrain ECAPA-TDNN, averages
the embeddings, and saves profiles.json next to this script.

Usage (Python 3.13 — the one with SpeechBrain installed):
    py -3.13 enroll.py            enroll the primary profile (5 takes)
    py -3.13 enroll.py --verify   speak once, compare against stored primary

Requires: pip install sounddevice   (small; SpeechBrain itself is installed)
First run downloads the ECAPA model from HuggingFace (one time).

IRON RULE: profiles.json and take*.wav NEVER leave this laptop.
Do not sync, upload, copy, or share them. They live in Downloads only.
"""

import argparse
import json
import os
import sys

SAMPLE_RATE = 16000
TAKES = 5
DURATION = 3.0
# VG-1 2026-10-27: all voice-profile data lives in C:\Jarvis\voiceprint (not Downloads).
VOICEPRINT = r"C:\Jarvis\voiceprint"
os.makedirs(VOICEPRINT, exist_ok=True)
PROFILE_FILE = os.path.join(VOICEPRINT, "profiles.json")
MODEL = "speechbrain/spkrec-ecapa-voxceleb"
MODEL_DIR = os.path.join(VOICEPRINT, "pretrained_models", "spkrec-ecapa-voxceleb")


def record_take(n, total=1):
    try:
        import sounddevice as sd
    except ImportError:
        print("sounddevice is missing. Run: py -3.13 -m pip install sounddevice")
        sys.exit(1)
    import soundfile as sf

    input(f"Take {n}/{total} — press Enter, then say 'hey local jarvis' clearly...")
    print("Recording... speak now.")
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    wav = audio.reshape(-1)
    fname = os.path.join(VOICEPRINT, f"take{n}.wav")  # VG-1
    sf.write(fname, wav, SAMPLE_RATE)
    print(f"Got it. Saved {fname}.")
    return wav


def load_model():
    from speechbrain.inference.speaker import SpeakerRecognition

    print(f"Loading {MODEL} (first run downloads it, one time)...")
    return SpeakerRecognition.from_hparams(source=MODEL, savedir=MODEL_DIR)


def embed_all(verification, wavs):
    import numpy as np
    import torch

    embs = []
    for i, wav in enumerate(wavs, 1):
        tensor = torch.from_numpy(wav).unsqueeze(0)
        emb = verification.encode_batch(tensor).squeeze().detach().cpu().numpy()
        embs.append(emb)
        print(f"Embedded take {i}.")
    return np.stack(embs)


def cosine(a, b):
    import numpy as np

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    import numpy as np

    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="speak once and compare against the stored primary")
    args = ap.parse_args()

    if args.verify:
        if not os.path.exists(PROFILE_FILE):
            print("No profiles.json yet — enroll first: py -3.13 enroll.py")
            return
        stored = np.array(
            json.load(open(PROFILE_FILE))["primary"]["embedding"], dtype=np.float32
        )
        wav = record_take(1, 1)
        emb = embed_all(load_model(), [wav])[0]
        score = cosine(emb, stored)
        print(f"Similarity to primary: {score:.3f}  (1.000 = identical.)")
        print("Above ~0.5 is a strong match; tune the live threshold from real scores.")
        return

    wavs = [record_take(n, TAKES) for n in range(1, TAKES + 1)]
    embs = embed_all(load_model(), wavs)
    mean = embs.mean(axis=0)
    mean = mean / np.linalg.norm(mean)
    data = {
        "primary": {
            "embedding": mean.tolist(),
            "takes": TAKES,
            "model": MODEL,
            "sample_rate": SAMPLE_RATE,
        }
    }
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f, indent=1)
    print(f"Saved primary profile to {os.path.abspath(PROFILE_FILE)} "
          f"— {TAKES} takes averaged.")
    print("IRON RULE: profiles.json and take*.wav never leave this laptop.")


if __name__ == "__main__":
    main()
