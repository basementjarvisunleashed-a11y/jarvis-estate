# REA Windows 11 laptop build — 2026-11-13

Public-safe record of the REA (Reverse Engineer Anything) toolkit
install on the estate Windows 11 laptop, 13 November 2026,
America/Toronto.

This folder is documentation only. It does not install software, and it
does not replace [`PLATFORM-KALI.md`](../PLATFORM-KALI.md) or the Kali
tool record in [`rea-tools/`](../rea-tools/). Personal paths, hostnames,
addresses, accounts, and secrets are not included. Tool and model
locations on a machine that follows this build are under
`%USERPROFILE%\Tools` unless noted.

Operator: HgX. The install was requested and approved in REA's chat
that morning. Nothing was deleted. No secrets were written. No
services, scheduled tasks, firewall rules, or other persistence were
added.

## Reference machine

- Windows 11 Home 64-bit, build 26300
- Acer Nitro AN515-55: Intel Core i7-10750H (6 cores, 12 threads),
  64 GB RAM, NVIDIA GeForce RTX 2060 (6 GB) plus Intel UHD
- A standard (non-administrator) user account
- Internal system drive with hundreds of gigabytes free

A second data drive was present and was not used for this install.

## Principles

- New tools went under `%USERPROFILE%\Tools`, user-level or portable.
- One user-PATH entry was appended: `%USERPROFILE%\Tools\bin`, holding
  small `.cmd` shims. Existing PATH entries were not replaced.
- Environment variables were set for the user, not machine-wide.
- `rea setup` was not run. It can rewrite client registrations and
  offer to install Hopper. Only run it if you want those clients
  refreshed, and review the plan it prints before approving.
- REA 6.9.0 was already on the machine (installed by the operator at
  10:07 AM America/Toronto). This build did not install, upgrade,
  clone, or overwrite it. Only environment variables were added for it.

## Already present — skipped

