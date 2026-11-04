# J.A.R.V.I.S. — OPERATOR PRIME Course Material
**J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System)** — public identity, first and prominent.
Operator: HgX (small). Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

> **HGX Academy** — OPERATOR PRIME is taught by HGX Academy, HgX's own academy. No university affiliation. No external accreditation claimed.

> **STATUS: LOCKED v1.0.0 — Acer fit audit, 2026-10-29. Hardware platform verification.**

> **Audience and hard rules:** Consenting adults only. Controlled laboratory only. Own devices, own tags, own networks, own targets only. Spine: SEE → DOCUMENT → LOG → PREVENT. Face work only on consenting adult participants, in the lab only, for defensive education. Templates stay in the lab, deleted after the exercise. Never family, never his son, never strangers, never real-world surveillance or deployment. Radio transmit only on own authorised frequencies. Drone only in a safe, controlled flying area, Transport Canada rules first. Lasers Class 1 only.

> **Licence:** Course text CC-BY-4.0. Code MIT. © HGX Engineering. No secrets in public. No personal data: no real names, no Wi-Fi names, no home addresses, no serials, no passwords, no credentials, no live location, no family details, no financial details. No 2.0/3.0 material. No prompt text reproduced.

---

# Acer Fit Audit — Everything from 2026-10-29, for this project
**Audit date:** 2026-10-29, on HgX's word: "go through everything from the beginning of the day… make sure it will fit on my laptop and everything will work on my laptop."
**Verdict: GOOD TO GO — no showstopper found in today's set, subject to the pre-wipe gates already in tonight's checklist (plus one disk check, below).**

