# REA Toolset — HgX's local reverse-engineering stack (Acer / Kali)
# Source: the 15 repos from @N01ennn's X post (2026-11-07), installed one at a time.
# Updated: 2026-11-07 — ALL FIVE groups are INSTALLED (15 of 15).
# This file is the record for Jarvis, REA, the big model (27B), the small model (9B),
# and the router — the local REA stack on the Acer. Not broadcast elsewhere.

## identify it (1-4) — INSTALLED
1. Detect-It-Easy (horsicq) — 4.0.0 — INSTALLED
   - /usr/bin/die, /usr/bin/diec (package detectiteasy 4.0.0)
   - Installed from the DIE-engine 4.0.0 .deb (die_4.0.0_kalilinux_amd64.deb, 28M, ~/Downloads/).
   - The apt detect-it-easy 3.21 was removed first (it owned /usr/bin/die and conflicted).
   - NOTE: removing detect-it-easy also removed the kali-linux-everything metapackage (2026.4.2).
     Harmless (a metapackage has no files; the tools stay). Do NOT reinstall
     kali-linux-everything — it would pull detect-it-easy 3.21 back and conflict with 4.0.0.
   - Orphaned Qt5 libs (autoremove only on HgX's word): libqt5concurrent5t64, libqt5scripttools5.
2. capa (mandiant) — 10.0.0 — INSTALLED
   - ~/opt/capa/capa, symlinked to ~/.local/bin/capa; capa --version -> "capa 10.0.0".
   - Standalone binary (capa-v10.0.0-linux.zip, 47.6M). Kali does NOT package capa.
3. ImHex (WerWolv) — 1.38.1 — INSTALLED
   - /usr/bin/imhex (apt imhex 1.38.1-0kali1 + imhex-patterns 1.38.1-0kali1) — this is what runs.
   - AppImage backup at ~/opt/imhex/imhex.AppImage (181M, 1.38.1) — kept as a backup, not the default.
   - The apt 1.38.1 equals the latest AppImage 1.38.1, so no upgrade was needed.
4. LIEF (lief-project) — 0.16.2 — INSTALLED
   - apt python3-lief 0.16.2-0kali3; python3 -c "import lief" -> "lief 0.16.1-" (the module's
     internal version string differs slightly from the package version — not a problem).
   - PyPI 1.0.0 was NOT used (Kali PEP 668 externally-managed block; would need a venv).

## read the logic (5-7) — INSTALLED
5. Ghidra (NationalSecurityAgency) — 12.2 — INSTALLED
   - TWO copies: apt 12.1.4 at /usr/share/ghidra (what ghidra runs) and upstream 12.2 at
     ~/opt/ghidra/ghidra_12.2_PUBLIC/ (launch via ~/opt/ghidra/ghidra_12.2_PUBLIC/ghidraRun).
   - 12.2 zip (ghidra_12.2_PUBLIC_20261016.zip, 544M) remains at ~/Downloads/.
   - To make 12.2 the default ghidra, the apt ghidra package would need removing — a separate
     decision, not made.
6. GhidraMCP (LaurieWired) — 2.0 — INSTALLED (port 8081, pending verification)
   - Plugin installed to ~/.ghidra/.ghidra_12.1.4_PUBLIC/Extensions/GhidraMCP (built for Ghidra 12.1.4 —
     install into the APT Ghidra, NOT the 12.2 copy).
   - MCP server: ghidra-mcp at ~/.local/bin/ghidra-mcp (uv tool install of the local .whl, 33 packages).
   - Port 8080 is held by the Bracelet PoC Orchestrator (HgX's choice: keep it running, move
     GhidraMCP to port 8081). The port is set in Ghidra's GUI (Edit > Tool Options > GhidraMCP
     HTTP Server). 8081 was EMPTY at the 19:18 ET check — the plugin enable (Configure > Developer,
     tick GhidraMCPPlugin) + port move + restart are UNCONFIRMED. Do NOT treat GhidraMCP as fully
     verified until 8081 answers. Then point the MCP server at http://127.0.0.1:8081/.
