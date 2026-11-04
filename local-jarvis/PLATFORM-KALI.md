# Local Jarvis — Platform Record: Kali Linux + REA

**Platform as of 2026-11-04. 1.0 only. Built and verified.**

Public identity: J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System) first and prominent. Operator: HgX. Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

## Hardware — built

- Laptop: Acer Nitro AN515-55
- CPU: i7-10750H
- RAM: 64GB
- GPU: RTX 2060, about 6GB VRAM
- Storage: 512GB NVMe internal drive

## Platform — built

- **Kali Linux, everything installed on the internal drive.** All tools updated, graphics driver installed, Bluetooth working, Wi-Fi working, login working.
- **Windows is no longer on the internal drive.** The Windows licence is motherboard-tied; a later reinstall via ISO is possible with no product key needed. This is a general licence note only; no product key or account detail is recorded here.
- The prior Windows build files in this folder are retained for reference only. The live platform is Kali Linux.

## REA — built and ready

- **REA: `rea-agents@6.7.0`**, installed via `npx rea-agents setup`.
- REA reverse-engineering skill installed for CLI use.
- CLI: `npx rea-agents analyze /path/to/app`
- Status: REA is ready for local app analysis.
- Deep analysis: Ghidra, guided reverse-engineering workflows installed.

## Voice stack — built

- Mic → Whisper small.en → voice gate → orchestrator on port 8080 → Ollama `qwen3:8b` → tools / VLC / REA → Piper TTS.
- The orchestrator listens only after you start it. The voice loop is deliberately not auto-started.
- Router v2.2, 50 second voice budget, 60 second client wait, freellmapi as fallback only.

## Planned, not yet built

The following are planned only. None are claimed as installed until confirmed built:

1. Ollama check.
2. A 4B abliterated local model resident on VRAM as the fast low-end brain.
3. A 27B abliterated local model on RAM as the slow high-end brain.
4. Switching logic in the orchestrator layers and usage router: default VRAM fast, escalate to RAM high for hard tasks, de-escalate back.
5. The remaining software stacks in efficient order.
6. Kali tools mapping into REA.
7. Project 25 prove-out.

No middle 8B test.

## Notes

- Passwords and user accounts in this tree are placeholders only (`CHANGE_ME`, `<user>`). Do not commit real values.
- No real names, home addresses, public IPs, Wi-Fi details, tokens, usernames, or voice recordings belong here. Refer to the operator as HgX.

---

@basementjarvisu · basementjarvisunleashed@gmail.com
