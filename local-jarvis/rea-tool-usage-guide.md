# REA Tool Usage Guide — for REA, the 9B, the 27B, and the Router

**Who this is for:** REA (the reverse-engineering agent on HgX's Acer Kali laptop), the 9B model (`qwen9b-abliterated`, fast, on GPU), the 27B model (`huihui_ai/Qwen3.8-abliterated:27b`, slow, on CPU RAM), and the little router (127.0.0.1:11435). Read this before starting any REA job. It is the operating manual for the 15 tools installed 2026-11-07 — every version, path, and quirk below is verified on this machine.

**Cross-use with BLA:** see `rea-bla-integration.md` — BLA shields what REA takes apart. On any project that needs a build, a shield, and a test of the shield, use both (build → shield → test).

**First rule of every job:** check the tool exists before you use it.

```bash
which <tool>
```

If the command is missing or the version is wrong, stop and report it. Do not guess a path, do not download a replacement unprompted, and do not install anything without HgX's word.

**A note on the brains (read this first):** both models are currently **UNLOADED** (HgX ordered them unloaded 2026-11-07 ~18:42 ET). The keep-alive cron reloads them at midnight, and `ollama serve` is running so they reload on demand. Do not assume either model is resident. Before a job, confirm with `ollama ps` plus `free -h` and `nvidia-smi` (a stale `ollama ps` listing is not proof — 0 processes is the truth), and load the model you need through the router / GPU orchestrator if it is not resident. Do **not** change the pinning: the 9B stays resident on VRAM, the 27B stays resident in system RAM (24 h pins, refreshed every 6 h). HgX likes the 27B resident.

---

## 1. IDENTIFY IT — start every unknown binary here

### 1. Detect-It-Easy (DIE) 4.0.0 — `/usr/bin/die`, `/usr/bin/diec`
**What:** identifies file type, packer, compiler, and linker. **When:** the very first thing you run on any unknown binary. **How:**

```bash
diec <file>            # console output — use this in scripts and agent loops
die <file>             # GUI
```

**Notes:** the apt `detect-it-easy` 3.21 was removed to install 4.0.0 (it owned `/usr/bin/die` and conflicted). Removing it also removed the `kali-linux-everything` metapackage — that is harmless (a metapackage has no files; the tools stay). **Never reinstall `kali-linux-everything`** — it would pull detect-it-easy 3.21 back and conflict with 4.0.0. Never use `--force-overwrite` for this class of dpkg file conflict; remove the old package instead.

### 2. capa 10.0.0 — `~/.local/bin/capa` (binary at `~/opt/capa/capa`)
**What:** Mandiant FLARE capa — detects capabilities in a binary (persistence, injection, crypto, networking, anti-analysis) by matching rules. **When:** right after DIE, to learn what the binary *can* do before you read its code. **How:**

```bash
capa <file>
capa -q <file>         # quiet — capabilities only, less rule detail
capa -j <file>         # JSON output, for parsing in a script
```

**Notes:** Kali does **not** package capa — this is the standalone binary (capa-v10.0.0-linux.zip). `capa --version` prints `capa 10.0.0`.

### 3. ImHex 1.38.1 — `/usr/bin/imhex` (apt) and `~/opt/imhex/imhex.AppImage`
**What:** hex editor with a pattern language, disassembler, and data inspector. **When:** you need to look at raw bytes, patch bytes, or run an ImHex pattern against a file. **How:**

```bash
imhex <file>           # GUI
```

**Notes:** both copies are 1.38.1. The AppImage is symlinked to `~/.local/bin/imhex`, and `~/.local/bin` comes first in PATH, so **the AppImage is what actually runs** — not the apt binary, even though the apt one was kept as the "default". Both are 1.38.1, so there is no functional difference. The AppImage (181 MB) is the backup as well as the live one; do not delete either without HgX's word. Do not put `imhex --version` in a paste — it is a GUI app and may open a window.

### 4. LIEF 0.16.2 — Python library (apt `python3-lief` 0.16.2-0kali3)
**What:** parses and modifies ELF, PE, and Mach-O binaries (headers, sections, symbols, imports, exports). **When:** a script needs to read or patch binary structure programmatically instead of by hand in a hex editor. **How:**

```bash
python3 -c "import lief; b = lief.parse('file'); print(b.header); print([s.name for s in b.sections])"
```

```python
import lief
b = lief.parse("file")
print(b.header.machine_type)          # architecture
print([s.name for s in b.sections])   # sections
print([s.name for s in b.symbols])    # symbols (ELF)
print([i.name for i in b.imported_functions])  # imports (PE)
```

**Notes:** `python3 -c "import lief; print(lief.__version__)"` prints `0.16.1-` — the module's internal version string differs slightly from the package version 0.16.2. That is not a problem; it imports and works. PyPI 1.0.0 was **not** used (Kali's PEP 668 externally-managed block); the apt package is the route.

