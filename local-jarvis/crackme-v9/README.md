# CrackMe v9 Sovereign — REA runner v1 (recon + first-pass analysis)

The red-vs-blue test: HgX's REA (red) against BLA's hardening (blue).
Target: the BLA-hardened CrackMe v9 Sovereign vault (BLA 3.0, bankrupt
intensity, weaveScore 100). Goal: the 16-character key. The unlock lives
in the WASM (SHA-256 KDF + ARX + commitment layout).

## What v1 does

1. **Setup** — verifies the five vault digests against SEAL.json, copies
   the files to `~/crackme-v9/work/`, gunzips `core.wasm.gz` → `core.wasm`
   there, and verifies the gunzipped digest and size. The originals in
   `~/opt/bla/challenge/v9/hardened/` are **never modified** (the
   license.cjs integrity self-check hard-fails on any tamper, so the
   runner verifies digests before and after every copy).
2. **Recon** — file types, sizes, line counts; a pure-Python WASM section
   parser (exports, function/code counts — no external tool needed);
   wabt `wasm-objdump` / `wasm2wat` if present (checked first, never
   assumed); a Node.js export cross-check; structure excerpts from
   license.cjs, policy.py, panel.html. The 201 KB license.cjs is **never**
   fed whole to the 27B.
3. **Tool applicability** — names all 15 REA tools and says which apply
   to a JS/WASM/Python vault and which do not, with a reason for each.
4. **Five 27B analysis calls** (one per task, short prompts under 3500
   chars): license.cjs (the gate), WASM exports + seal.json (the unlock
   entry points), policy.py (the ledger), the WASM disassembly excerpt
   (only if wasm2wat worked), panel.html (the UI). Each finding is
   appended to `~/crackme-v9/report.md` immediately after it lands, or an
   honest placeholder naming the tool and the reason when it fails.
5. **Candidate keys** — if a 27B reply proposes a 16-character key, the
   runner verifies at most 3 candidates with `node license.cjs <key>` in
   the **working copy** and records UNLOCKED + FLAG (with the FLAG's
   SHA-256 checked against the public commitment) or DENIED. It does
   **not** brute-force and does **not** search the key space in v1.
6. **Summary** — what v1 found, what is still unknown, what the next
   round should do.

## How to run

```bash
bash start-crackme-v9.sh
```

It runs in the background. Expect roughly 30–90 minutes (five short
27B calls at ~5–27 min each, plus the WASM disassembly if wabt is
present). Re-running is safe: completed tasks are skipped (resumable).

## How to check it

```bash
tail -30 ~/crackme-v9/crackme-v9.log
cat ~/crackme-v9/status.txt
cat ~/crackme-v9/report.md
```

Stop it with `pkill -f crackme-v9.py` (only one 27B runner at a time —
never run two).

## How to verify a candidate key by hand

```bash
node ~/crackme-v9/work/license.cjs <16-char-key>
```

UNLOCKED prints the FLAG; anything else prints DENIED. Confirm a FLAG
by checking its SHA-256 against the public commitment
`06772462f4ba0586ca27aaecf8fd4da5919a336b84f6855de009fc0751c5cf0e`
(SEAL.json `flagSha256`):

```bash
printf '%s' 'FLAG{...}' | sha256sum
```

## Files the runner writes (all under ~/crackme-v9/)

- `work/` — working copies of the five vault files + core.wasm
  (gunzipped) + core.wat (if wasm2wat worked) + tool outputs
- `report.md` — the findings, one section per 27B call
- `27b-calls.jsonl` — every 27B prompt + reply (response capture)
- `crackme-v9.log` — the job log
- `status.txt` — result, tasks, candidates, solved or not

## Rollback

Delete `~/crackme-v9/` (the working copies, the report, and the logs).
Nothing else is touched — the vault originals, the dashboard, the
webcam app, the brains, and the router are never modified.

## Honest limits

- v1 is recon + first-pass analysis. It does **not** crack the vault on
  its own and does **not** search the key space. A later round does the
  deeper WASM work and, only if the analysis points to a searchable
  space, a key-space search.
- wabt availability is unknown until the Acer run. If it is absent, the
  disassembly task is a placeholder and the WASM task analyses the
  export list instead.
- The 27B sometimes returns empty replies. Every call retries (4
  attempts, backoffs 30/90/180s) and a failed task gets an honest
  placeholder, not an invented finding.
- The 27B prompts are short and chunked (under 3500 chars) by design —
  the 27B fails on long outputs (one-shot) but succeeds reliably on
  short, chunked prompts. That lesson is from the C270 breakdown.
- This runner has been verified only with simulated tests on this
  machine (see the test file). The first real proof is HgX running it
  on the Acer.