7. angr (angr) — 10.0.5 — INSTALLED
   - Python library (not a CLI). uv venv at ~/opt/angr-venv (Python 3.13.18); import angr -> 10.0.5.
   - 42 packages (angr, archinfo, cle, pyvex, capstone, z3-solver, etc.).
   - Unicorn support DISABLED (unicornlib.so failed to load) — optional; core angr works without it.
     Do not chase unless HgX needs concrete execution via Unicorn.

## watch it run (8-9) — INSTALLED
8. Frida (frida) — 17.26.2 — INSTALLED
   - uv tool install frida-tools (14.13.0) — 7 packages, 17 executables in ~/.local/bin
     (frida, frida-ps, frida-trace, frida-apk, frida-compile, etc.).
   - frida --version -> 17.26.2. Core 17.26.2, tools 14.13.0 (versions are deliberately separate).
9. objection (sensepost) — 1.12.5 — INSTALLED
   - uv tool install objection — 31 packages, ~/.local/bin/objection.
   - objection --version is NOT a supported flag (it prints the Usage help after a version check);
     the 1.12.5 confirmation rests on the install package list.

## open the app itself (10-13) — INSTALLED
10. jadx (skylot) — 1.5.6 — INSTALLED
    - /usr/bin/jadx (apt jadx 1.5.6-0kali1) — the installed version EQUALS the latest 1.5.6,
      no upgrade needed. /usr/bin/jadx is a 59-byte shell launcher.
11. Apktool (iBotPeaches) — 3.0.3 — INSTALLED
    - /usr/local/bin/apktool + /usr/local/bin/apktool.jar (shadows the apt 2.7.0-dirty in
      /usr/bin/apktool, which remains as a fallback). apktool --version -> 3.0.3.
    - LESSON: after installing a tool that shadows an existing one, run hash -r (or open a new
      shell) before trusting which / the version — a stale zsh hash reports the old location.
      (The 3.0.3 install had worked all along; the hash was the only problem.)
12. ILSpy (icsharpcode) — ilspycmd 11.2.0.10050 — INSTALLED
    - ~/.dotnet/tools/ilspycmd (dotnet global tool). ilspycmd --version ->
      "ilspycmd: 11.2.0.10050", "ICSharpCode.Decompiler: 11.2.0.10050".
    - .NET 10.0.403 SDK installed at /usr/share/dotnet (alongside 6.0.400) — ilspycmd 11.2 targets
      .NET 10.0, and the old 6.0 SDK could not install it ("unsupported runner").
    - dotnet on this machine needs TERM=dumb to run (the terminfo database is valid for ncurses
      but .NET's own reader cannot parse it — "The terminfo database is invalid").
    - The "workloads" warning during install ("An issue was encountered verifying workloads") is
      harmless (mobile tooling ilspycmd does not need) — do not chase it.
13. asar (electron) — 4.3.1 — INSTALLED
    - /usr/local/bin/asar (npm global @electron/asar). asar --version -> v4.3.1.
    - Node v24.21.0, npm 12.2.0 (meets the >= 22.12.0 requirement).
    - Installed with sudo — npm's global prefix /usr/local/lib/node_modules is root-owned
      (a plain npm install -g fails with EACCES).

## follow the traffic (14-15) — INSTALLED
14. mitmproxy (mitmproxy) — 12.3.1 — INSTALLED
    - ~/opt/mitmproxy/mitmproxy, mitmdump, mitmweb (standalone binaries, 34M/35M/35M),
      symlinked to ~/.local/bin — these shadow the apt 12.2.3 in /usr/bin, which remains
      as a fallback. mitmdump --version -> "Mitmproxy: 12.3.1 binary", Python 3.15.1, OpenSSL 4.0.3.
    - Standalone tarball (mitmproxy-12.3.1-linux-x86_64.tar.gz, 103M) at ~/Downloads/.
    - Kali's apt repo has 12.2.3 only, so apt will NOT get 12.3.1 — the standalone binary is the route.
15. Wireshark (wireshark) — 4.6.9 — INSTALLED
    - /usr/bin/wireshark, /usr/bin/tshark (apt wireshark 4.6.9-1, libwireshark 4.6.9-1+b1).
    - tshark --version -> "TShark (Wireshark) 4.6.9." The installed 4.6.9 EQUALS the latest
      stable 4.6.9 (wireshark.org), no upgrade needed.
