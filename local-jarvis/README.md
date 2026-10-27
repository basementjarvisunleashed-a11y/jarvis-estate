# Local Jarvis (laptop stack)

Bench copy of the basement laptop stack. It stays on the machine that runs
it. Nothing in this folder starts by itself: the voice loop is manual, and
the orchestrator listens only after you start it.

Passwords in this tree are the placeholder `CHANGE_ME`. Set them on the
laptop. Do not commit the real values. Paths that would name a Windows
account use `C:\Users\<user>`.

## What runs where

```
mic → Whisper small.en → speaker voice gate → POST /jarvis → Piper TTS
                              ↑
                    orchestrator :8080
                    Ollama qwen3:8b  /api/chat  (think off)
                    VLC HTTP remote  127.0.0.1:8090
                    read-only rea_analyze
```

| Piece | File | Role |
|---|---|---|
| Orchestrator | `orchestrator.py` | HTTP brain on port **8080**. |
| Voice loop | `jarvis_voice.py` | Mic, Whisper, gate, orchestrator, Piper. **Does not auto-start.** |
| Voice loop launcher | `jarvis_voice.cmd` | Manual launcher only. Not a login or startup item. |
| Voice gate | `voice_gate.py`, `voice_gate.json` | Speaker check before a turn is acted on. |
| VLC remote | `vlc_remote.cmd` | Starts VLC's HTTP interface on `127.0.0.1:8090`. |

## Orchestrator (`orchestrator.py`)

```
python orchestrator.py
```

Then open `http://localhost:8080`. Local Jarvis turns are `POST /jarvis`
with `{"text": "<utterance>"}`.

- **Ollama.** `POST {OLLAMA_URL}/api/chat` (default `http://127.0.0.1:11434`),
  model `qwen3:8b` (`OLLAMA_MODEL`). The request sets `think` to false.
- **Fast path.** A regex handles plain VLC media commands (`pause`, `play`,
  `resume`, `stop`, `next`, `skip`, `previous`, with an optional "hey
  jarvis") and runs the matching tool without a model round trip.
- **VLC.** HTTP remote at `http://127.0.0.1:8090`. The password is
  `VLC_HTTP_PASSWORD`, default `CHANGE_ME`. Set the same password in VLC's
  Lua HTTP interface. `vlc_remote.cmd` binds that interface to
  `127.0.0.1:8090` and does not contain a password.
- **`rea_analyze`.** Read-only reverse-engineering inspection via
  `rea-agents` (`analyze`, PE import/certificate/resource/load-config
  checks, JavaScript app analysis). It does not modify the target.
- **Files.** List, search, read, and move stay inside Desktop, Documents,
  and Downloads (or `JARVIS_ROOTS`). There is no delete tool.

Other environment knobs: `OLLAMA_URL`, `OLLAMA_MODEL`, `VLC_HTTP_PORT`,
`VLC_HTTP_PASSWORD`, `JARVIS_ROOTS`, `JARVIS_LAN_IP`, `XAI_API_KEY` (optional
demo briefs; unset means a canned DEMO card). The Meshtastic MQTT password
is also `CHANGE_ME` until you set it locally.

`verdicts.log` and `actions.log` are written next to the script when it
runs. They are local runtime logs. Do not commit them.

## Voice loop (`jarvis_voice.py`)

The loop does **not** auto-start. `jarvis_voice.cmd` is a manual launcher
and is not installed as a startup task. Run it only when you mean to:

```
jarvis_voice.py loop [seconds]
jarvis_voice.py test WAV [--bypass-gate]
```

Pipeline: microphone → Whisper `small.en` → speaker voice gate →
`POST http://127.0.0.1:8080/jarvis` → Piper TTS.

The loop reuses the laptop's existing `C:\Jarvis\jarvis.py` for devices,
`transcribe()`, and the Piper voice path. That module is not in this
folder. Whisper loads `small.en` on CPU unless `JARVIS_WHISPER_DEVICE=cuda`.
The gate runs under the Python that has SpeechBrain
(`C:\Users\<user>\AppData\Local\Programs\Python\Python313\python.exe` in
`jarvis_voice.py`).

Unenrolled voices are ignored. A turn is spoken only when the gate accepts
the speaker (or a one-off `test` is run with `--bypass-gate`).

## Voice gate — threshold 0.45, UNCALIBRATED

`voice_gate.json` sets the threshold to **0.45** and marks it
**UNCALIBRATED**, pending measurements for:

- quiet voice
- across the room
- unknown voice

`voice_gate.py` uses that file when it is present (`C:\Jarvis\voice_gate.json`
on the laptop) and otherwise the same provisional default, 0.45. It scores
against the enrolled profile only. It does not re-enroll. Anything below
the threshold — any voice that is not the enrolled speaker — is ignored.

The profile (`profiles.json`) and model weights (`pretrained_models/`,
`*.npy` embeddings) stay on the laptop. They are gitignored.

## What not to commit

Voice profiles, embeddings, audio, model weights, `.env` files, and backups
are ignored from the repo root (see `.gitignore`). This folder ships source
and the uncalibrated gate config only.
