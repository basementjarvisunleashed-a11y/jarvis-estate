PUBLISHING NOTE — this is the dated record of the night of Friday
2026-11-06, published as written except for the tailnet address
below (replaced with a placeholder). Two things changed later the
same night: the dashboard step below used v3, which was superseded
by v7 before the night was out (current dashboard: v7 in
local-jarvis/dashboard/v7/), and the brain backup in step 0B was
started but its completion was not confirmed in the record — do
not read this runbook as proof the backup finished.

# Tonight — Friday 2026-11-06 — the runbook

Everything in terminal script, one paste at a time, exactly how we work.
Send me what each step prints before moving on. If anything bites: stop,
send the output, we fix that one thing before moving on. No silent retries.

## 0. When you are home, at the Acer — first checks

```bash
ls /mnt/hgx && df -h /mnt/hgx
ollama ps
curl -s http://127.0.0.1:11435/health
curl -s -o /dev/null -w "dashboard %{http_code}\n" http://127.0.0.1:8899/api/status
```

- Drive mounted? Expect 3.7T total, 1.1T free. If not mounted, run
  `~/tonight-scripts/mount-media-drive.sh` (finds it by label HgX).
  Manual fallback: unmount any auto-mount at /run/media/hgx/HgX first,
  then `sudo mount -t ntfs-3g -o rw /dev/sda2 /mnt/hgx`.
- `ollama ps` should list BOTH brains (9B + 27B).
- Router /health should answer. Dashboard should answer HTTP 200.

## 0B. Brain inventory + backup — NEW, right after the first checks

The drive is confirmed mounted in step 0, so the backup runs now, before
anything else changes tonight. Copy only — nothing is moved or deleted.

```bash
bash ~/tonight-scripts/llm-inventory.sh
```

Send the whole output. Expect, in order: the 9B, the 27B, qwen3:8b,
qwen2.5:3b, agents-a1-4b-heretic — plus the GGUFs and the Hugging Face
speech models. That is the stack, in order, with what each one is for.

```bash
bash ~/tonight-scripts/llm-backup.sh
```

Copies everything to `/mnt/hgx/JarvisBackup/llm-2026-11-06/` — the Ollama
models, the Hugging Face cache, and every loose GGUF. The script checks
the drive is mounted and that the free space covers the copy, then
verifies with sizes and file counts. Send the whole output.

After this, every model exists twice: once on the laptop, once on the
drive. That is what makes any future cleanup safe. NOTHING is deleted
tonight — deletion is still deferred on your word.

## 1. Dashboard fix — FIRST

```bash
cd ~/Downloads && unzip -o dashboard-fixed-2026-11-06-v3.zip -d ~/tonight-scripts/dashboard/
cd ~/tonight-scripts/dashboard && chmod +x restart-dashboard-tailnet.sh && ./restart-dashboard-tailnet.sh
```

Expect: `GET /api/status -> HTTP 200`. Send the output.

```bash
curl -s http://127.0.0.1:8899/api/media | python3 -c "import sys,json; d=json.load(sys.stdin); print([s['name'] for s in d['shows']])"
```

Expect: THE SOPRANOS, THE BIG BANG THEORY (and the rest) listed.
Then on the iPhone/iPad, on the tailnet: **http://<acer-tailnet-ip>:8899** (printed by the restart script; find it with `tailscale ip -4`)
— the clock ticks every second, both shows have episodes, the Sports,
Tailscale and Health & Heat tiles are filled, and the webcam panel
bottom-right shows a LIVE moving feed (laptop camera first — Switch to
the C270 to check it). Stream check (it streams, so cap the wait):

```bash
curl -s -o /dev/null -w "%{http_code}\n" --max-time 15 http://127.0.0.1:8899/api/webcam-stream
```

Expect 200 with a camera live. 503 means no camera was found — send it
to me and we fix that one thing.

Make the tailnet bind survive a reboot:

```bash
cat ~/Jarvis/autostart/start-dashboard.sh
```

Send it to me — I will give the exact edit (add
`export DASHBOARD_HOST=0.0.0.0` before the python3 line).

## 2. Patch v5 + voice loop — the hands

```bash
python3 ~/Downloads/voice-loop-patch-v5-rebuilt.py
```

Send what it prints.

Offline test — record 5 seconds, speaking "open Firefox" into the
MaonoCaster while it records:

```bash
arecord -D plughw:0,0 -f S16_LE -r 48000 -c 2 -d 5 /tmp/test-firefox.wav
cd ~/Jarvis && python3 jarvis_voice.py test /tmp/test-firefox.wav --bypass-gate
```

