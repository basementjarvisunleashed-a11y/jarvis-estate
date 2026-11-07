# Voice loop — patch v5 (2026-11-06)

The voice loop's hands: a deterministic dispatcher for `jarvis_voice.py`
that runs spoken commands directly instead of leaving them to the model
to merely talk about.

**Status: applied on the Acer.** The patch was rebuilt fresh from the
repo copy of `jarvis_voice.py`; its self-test passed all cases.

**Files:**

| File | What it is |
|---|---|
| `voice-loop-patch-v5-rebuilt.py` | The patch. Backs up the target to `jarvis_voice.py.bak5`, asserts both anchors before patching, never half-patches. Run: `python3 voice-loop-patch-v5-rebuilt.py` (defaults to `~/Jarvis/jarvis_voice.py`); `--self-test` runs the mocked test. |
| `voice-loop-patch-v5-RUNBOOK.md` | Apply & test runbook: Maono levels first, apply, offline test (`arecord` + `jarvis_voice.py test`), live loop, what "done" looks like. (Publishing note: two file references updated to the rebuilt filename; one scheduling line removed.) |

**The nine routes:** "open Firefox" / "open fire" → Firefox; "open a
terminal" → terminal; "VLC on" / "play the Sopranos" → VLC `--loop` on
the Sopranos folder (drive guard if `/mnt/hgx` is not mounted, no second
VLC if one runs); "list the files" → home folder names; "stop" / "exit" /
"goodbye" → "Goodbye, sir." (exempt from confirm). "move" / "commit" /
"verdict" and anything else fall through to the confirm gate and the
model, as before. "What time is it" and "play a random episode" go to
the model.

The dispatcher runs AFTER transcription and BEFORE the VG-2c confirm
gate and BEFORE `orchestrate()`, so acting commands are no longer killed
by "unconfirmed".
