# Set up Local Jarvis from scratch

Run the whole system yourself, from this repo alone. Clone it, follow the
steps in order, and you end up with the same machine: a Kali laptop that
listens, reasons on two local brains, shows everything on a dashboard, and
renders pictures — with the GPU handed between them automatically.

**Status: 2026-11-07.** This guide covers what is in the repo today: the
core voice stack, the dual brain, REA, dashboard v7, and the GPU
orchestrator. The router script, the voice-loop scripts, the autostart
scripts, the C270 camera work, and the brain inventory/backup scripts are
Acer-side files that land in a later batch; this guide says plainly where
each one goes and will be updated when they arrive. Nothing here is
faked: a step marked pending is pending.

**What is NOT in this repo (by design):** no model weights, no backups,
no personal media, no credentials, no personal data. Model names and tags
are listed so you download the weights from the source. Passwords in this
tree are the placeholder `CHANGE_ME`; user accounts are `<user>`. Set both
on your own machine. Do not commit the real values.

## Inventory — everything, and where it lives

| Component | In the repo | Status | Port |
|---|---|---|---|
| Kali platform | `local-jarvis/PLATFORM-KALI.md` | Built | — |
| Core voice stack + orchestrator | `local-jarvis/README.md`, `orchestrator.py`, `jarvis_voice.py` | Built | 8080 |
| Voice gate + enrollment | `voice_gate.py`, `enroll.py`, `calibrate.py` | Built | — |
| Dual brain (9B VRAM + 27B RAM) | `local-jarvis/LOCAL-JARVIS-STACK.md` §2, §4.1 | Built | via 11434/11435 |
| Router (easy → 9B, hard → 27B) | Documented in `LOCAL-JARVIS-STACK.md` + `gpu-orchestrator/DESIGN.md` | Script lands in a later batch | 11435 |
| REA (reverse engineering) | `local-jarvis/LOCAL-JARVIS-STACK.md` §3 | Built | CLI |
| Dashboard v7 | `local-jarvis/dashboard/v7/` | Built, live on the reference machine | 8899 |
| GPU orchestrator | `local-jarvis/gpu-orchestrator/` | Built, verified, not deployed | 11436 |
| ComfyUI (picture brain) | See `gpu-orchestrator/DESIGN.md` → "ComfyUI contract" | Installed separately | 8188 |
| VLC remote | `vlc_remote.sh` / `vlc_remote.cmd` | Built | 8090 |
| C270 camera work | Lands in a later batch | Pending | — |
| Brain inventory + backup scripts | Lands in a later batch | Pending | — |

## Prerequisites

- A laptop with an NVIDIA GPU (the reference machine: Acer Nitro AN515-55,
  i7-10750H, 64 GB RAM, RTX 2060 ~6 GB VRAM, 512 GB NVMe). A smaller card
  works for the 9B alone; the dual-brain + ComfyUI sharing needs the 6 GB
  card and the GPU orchestrator below.
- **Kali Linux** installed on the internal drive, all tools updated,
  graphics driver in, Bluetooth and Wi-Fi working. See
  `local-jarvis/PLATFORM-KALI.md`.
- **Ollama** running on `127.0.0.1:11434`.
- **Python 3** (system Python 3.13 on the reference machine), **VLC**,
  **curl**, **Tailscale** (for reaching the dashboard from a phone/tablet).
- A media drive is optional: the dashboard reads shows from a mounted
  drive (the reference mount is `/mnt/hgx`). Without one, the media tile
  simply reports unmounted.

## The models — names and tags only

Download the weights from the source (`ollama pull <tag>`). Nothing is
shipped here.

| Model | Tag | Size | Home | Context | Role |
|---|---|---|---|---|---|
| Small brain | `qwen9b-abliterated` | ~6 GB loaded | VRAM (fast, default) | 8192 | REA default, voice loop, easy calls |
| Large brain | `huihui_ai/Qwen3.8-abliterated:27b` | ~18 GB loaded | System RAM (slow, hard reasoning) | 4096 | Hard reasoning, long code, multi-step chains |
| Helper | `qwen2.5:3b` | Small | CPU/VRAM | — | `jarvis.py` helper (list/play/ask/say/chat) |
| Voice in | Whisper `small.en` | — | CPU | — | Speech to text |
| Voice out | Piper `en_GB-alan-medium` | — | CPU | — | Text to speech |
| Picture brain | SD 1.5 (`v1-5-pruned-emaonly-fp16.safetensors`) | ~2 GB VRAM | ComfyUI | — | Image renders |

