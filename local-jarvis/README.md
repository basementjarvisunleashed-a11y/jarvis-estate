# Local Jarvis

Laptop voice stack. Platform as of 2026-11-04: Kali Linux on the internal
drive, with an NVIDIA GPU, an RTX 2060 (about 6GB VRAM). On the
reference machine the services autostart (router, orchestrator,
dashboard — see [`SETUP.md`](SETUP.md)); the voice loop itself is
deliberately not auto-started.

Kali Linux: all tools updated, graphics driver installed, Bluetooth
working, Wi-Fi working, login working. Windows is no longer on the
internal drive. The Windows licence is motherboard-tied; a later reinstall
via ISO is possible with no product key needed.

Passwords in this tree are the placeholder `CHANGE_ME`. User accounts
are the placeholder `<user>`. Set both on the machine. Do not commit the
real values.

See [`PLATFORM-KALI.md`](PLATFORM-KALI.md) for the current platform record:
Kali Linux with all tools updated, graphics driver installed, Bluetooth
and Wi-Fi working, login working, and REA ready for local app analysis.

Run the whole system from this repo alone — start at
[`SETUP.md`](SETUP.md): clone, install in order, verify. It lists every
component, the models by name and tag only (no weights shipped), and what
is still to land.

## Architecture

```
mic → Whisper small.en → voice gate → orchestrator :8080 → Ollama qwen9b-abliterated → tools / VLC / REA → Piper TTS
```

```mermaid
flowchart LR
    mic[Mic] --> whisper[Whisper small.en]
    whisper --> gate[Voice gate]
    gate --> orch["Orchestrator :8080"]
    orch --> ollama["Ollama qwen9b-abliterated"]
    ollama --> tools["Tools / VLC / REA"]
    tools --> piper["Piper TTS"]
```

A turn is audio in and audio out. Whisper transcribes the mic (or a wav
file). The voice gate scores that audio against the enrolled profile and
drops the turn when the speaker is unenrolled. The orchestrator on port
8080 sends the text to Ollama `qwen9b-abliterated` with thinking off, may call a
tool, and returns a short reply. Piper speaks that reply with the
`en_GB-alan-medium` voice.

Plain VLC commands (`pause`, `play`, `resume`, `stop`, `next`, `skip`,
`previous`, with an optional "hey jarvis") match a regex and run the
tool without a model round trip.

`jarvis.py` is a separate helper for list / play / pause / ask / say /
listen / chat. Its model is `qwen2.5:3b` (`JARVIS_MODEL`), via Ollama
`/api/generate`. The voice loop does not use that model.

## Prerequisites

Kali Linux on the internal drive, and an NVIDIA GPU if you want Whisper
on CUDA. The reference run used an RTX 2060 (about 6GB VRAM). CPU Whisper
works without the GPU.

1. **Python 3.13** (Kali package `python3`).
   `voice_gate.py` and `enroll.py` run on this interpreter.
   `jarvis.py` and `jarvis_voice.py` run in `~/Jarvis/venv`, also Python 3.13.