## Scope — what was audited, and what was deliberately left out
**In scope (today's project):** Acer Kali build (3 pillars + 10 stacks + voice layer + Jarvis-feel + Cloud takeover rebuild + son enrollment + Shortcuts) + Course Structure v1 (M0–M10, 11 hardware pieces) + Project 25 prove-out.
**Out of scope (dropped / parked today, NOT audited as laptop work):** dual-boot (dropped), portable/temp stick (dropped), Windows disk image / big external drive (dropped), old Kali laptop walkthrough (closed — Acer is the main build), Mac mini buy (separate Thread Two, end of October after Tvisha's birthday), Tesla car node (parked).

## Acer baseline (DXDIAG-verified 2026-10-26, file ~/workspace/user/files/DxDiag.txt)
- Acer Nitro AN515-55, Windows 11 Home 64-bit, Intel i7-10750H (12 CPUs @ 2.6 GHz), 65,536 MB RAM (64 GB), NVIDIA RTX 2060 (5,955 MB dedicated, ~6 GB) + Intel UHD Graphics.
- **Internal disk: Drive C: 487.0 GB total, 365.1 GB free at DXDIAG time.** This is the Kali install target after wipe — full 487 GB becomes available.
- **Drive M: Seagate Expansion, 3,815.3 GB total — EXTERNAL, do NOT wipe, do NOT select in the installer.** Installer disk selection must be the internal disk only.
- MaonoCaster AU-AM200 enumerated, Logi C270 webcam mic present, all DXDIAG tabs "No problems found."

## Disk fit — the math
- Kali everything installed set: ~34–36 GB (approximate, secondary sources — installer + metapackages, not a vendor guarantee).
- Kali system + tools + Node/Python/Docker/Java: ~10 GB allowance.
- Ollama qwen3:8b: 5.2 GB. Whisper small.en: ~0.5 GB. VoiceStudio / ComfyUI: app small; MODELS are the variable — do NOT download every model. Course models only, quantized/small for 6 GB VRAM, cap at ~20–30 GB.
- Course evidence, logs, reports: a few GB.
- **Total planned: well under 100 GB against 487 GB internal. Headroom: ~380+ GB after wipe.** Fit is not tight. The only way to break fit is downloading every diffusion / voice model blindly — don't.
- **Pre-wipe disk check (1 minute, add to tonight list):** in Windows, This PC → confirm C: still ~487 GB total and healthy. Free-space drift since Oct 26 does not change the verdict — total is what matters after wipe.

## Item-by-item verdicts
**GO — fits and works on Acer/Kali x64:**
- Kali everything (Debian-based, OffSec, rolling, 600+ tools, x86_64) — after BIOS steps (Secure Boot off, Fast Boot off, SATA → AHCI, Rufus GPT/DD, nouveau.modeset=0 if black screen, then NVIDIA drivers).
- REA everything — Node 22/24/26 + npm + procps `ps` on Kali; official morluto/rea, rea.tools, npm rea-agents only. Exact tool count unverified until `rea doctor --json` on the box — that command is authoritative, not today's count.
- Grokbot — Linux x64 supported (docs.x.ai, updated 2026-10-28); dashboard / x.ai/bot; cloud computer unaffected by Acer wipe.
- Graphify local CLI — Python 3.10+ + uv, local tree-sitter parsing, no LLM, no cloud.
- HyperFrames — Node 22+ + FFmpeg + headless Chrome, local CLI only.
- ComfyUI — manual Linux install (desktop app is Windows/macOS only); 4 GB VRAM floor, RTX 2060 6 GB clears it; big models slow, use quantized/smaller models; fully offline, partner/cloud off.
- FreeLLMAPI — Node 20+ / Docker on Kali; local-only mode = router → local Ollama; cloud free providers off by default.
- ai-memory — Rust, Linux supported, zero LLM by default, local server.
- VoiceStudio (#9) — Linux x64 .deb primary, NVIDIA CUDA + CPU fallback; models download only on app ask; cloning only with permission.
- GenOffice (#10) — Linux .deb, files/conversions local, AI backend = local Ollama; Genspark sign-in excluded; TypeSafe Jev rerank off by default.
- Kali voice layer — PipeWire (Kali default mixer, VoiceMeeter does NOT carry over), Pulsemeeter/qpwgraph + null sinks, openWakeWord custom "hey local jarvis", SpeechBrain ECAPA (fresh enrollment on Kali), faster-whisper small.en, Ollama qwen3:8b, Linux orchestrator (VLC/files, no delete, actions.log), Piper fallback / VoiceStudio primary.
- Jarvis-feel layer — XFCE dark arc-blue HUD (original-inspired only, no Marvel assets), VoiceStudio primary voice (designed Jarvis manner, NOT a film-actor clone), voice-first, speak only when changed/needed.
- Cloud takeover rebuild — Tailscale Linux + OpenSSH server on Kali, fresh node + new key after wipe (Windows key/node wiped with Windows), stay-awake + lid-close-do-nothing + auto-start via systemd, full SSH (approved Q3), gated voice-loop auto-start (approved Q5), autonomy with never-delete / never-publish guardrails + morning summary (approved Q10–Q12).
- Shortcuts — iPhone + iPad + Apple Watch, un-parked Q22; URL updates to Kali path (new IP / Tailscale) after rebuild.
- Son enrollment — fresh on Kali, young-master rate-limited (1 full answer / 10 min), distress breaks limit, never commands.
- acersense — see Conditional below; otherwise AcerSense Pro Linux v2.1.0 claims AN515-55 support.
- Hardware (USB, Linux drivers in Kali): Flipper Zero + kit, T-Watch Meshtastic, HackRF One, Proxmark3 RDV4, Ubertooth One, ChipWhisperer-Lite, T-Beam, OpenMV Cam, GreatFET One — all GO.
- Course M0–M10 structure — GO as structure; hands-on for the 8 secretary pieces starts on arrival.
- Project 25 — GO: Tier 1 (21 family presence + safe self-test) after build; Tier 2 needs one lab VM target (second session); hardware families now in hand for Flipper/watch/glasses, 8 pending arrival.
- OBS / Discord / X on Kali — OBS native, Discord Linux client/web, X in browser, Grok via web. GO.

**CONDITIONAL — works, with a named condition (not a blocker):**
- security-audit-skill (#2) — needs a coding agent + Node validators + OS-enforced sandbox for target-controlled code; without sandbox, leads stay `needs_validation`.
- claude-plugins-official (#8) — NOT standalone; needs Claude Code first, and Claude Code's model is cloud by default unless routed to a local endpoint — do NOT call #8 fully local until routing is set.
- acersense — project claim "verified on AN515-55" is the project's claim, not proven on HgX's unit until post-install test (`acersense status` first, Auto first, brief Max burst with temp watch). Young repo (created 2026-09-02, 27 commits, 0 stars at check) — test, don't trust blindly.
- KrakenSDR — Linux PC qualifies as host, but needs 5-antenna array space + setup; direction-finding lab, not plug-and-play.
- Mentra glasses — screenless camera glasses, MentraOS open + SDK, Wi-Fi/Bluetooth, phone app primary. Laptop integration (BT/Wi-Fi/MiniApp via Acer) must be walk-tested on Kali — no native Linux client assumed.
- Acer internal Wi-Fi monitor mode (Project 25 wireless family) — if internal adapter cannot, record limitation + external adapter as fix. Does not block the rest of Project 25.
- NVIDIA drivers — RTX 2060 needs proprietary driver AFTER Kali install (apt, reboot, `nvidia-smi`); installer uses Intel-side display; black screen → `nouveau.modeset=0`.

**NOT on Kali (by design, not a failure):**
- VoiceMeeter Banana — Windows-only. Replaced by PipeWire on Linux. B1/B2 routing is re-built, not carried over.
- Windows Local Jarvis stack (orchestrator.py patched version, Downloads profiles.json, take*.wav, logs) — lost at wipe by design, fresh install on Kali. Accepted under the fresh-install decision.
- Steam / kernel anti-cheat games — Proton plays many, Valorant/Vanguard and Fortnite do NOT run on Linux. Out of course scope; check his games on ProtonDB separately if he wants them.

## Pre-wipe gates (tonight checklist, unchanged, plus disk check)
Sticks (32 GB Windows via Media Creation Tool + 64 GB Kali ISO from kali.org, SHA256 verified, Rufus) → Activation check (digital license, Home) → Device Manager photos → BIOS peek only → disk check (C: ~487 GB) → make BOTH sticks BEFORE any BIOS change → Live USB gate (Wi-Fi, cable, sound out + Maono in, webcam, all screens, mouse/keyboard, Bluetooth, installer sees INTERNAL disk, clean shutdown, suspend/wake) → BIOS changes (Secure Boot off, Fast Boot off, SATA → AHCI, VMD off if present) → wipe + install Kali once → update → NVIDIA drivers → Kali everything → REA + providers → Grokbot → PipeWire/voice stages → 10 local + Claude Code → VoiceStudio → GenOffice → Jarvis-feel → Cloud takeover rebuild → son enrollment + calibration → Shortcuts update → acersense test → Project 25 prove-out.
**Ordering rule locked:** sticks + license + inventory FIRST while Windows boots, BIOS changes SECOND. Installer disk = internal only, never the external Seagate M:.

## Honest limits of this audit
- Kali metapackage sizes and REA tool count are approximate / unverified until measured on the box (`rea doctor --json`, `df -h` after install).
- Hardware arrival for the 8 is "secretary sent to buy" — not delivered, not in hand. Course structure is ready; those 8 hands-on labs wait for arrival.
- AMENDMENT 2026-10-29 15:56 ET: the 8 are now ordered AND already here (via secretary). Arrival confirmed; unpack/test/inventory still pending. Hands-on labs for the 8 no longer wait for delivery — they wait for the home one-by-one start.
- No purchase was made by the lab in this audit. No file was sent to Dropbox/GitHub/website as part of this audit — this file lives in the lab goal workspace only.


---

@basementjarvisu · basementjarvisunleashed@gmail.com
