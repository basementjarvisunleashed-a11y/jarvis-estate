# Brains autostart — load 9B + 27B at login

HgX's order (2026-11-08 ~19:25 ET): everything must load at reboot,
including the two LLM brains (which previously loaded only on demand or
at the 6-hourly keep-alive cron).

## What it does

- `start-brains.sh` (installed to `~/Jarvis/autostart/start-brains.sh`):
  waits for ollama serve to answer, then loads the 9B
  (`qwen9b-abliterated`, GPU, ctx 8192) first, then the 27B
  (`huihui_ai/Qwen3.8-abliterated:27b`, RAM, `num_gpu 0`, ctx 4096).
  Both pinned with `keep_alive 24h`. Load order matters: 9B first,
  then 27B (reloading 9B after 27B evicts the 27B).
  Logs to `~/Jarvis/start-brains.log`. Safe to run by hand any time.
- `brains.desktop` (installed to `~/.config/autostart/brains.desktop`):
  Xfce autostart entry that runs `start-brains.sh` at login.
- The 6-hourly keep-alive cron
  (`0 */6 * * * ~/Jarvis/autostart/keep-brains-alive.sh`) is unchanged
  and still refreshes the 24h pins.

## How to apply

```bash
cd ~
curl -L -o brains-autostart.zip "<URL>"
echo "<MD5>  brains-autostart.zip" | md5sum -c -
mkdir -p ~/brains-apply
unzip -o brains-autostart.zip -d ~/brains-apply
cd ~/brains-apply
bash apply-brains-autostart.sh
```

The apply script installs both files and starts a background load of
both brains immediately (so they load now, not only at the next reboot).
The 9B loads first (fast), then the 27B (a few minutes, 18 GB into RAM).

## How to verify

- Right after applying: `ollama ps` — after a few minutes it should
  list both `qwen9b-abliterated` and
  `huihui_ai/Qwen3.8-abliterated:27b` (the 27B takes a few minutes).
- Log: `tail -n 50 ~/Jarvis/start-brains.log`
- After the next reboot/login: `ollama ps` should list both brains
  within a few minutes of login, without anyone asking.

## How to remove

```bash
rm ~/.config/autostart/brains.desktop ~/Jarvis/autostart/start-brains.sh
```

The brains will then go back to loading on demand / at the keep-alive
cron only. Removing the autostart does not unload brains that are
already resident.

## Publication note (Release Bot, 2026-11-10)

Scrubbed for publication: the only identity/path hit in this parcel was
`brains.desktop` line 5 (the `Exec` path, `/home/<username>/Jarvis/autostart/start-brains.sh`
→ `Exec=/home/owner/Jarvis/autostart/start-brains.sh`). `start-brains.sh`,
`apply-brains-autostart.sh`, and this README use `$HOME` / `~/` only and
are verbatim. No other change: `start-brains.sh` still loads the 9B with
`num_ctx` 8192 — the 32768 update is a separate pending Acer-side fix,
not made here. Verified on the Acer 2026-11-08: both brains load in ~41s
at reboot (9B ctx 8192, 27B ctx 4096, both 24h pins); keep-alive cron
unchanged (`0 */6 * * *`). Source zip MD5
`1525f2d9036279de4cd1697b353420c9` (2,862 bytes). Note: the `.desktop`
`Exec` path is a placeholder — adjust it to your own home directory if
you install by hand; `apply-brains-autostart.sh` installs the file
verbatim.

---

## Update 2026-11-10 (publishing-house note)

The live `start-brains.sh` on the Acer was updated after fcc-claude was
confirmed working: it now loads `qwen9b-abliterated-32k` with `num_ctx`
32768 at boot (line 18, backup `start-brains.sh.bak-32kmodel`). The
repo copy of `start-brains.sh` in this folder predates that update —
the updated file follows when the REA room sends it. The Modelfile for
the custom model is at `../models/qwen9b-abliterated-32k.Modelfile`.
