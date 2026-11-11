# REA ↔ BLA Integration — when to use each, and when to use both

REA and BLA are complementary, not alternatives. REA takes things apart; BLA puts a shield around them. On any project, use the right one at the right step — and use both when the project needs a build, a shield, and a test of the shield.

## REA — reverse-engineer-anything (take it apart)

Use REA when you need to understand how something works, find a flaw, extract logic, or analyse a binary, an app, or traffic. The 15 tools (registry: `REA-TOOLSET.md`, guide: `REA-TOOL-USAGE-GUIDE.md`):

- **Identify:** DIE/diec, capa, ImHex, LIEF
- **Read the logic:** Ghidra, GhidraMCP, angr
- **Watch it run:** Frida, objection
- **Open the app:** jadx, Apktool, ILSpy, asar
- **Follow the traffic:** mitmproxy, Wireshark/tshark

## BLA — blind-llm-agents (put a shield around it)

Use BLA when you need to protect an artifact (code, a challenge, a build) from LLM-based reverse-engineering.

- `bla harden [dir]` — expects a **directory** (not a file). Writes hardened copies to `.bla-hardened/`; originals untouched.
- `bla benchmark` — models REA-tool effectiveness against a hardened artifact (modelled estimates, not measured runs).
- BLA is self-contained: it does **not** run the 15 REA tools. Its shields account for tshark/Frida without invoking them.

## When to use BOTH (the integration)

1. **Build → shield → test.** Build or analyse with REA, harden with BLA, then test the shield with REA (red team). This is the proving loop.
2. **CrackMe / challenge.** BLA hardens the challenge; REA tools try to recover the secret. A solve is proven only by the FLAG SHA-256 — never claim a solve the evidence does not support.
3. **The overnight runner is the reference implementation.** It runs `bla harden` on a target, then a 27B REA-style analysis to test recovery. Follow that pattern for any shield test.
4. **Counter-REA.** When REA finds a weakness in your own artifact, harden it with BLA. When BLA hardens an artifact, verify the shield with REA.

## The rule

Never assume a shield holds — test it with REA. Never assume an analysis is complete — if the artifact is meant to be protected, harden it with BLA.

## Where the tools live

- REA skill: `~/.agents/skills/reverse-engineer-anything/` (registry `REA-TOOLSET.md`, guide `REA-TOOL-USAGE-GUIDE.md`). The registry is the REA source of truth.
- BLA: `~/opt/bla` (skill `~/opt/bla/.agents/skills/blind-llm-agents/`; binary `/usr/local/bin/bla`). `bla setup` registers BLA's MCP server + skill with the agents.
