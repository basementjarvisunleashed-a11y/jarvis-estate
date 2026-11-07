# Set up Local Jarvis from scratch

Run the whole system yourself, from this repo alone. Clone it, follow the
steps in order, and you end up with the same machine: a Kali laptop that
listens, reasons on two local brains, shows everything on a dashboard, and
renders pictures — with the GPU handed between them automatically.

**Status: 2026-11-07.** This guide covers what is in the repo today: the
core voice stack, the dual brain, REA, dashboard v7, the GPU
orchestrator (deployed), the voice-loop patch v5, the Acer setup scripts,
the brain inventory/backup scripts, the iPad Kali plan, tonight's
runbook, and the Acer source snapshot — the live router, orchestrator,
voice loop, autostart launchers, and C270 captures from the laptop
(2026-11-06 23:36 ET).
Still to land: the iPad Kali downloads (UTM, Kali ISO, StikDebug —
sources documented in the plan, installers never uploaded) and dashboard
v8 (built and verified 2026-11-06 ~23:54 ET, awaiting HgX's word — not
applied, not published). Nothing here is faked: a step marked pending
is pending.

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
| Router (easy → 9B, hard → 27B) | `local-jarvis/router/04-little-router.py` | Live on the reference machine (23:36 snapshot; integration wiring post-snapshot, see `router/README.md`) | 11435 |
| REA (reverse engineering) | `local-jarvis/LOCAL-JARVIS-STACK.md` §3 | Built | CLI |
| Dashboard v7 | `local-jarvis/dashboard/v7/` | Previous dashboard, kept as history | 8899 |
| Dashboard v8 | `local-jarvis/dashboard/v8/` | Previous dashboard, kept as history (live until 2026-11-07 ~00:18 ET) | 8899 |
| Dashboard v9 | `local-jarvis/dashboard/v9/` | Previous dashboard, kept as history (live until 2026-11-07 ~00:45 ET) | 8899 |
| Dashboard v10 | `local-jarvis/dashboard/v10/` | LIVE on the reference machine since 2026-11-07 ~00:45 ET (v9 backed up) — two media roots: the iPad Pro MP4 folder primary, the drive secondary | 8899 |
| GPU orchestrator | `local-jarvis/gpu-orchestrator/` | DEPLOYED on the reference machine 2026-11-06 ~23:50 ET, loop proven | 11436 |
| Live orchestrator + voice loop | `local-jarvis/orchestrator.py`, `local-jarvis/jarvis_voice.py` | Live files from the Acer (Kali versions; voice loop carries patch v5) | 8080 |
| Current state snapshot | `local-jarvis/STATE-2026-11-07.md` | The exact moment, 2026-11-07 ~00:10 ET — the whole system, as it stands | — |
| Model responses | `local-jarvis/transcripts/` | The transcript archive: every model response (9B, 27B, REA), scrubbed, one file per day | — |
| Day's recap | `local-jarvis/RECAP-2026-11-06.md` | The full day 2026-11-06 into 2026-11-07, state as of ~00:35 ET — done, in progress, parked, standing rules | — |
| Autostart launchers | `local-jarvis/autostart/` | Live launchers (23:36 snapshot; keep-alive v2 superseded the ping at 23:46) | — |
| C270 captures | `local-jarvis/c270/` | Descriptors, usbmon, 9B summary, rainbow clip | — |
| Voice-loop patch v5 | `local-jarvis/voice-loop/` | Built, applied on the reference machine | — |
| Acer setup scripts | `local-jarvis/scripts/` | Built (autostart, keep-alive, CPU fix, router test, inventory, backup) | — |
| iPad Kali plan | `local-jarvis/ipad-kali-plan.md` | PARKED (HgX's order 2026-11-06 22:02 ET); downloads done, build not started | — |
| Build plans | `local-jarvis/plans/` | The design records: dashboard, drive clean-out, C270 teardown, REA bench shopping list | — |
| Pi 500+ rig | `local-jarvis/pi500/` | The Raspberry Pi 500+ rig: top 10, software stack, accessories (ordered + paid 2026-11-05) | — |
| Tonight's runbook (2026-11-06) | `local-jarvis/tonight-runbook-2026-11-06.md` | Dated record of the build night | — |
| ComfyUI (picture brain) | See `gpu-orchestrator/DESIGN.md` → "ComfyUI contract" | Installed separately | 8188 |
| VLC remote | `vlc_remote.sh` / `vlc_remote.cmd` | Built | 8090 |
| C270 camera work | Lands in a later batch | Pending | — |
| Brain inventory + backup scripts | Lands in a later batch | Pending | — |

## Reference machine — the complete list (2026-11-06)

Everything below is the machine this guide reproduces. It is the whole
list: if it is not here, it is not part of the setup. The dated
snapshot `local-jarvis/STATE-2026-11-07.md` is the exact moment as of
2026-11-07 ~00:10 ET — read that first for the current state; this
section is the stable reference underneath it.

**Hardware:** Acer Nitro laptop; 512 GB NVMe internal drive; 64 GB RAM,
DDR4, 2× 32 GB, 3200 MT/s rated, 2933 MT/s running; NVIDIA GeForce RTX
2060, 6 GB VRAM; graphics driver 550.163.01, CUDA 12.4.

**OS:** Kali Linux, everything on the internal drive.

**AI brains (Ollama):** `qwen9b-abliterated` (9B, VRAM, default, fast);
`huihui_ai/Qwen3.8-abliterated:27b` (27B, system RAM, hard reasoning).
Also present: `qwen3:8b` (former orchestrator default, fallback only),
`qwen2.5:3b` (helper, fallback only),
`richardyoung/agents-a1-4b-heretic:Q4_K_M` (present, in no live code).
The inventory script (`scripts/llm-inventory.sh`) also documents the
embedding model, the speech models, and the unused weight files — see
its output notes in the script itself.

**Router:** model router on port 11435 — easy calls to the 9B, hard calls
to the 27B, cloud route (Grok) unconfigured, free route on port 3001
(FreeLLMAPI, fallback only).

**Orchestrator:** voice orchestrator on port 8080.

**Dashboard:** port 8899, reachable over the tailnet.

**Picture brain:** ComfyUI 0.44.0 on port 8188 (SD 1.5) — DOWN as of
2026-11-07 ~00:10 ET (parked, the 9B has the GPU).

**Voice:** faster-whisper `small.en` for speech-to-text, Piper
`en_GB-alan-medium` for speech; VoiceStudio 0.5.7 (not running);
Hex 3.3.0 (never run).

**REA:** `rea-agents@6.7.0`.

**Peripherals:** Logitech C270 webcam, MaonoCaster AU-AM200 audio
interface, 4 TB external drive (mounted at `/mnt/hgx`), second monitor,
cooling mat.

**Brain backup (NOT on GitHub):** `/mnt/hgx/JarvisBackup/llm-2026-11-06/`
— 58 GB on the 4 TB drive (Hugging Face cache 12 GB, loose GGUFs
~14.5 GB, Ollama models 32 GB). Documented so the copy is known; the
weights and the backup never go to GitHub.

**Apple devices:** iPhone 16 Pro Max (iOS 26.6.2, 256 GB); iPad Pro 11"
3rd gen (M1, 1 TB, 16 GB RAM, iPadOS 26.6.2); Apple Watch Ultra 2
(49mm, watchOS 26.6, 64 GB). iPad Kali: PARKED, downloads done (UTM
5.0.8, Kali 2026.3 ISO + SHA256, StikDebug 3.2.0), build not started —
see `local-jarvis/ipad-kali-plan.md`.

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
| Also present | `qwen3:8b`, `qwen2.5:3b`, `richardyoung/agents-a1-4b-heretic:Q4_K_M` | — | — | — | Fallbacks / unused; see `scripts/llm-inventory.sh` |

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
orchestrator `:8080` → Ollama `qwen9b-abliterated` → tools / VLC / REA → Piper
(`en_GB-alan-medium`). Router v2.2, 50 second voice budget, 60 second
client wait.

### 4. The router (port 11435)

The router is the single door for LLM calls: easy calls go to the 9B,
hard calls go to the 27B. The live file is in the repo:
`local-jarvis/router/04-little-router.py` (snapshot 2026-11-06 23:36
ET). It already carries the CPU fix (hard route `num_gpu 0`). The GPU
orchestrator wiring — ask the orchestrator before an easy call, fail
open when it is down, fail closed with 503 when the GPU is busy
rendering — was applied to the live router after the snapshot (~23:44
ET); apply it exactly as documented in `gpu-orchestrator/DESIGN.md` →
"Router integration" (helper: `router_integration.py` in the
orchestrator folder). Test it with
`scripts/jarvis-router-both-brains-test.sh` (easy → 9B, hard → 27B).

### 5. REA

```bash
npx rea-agents setup
npx rea-agents analyze /path/to/app
```

`rea-agents@6.7.0`, with the reverse-engineering skill and Ghidra guided
workflows. Local app analysis only — own devices and own targets only,
consenting adults, controlled lab only, spine SEE → DOCUMENT → LOG →
PREVENT. See `LOCAL-JARVIS-STACK.md` §3.

### 6. Dashboard v10 (port 8899)

**v10 is live** on the reference machine since 2026-11-07 ~00:45 ET
(applied from `local-jarvis/dashboard/v10/`, v9 backed up to
`dashboard.bak-v9`). Install it the same way below, from the v10
folder. v9, v8, and v7 stay in the repo as history.

What changed vs v9: two media roots, primary first. A local folder of
2,785 H.264/AAC MP4 files (239 GB, 24 shows) is the primary media
source for VLC and in-browser playback; the drive is secondary, only
for shows not in that folder. One entry per show, MP4 version wins, no
duplicates; `/api/media` reports the roots. If the MP4 folder is
missing, the drive alone carries the list. First media call after a
restart may be slow (the real folder was tested only on a small copy),
then cached.

What it is: the always-on screen — GPU, temperatures, RAM, what's
running, what each model is doing, local weather, Wi-Fi, REA status,
models online/offline, the last things REA did, a media tile (one quarter
of the screen; voice or button takes it fullscreen), a live two-way
conversation feed, and a live webcam panel.

```bash
# from the repo:
cp -r local-jarvis/dashboard/v10 ~/tonight-scripts/dashboard/   # or any folder
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

Checks (from `dashboard/v9/README-FIRST.txt`): the clock ticks every
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

Deployed on the reference machine 2026-11-06 (~23:42–23:50 ET), in this
order:

1. **Router:** `router_integration.py` (`ensure_gpu_llm`) wired into the
   easy route only. The hard route never asks.
2. **Autostart:** `start-gpu-orchestrator.sh` in `~/Jarvis/autostart/`
   and `gpu-orchestrator.desktop` in `~/.config/autostart/`; service
   answers on `:11436`.
3. **Keep-alive:** `keep-brains-alive.sh` replaced with
   `keep-brains-alive-v2.sh` (old kept as `.bak`). Same log file, same
   order (9B first, then 27B) — the one change is that it skips the 9B
   ping while the 9B is parked, so it never reloads it mid-render. Cron
   stays `0 */6 * * *`. Dry-run first: `./keep-brains-alive-v2.sh
   --dry-run`.
4. **Loop proven:** acquire `comfy` → 9B parked, ComfyUI up, VRAM 132
   of 6,144; one easy router call → 9B back, both brains resident, VRAM
   4,830, mode `llm`.

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
| 8899 | Dashboard v10 (live; v9/v8/v7 history) |
| 11434 | Ollama |
| 11435 | Router |
| 11436 | GPU orchestrator |
| 3001 | FreeLLMAPI (free route, fallback only) |

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
