# Local Jarvis

Installable Windows build of the laptop voice stack. Tested on Windows with
an NVIDIA GPU, an RTX 2060 6GB. Nothing in this folder starts on its own.
The orchestrator listens only after you start it, and the voice loop is
deliberately not auto-started.

Passwords in this tree are the placeholder `CHANGE_ME`. Windows accounts
are the placeholder `<user>`. Set both on the machine. Do not commit the
real values.

## Architecture

```
mic → Whisper small.en → voice gate → orchestrator :8080 → Ollama qwen3:8b → tools / VLC / REA → Piper TTS
```

```mermaid
flowchart LR
    mic[Mic] --> whisper[Whisper small.en]
    whisper --> gate[Voice gate]
    gate --> orch["Orchestrator :8080"]
    orch --> ollama["Ollama qwen3:8b"]
    ollama --> tools["Tools / VLC / REA"]
    tools --> piper["Piper TTS"]
```

A turn is audio in and audio out. Whisper transcribes the mic (or a wav
file). The voice gate scores that audio against the enrolled profile and
drops the turn when the speaker is unenrolled. The orchestrator on port
8080 sends the text to Ollama `qwen3:8b` with thinking off, may call a
tool, and returns a short reply. Piper speaks that reply with the
`en_GB-alan-medium` voice.

Plain VLC commands (`pause`, `play`, `resume`, `stop`, `next`, `skip`,
`previous`, with an optional "hey jarvis") match a regex and run the
tool without a model round trip.

`jarvis.py` is a separate helper for list / play / pause / ask / say /
listen / chat. Its model is `qwen2.5:3b` (`JARVIS_MODEL`), via Ollama
`/api/generate`. The voice loop does not use that model.

## Prerequisites

Windows 10 or 11, and an NVIDIA GPU if you want Whisper on CUDA. The
reference run used an RTX 2060 6GB. CPU Whisper works without the GPU.