2. **Ollama** ([ollama.com](https://ollama.com/download)):

   ```
   ollama pull qwen9b-abliterated
   ollama pull qwen2.5:3b
   ollama pull qwen3:8b  # fallback only
   ```

   `qwen9b-abliterated` is the orchestrator. `qwen2.5:3b` is `jarvis.py`.
3. **VLC**, with the HTTP remote on `127.0.0.1:8090`.
   Install VLC, then in Preferences (Show settings: All):
   - Interface → Main interfaces → check **Web**
   - Interface → Main interfaces → Lua → **Lua HTTP** → set a password

   `vlc_remote.sh` starts VLC bound to `127.0.0.1:8090`. It does not
   contain the password. The password lives in VLC's preferences and in
   `VLC_HTTP_PASSWORD`, and the two must match.
4. **Piper voice** `en_GB-alan-medium` in `~/Jarvis/voices`. Download both
   files into that folder:

   - [en_GB-alan-medium.onnx](https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx)
   - [en_GB-alan-medium.onnx.json](https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json)

5. **Optional.** PipeWire audio routing if you want the mic mix the
   reference laptop used. Kali ships PipeWire by default.
6. **REA** for read-only reverse engineering. Installed via
   `npx rea-agents setup` (`rea-agents@6.7.0`). The REA
   reverse-engineering skill is installed for CLI use. CLI:
   `npx rea-agents analyze /path/to/app`. Deep analysis uses Ghidra
   with guided workflows installed. The orchestrator calls REA for
   local app analysis only.

## Virtual environment and requirements

Two requirements files, two interpreters:

| File | Interpreter | What it runs |
|---|---|---|
| `requirements-voice.txt` | `~/Jarvis/venv` (Python 3.13) | `jarvis.py`, `jarvis_voice.py` (Whisper, Piper, audio) |
| `requirements-orchestrator.txt` | System Python 3.13, and the venv | `voice_gate.py`, `enroll.py` (SpeechBrain). The orchestrator itself is stdlib. |

From this folder:

```
./install.sh
```

`install.sh` is idempotent. It checks the prerequisites above, creates
`~/Jarvis` and `~/Jarvis/venv` when they are missing, and pip-installs
both requirements files (voice requirements into the venv; orchestrator
requirements into the venv and into system `python3`, because the gate runs
outside the venv). It copies each package file into `~/Jarvis` only
when that filename is not already there, so a later run leaves local
edits in place. It does not remove files, does not write secrets, and
does not register autostart unless you pass `--register-autostart`.

## Environment variables

The programs read the process environment. They do not load `.env`.
[`.env.example`](.env.example) lists the names with placeholders only.
Set them in `~/.bashrc`, or export them in the terminal before starting.
Do not commit the real values.

| Variable | Role |
|---|---|
| `VLC_HTTP_PASSWORD` | Password for VLC's Lua HTTP interface. Source default and the example are `CHANGE_ME`. Set the same value you saved in VLC's preferences. |
| `JARVIS_OPERATOR_NAME` | How the orchestrator addresses you. Default `sir`. |
| `JARVIS_MODEL` | Ollama model for `jarvis.py` (`ask`, `chat`). Default `qwen2.5:3b`. |
| `JARVIS_WHISPER_DEVICE` | `cuda` loads Whisper `small.en` on the GPU in the voice loop. Unset, or any other value, uses the CPU. |
| `XAI_API_KEY` | Optional. When set, demo briefs are drafted by Grok. When unset, the orchestrator serves a canned DEMO card. |

Also read by the orchestrator, with safe defaults: `OLLAMA_URL`
(`http://127.0.0.1:11434`), `OLLAMA_MODEL` (`qwen9b-abliterated`), `VLC_HTTP_PORT`
(`8090`), `JARVIS_ROOTS` (Desktop, Documents, and Downloads under your
home directory), `JARVIS_LAN_IP` (printed for a watch on the same
network; unset prints a placeholder).

The Meshtastic MQTT password inside `orchestrator.py` is `CHANGE_ME`.
Set it on the machine if you use the watch mesh. `paho-mqtt` is commented
out of the requirements file; HTTP works without it.

## Enrollment and calibration

`voice_gate.py` reads the profile from `~/Downloads` and
the threshold from `~/Jarvis/voice_gate.json`. Before the first enroll,
edit the installed copies (the copies in git keep the placeholder):

- `~/Jarvis/voice_gate.py` — set `DL` to your Downloads folder.
- `~/Jarvis/jarvis_voice.py` — set `GATE_PY` to the Python 3.13
  executable that has SpeechBrain
  (`python3 -c "import sys; print(sys.executable)"`).
- `~/Jarvis/jarvis.py` — `MIC` and `SPK` are the reference laptop's
  Maono device names. Change them to this machine's PipeWire/PulseAudio
  device names (see `pactl list sources` and `pactl list sinks`).

Enrollment records **5 takes** of "hey local jarvis" (3 seconds each),
embeds them with SpeechBrain ECAPA-TDNN, and writes `profiles.json` in
the current directory. The first run downloads the ECAPA model into
`pretrained_models/` under that directory. Run it from the same
Downloads folder `voice_gate.py` reads:

```
cd ~/Downloads
python3 ~/Jarvis/enroll.py
python3 ~/Jarvis/enroll.py --verify
```

`--verify` records one take and prints similarity to the stored primary.
`profiles.json`, `take1.wav` … `take5.wav`, and `pretrained_models/`
stay on this machine.

The gate threshold **starts at 0.45 and is UNCALIBRATED**. Treat 0.45
as a starting point, not a measured cutoff. `voice_gate.json` says so.
Score three clips with `python3 ~/Jarvis/voice_gate.py clip.wav`
before you change the number:

- your voice, quiet
- your voice, across the room
- an unknown voice

A clip is accepted when its score is at least the threshold. Anything
below the threshold is ignored, including every unenrolled voice. One
`--verify` score is not a threshold.

## Running and testing

1. Ollama is running.
2. Start the orchestrator and leave the terminal open:

   ```
   python3 ~/Jarvis/orchestrator.py
   ```

   Open `http://localhost:8080`. Turns are `POST /jarvis` with
   `{"text": "<utterance>"}`.
3. For media commands, start VLC:

   ```
   ~/Jarvis/vlc_remote.sh
   ```

4. One file through the pipeline (reply written to `~/Jarvis/out/reply.wav`):

   ```
   ~/Jarvis/jarvis_voice.sh test file.wav
   ```

5. Live loop, 5 seconds per listen. Say "stop" to end it:

   ```
   ~/Jarvis/jarvis_voice.sh loop 5
   ```

`jarvis_voice.sh` is a manual launcher. It is not a login item.
`test file.wav --bypass-gate` still scores the gate and still speaks,
which is how you hear Piper before enrollment is finished. Without
`--bypass-gate`, an unenrolled voice is ignored.

`~/Jarvis/jarvis.sh` is the direct helper (`ask`, `say`, `listen`,
`chat`, VLC) on `qwen2.5:3b`.

## Optional autostart

The voice loop is deliberately not auto-started. There is no service for it.

Two optional systemd user units ship in [`units/`](units/):

| File | Unit name | What it starts |
|---|---|---|
| `units/orchestrator.service` | jarvis-orchestrator | The orchestrator at login, if port 8080 is not already listening. |
| `units/pipewire-mix.service` | jarvis-pipewire-mix | PipeWire audio routing at login. |

The first `install.sh` run copies these templates to `~/.config/systemd/user/`
when those filenames are not already there. Edit the **~/.config/systemd/user**
copies. Leave the git copies generic, and do not commit a real username.

Replace, in both files:

- `CHANGE_ME_USER` with your Linux username
- in `orchestrator.service`, the Python executable and the working directory
  (`/home/<user>/Jarvis/...`)

Enable only after the placeholders are gone:

```
systemctl --user enable jarvis-orchestrator.service
systemctl --user start jarvis-orchestrator.service
```

The script refuses `--register-autostart` while `CHANGE_ME` or `<user>`
is still in either file, and it registers nothing in that case. It never
registers the voice loop.

## Security

This build has no delete tool. File list, search, read, and move stay
inside Desktop, Documents, and Downloads (or `JARVIS_ROOTS`). `..` is
refused.

The voice path, VLC, and Ollama are bound to localhost. VLC's HTTP
remote is `127.0.0.1:8090`. Ollama is `127.0.0.1:11434`. The voice loop
posts only to `http://127.0.0.1:8080/jarvis`. The orchestrator listens
on port 8080 on the local interfaces of the machine that runs it, so a watch
on the same network can reach it. The address it prints is the
placeholder `<this-laptop's-LAN-IP>` unless you set `JARVIS_LAN_IP`.
This tree does not contain a public IP.

Never commit `profiles.json`, audio (`take*.wav` and other recordings),
model weights (`pretrained_models/`, `voices/*.onnx`, other `*.onnx`),
or a real `.env`. Runtime logs `verdicts.log` and `actions.log` stay
local too. See the root `.gitignore`.

## Troubleshooting

**CUDA runtime is missing.** Whisper tried the CUDA 12 runtime and
did not find it. Install the CUDA 12 runtime (Kali package
`nvidia-cuda-toolkit`), or leave `JARVIS_WHISPER_DEVICE` unset so
`jarvis_voice.py` loads `small.en` on CPU (`int8`). Setting
`JARVIS_WHISPER_DEVICE=cuda` asks for the GPU build on purpose.
`jarvis.py` tries CUDA first and falls back to CPU when that load fails.

**`qwen9b-abliterated` feels slow.** Thinking is off by default. Every orchestrator
call sends `"think": false`, so the wait is the 9B model generating on
this GPU (the reference card is an RTX 2060 6GB), not a hidden reasoning
pass. `jarvis.py` uses the smaller `qwen2.5:3b` for `ask` and `chat`.

**VLC is unreachable.** Start `~/Jarvis/vlc_remote.sh`. That binds the
HTTP interface to `127.0.0.1:8090`. If VLC answers 401, `VLC_HTTP_PASSWORD`
does not match the password in VLC's Lua HTTP preferences.

**PipeWire device names changed.** Run `pactl list sources` and
`pactl list sinks` to see current device names, then update `MIC` and
`SPK` in `~/Jarvis/jarvis.py` to match.

## Files

| File | Role |
|---|---|
| `orchestrator.py` | HTTP brain on port **8080**. Stdlib only. |
| `jarvis_voice.py` | Mic, Whisper, gate, orchestrator, Piper. Manual. |
| `jarvis_voice.sh` | Launches the voice loop with `~/Jarvis/venv`. |
| `jarvis.py` | Direct helper. Model `JARVIS_MODEL`, default `qwen2.5:3b`. |
| `jarvis.sh` | Launches `jarvis.py` with the venv. |
| `enroll.py` | Records 5 takes and writes `profiles.json`. |
| `voice_gate.py`, `voice_gate.json` | Speaker check. Threshold 0.45, UNCALIBRATED. |
| `vlc_remote.sh` | VLC HTTP on `127.0.0.1:8090`. No password in the file. |
| `requirements-voice.txt` | Venv packages. |
| `requirements-orchestrator.txt` | SpeechBrain stack for the gate and enrollment. |
| `install.sh` | Prerequisite check, venv, pip, next steps. |
| `.env.example` | Placeholder names only. |
| `units/orchestrator.service` | Optional login service for the orchestrator. |
| `units/pipewire-mix.service` | Optional login service for PipeWire routing. |
| `dashboard/v7/` | The previous dashboard, kept as history. |
| `dashboard/v8/` | The previous dashboard, kept as history (live until 2026-11-07 ~00:18 ET). |
| `dashboard/v9/` | The previous dashboard, kept as history (live until 2026-11-07 ~00:45 ET). |
| `dashboard/v10/` | Two media roots, primary first: the iPad Pro MP4 folder for VLC and in-browser playback, the drive secondary. LIVE on the Acer since 2026-11-07 ~00:45 ET. |
| `gpu-orchestrator/` | GPU brain manager (9B VRAM / 27B RAM). **DEPLOYED 2026-11-06, loop proven, keep-alive v2** (midnight run confirmed 2026-11-07 00:02). |
| `router/` | The little router (`04-little-router.py`, port 11435) + its design record (`03-router.md`, `PLAN.md`, `TONIGHT-RUNBOOK-2026-11-05.md`). |
| `scripts/` | Acer setup scripts in run order: drive mount + inventory, the 2026-11-05 consolidation scripts, autostart, keep-alive, router tests, brain inventory + backup. |
| `plans/` | The design plans behind the build (dashboard, drive clean-out, C270 teardown, REA bench shopping list), each with a dated status note. |
| `pi500/` | The Raspberry Pi 500+ rig: top 10, software stack, accessories. Ordered and paid for 2026-11-05; role still to be decided. |
| `c270/` | The Logitech C270 enumeration, captures and the rainbow clip. |
| `autostart/` | The autostart launchers (router, orchestrator, dashboard, keep-alive). |
| `ipad-kali-plan.md` | Kali on the iPad plan. PARKED; downloads done, build not started. |
| `transcripts/` | The model-response archive: every reply from the 9B, the 27B and REA, scrubbed, one file per day. Capture starts 2026-11-07 ~00:31 ET. |
| `RECAP-2026-11-06.md` | The full day 2026-11-06 into 2026-11-07, state as of ~00:35 ET — done, in progress, parked, standing rules. |
| `STATE-2026-11-07.md` | The exact moment, 2026-11-07 ~00:10 ET — the whole system, as it stands. |

## History note

The prior Windows build of this guide (with `install.ps1`, `C:\Jarvis`
paths, Windows scheduled tasks, and VoiceMeeter) is preserved in git
history. It was removed from this file on HgX's explicit word
(2026-11-04) and rewritten for Kali Linux. The live platform is Kali
Linux; the Windows build is not the current platform.

---

@basementjarvisu · basementjarvisunleashed@gmail.com