---

## 2. READ THE LOGIC — understand what the code does

### 5. Ghidra 12.2 — `/usr/share/ghidra` (apt 12.1.4) and `~/opt/ghidra/ghidra_12.2_PUBLIC/` (upstream 12.2)
**What:** decompiler / disassembler — turns a binary into readable C-like pseudocode. **When:** you need to read a binary's logic, not just its capabilities. **How:**

```bash
ghidra                              # GUI, project-based (this runs the apt 12.1.4)
~/opt/ghidra/ghidra_12.2_PUBLIC/ghidraRun   # GUI, upstream 12.2 — prefer this for new work
```

Headless (no GUI — use this in scripts and agent loops):

```bash
/usr/share/ghidra/support/analyzeHeadless /tmp/ghidra-proj MyProj \
  -import /path/to/binary -postScript "Decompile" -scriptPath /path/to/scripts
```

**Notes:** there are **two** Ghidras. The apt 12.1.4 is what the bare `ghidra` command runs; the upstream 12.2 lives at `~/opt/ghidra/ghidra_12.2_PUBLIC/` (the 544 MB zip is still in `~/Downloads/`). **Prefer 12.2 for new work.** Keep 12.1.4 — GhidraMCP is built for 12.1.4 specifically (see §6). Making 12.2 the default `ghidra` would need the apt package removed; that decision has **not** been made — do not do it unprompted.

### 6. GhidraMCP 2.0 — plugin + `ghidra-mcp` at `~/.local/bin/ghidra-mcp`
**What:** lets an AI agent query a running Ghidra over MCP/HTTP — list functions, decompile a function, rename symbols, get cross-references. This is the bridge between the models and Ghidra. **When:** a model needs Ghidra's analysis inside an agent loop instead of a human driving the GUI. **How:**

```bash
ghidra-mcp --ghidra-server http://127.0.0.1:8081/
ghidra-mcp --help                   # flags: --ghidra-server, --transport, --headless, --binary, --project
```

**Port — read carefully:** GhidraMCP listens on **port 8081, NOT 8080**. Port 8080 is held by the Bracelet PoC Orchestrator. **Do not stop the bracelet orchestrator.** The port is set inside Ghidra's GUI: **Edit > Tool Options > GhidraMCP HTTP Server**. The plugin must be enabled first: **File > Configure > Developer**, tick **GhidraMCPPlugin**, then restart Ghidra.

**✅ VERIFIED LIVE 2026-11-11:** 127.0.0.1:8081 answers — `ss` shows Java listening, and `curl` returns the JSON `UNKNOWN_ENDPOINT` error for `/`, which is expected (no root endpoint). The plugin is enabled, Server Port 8081 is saved, and the bridge runs while CodeBrowser is open with a program loaded. Check with:

```bash
ss -tlnp | grep 8081
curl -s http://127.0.0.1:8081/
```

**Notes:** the plugin is installed via File → Install Extensions into the apt Ghidra DEV settings dir (`~/.config/ghidra/ghidra_12.1.4_DEV/`) and is built for **Ghidra 12.1.4 only** — install/use it with the **apt** Ghidra, not the 12.2 copy. CORRECTION 2026-11-11: the manual copy at `~/.ghidra/.ghidra_12.1.4_PUBLIC/Extensions/GhidraMCP` is a DEAD DUPLICATE in the wrong dir. The MCP server was installed with `uv tool install` from the local wheel (33 packages: ghidra-mcp 2.0.0, mcp 1.30.0, pydantic, httpx, uvicorn, starlette, …).