| Software | Version / note |
|---|---|
| Node.js | v26.12.1 at `C:\Program Files\nodejs` (winget id `OpenJS.NodeJS`), npm 11.20.0 |
| REA (`rea-agents`) | 6.9.0, npm global. `rea --version` prints `6.9.0`. Commands live under `%USERPROFILE%\AppData\Roaming\npm\` (`rea.cmd`, `rea.ps1`, `rea-agents.cmd`). Package dir: `%USERPROFILE%\AppData\Roaming\npm\node_modules\rea-agents`. Not present in pip or pipx. |
| winget | v1.29.380 |
| GitHub Desktop | 3.6.10. Its bundled git was left unused; portable MinGit was added instead. |
| Python Install Manager | Microsoft Store version 26.4.240 (stubs only, no usable interpreter). No Python 3.11 install was on disk. The manager was not changed. |

There was no Scoop, no Chocolatey, no Cursor, no system Git, no JDK, no
.NET SDK, and no Ghidra or other reverse-engineering tools on PATH
before this install. Other apps already on the machine were left
untouched.

## Installed (user-level / portable)

| Tool | Version | Path |
|---|---|---|
| Eclipse Temurin JDK | 25.0.5+8 | `%USERPROFILE%\Tools\jdk-25.0.5+8` (portable zip; Ghidra 12.2 needs JDK 25, not 21) |
| Ghidra | 12.2 | `%USERPROFILE%\Tools\ghidra_12.2_PUBLIC`, `MAXMEM=16G` in `support\launch.properties` (UTF-8, no BOM) |
| radare2 | 6.2.6 | `%USERPROFILE%\Tools\radare2-6.2.6-w64` |
| Rizin | 0.9.1 | `%USERPROFILE%\Tools\rizin-win-installer-clang_cl-64` |
| Cutter | 2.5.0 | `%USERPROFILE%\Tools\Cutter-v2.5.0-Windows-x86_64` |
| JADX | 1.5.6 | `%USERPROFILE%\Tools\jadx` |
| ILSpy GUI | 11.2.0 self-contained | `%USERPROFILE%\Tools\ILSpy` |
| ilspycmd | 9.1.0.7988 | `%USERPROFILE%\Tools\dotnet-cli-home\.dotnet\tools\ilspycmd.exe` (latest 11.2 needs .NET 10; the CLI uses the portable .NET 8 runtime under `Tools\dotnet`) |
| .NET SDK 8 (portable) | 8.0.428 | `%USERPROFILE%\Tools\dotnet` |
| .NET SDK 9 (portable) | 9.0.321 | `%USERPROFILE%\Tools\dotnet9` |
| dnSpyEx | 6.6.0 | `%USERPROFILE%\Tools\dnSpyEx` |
| capa | 10.0.0 | `%USERPROFILE%\Tools\capa` |
| FLOSS | 3.2.0 (latest stable, not the v4 alpha) | `%USERPROFILE%\Tools\floss` |
| YARA | 4.6.0 | `%USERPROFILE%\Tools\yara` |
| wabt | 1.0.42, plus wasm-decompile 1.0.41 | `%USERPROFILE%\Tools\wabt-1.0.42` (the 12.2 Windows build of 1.0.42 omitted `wasm-decompile`; the official 1.0.41 binary was copied in) |
| Detect It Easy | 4.0.0 | `%USERPROFILE%\Tools\die` |
| MinGit | 2.56.1 | `%USERPROFILE%\Tools\MinGit` |
| CFR | 0.152 | `%USERPROFILE%\Tools\cfr\cfr-0.152.jar` |
| Procyon | 0.6.0 | `%USERPROFILE%\Tools\procyon\procyon-decompiler-0.6.0.jar` |
| apktool | 3.0.3 | `%USERPROFILE%\Tools\apktool\apktool_3.0.3.jar` |
| RetDec | 5.0 Windows | `%USERPROFILE%\Tools\retdec` (extracted; the exe currently fails, see below) |
| Python 3.12.10 | official installer, user-level | `%USERPROFILE%\Tools\Python312` (no Start Menu shortcuts, no file associations, PATH not rewritten by the installer) |
| RE venv | Python 3.12.10 | `%USERPROFILE%\Tools\re-venv` |
| 7zr | portable | `%USERPROFILE%\Tools\7zip\7zr.exe` |
| Ollama | 0.40.16, per-user | (installer not re-documented here; see the Ollama section) |

Python packages in `%USERPROFILE%\Tools\re-venv` (all pip-installed
successfully): pefile 2024.8.26, capstone 5.0.9, unicorn 2.1.4,
keystone-engine 0.9.2, lief 1.0.0, yara-python 4.5.4, frida-tools
14.13.1 / frida 17.26.3, angr 10.0.6, volatility3 2.28.2, decompyle3
3.9.3, uncompyle6 3.9.3, binwalk 2.1.0 (installs, but the import is
broken on Windows — see failures).

Official release SHA-256 hashes were verified for the main archives
(Ghidra, JDK, radare2, Rizin, Cutter, JADX, ILSpy, dnSpyEx, capa,
FLOSS, YARA, wabt, DIE, MinGit, apktool, and others listed in the
installer log). The hashes themselves are not republished here; use
each vendor's published digest.

## User environment

Set (not machine-wide):

```
JAVA_HOME=%USERPROFILE%\Tools\jdk-25.0.5+8
GHIDRA_INSTALL_DIR=%USERPROFILE%\Tools\ghidra_12.2_PUBLIC
REA_ANALYSIS_PROVIDER=ghidra
```

Open a new PowerShell window so these and `%USERPROFILE%\Tools\bin` are
picked up, along with the existing npm directory.

## Skills

All 30 skill files from the estate workflows library were copied to
`%USERPROFILE%\Jarvis\rea-skills\`. File count 30; SHA-256 of every
file matched the source. The skill files are not published in this
folder.

## Ollama

Ollama 0.40.16 was installed per-user. Two models were set up:

- GPU: `huihui_ai/qwen3-abliterated:4b-q8_0` — 100% GPU, about 41 tok/s
- RAM: `gemma3-27b-ram` (`gemma3:27b` Q4_K_M, `num_gpu 0`) — 100% CPU, about 1.9 tok/s

A small-model tool call to REA (`capabilities`) passed.

A 30 GB abliterated Gemma 27B was postponed by the operator to
2026-11-14 and was not installed.

## `rea doctor` (read-only; `rea setup` not run)

After the user environment variables were set, Ghidra is detected as
healthy:

- node: healthy, 26.12.1
- host: healthy, win32 x64
- ghidra: healthy, `%USERPROFILE%\Tools\ghidra_12.2_PUBLIC`
- ghidra-version: 12.2 (compatible 12.x >= 12.1)
- ghidra-headless: `support\analyzeHeadless.bat` healthy
- ghidra-java: Temurin JDK 25.0.5, 64-bit, `%USERPROFILE%\Tools\jdk-25.0.5+8`
- native decompiler and Windows native controls: healthy
- skill: version 62, 255 tools, aligned

`rea doctor` overall reports `healthy: false` only because these are
unset (none were installed or configured):

- Hopper — commercial; not installed
- IDA MCP registration — commercial; not installed
- JADX MCP — missing `REA_JADX_MCP_JAR` for a caller-supplied
  `jadx-headless-mcp` 0.7.1 JAR (JADX CLI/GUI 1.5.6 is installed; REA
  does not download the MCP JAR)
- Kuna — not configured (REA does not install Kuna)
- Copilot CLI registration — config drift at
  `%USERPROFILE%\.copilot\mcp-config.json`; would need `rea setup` if
  that client should be refreshed

## Smoke tests (verified with on-machine output)

CLI tools only. GUIs were not launched, so they would not pop up on the
desktop.

| Check | Result |
|---|---|
| java / javac 25.0.5 | pass |
| git 2.56.1 | pass |
| radare2 6.2.6 | pass |
| rizin 0.9.1 | pass |
| jadx 1.5.6 | pass |
| capa 10.0.0 | pass |
| floss 3.2.0 | pass |
| yara 4.6.0 | pass |
| wasm-objdump 1.0.42, wasm-decompile 1.0.41 | pass |
| cfr 0.152, apktool 3.0.3, procyon 0.6.0 (usage/help) | pass |
| python 3.12.10, vol 2.28.2, frida 17.26.3, decompyle3 3.9.3, uncompyle6 3.9.3 | pass |
| diec (Detect It Easy 4.0.0 CLI) | pass |
| dotnet 9.0.321 | pass |
| ilspycmd 9.1.0.7988 | pass (after pointing the shim at the .NET 8 runtime) |
| rea 6.9.0, node 26.12.1 | pass |
| Python imports: pefile, capstone, unicorn, keystone, lief, yara, frida, angr, volatility3, decompyle3, uncompyle6 | pass |

Ghidra `analyzeHeadless` on `C:\Windows\System32\notepad.exe`, project
under `%USERPROFILE%\Tools\scratch\ghidra-proj\notepad_test`:

- First run failed: a UTF-8 BOM from the `MAXMEM` edit broke
  `launch.properties`. That BOM was stripped; `MAXMEM` is still 16G.
- Second run: exit 0, about 3 minutes 12 seconds. Log lines: "Analysis
  succeeded", "Save succeeded", "Import succeeded" for notepad.exe.
  Analysis time 163 seconds. Project database written under
  `scratch\ghidra-proj`.

`rea doctor --provider ghidra` after the env vars: healthy. Ghidra
provider configured and available, version 12.2, JDK 25.0.5 accepted.

## Failed or incomplete

- **RetDec 5.0**: extracted to `%USERPROFILE%\Tools\retdec`, but
  `retdec-decompiler.exe --version` exits with Windows status
  `0xC0000135` (missing DLL). The `bin` folder has no bundled runtime
  DLLs. Likely needs the Visual C++ Redistributable (admin). Not forced.
- **binwalk 2.1.0**: pip installed, but `import binwalk` fails with
  `No module named 'binwalk.core'`. That old package is unreliable on
  Windows / Python 3.12.
- **pycdc**: no official prebuilt Windows binary in the zrax/pycdc
  releases; not installed.
- **Wireshark / tshark**: the winget package is a machine-scope MSI
  (Npcap needs admin). Not installed.
- **ilspycmd latest (11.2)**: needs .NET SDK 10. The ILSpy 11.2 GUI is
  installed; the CLI is the last version that runs on the portable
  .NET 8 runtime (9.1.0.7988).
- **wabt 1.0.42 Windows** did not ship `wasm-decompile.exe`; 1.0.41's
  official binary was copied in.

## In progress (requested, not claimed done)

These were asked for on 2026-11-13 and were still in progress at the
time of this record. They are not part of the verified install:

- OpenCode with an Ollama provider and REA as an MCP server
- A full REA toolset test on both Ollama models, with a report and
  full logs under `%USERPROFILE%\Documents\REA`
- Keeping both models loaded permanently (`OLLAMA_KEEP_ALIVE=-1`). No
  scheduled task was created; a preload script was planned only. That
  script is not in this folder.

## Not done / needs the operator

Paid or optional tools (do not buy or run setup unless you want them):

- Hopper Disassembler — commercial. `rea doctor` suggests `rea setup`
  or `HOPPER_LAUNCHER_PATH`.
- IDA — commercial. Would need `REA_IDA_MCP_CONFIG` if you already own it.
- Kuna — REA does not download it; set `REA_KUNA_COMMAND` if you have
  a kuna 1.990 executable.
- JADX MCP JAR — REA wants a caller-supplied `jadx-headless-mcp` 0.7.1
  JAR at `REA_JADX_MCP_JAR`. The JADX 1.5.6 CLI is already on the PATH.

Admin commands (not run on this install):

```
winget install --id Microsoft.VCRedist.2015+.x64 --accept-package-agreements --accept-source-agreements
```

```
winget install --id WiresharkFoundation.Wireshark --accept-package-agreements --accept-source-agreements
```

The first is the Visual C++ Redistributable (x64), if you want RetDec
to start. The second is Wireshark / tshark (Npcap driver, UAC).

## How to reproduce on a Windows 11 laptop

These steps match what was verified on the reference machine. They
assume a standard (non-administrator) Windows 11 account, winget, and
an official Node.js already on `PATH` if you want REA via npm. They do
not require this repository's other Local Jarvis services.

1. **Do not run `rea setup` unless you intend to rewrite client
   config.** If REA is not yet installed, install Node.js LTS or
   current from the official OpenJS distribution, then
   `npm install -g rea-agents@6.9.0`. Confirm with `rea --version`.
2. Create `%USERPROFILE%\Tools` and `%USERPROFILE%\Tools\bin`.
3. Add `%USERPROFILE%\Tools\bin` to the *user* PATH (append; do not
   replace existing entries).
4. Download each official release at the versions in the table above
   (Eclipse Temurin JDK 25.0.5+8, Ghidra 12.2, radare2 6.2.6, Rizin
   0.9.1, Cutter 2.5.0, JADX 1.5.6, ILSpy 11.2.0, dnSpyEx 6.6.0, capa
   10.0.0, FLOSS 3.2.0, YARA 4.6.0, wabt 1.0.42 plus wasm-decompile
   from official wabt 1.0.41, Detect It Easy 4.0.0, MinGit 2.56.1, CFR
   0.152, Procyon 0.6.0, apktool 3.0.3, RetDec 5.0 Windows, portable
   .NET SDK 8.0.428 and 9.0.321, portable 7zr). Verify each archive
   against the vendor's published SHA-256, then extract to the paths
   in the table.
5. Edit Ghidra's `support\launch.properties` and set `MAXMEM=16G`.
   Save as UTF-8 **without a BOM**. A UTF-8 BOM will break
   `analyzeHeadless`.
6. Install Python 3.12.10 with the official installer, user-level,
   prefix `%USERPROFILE%\Tools\Python312`. Do not add Start Menu
   shortcuts, file associations, or let the installer rewrite PATH.
7. Create the venv and install the packages listed above:

   ```
   %USERPROFILE%\Tools\Python312\python.exe -m venv %USERPROFILE%\Tools\re-venv
   %USERPROFILE%\Tools\re-venv\Scripts\python.exe -m pip install pefile==2024.8.26 capstone==5.0.9 unicorn==2.1.4 keystone-engine==0.9.2 lief==1.0.0 yara-python==4.5.4 frida-tools==14.13.1 frida==17.26.3 angr==10.0.6 volatility3==2.28.2 decompyle3==3.9.3 uncompyle6==3.9.3 binwalk==2.1.0
   ```

   Expect `import binwalk` to fail on Windows / Python 3.12.
8. Put small `.cmd` shims in `%USERPROFILE%\Tools\bin` so `java`,
   `analyzeHeadless`, `radare2`, `rizin`, `jadx`, `capa`, `floss`,
   `yara`, `wasm-objdump`, `wasm-decompile`, `cfr`, `apktool`,
   `procyon`, `diec`, `git`, `python`, `vol`, `frida`, `dotnet`,
   `ilspycmd`, and the other CLI tools resolve. Point the `ilspycmd`
   shim at the portable .NET 8 runtime; install ilspycmd 9.1.0.7988
   (not 11.2) unless you also have .NET 10.
9. Set the three user environment variables listed above.
10. Open a **new** PowerShell window. Run the smoke tests in the table,
    then:

    ```
    rea doctor --provider ghidra
    ```

    And a Ghidra headless smoke test:

    ```
    analyzeHeadless %USERPROFILE%\Tools\scratch\ghidra-proj notepad_test -import C:\Windows\System32\notepad.exe -deleteProject
    ```

    On the reference machine the kept project lived at
    `%USERPROFILE%\Tools\scratch\ghidra-proj\notepad_test` and was not
    deleted; `-deleteProject` is only a suggestion if you do not want
    to keep the test database. Expect about three minutes on similar
    hardware. If it fails immediately, check `launch.properties` for a
    BOM.
11. Optional, if you want the same local models: install Ollama 0.40.16
    per-user, pull `huihui_ai/qwen3-abliterated:4b-q8_0` for the GPU
    and set up `gemma3:27b` Q4_K_M with `num_gpu 0` as a RAM-only
    model (named `gemma3-27b-ram` on the reference machine). Confirm a
    small-model tool call to REA (`capabilities`) if you use REA with
    those models.
12. If you need RetDec or Wireshark, run the admin `winget` commands
    in the previous section yourself. They were not run here.
13. Copy any REA skill files you use to `%USERPROFILE%\Jarvis\rea-skills\`
    and check their hashes against your source. This folder does not
    ship those files.

Disk use for the toolkit itself is modest next to the optional 27B
models. The reference machine had hundreds of gigabytes free on the
system drive.

## What is not in this folder

- Installer archives, hashes, shims, skill files, models, or logs
- A preload script or scheduled task for Ollama
- OpenCode configuration
- The on-machine install report and Ollama report files
- Any material from private key or memory folders

No scripts or configs from the source reports were complete enough to
publish alongside this README.