1. **Python 3.13**, with the `py` launcher
   ([python.org](https://www.python.org/downloads/)).
   `voice_gate.py` and `enroll.py` run on this interpreter.
   `jarvis.py` and `jarvis_voice.py` run in `C:\Jarvis\venv`, also Python 3.13.
2. **Ollama** ([ollama.com](https://ollama.com/download)):

   ```
   ollama pull qwen3:8b
   ollama pull qwen2.5:3b
   ```

   `qwen3:8b` is the orchestrator. `qwen2.5:3b` is `jarvis.py`.
3. **VLC**, with the HTTP remote on `localhost:8090`.
   Install VLC, then in Preferences (Show settings: All):
   - Interface → Main interfaces → check **Web**
   - Interface → Main interfaces → Lua → **Lua HTTP** → set a password

   `vlc_remote.cmd` starts VLC bound to `localhost:8090`. It does not
   contain the password. The password lives in VLC's preferences and in
   `VLC_HTTP_PASSWORD`, and the two must match.
4. **Piper voice** `en_GB-alan-medium` in `C:\Jarvis\voices`. Download both
   files into that folder:

   - [en_GB-alan-medium.onnx](https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx)
   - [en_GB-alan-medium.onnx.json](https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json)

5. **Optional.** [VoiceMeeter Banana](https://vb-audio.com/Voicemeeter/)
   if you want the mic mix the reference laptop used. The logon task
   starts `C:\Program Files (x86)\VB\Voicemeeter\voicemeeterpro.exe`.
6. **Optional.** [Node.js](https://nodejs.org/) plus `rea-agents` for
   read-only REA. The orchestrator calls
   `C:\Program Files\nodejs\npx.cmd -y rea-agents@6.8.0`. No separate
   install of the package is required beyond Node.

## Virtual environment and requirements

Two requirements files, two interpreters:

| File | Interpreter | What it runs |
|---|---|---|
| `requirements-voice.txt` | `C:\Jarvis\venv` (Python 3.13) | `jarvis.py`, `jarvis_voice.py` (Whisper, Piper, audio) |
| `requirements-orchestrator.txt` | System Python 3.13, and the venv | `voice_gate.py`, `enroll.py` (SpeechBrain). The orchestrator itself is stdlib. |

From this folder:

```
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

`install.ps1` is idempotent. It checks the prerequisites above, creates
`C:\Jarvis` and `C:\Jarvis\venv` when they are missing, and pip-installs
both requirements files (voice requirements into the venv; orchestrator
requirements into the venv and into `py -3.13`, because the gate runs
outside the venv). It copies each package file into `C:\Jarvis` only
when that filename is not already there, so a later run leaves local
edits in place. It does not remove files, does not write secrets, and
does not register scheduled tasks unless you pass `-RegisterTasks`.

## Environment variables

The programs read the process environment. They do not load `.env`.
[`.env.example`](.env.example) lists the names with placeholders only.
Set them in System Properties, or with `setx` (open a new terminal
afterwards). Do not commit the real values.

| Variable | Role |
|---|---|
| `VLC_HTTP_PASSWORD` | Password for VLC's Lua HTTP interface. Source default and the example are `CHANGE_ME`. Set the same value you saved in VLC's preferences. |
| `JARVIS_OPERATOR_NAME` | How the orchestrator addresses you. Default `sir`. |
| `JARVIS_MODEL` | Ollama model for `jarvis.py` (`ask`, `chat`). Default `qwen2.5:3b`. |
| `JARVIS_WHISPER_DEVICE` | `cuda` loads Whisper `small.en` on the GPU in the voice loop. Unset, or any other value, uses the CPU. |
| `XAI_API_KEY` | Optional. When set, demo briefs are drafted by Grok. When unset, the orchestrator serves a canned DEMO card. |

Also read by the orchestrator, with safe defaults: `OLLAMA_URL`
(`http://localhost:11434`), `OLLAMA_MODEL` (`qwen3:8b`), `VLC_HTTP_PORT`
(`8090`), `JARVIS_ROOTS` (Desktop, Documents, and Downloads under your
home directory), `JARVIS_LAN_IP` (printed for a watch on the same
network; unset prints a placeholder).

The Meshtastic MQTT password inside `orchestrator.py` is `CHANGE_ME`.
Set it on the machine if you use the watch mesh. `paho-mqtt` is commented
out of the requirements file; HTTP works without it.

## Enrollment and calibration

`voice_gate.py` reads the profile from `C:\Users\<user>\Downloads` and
the threshold from `C:\Jarvis\voice_gate.json`. Before the first enroll,
edit the installed copies (the copies in git keep the placeholder):

- `C:\Jarvis\voice_gate.py` — set `DL` to your Downloads folder.
- `C:\Jarvis\jarvis_voice.py` — set `GATE_PY` to the Python 3.13
  executable that has SpeechBrain
  (`py -3.13 -c "import sys; print(sys.executable)"`).
- `C:\Jarvis\jarvis.py` — `MIC` and `SPK` are the reference laptop's
  Maono device names. Change them to this PC's Windows sound devices.

Enrollment records **5 takes** of "hey local jarvis" (3 seconds each),
embeds them with SpeechBrain ECAPA-TDNN, and writes `profiles.json` in
the current directory. The first run downloads the ECAPA model into
`pretrained_models\` under that directory. Run it from the same
Downloads folder `voice_gate.py` reads:

```
cd C:\Users\<user>\Downloads
py -3.13 C:\Jarvis\enroll.py
py -3.13 C:\Jarvis\enroll.py --verify
```

`--verify` records one take and prints similarity to the stored primary.
`profiles.json`, `take1.wav` … `take5.wav`, and `pretrained_models\`
stay on this PC.

The gate threshold **starts at 0.45 and is UNCALIBRATED**. Treat 0.45
as a starting point, not a measured cutoff. `voice_gate.json` says so.
Score three clips with `py -3.13 C:\Jarvis\voice_gate.py clip.wav`
before you change the number:

- your voice, quiet
- your voice, across the room
- an unknown voice

A clip is accepted when its score is at least the threshold. Anything
below the threshold is ignored, including every unenrolled voice. One
`--verify` score is not a threshold.

## Running and testing

1. Ollama is running.
2. Start the orchestrator and leave the window open:

   ```
   py -3.13 C:\Jarvis\orchestrator.py
   ```

   Open `http://localhost:8080`. Turns are `POST /jarvis` with
   `{"text": "<utterance>"}`.
3. For media commands, start VLC:

   ```
   C:\Jarvis\vlc_remote.cmd
   ```

4. One file through the pipeline (reply written to `C:\Jarvis\out\reply.wav`):

   ```
   C:\Jarvis\jarvis_voice.cmd test file.wav
   ```

5. Live loop, 5 seconds per listen. Say "stop" to end it:

   ```
   C:\Jarvis\jarvis_voice.cmd loop 5
   ```

`jarvis_voice.cmd` is a manual launcher. It is not a login item.
`test file.wav --bypass-gate` still scores the gate and still speaks,
which is how you hear Piper before enrollment is finished. Without
`--bypass-gate`, an unenrolled voice is ignored.

`C:\Jarvis\jarvis.cmd` is the direct helper (`ask`, `say`, `listen`,
`chat`, VLC) on `qwen2.5:3b`.

## Optional autostart

The voice loop is deliberately not auto-started. There is no task for it.

Two optional logon tasks ship in [`tasks/`](tasks/):

| File | Task name | What it starts |
|---|---|---|
| `tasks/orchestrator.xml` | Jarvis - Orchestrator 8080 | The orchestrator at logon, if port 8080 is not already listening. |
| `tasks/voicemeeter.xml` | Jarvis - VoiceMeeter Banana | VoiceMeeter Banana at logon. |

The first `install.ps1` run copies these templates to `C:\Jarvis\tasks\`
when those filenames are not already there. Edit the **C:\Jarvis\tasks**
copies. Leave the git copies generic, and do not commit a real SID.

Replace, in both files:

- `S-1-5-21-CHANGE_ME_USER_SID` with the SID from `whoami /user`
- `<COMPUTER>\<user>` with this PC and this Windows account
- in `orchestrator.xml`, the Python executable and the working directory
  (`C:\Users\<user>\...`)

The committed files declare UTF-16 and are stored as UTF-8 text so they
stay readable in git. `install.ps1 -RegisterTasks` reads
`C:\Jarvis\tasks\*.xml`, registers that text, and does not rewrite the
files. Import only after the placeholders are gone:

```
powershell -ExecutionPolicy Bypass -File .\install.ps1 -RegisterTasks
```

The script refuses `-RegisterTasks` while `CHANGE_ME`, `<user>`,
`<COMPUTER>`, or `CHANGE_ME_USER_SID` is still in either file, and it
registers nothing in that case. It never registers the voice loop.

To import with `schtasks` instead, re-save the edited XML as UTF-16 LE
and then:

```
schtasks /Create /TN "Jarvis - Orchestrator 8080" /XML C:\Jarvis\tasks\orchestrator.xml /F
schtasks /Create /TN "Jarvis - VoiceMeeter Banana" /XML C:\Jarvis\tasks\voicemeeter.xml /F
```

## Security

This build has no delete tool. File list, search, read, and move stay
inside Desktop, Documents, and Downloads (or `JARVIS_ROOTS`). `..` is
refused.

The voice path, VLC, and Ollama are bound to localhost. VLC's HTTP
remote is `localhost:8090`. Ollama is `localhost:11434`. The voice loop
posts only to `http://localhost:8080/jarvis`. The orchestrator listens
on port 8080 on the local interfaces of the PC that runs it, so a watch
on the same network can reach it. The address it prints is the
placeholder `<this-laptop's-LAN-IP>` unless you set `JARVIS_LAN_IP`.
This tree does not contain a public IP.

Never commit `profiles.json`, audio (`take*.wav` and other recordings),
model weights (`pretrained_models/`, `voices/*.onnx`, other `*.onnx`),
or a real `.env`. Runtime logs `verdicts.log` and `actions.log` stay
local too. See the root `.gitignore`.

## Troubleshooting

**`cublas64_12.dll` is missing.** Whisper tried the CUDA 12 runtime and
did not find it. Install the CUDA 12 runtime, or leave
`JARVIS_WHISPER_DEVICE` unset so `jarvis_voice.py` loads `small.en` on
CPU (`int8`). Setting `JARVIS_WHISPER_DEVICE=cuda` asks for the GPU
build on purpose. `jarvis.py` tries CUDA first and falls back to CPU
when that load fails.

**`qwen3:8b` feels slow.** Thinking is off by default. Every orchestrator
call sends `"think": false`, so the wait is the 8B model generating on
this GPU (the reference card is an RTX 2060 6GB), not a hidden reasoning
pass. `jarvis.py` uses the smaller `qwen2.5:3b` for `ask` and `chat`.

**VLC is unreachable.** Start `C:\Jarvis\vlc_remote.cmd`. That binds the
HTTP interface to `localhost:8090`. If VLC answers 401, `VLC_HTTP_PASSWORD`
does not match the password in VLC's Lua HTTP preferences.

## Files

| File | Role |
|---|---|
| `orchestrator.py` | HTTP brain on port **8080**. Stdlib only. |
| `jarvis_voice.py` | Mic, Whisper, gate, orchestrator, Piper. Manual. |
| `jarvis_voice.cmd` | Launches the voice loop with `C:\Jarvis\venv`. |
| `jarvis.py` | Direct helper. Model `JARVIS_MODEL`, default `qwen2.5:3b`. |
| `jarvis.cmd` | Launches `jarvis.py` with the venv. |
| `enroll.py` | Records 5 takes and writes `profiles.json`. |
| `voice_gate.py`, `voice_gate.json` | Speaker check. Threshold 0.45, UNCALIBRATED. |
| `vlc_remote.cmd` | VLC HTTP on `localhost:8090`. No password in the file. |
| `requirements-voice.txt` | Venv packages. |
| `requirements-orchestrator.txt` | SpeechBrain stack for the gate and enrollment. |
| `install.ps1` | Prerequisite check, venv, pip, next steps. |
| `.env.example` | Placeholder names only. |
| `tasks/orchestrator.xml` | Optional logon task for the orchestrator. |
| `tasks/voicemeeter.xml` | Optional logon task for VoiceMeeter Banana. |
