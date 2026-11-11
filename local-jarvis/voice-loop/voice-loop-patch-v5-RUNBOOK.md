# Voice-loop patch v5 — apply & test runbook (2026-11-06)

HgX's order, 2026-11-05 ~21:15 ET (Cloud Jarvis): "Just fix it. Just get it done."
Patch file: `local-jarvis/voice-loop/voice-loop-patch-v5-rebuilt.py` — rebuilt
fresh from the repo copy of `jarvis_voice.py`; its self-test passed all cases
(see the patch file header). (Publishing note: the runbook originally named
the earlier patch file; the rebuilt file is the one published here.)

## Do this at the Acer keyboard.

## 0. Kill the feedback loop first (his own levels, 2026-11-05 ~21:15 ET)
Maono: Monitor to 0, Music to 0, Mic stays at 25%. At 50/50/25 the loop
hears itself and the music as if HgX spoke.

## 1. Get the patch onto the Acer
SSH/Tailscale to the Acer failed on 2026-11-05 ~18:10 ET, so the working
route is the one used all last night: paste into the laptop terminal.
If SSH works, copy the file instead — same result either way.

## 2. Apply (one command; backs up to jarvis_voice.py.bak5, never overwrites)
```
python3 local-jarvis/voice-loop/voice-loop-patch-v5-rebuilt.py  # from the repo root
python3 -m py_compile ~/Jarvis/jarvis_voice.py
```
If it aborts with "handle() anchor not found" or "gate block not found",
the Acer's file has drifted from the repo copy — stop, do not hand-edit,
send the Acer file back. It never half-patches.

## 3. Test — speak "open Firefox" into the Maono mics
```
arecord -D plughw:0,0 -f S16_LE -r 48000 -c 2 -d 5 /tmp/cmd2.wav
~/Jarvis/venv/bin/python ~/Jarvis/jarvis_voice.py test /tmp/cmd2.wav --bypass-gate
```
Expect `"action": "dispatched"` in the JSON — and a Firefox window.
Then the live loop: `cd ~/Jarvis && ~/Jarvis/venv/bin/python jarvis_voice.py loop`

## 4. What "done" looks like
- "open Firefox" opens Firefox; "open a terminal" opens a terminal;
  "VLC on, play the Sopranos" plays the Sopranos (no second VLC if one
  is already playing); "stop" says goodbye and ends the loop.
- Note: a bare "play a random episode" still goes to the model and the
  confirm gate — only the listed commands dispatch. That is per the plan.

## Still unknown (state plainly, do not assume)
- Whether the Acer's `~/Jarvis/jarvis_voice.py` still matches the repo
  copy the patch was verified against. The patch's asserts are the check.
- Whether patch v3 (48 kHz speaking fix) was ever applied on the Acer.
  v5 does not touch play(), so it applies either way — but if replies
  still crash on playback, v3 is the next step, not v5 again.
- Whether the Monitor/Music knobs were turned to 0 last night.