**The safe order (do not break it):** load the 9B first, then the 27B.
Reloading the 9B while the 27B is resident can evict the 27B. The 27B
always loads with `num_gpu 0` — it is 18 GB and can never live on a 6 GB
card. Keep both pinned: a keep-alive run every 6 hours pins each brain
for 24 hours (`keep-brains-alive-v2.sh` in the orchestrator folder, once
it is deployed; see step 8).

## Setup, in order

### 1. Clone the repo and install the core

```bash
git clone https://github.com/basementjarvisunleashed-a11y/jarvis-estate.git
cd jarvis-estate/local-jarvis
./install.sh
```

That checks the prerequisites, creates `~/Jarvis` and its venv, and
installs the voice and orchestrator requirements. Full detail —
prerequisites, virtual environment, environment variables, enrollment and
calibration, running and testing, autostart, troubleshooting — is in
`local-jarvis/README.md`. Read it; this guide does not repeat it.

### 2. Pull the brains

```bash
ollama pull qwen9b-abliterated
ollama pull huihui_ai/Qwen3.8-abliterated:27b
ollama pull qwen2.5:3b
```

Verify both resident: `ollama ps` should show the 9B on the GPU and the
27B on the CPU. If the 27B is missing after a 9B reload, reload the 9B
first, then the 27B with `num_gpu 0` — the safe order above.

### 3. Start the orchestrator and the voice loop

```bash
# from local-jarvis/
python3 orchestrator.py        # HTTP brain on :8080 (stdlib only)
python3 jarvis_voice.py        # mic → Whisper → gate → orchestrator → Piper
```

Neither starts on its own, by design. The orchestrator listens only
after you start it; the voice loop is deliberately not auto-started.
Enroll first (`enroll.py`, 5 takes) and calibrate (`CALIBRATE.md`): the
voice gate scores audio against the enrolled profile and drops the turn
when the speaker is unenrolled. Mic → Whisper `small.en` → voice gate →
orchestrator `:8080` → Ollama `qwen3:8b` → tools / VLC / REA → Piper
(`en_GB-alan-medium`). Router v2.2, 50 second voice budget, 60 second
client wait.

### 4. The router (port 11435)

The router is the single door for LLM calls: easy calls go to the 9B,
hard calls go to the 27B. Its script lands with the Acer-side batch; the
behaviour it must have is already documented in
`gpu-orchestrator/DESIGN.md` → "Router integration" (ask the orchestrator
before an easy call; fail open when the orchestrator is down; fail closed
with 503 when the GPU is busy rendering). Do not guess the router's
internals from this guide — wire in `router_integration.py` from the
orchestrator folder when the script arrives.

### 5. REA

```bash
npx rea-agents setup
npx rea-agents analyze /path/to/app
```

`rea-agents@6.7.0`, with the reverse-engineering skill and Ghidra guided
workflows. Local app analysis only — own devices and own targets only,
consenting adults, controlled lab only, spine SEE → DOCUMENT → LOG →
PREVENT. See `LOCAL-JARVIS-STACK.md` §3.

### 6. Dashboard v7 (port 8899)

What it is: the always-on screen — GPU, temperatures, RAM, what's
running, what each model is doing, local weather, Wi-Fi, REA status,
models online/offline, the last things REA did, a media tile (one quarter
of the screen; voice or button takes it fullscreen), a live two-way
conversation feed, and a live webcam panel.

```bash
# from the repo:
cp -r local-jarvis/dashboard/v7 ~/tonight-scripts/dashboard/   # or any folder
cd ~/tonight-scripts/dashboard/
chmod +x restart-dashboard-tailnet.sh
./restart-dashboard-tailnet.sh
```

That kills any old server and relaunches `server.py` unbuffered on
`0.0.0.0:8899`, then checks itself (`GET /api/status` must answer 200)
and prints the tailnet address. Open it on the laptop at
`http://127.0.0.1:8899`, or on a phone/tablet on the tailnet at
`http://<acer-tailnet-ip>:8899` (find yours with `tailscale ip -4`).

The media tile reads shows from your mounted media drive
(`/mnt/hgx` on the reference machine; categories `TV SHOWS`, `MOVIES`,
`MUSIC`, `VIDEOS`). Backup and system folders are never entered. One
folder name in the published copy is a placeholder (`ownerlaptop` in
`SKIP_DIRS` in `server.py`): rename it to match your own old laptop
backup folder. The media endpoints have no password by design — the
dashboard is meant to be reachable over the private tailnet only.

Checks (from `dashboard/v7/README-FIRST.txt`): the clock ticks every
second; the shows list episodes; Sports, Tailscale and Health tiles are
filled; the webcam panel shows a LIVE feed. Stream check:
`curl -s -o /dev/null -w "%{http_code}\n" --max-time 15
http://127.0.0.1:8899/api/webcam-stream` — expect 200 with a camera live,
503 when no camera is found.

