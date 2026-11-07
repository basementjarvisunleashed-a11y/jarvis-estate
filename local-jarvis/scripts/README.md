# Acer setup scripts (2026-11-06)

One-shot setup and check scripts for the reference machine. All are
idempotent where stated, delete nothing (except where a backup is kept),
and print what they did. Run them on the Acer, in this order.

**Earlier steps (the 2026-11-05 build night, before the list above):**

1. `mount-media-drive.sh` — mount the 4 TB media drive read-write at
   `/mnt/hgx` (finds it by label, never by device name).
2. `drive-inventory.sh` — read-only listing of the drive (top level,
   biggest folders, total). Deletes nothing; run any time.
3. `01-check.sh` — read-only diagnosis for the LLM consolidation: what
   is running, what is loaded, where the 9B GGUF lives, disk use.
4. `05-import-9b.sh` — move the 9B GGUF out of Locally Uncensored and
   into Ollama as `qwen9b-abliterated` (finds the GGUF, builds the
   Modelfile, imports, proves it answers on the GPU). Run BEFORE the
   cleanup — deleting first would destroy the model being kept.
5. `02-cleanup.sh` — DRAFT, gated: do NOT run until the 9B is confirmed
   inside Ollama AND the voice audit has confirmed which models are
   unused (it asks for `AUDIT-DONE`). Removes only the named Ollama
   models, one by one, each with a confirmation prompt.

**Run order (matters):**

1. `jarvis-autostart-setup.sh` — creates the Xfce autostart entries
   (router :11435, orchestrator :8080, dashboard :8899) and launchers in
   `~/Jarvis/autostart/`, starts the services now, and verifies them.
2. `jarvis-keep-brains-alive-setup.sh` — writes `keep-brains-alive.sh`
   (pings both brains, 24h pin) and installs the 6-hour cron; rewrites
   the router launcher so the hard route pins 24h (was 1h).
3. `jarvis-both-brains-cpu-fix.sh` — pins the 27B to CPU/system RAM
   (`num_gpu 0`) in the router and in the keep-alive ping, restarts the
   router, reloads both brains, prints `ollama ps` + `free` +
   `nvidia-smi`. Run AFTER step 2: it rewrites the keep-alive script
   step 2 just wrote, with the CPU-only 27B ping.
4. `jarvis-router-both-brains-test.sh` — asks the router an easy question
   (expect the 9B) and a hard question (expect the 27B, CPU-only, takes
   a minute or two), prints each answer with the model the router
   reports, then `ollama ps` and the router log.

**Brain inventory + backup (run any time, after step 0 checks):**

| File | What it is |
|---|---|
| `llm-inventory.sh` | Read-only: `ollama list` + `ollama ps`, every GGUF on disk, Hugging Face cache, Ollama store size, and what each model is for. Send the whole output to Jarvis. |
| `llm-backup.sh` | Copy-only to `/mnt/hgx/JarvisBackup/llm-2026-11-06/`: Ollama models + Hugging Face cache + loose GGUFs. Guards on the drive being mounted and free space covering the copy; verifies with sizes and file counts. Nothing is moved or deleted. The backup exists there (58 GB total: Hugging Face cache 12 GB, loose GGUFs ~14.5 GB, Ollama models 32 GB) — see `local-jarvis/STATE-2026-11-07.md`. |

**Superseded (do not use the old one):** the GPU orchestrator IS deployed
(2026-11-06), so `keep-brains-alive-v2.sh` (in
`local-jarvis/gpu-orchestrator/`) is the live keep-alive — swapped in on
the Acer at 23:46, old file kept as `.bak`. The `keep-brains-alive.sh`
in `local-jarvis/autostart/` is the pre-swap version (23:36 snapshot).

**Files:**

| File | What it is |
|---|---|
| `mount-media-drive.sh` | Mount the 4 TB media drive read-write at `/mnt/hgx` (by label). |
| `drive-inventory.sh` | Read-only listing of the media drive. |
| `01-check.sh` | Read-only diagnosis for the LLM consolidation. |
| `05-import-9b.sh` | Move the 9B GGUF into Ollama as `qwen9b-abliterated`. |
| `02-cleanup.sh` | DRAFT, audit-gated: remove only the models the audit cleared. |
| `jarvis-autostart-setup.sh` | Router + orchestrator + dashboard autostart (see order above). |
| `jarvis-keep-brains-alive-setup.sh` | Keep-alive script + 6-hour cron + router launcher pin. |
| `jarvis-both-brains-cpu-fix.sh` | 27B to CPU-only (`num_gpu 0`) in router + keep-alive. |
| `jarvis-router-both-brains-test.sh` | Easy/hard router test with model reporting. |
| `llm-inventory.sh` | Read-only brain inventory. |
| `llm-backup.sh` | Copy-only brain backup to the media drive. |