Expect: `action="dispatched"` and a Firefox window opens. Send the output.

Live loop:

```bash
cd ~/Jarvis && python3 jarvis_voice.py loop
```

Say "open Firefox", then the acceptance test: **"VLC on, play the
Sopranos"** — VLC must open and play, and Jarvis must confirm by voice.

## 3. VoiceOver — first clips

```bash
bash ~/tonight-scripts/voiceover-check.sh
```

Send the whole output. (Read-only: VoiceStudio process + backend,
Hugging Face speech models, Hex, Ollama list, GPU.)

Then in the VoiceStudio app:
- Settings → Models — tell me which engines are installed and selected.
- Generate ONE clip in the default voice (OmniVoice).
- Then a cloned clip — record 5–15 seconds of your voice in the app first.

Hex check:

```bash
hex
```

First run may download its speech model — give it a minute, send output.

## 4. GPU pause — built live tonight

Park the 9B so VoiceStudio / ComfyUI / HyperFrames can take the card:

```bash
ollama stop qwen9b-abliterated
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

Expect VRAM used near 0 MiB. Send the output. Use the GPU while parked.

Bring the 9B back:

```bash
curl -s http://127.0.0.1:11434/api/chat -H 'Content-Type: application/json' -d '{"model":"qwen9b-abliterated","messages":[{"role":"user","content":"ping"}],"stream":false,"keep_alive":"24h","think":false}'
ollama ps
```

Expect the 9B back on VRAM. Send the output.

Catch: while parked, the 6-hour refresh would reload the 9B mid-render —
tonight we add the skip (one small change, at the keyboard, when we get
there). The 27B stays on RAM throughout — it never touches the card.

## 5. Reboot proof

```bash
sudo reboot
```

Log in, then:

```bash
ollama ps
curl -s http://127.0.0.1:11435/health
curl -s -o /dev/null -w "dashboard %{http_code}\n" http://127.0.0.1:8899/api/status
```

Send all three. Router, orchestrator and dashboard must all be up alone.

## 6. Screensaver fix + dashboard on screen

Paste Script 8 (all terminal, no GUI):

```bash
xfconf-query -c xfce4-screensaver -p /saver/enabled -n -t bool -s false
xfconf-query -c xfce4-screensaver -p /lock/enabled -n -t bool -s false
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-ac -n -t int -s 0
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-battery -n -t int -s 0
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-enabled -n -t bool -s false
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/lock-screen-suspend-hibernate -n -t bool -s false
pkill xfce4-screensaver 2>/dev/null; xset s off; xset -dpms; xset dpms 0 0 0
```

Then the read-back checks, open http://127.0.0.1:8899 fullscreen, check
the Audio tile (all mics, live states), and leave it up — it must never
blank, lock, or sign out.

## 7. iPad Kali build — the long block (2–3 h)

Full plan in `ipad-kali-plan.md` (in this parcel). iPad off Airplane Mode,
on Wi-Fi. Order: iloader on the Acer → SideStore → trust the profile →
Developer Mode → LocalDevVPN → UTM.ipa 5.0.8 → StikDebug JIT →
**JIT test FIRST — that is the gate** → Kali ARM64 ISO (~4 GB, from
kali.org, Installer Images → Apple Silicon ARM64) → VM (4 CPU cores,
8 GB RAM, 40 GB disk) → install Kali (Xfce) → SPICE guest tools → stack
(Ollama ARM64 + little Qwen 3B, rea-agents, Ghidra) → Tailscale to the
Acer brains.

First tests: Kali boots + internet in the VM; nmap scan of the home
network; REA analyzes a binary with the little Qwen summarising; the VM
reaches the Acer router over Tailscale.

## 8. Picture brain — 19:00 (jumps the queue)

Session at 19:00. When the clock says so, we pause the list and do it.

## 9. MaonoCaster clipping

Record 5 seconds, speaking normally:

```bash
arecord -D plughw:0,0 -f S16_LE -r 48000 -c 2 -d 5 /tmp/mic-test.wav
python3 -c "import wave,array; w=wave.open('/tmp/mic-test.wav'); d=w.readframes(w.getnframes()); a=array.array('h'); a.frombytes(d); print('peak:', max(abs(x) for x in a)/32768.0)"
```

Send the number. If the peak is 1.0, turn the mic gain down / step back
from the mic and repeat until it is under 1.0.

## If anything bites

Stop. Send me what it printed. We fix that one thing before moving on.
