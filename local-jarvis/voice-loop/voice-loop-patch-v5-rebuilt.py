#!/usr/bin/env python3
"""Rebuild of patch v5 — deterministic dispatcher for jarvis_voice.py.

Built FRESH from the repo copy (~/workspace/jarvis-estate-main/local-jarvis/
jarvis_voice.py, 119 lines) and the nine-route spec in memory. The flagged
earlier patch file was NOT read, run, pasted, or reused in any way.

What it does, on the Acer, at the keyboard:
  python3 voice-loop-patch-v5-rebuilt.py ~/Jarvis/jarvis_voice.py
  - asserts both anchors are present in the target file, aborts loudly
    rather than half-patching if either is missing
  - inserts dispatch() + helpers before def handle()
  - inserts a dispatch call in handle(), AFTER transcription and BEFORE
    the VG-2c confirm gate and BEFORE orchestrate()
  - backs up the target to jarvis_voice.py.bak5 (first run only)
  - runs py_compile on the result

Dispatch routes (nine, from the spec):
  open Firefox / "open fire" (Whisper's clipped "open Firefox") -> Firefox
  open a terminal -> xfce4-terminal / gnome-terminal / konsole / xterm
  VLC on / play the Sopranos -> VLC --loop on the Sopranos folder,
      drive guard if /mnt/hgx is not mounted, no second VLC if one runs
  list the files -> names in the home folder
  stop / exit / goodbye -> "Goodbye, sir." (exempt from confirm)
  move / commit / verdict and anything else -> None, falls through to
      the confirm gate / the model as before
  "what time is it" and "play a random episode" -> None (to the model)

Self-test (no Acer needed, no Firefox/VLC launched — Popen is mocked):
  python3 voice-loop-patch-v5-rebuilt.py --self-test
"""
import argparse
import os
import shutil
import subprocess
import sys

DISPATCH_CODE = '''
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
    neat = "/mnt/hgx/TV SHOWS/THE SOPRANOS/The Sopranos/"
    if _os.path.isdir(neat):
        return neat
    for cand in glob.glob("/mnt/hgx/TV SHOWS/**/The Sopranos/", recursive=True):
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

'''

CALL_SITE = '''    d = dispatch(text)
    if d is not None:
        s = time.time(); tts(d["reply"], out_wav); t["piper_s"] = time.time() - s
        if speak: s = time.time(); play(out_wav); t["play_s"] = time.time() - s
        res.update(action=d.get("action", "dispatched"), reply=d["reply"], wav=out_wav, t=t); return res
'''

ANCHOR_HANDLE = "def handle(wav, gate, out_wav, speak, bypass=False):"
ANCHOR_GATE = '    if MUTATING_RE.search(text) and not confirm(gate, speak):  # VG-2c'


def apply_patch(target):
    with open(target) as f:
        src = f.read()
    if "def dispatch(text):" in src:
        print("already patched: dispatch() is present, no change")
        return
    assert ANCHOR_HANDLE in src, "anchor missing: def handle(...) not found — aborting, no change"
    assert ANCHOR_GATE in src, "anchor missing: VG-2c confirm line not found — aborting, no change"
    src = src.replace(ANCHOR_HANDLE, DISPATCH_CODE.lstrip("\n") + ANCHOR_HANDLE, 1)
    src = src.replace(ANCHOR_GATE, CALL_SITE + ANCHOR_GATE, 1)
    backup = target + ".bak5"
    if not os.path.exists(backup):
        shutil.copyfile(target, backup)
        print("backup:", backup)
    else:
        print("backup already exists:", backup)
    with open(target, "w") as f:
        f.write(src)
    subprocess.run([sys.executable, "-m", "py_compile", target], check=True)
    print("patched OK, compiles OK:", target)


def self_test(repo_copy):
    import tempfile
    tmp = tempfile.mkdtemp(prefix="v5-rebuilt-test-")
    target = os.path.join(tmp, "jarvis_voice.py")
    shutil.copyfile(repo_copy, target)
    apply_patch(target)
    with open(target) as f:
        patched = f.read()
    # Extract only the dispatcher block (helpers + dispatch) and exec it
    # in isolation, with Popen mocked so nothing is launched.
    start = patched.index("def _vlc_running():")
    end = patched.index("def handle(")
    block = patched[start:end]
    calls = []

    class FakePopen:
        def __init__(self, argv, **kw):
            calls.append(list(argv))

    ns = {"os": os, "subprocess": subprocess, "shutil": shutil}
    # Replace Popen in the exec namespace via a shim module object.
    import types
    fake_sub = types.SimpleNamespace(Popen=FakePopen, run=subprocess.run,
                                     DEVNULL=subprocess.DEVNULL)
    ns["subprocess"] = fake_sub
    exec(block, ns)
    dispatch = ns["dispatch"]
    cases = [
        ("open Firefox", "firefox", "Opening Firefox"),
        ("open fire", "firefox", "Opening Firefox"),
        ("stop", None, "Goodbye"),
        ("VLC on", None, "not mounted"),
        ("play the Sopranos", None, "not mounted"),
        ("list the files", None, "home folder"),
        ("what time is it", None, None),
        ("play a random episode", None, None),
    ]
    ok = True
    for text, expect_cmd, expect_reply in cases:
        calls.clear()
        r = dispatch(text)
        if expect_reply is None:
            passed = r is None
            print(("PASS " if passed else "FAIL ") + repr(text) + " -> None")
        else:
            passed = (r is not None and expect_reply in r["reply"]
                      and (expect_cmd is None or any(expect_cmd in c for c in calls)
                           or expect_cmd is None))
            # For drive-guard cases there is no Popen call; that is correct.
            if expect_cmd and "not mounted" in expect_reply:
                passed = r is not None and expect_reply in r["reply"] and not calls
            print(("PASS " if passed else "FAIL ") + repr(text) + " -> " + repr(r)
                  + (" calls=" + repr(calls) if calls else ""))
        ok = ok and passed
    # Terminal case: accept either a launch or the honest not-found reply.
    calls.clear()
    r = dispatch("open a terminal")
    term_ok = r is not None and ("Opening a terminal" in r["reply"]
                                 or "could not find a terminal" in r["reply"])
    print(("PASS " if term_ok else "FAIL ") + "'open a terminal' -> " + repr(r))
    ok = ok and term_ok
    print("self-test:", "ALL PASS" if ok else "FAILURES — see above")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", default=os.path.expanduser("~/Jarvis/jarvis_voice.py"))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--repo", default=os.path.expanduser(
        "~/workspace/jarvis-estate-main/local-jarvis/jarvis_voice.py"))
    a = ap.parse_args()
    if a.self_test:
        repo = a.repo
        if not os.path.exists(repo):
            # Fall back to a copy next to this script, or the target itself.
            print("repo copy not found at", repo)
            sys.exit(2)
        sys.exit(0 if self_test(repo) else 1)
    apply_patch(a.target)


if __name__ == "__main__":
    main()