### 7. angr 10.0.5 — Python library in a uv venv at `~/opt/angr-venv` (Python 3.13.18)
**What:** symbolic execution and binary analysis — find reachable paths, solve for inputs that reach a target, analyse control flow symbolically. **When:** a question cannot be answered by reading the decompilation alone ("what input reaches this branch?", "is this path reachable?"). **How:**

```bash
~/opt/angr-venv/bin/python -c "import angr; print(angr.__version__)"   # prints 10.0.5
```

```python
import angr
p = angr.Project("file", auto_load_libs=False)
state = p.factory.entry_state()
sim = p.factory.simgr(state)
sim.explore(find=0x401234)     # address you want to reach
print(sim.found[0].posix.dumps(0))  # the input that gets there
```

**Notes:** angr is a **library, not a CLI** — always invoke it through the venv's Python (`~/opt/angr-venv/bin/python`). The system Python does not have it. **Unicorn support is DISABLED** (`unicornlib.so` failed to load, so concrete execution via Unicorn is off). Core angr works without it. Do not chase the Unicorn fix unless a job actually needs concrete execution.

---

## 3. WATCH IT RUN — see what the app actually does

### 8. Frida 17.26.2 (core) + frida-tools 14.13.0 — 17 executables in `~/.local/bin`
**What:** dynamic instrumentation — hook functions, trace calls, inspect memory while an app runs. **When:** you need to see what a running app *actually* does (which APIs it calls, what crypto it uses, what it sends). **How:**

```bash
frida-ps -U                    # list processes on a USB device
frida-ps                       # list processes on this machine
frida-trace -U -i "open*" <app>        # trace calls matching open* in an app
frida -U -f <app> -l script.js         # spawn an app with a hook script
frida-ls-devices               # show attached devices
```

A minimal hook script (`script.js`) — standard Frida usage, included here as a starting pattern:

```javascript
Interceptor.attach(Module.getExportByName(null, "open"), {
  onEnter: function (args) { console.log("open:", Memory.readUtf8String(args[0])); }
});
```

**Notes:** installed with `uv tool install frida-tools` (7 packages). Core 17.26.2 and tools 14.13.0 are **deliberately separate versions** — that is normal, not a mismatch. `frida --version` prints 17.26.2. The 17 executables include `frida`, `frida-ps`, `frida-trace`, `frida-apk`, `frida-compile`, `frida-create`, `frida-discover`, `frida-ls-devices`, `frida-kill`, `frida-ls`, `frida-pull`, `frida-push`, `frida-rm`, `frida-strace`, `frida-itrace`, `frida-join`, `frida-pm`.

### 9. objection 1.12.5 — `~/.local/bin/objection`
**What:** runtime mobile exploration, powered by Frida — inspect an app's files, bypass SSL pinning, dump keychains, explore memory and the heap. Works on iOS/Android **without jailbreak**. **When:** the target is a mobile app and you need to look inside it while it runs. **How:**

```bash
objection -g <package-name> explore
```

Inside the objection REPL (standard objection usage):

```
android sslpinning disable
android hooking list activities
android heap search instances java.lang.String
ios keychain dump
env
```

**Notes:** installed with `uv tool install objection` (31 packages; Frida 17.26.2 sits underneath). **`objection --version` is NOT a supported flag** — it prints "Checking for a newer version of objection..." then the Usage help. The 1.12.5 confirmation comes from the install package list, not from a version flag. Do not report objection as broken because `--version` prints help.

---

## 4. OPEN THE APP ITSELF — unpack the package format

### 10. jadx 1.5.6 — `/usr/bin/jadx` (apt 1.5.6-0kali1)
**What:** Dex-to-Java decompiler. Turns an Android APK's Dalvik bytecode back into readable Java. **When:** the target is any APK — jadx is the first tool you run on it. **How:**

