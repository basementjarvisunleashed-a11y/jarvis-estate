# Overnight BLA + 27B runner v1

HgX starts this before bed; it runs while he sleeps and leaves a morning
report. Two jobs, in order:

1. **Resume the CrackMe v9 Sovereign runner to completion.** The CrackMe
   v1 runner was killed at 08:25 ET 2026-11-10 to free the CPU for Claude
   Code. It is resumable: the license task is DONE (07:41, 1,870 chars)
   and the WASM task was on attempt 2 when killed. This runner launches
   it, waits for it to finish (it may take hours — WASM + policy + wat +
   panel + key verification, up to a 12-hour wait cap), and records the
   result. It never kills the CrackMe runner.
2. **A BLA red-vs-blue test.** `bla harden` on a tiny test license-check
   file (created by this runner in its own work dir — NOT a real
   artifact, NOT the Jarvis dashboard), then ONE short 27B call analyses
   the hardened output and reports whether the 27B can still recover the
   secret key. The verdict is honest: "recovered" only if the 27B quotes
   the exact secret, "not recovered" if it cannot, "inconclusive" if the
   harden step or the 27B call failed. One small test only — it says
   whether BLA held up against THIS tiny license check, not whether BLA
   holds up in general.

## Before it starts

- **The HARD RULE guard.** It checks for any running 27B runner
  (crackme-v9.py, overnight-27b.py, or other 27B rounds). If one is
  running, this runner exits cleanly and does NOT start a second one.
- **The 27B is loaded and resident.** It checks `ollama ps`; if the 27B
  is not loaded, it loads it (num_ctx 4096, num_gpu 0, keep_alive 24h)
  and verifies it. The 9B is untouched — it lives on the GPU, the 27B
  lives on CPU/RAM, they coexist.

## How to run

```bash
bash start-overnight.sh
```

It runs in the background. Expect hours (the CrackMe alone is ~2–3.5
hours for its four remaining tasks, plus the BLA test). Re-running is
safe: completed work is skipped (resumable). Flags:

- `bash start-overnight.sh` — normal run (skips completed work).
- To force a full re-run, edit the start command: `python3
  overnight-27b.py --force` (ignores saved state).
- To re-run only the BLA test: `python3 overnight-27b.py --redo-bla`.

## How to check it (in the morning)

```bash
tail -30 ~/overnight-27b/overnight.log
cat ~/overnight-27b/status.txt
cat ~/overnight-27b/report.md
```

Stop it with `pkill -f overnight-27b.py` (only one 27B runner at a
time — never run two). Note: stopping the overnight runner does NOT
stop the CrackMe runner if it already launched it — stop that
separately with `pkill -f crackme-v9.py` if you really mean to (the
CrackMe runner is resumable, so stopping it loses nothing but time).

## How to verify a CrackMe candidate key by hand

```bash
node ~/crackme-v9/work/license.cjs <16-char-key>
```

UNLOCKED prints the FLAG; anything else prints DENIED. Confirm a FLAG
by checking its SHA-256 against the public commitment
`06772462f4ba0586ca27aaecf8fd4da5919a336b84f6855de009fc0751c5cf0e`:

```bash
printf '%s' 'FLAG{...}' | sha256sum
```

## Files the runner writes (all under ~/overnight-27b/)

- `work/bla-test/` — the BLA test target (license-check.js, a test-only
  secret), the `bla harden` output, and the hardened files
- `report.md` — the morning report (CrackMe result, BLA verdict, 27B
  calls, failures)
- `status.txt` — result, CrackMe outcome, BLA verdict
- `state.json` — what is already done (resumability)
- `overnight.log` — the job log
- `27b-calls.jsonl` — every 27B prompt + reply this runner made
  (response capture; the CrackMe runner's own calls are in
  ~/crackme-v9/27b-calls.jsonl)
- `crackme-run.log` — the CrackMe runner's stdout while this runner
  waited for it (its own log is ~/crackme-v9/crackme-v9.log)

## Rollback

Delete `~/overnight-27b/` (the work dir, the report, the state, and the
logs). Nothing else is touched — the BLA vault originals, the CrackMe
work dir, the dashboard, the webcam app, the brains, and the router
are never modified. (The CrackMe runner's own files live in
~/crackme-v9/ and are left alone.)

## Honest limits

- This runner has been verified only with simulated tests on this
  machine (see the test file). The first real proof is HgX running it
  on the Acer.
- The 27B sometimes returns empty replies. Every call retries (4
  attempts, backoffs 30/90/180s) and a failed task gets an honest
  placeholder, not an invented finding. Prompts are short and chunked
  (under 3400 chars) by design — the 27B fails on long outputs
  (one-shot) but succeeds reliably on short, chunked prompts.
- The BLA test hardens ONE tiny file and asks the 27B ONE question
  about it. It is a smoke test of the red-vs-blue loop, not a proof
  about BLA in general. `bla harden` behaviour (where it writes the
  hardened output) is taken from whatever the CLI actually does on the
  Acer — the runner finds changed/new files in its test dir and
  analyses the first one; if nothing changed, it records that honestly.
- The CrackMe wait cap is 12 hours. If the CrackMe is still running
  after that, this runner stops waiting (it does NOT kill it), defers
  the BLA test (it needs the 27B too), and the next night's run picks
  up the result. In practice the CrackMe should finish in ~2–3.5 hours.
- The 27B load step uses the Ollama direct API. If Ollama is down, the
  run fails honestly at the start (nothing runs, no time wasted).
- A solve requires the FLAG's SHA-256 to match the public commitment.
  No key, FLAG, or verdict is ever invented.

---

## Publication note (publishing house, 2026-11-10)

Published as-is from the REA room's parcel
(`overnight-bla-27b-2026-11-10.zip`, 16,864 bytes, MD5
`cf91aa3aed32596ce4b60586c2d5aab0`). Identity grep clean (no real name, no private home paths); `py_compile` clean. One stale path in the
script's own docstring: it cites `~/crackme-v9-runner/crackme-v9.py`
— the actual runner lives at `~/crackme-v9/crackme-v9.py` (as this
README states). The BLA test secret in the script is a test fixture
invented for the smoke test, not a real credential.