### 7. GPU orchestrator (port 11436)

What it is: one service owns the 6 GB card, so nobody says "swap" again.
Callers ask by purpose (`llm` or `comfy`); it parks and loads in the safe
order and reports the state. The router asks before an easy call; the
dashboard asks before a render. Full design, states, operations, safe
rules, failure modes and deployment steps: `gpu-orchestrator/DESIGN.md`.

```bash
# from the repo:
cp -r local-jarvis/gpu-orchestrator ~/tonight-scripts/gpu-orchestrator
cd ~/tonight-scripts/gpu-orchestrator
python3 -m py_compile gpu_orchestrator.py router_integration.py
python3 test/run_tests.py        # 7/7 scenarios must PASS
python3 gpu_orchestrator.py --serve   # HTTP on 127.0.0.1:11436
```

Then wire it in, in this order:

1. **Router:** call `router_integration.py` (`ensure_gpu_llm`) before an
   easy call only. The hard route never asks.
2. **Autostart:** place `start-gpu-orchestrator.sh` in
   `~/Jarvis/autostart/` and `gpu-orchestrator.desktop` in
   `~/.config/autostart/`; confirm the service answers on `:11436`
   after a reboot.
3. **Keep-alive:** replace `keep-brains-alive.sh` with
   `keep-brains-alive-v2.sh` (keep the old one as `.bak`). Same log file,
   same order (9B first, then 27B) — the one change is that it skips the
   9B ping while the 9B is parked, so it never reloads it mid-render.
   Cron stays `0 */6 * * *`. Dry-run first:
   `./keep-brains-alive-v2.sh --dry-run`.
4. **Prove the loop:** render in ComfyUI (GPU goes to COMFY), then an
   easy router call (GPU comes back to LLM, both brains resident), then
   the next keep-alive (9B skipped while parked).

State and health: `GET /state` (mode, models, ComfyUI, VRAM, last swap,
last error), `GET /health` (liveness). A swap takes roughly 30–90 s; the
first LLM call after a render waits for it. A running render is never
killed — an LLM ask during one waits up to 120 s, then reports busy.

### 8. ComfyUI (picture brain, port 8188)

Installed separately in its own virtual environment (the reference
install: `~/ComfyUI`, SD 1.5 checkpoint
`v1-5-pruned-emaonly-fp16.safetensors`). Start it only through the GPU
orchestrator (`POST /acquire {"purpose": "comfy"}`) once the orchestrator
is deployed — starting it by hand while the 9B is resident risks an
out-of-memory failure. The orchestrator's ComfyUI contract (start, stop,
busy, idle) is in `gpu-orchestrator/DESIGN.md`.

## Verify everything

```bash
curl -s http://127.0.0.1:11434/api/ps | head -c 400     # both brains listed
curl -s http://127.0.0.1:11435/health || echo "router: not up yet"
curl -s http://127.0.0.1:8080/health || echo "orchestrator: not started"
curl -s http://127.0.0.1:11436/health || echo "gpu orchestrator: not started"
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8899/api/status  # dashboard: 200
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8188/  # comfy: 200 only in COMFY mode
ollama ps
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

## Ports

| Port | Service |
|---|---|
| 8080 | Orchestrator (voice-loop brain) |
| 8090 | VLC HTTP remote |
| 8188 | ComfyUI (only in COMFY mode) |
| 8899 | Dashboard v7 |
| 11434 | Ollama |
| 11435 | Router |
| 11436 | GPU orchestrator |

## Troubleshooting

- **A brain is missing after a reload:** reload the 9B first, then the
  27B with `num_gpu 0`. Never the other way round.
- **Out of memory on a render:** the 9B was resident. Use the GPU
  orchestrator (`acquire comfy`) instead of starting ComfyUI by hand.
- **Dashboard says a service is offline:** check the service, not the
  dashboard — the dashboard reports what it can reach. The router dot
  reads the router log; if the log path is wrong the dot lies.
- **Dashboard shows no shows:** the media drive is not mounted, or the
  scan timed out walking it. Check the mount, then the dashboard log.
- **Ghost audio after closing VLC:** press Stop on the dashboard tile;
  it kills every VLC process by name. If it persists, a VLC was launched
  by hand — `pgrep -a vlc` shows it.
- **Voice loop hears the TV as commands:** keep the loop's mic away
  from speakers; mics go quiet while Jarvis speaks.
- Deeper detail: `local-jarvis/README.md` → "Troubleshooting";
  `gpu-orchestrator/DESIGN.md` → "Failure modes";
  `dashboard/v7/README-FIRST.txt` → the v7 fix list and the tonight checks.

---

@basementjarvisu · basementjarvisunleashed@gmail.com