```bash
jadx <app.apk>                  # GUI
jadx -d out <app.apk>           # CLI — decompile to the directory `out`
jadx --no-res -d out <app.apk>  # code only, skip resources (faster triage)
```

**Notes:** installed version **equals** the latest 1.5.6 — no upgrade was needed. `/usr/bin/jadx` is a 59-byte shell launcher script, not the binary itself. `jadx --version` prints 1.5.6.

### 11. Apktool 3.0.3 — `/usr/local/bin/apktool` + `/usr/local/bin/apktool.jar`
**What:** decodes an APK into its manifest, resources, and smali, and rebuilds a modified APK. **When:** you need the manifest, the resources, or the smali — or you need to change something and rebuild the APK. **How:**

```bash
apktool d <app.apk>             # decode into a directory named after the APK
apktool d -o out <app.apk>      # decode into `out`
apktool b <dir>                 # rebuild the APK from a decoded directory
apktool b -o rebuilt.apk <dir>  # rebuild to a named file
```

**Notes:** 3.0.3 lives in `/usr/local/bin` and **shadows** the apt 2.7.0-dirty in `/usr/bin/apktool`, which remains as a fallback. `/usr/local/bin` comes before `/usr/bin` in PATH, so 3.0.3 is what runs. **Lesson (learned the hard way):** after installing a tool that shadows an existing one, run `hash -r` before trusting `which` — a stale zsh hash reports the old location. The 3.0.3 install had worked all along; the hash was the only problem. The wrapper (`/usr/local/bin/apktool`, 2.6 KB) and the jar (`/usr/local/bin/apktool.jar`, 15 MB) were downloaded from the Apktool 3.0.3 release; `apktool --version` prints 3.0.3.

### 12. ILSpy / ilspycmd 11.2.0.10050 — `~/.dotnet/tools/ilspycmd`
**What:** .NET assembly decompiler — turns a `.dll` / `.exe` back into readable C#. **When:** the target is any .NET assembly. **How:**

```bash
TERM=dumb ilspycmd <assembly.dll>
TERM=dumb ilspycmd -p -o out <assembly.dll>   # decompile the whole project into `out`
TERM=dumb ilspycmd --help
```

**⚠️ TERM=dumb is mandatory.** `dotnet` on this machine **aborts** with `System.InvalidOperationException: The terminfo database is invalid` unless TERM is `dumb`. The terminfo database itself is fine (ncurses reads it); .NET's own reader cannot parse it. So **every** dotnet or ilspycmd command must be prefixed with `TERM=dumb`:

```bash
TERM=dumb dotnet --version          # prints 10.0.403
TERM=dumb dotnet --list-sdks        # 6.0.400 and 10.0.403
TERM=dumb ilspycmd --version        # ilspycmd: 11.2.0.10050, ICSharpCode.Decompiler: 11.2.0.10050
```

Do not "fix" this by editing the terminfo database or reinstalling ncurses — the database is not broken, and plain `TERM=xterm` does not fix it either. `TERM=dumb` is the fix.

**Notes:** ilspycmd is a dotnet global tool (installed with `dotnet tool install -g ilspycmd`). It targets **.NET 10.0** — that is why the .NET 10.0.403 SDK was installed at `/usr/share/dotnet` alongside the old 6.0.400 (the 6.0 SDK could not install it: "unsupported runner"). Both SDKs coexist; 10.0.403 is now the default. The "workloads" warning during install ("An issue was encountered verifying workloads") is **harmless** — mobile tooling ilspycmd does not need. Do not chase it.

### 13. asar 4.3.1 — `/usr/local/bin/asar` (npm global `@electron/asar`)
**What:** Electron archive tool — packs, lists, and extracts `.asar` archives. **When:** the target is any Electron app — asar is the first tool you run on it, to get at its JavaScript source. **How:**

```bash
asar list <app.asar>               # list the files inside
asar extract <app.asar> <dest>     # extract everything to <dest>
asar extract-file <app.asar> <file>   # extract one file (also: asar ef)
asar pack <dir> <out.asar>         # pack a directory into an archive (also: asar p)
asar --help
```

**Notes:** installed with `sudo npm install -g @electron/asar` (8 packages). It **needed sudo** — npm's global prefix `/usr/local/lib/node_modules` is root-owned, and a plain `npm install -g` fails with EACCES. Requires Node ≥ 22.12.0; this machine has Node v24.21.0 and npm 12.2.0. `asar --version` prints `v4.3.1`.

---

## 5. FOLLOW THE TRAFFIC — watch what leaves the machine

### 14. mitmproxy 12.3.1 — `~/.local/bin/mitmproxy`, `mitmdump`, `mitmweb` (binaries in `~/opt/mitmproxy/`)
**What:** interactive HTTPS proxy (man-in-the-middle) — intercept, inspect, and modify an app's HTTP(S) traffic. **When:** you need to see what an app sends over the network, or change it in flight. **How:**

```bash
mitmproxy                          # interactive TUI
mitmdump                           # non-interactive — use this in scripts
mitmdump -w traffic.flow           # capture to a flow file
mitmdump -r traffic.flow           # replay a flow file
mitmweb                            # web UI
mitmdump --version                 # Mitmproxy: 12.3.1 binary, Python 3.15.1, OpenSSL 4.0.3
```

To actually see HTTPS traffic, the mitmproxy CA certificate must be installed on the target (the app's device). Without it you see TLS handshakes, not plaintext. That step is per-target and is not covered here — flag it when it is needed, do not skip it silently.

**Notes:** these are **standalone binaries** (34 MB mitmdump, 35 MB mitmproxy, 35 MB mitmweb) in `~/opt/mitmproxy/`, symlinked into `~/.local/bin`, where they **shadow** the apt 12.2.3 in `/usr/bin` (which remains as a fallback). Kali's apt repo has 12.2.3 only — the standalone binary is the route for 12.3.1. The tarball (103 MB) is still in `~/Downloads/`.

### 15. Wireshark 4.6.9 — `/usr/bin/wireshark`, `/usr/bin/tshark`
**What:** packet capture and analysis — every protocol, not just HTTP. **When:** you need raw network capture, or you need to read a `.pcap` someone else made. **How:**

```bash
tshark -i <iface> -w capture.pcap        # capture on an interface
tshark -r capture.pcap                   # read a capture
tshark -r capture.pcap -Y "http"         # read it, showing only HTTP
tshark -r capture.pcap -T fields -e http.host -e http.request.uri   # pull out hosts + URIs
wireshark                                # GUI
```

**Notes:** installed 4.6.9 **equals** the latest stable 4.6.9 — no upgrade was needed. **Live capture needs permission:** run as root, or be in the `wireshark` group. If `tshark -i` fails with a permission error, that is the cause — do not "fix" it by changing the tool. `tshark --version` prints `TShark (Wireshark) 4.6.9.`

---

## 6. THE REA WORKFLOW — the order a job runs in

A typical job follows this order. Skip steps that do not apply to the target; never skip the identify step.

```
1. IDENTIFY        DIE, capa                     — what is it, what can it do?
2. READ THE LOGIC  Ghidra (or jadx / ilspycmd / asar for the target's own format)
                   angr when a path/input question needs solving
3. OPEN IT         Apktool (APK resources/smali) — only if the target needs it
4. WATCH IT RUN    Frida, objection               — what does it do live?
5. FOLLOW IT       mitmproxy, Wireshark           — what does it send?
6. PATCH / INSPECT ImHex, LIEF                    — whenever bytes or structure need
                                                    changing, at any stage
```

### Worked example 1 — an Android APK

```bash
# 1. Identify
diec app.apk
capa app.apk
# 2. Read the logic — decompile to Java first
jadx -d jadx-out app.apk
# 3. Open it — manifest, resources, smali
apktool d app.apk -o apktool-out
cat apktool-out/AndroidManifest.xml
# 4. Watch it run — hook the interesting calls (Frida), or explore live (objection)
frida -U -f com.example.app -l hook.js
objection -g com.example.app explore
# 5. Follow the traffic — what does it phone home to?
mitmdump -w app-traffic.flow
tshark -r capture.pcap -Y "http"
```

### Worked example 2 — a .NET assembly

```bash
# 1. Identify
diec app.dll
capa app.dll
# 2. Read the logic — decompile to C# (note TERM=dumb — mandatory for dotnet)
TERM=dumb ilspycmd -p -o csharp-out app.dll
# 3. If the assembly has native parts, decompile those in Ghidra
ghidra            # or: ~/opt/ghidra/ghidra_12.2_PUBLIC/ghidraRun (prefer 12.2)
# 4. Watch it run — hook the .NET methods at runtime
frida -U -f com.example.app -l hook.js
# 5. Follow the traffic
mitmdump -w app-traffic.flow
```

### Worked example 3 — an Electron app

```bash
asar list app.asar
asar extract app.asar extracted/
# now read the JavaScript in extracted/ — then Frida / mitmproxy as in the examples above
```

---

## 7. WHICH MODEL FOR WHICH JOB — and how the router picks

| Job | Model | Why |
|---|---|---|
| Triage an unknown file (DIE + capa output, short summaries) | **9B** | fast, on GPU, default |
| Quick reads, short tool-output summaries, single-command answers | **9B** | fast, on GPU, default |
| Deep decompilation analysis (a Ghidra/jadx/ilspycmd dump, long reasoning) | **27B** | slow, on CPU RAM, built for hard reasoning |
| Multi-step REA chains (identify → decompile → hook → intercept, with state across steps) | **27B** | slow, on CPU RAM, long chains |
| Anything where the prompt is long (over ~8,000 characters) | **27B** (automatic) | the router escalates on length |

**How the router decides (127.0.0.1:11435, `/v1/chat/completions`):** it routes by the **model name you pass** — `"easy"` goes to the 9B, `"hard"` / `"heavy"` / `"27b"` goes to the 27B — or by prompt length (over 8,000 characters goes to the 27B). **It does not judge content.** It does not route by the 27B's full model tag (that goes to the 9B). If you want the 27B, say so in the model name. If you want the 9B, say `"easy"`.

**Calling conventions (do not get these wrong):**

- **9B:** pass `"think": false`. The 9B thinks out loud otherwise, and the reasoning leaks into the answer. It runs on the GPU (6.1 GB, context 8192).
- **27B:** call with `num_gpu 0` — it runs on **CPU RAM only** (18 GB, context 4096). Never try to put it on the GPU; the 6 GB card cannot hold it alongside the 9B, and the 9B owns the GPU.
- **Never generate with both at once.** One model per call; the router picks one.
- **Load order, if you ever reload them:** 9B first, then 27B. Reloading the 9B after the 27B evicts the 27B (proven 2026-11-06). Use the GPU orchestrator (`127.0.0.1:11436`, `POST /ensure` with `{"purpose":"llm","holder":...,"reason":...}`) to hand the GPU back to the 9B after ComfyUI has used it.
- **If the GPU orchestrator reports an error** (e.g. "could not load the 9B"), do not believe it until you have checked `ollama ps`, `nvidia-smi`, and made an actual test call — the orchestrator has reported `ok:false` while the 9B was in fact loaded (its load call timed out but Ollama loaded the model anyway), and its stored mode can be stale.

**Cloud and free routes:** the cloud route (grok-4) is **not configured** (no key — checking the grok-bot config is parked, do not chase it). The free route (FreeLLMAPI) **failed** with an invalid API key and is parked. Local only: 9B and 27B through the router.

---

## 8. PRACTICAL RULES — the ones that cost time when ignored

1. **Check first:** `which <tool>` before using it. If it is missing, stop and report.
2. **`hash -r` after any install that shadows an old tool.** A stale zsh hash reports the old location (this bit Apktool 3.0.3 — the install had worked; the hash was the only problem). Open a new shell if in doubt.
3. **`TERM=dumb` for every dotnet / ilspycmd command.** Plain `dotnet` aborts on this machine.
4. **Never use `--force-overwrite` for a dpkg file conflict.** Remove the old package instead (this is how DIE 4.0.0 replaced 3.21).
5. **Never reinstall `kali-linux-everything`.** It would pull detect-it-easy 3.21 back over 4.0.0.
6. **Do not stop the Bracelet PoC Orchestrator on port 8080.** GhidraMCP lives on 8081 for exactly that reason.
7. **GhidraMCP is verified — 8081 answers as of 2026-11-11** (`ss -tlnp | grep 8081` shows Java listening; `curl http://127.0.0.1:8081/` returns the JSON `UNKNOWN_ENDPOINT` for `/`, which is expected). The bridge only runs while CodeBrowser is open with a program loaded + plugin enabled.
8. **Do not delete anything from HgX's drives or system without his explicit word per item.** That includes old installers in `~/Downloads`, the orphaned Craft Anything 0.3.0 files in `~/Applications/craft-anything/`, the orphaned Qt5 libs from the DIE removal, and the old models / unused GGUFs (deletion of those is **deferred** on his order — do not revive it).
9. **Do not change the brain pinning.** 9B on VRAM, 27B on CPU RAM, both 24 h. If a job is slow, that is the 27B on CPU — it is the price of the big model on this machine, not a fault to fix by moving it.
10. **The registry is the record.** `~/Jarvis/rea-toolset.md` (copied to `~/.agents/skills/reverse-engineer-anything/REA-TOOLSET.md`) lists all 15 tools with versions and locations. If this guide and the registry disagree, the registry wins — and report the disagreement.

---

## 9. QUICK REFERENCE — all 15 in one table

| # | Tool | Version | Where | First command |
|---|---|---|---|---|
| 1 | Detect-It-Easy | 4.0.0 | `/usr/bin/die`, `/usr/bin/diec` | `diec <file>` |
| 2 | capa | 10.0.0 | `~/.local/bin/capa` | `capa <file>` |
| 3 | ImHex | 1.38.1 | `/usr/bin/imhex` / `~/opt/imhex/imhex.AppImage` | `imhex <file>` |
| 4 | LIEF | 0.16.2 | Python library (apt `python3-lief`) | `python3 -c "import lief; b = lief.parse('file')"` |
| 5 | Ghidra | 12.2 (apt 12.1.4) | `/usr/share/ghidra` / `~/opt/ghidra/ghidra_12.2_PUBLIC/` | `ghidra` or `…/ghidra_12.2_PUBLIC/ghidraRun` |
| 6 | GhidraMCP | 2.0 | `~/.local/bin/ghidra-mcp` (plugin in Ghidra 12.1.4) | `ghidra-mcp --ghidra-server http://127.0.0.1:8081/` |
| 7 | angr | 10.0.5 | `~/opt/angr-venv/bin/python` | `~/opt/angr-venv/bin/python -c "import angr"` |
| 8 | Frida | 17.26.2 / tools 14.13.0 | `~/.local/bin/frida*` (17 executables) | `frida-ps -U` |
| 9 | objection | 1.12.5 | `~/.local/bin/objection` | `objection -g <package> explore` |
| 10 | jadx | 1.5.6 | `/usr/bin/jadx` | `jadx -d out <app.apk>` |
| 11 | Apktool | 3.0.3 | `/usr/local/bin/apktool` (+ `.jar`) | `apktool d <app.apk>` |
| 12 | ilspycmd | 11.2.0.10050 | `~/.dotnet/tools/ilspycmd` | `TERM=dumb ilspycmd <assembly.dll>` |
| 13 | asar | 4.3.1 | `/usr/local/bin/asar` | `asar list <app.asar>` |
| 14 | mitmproxy | 12.3.1 | `~/.local/bin/mitmproxy` (+ `mitmdump`, `mitmweb`) | `mitmdump -w traffic.flow` |
| 15 | Wireshark | 4.6.9 | `/usr/bin/wireshark`, `/usr/bin/tshark` | `tshark -i <iface> -w capture.pcap` |

*Written 2026-11-07, after all 15 tools were installed and version-verified on the Acer. If a version or path changes, update this guide and the registry together.*
