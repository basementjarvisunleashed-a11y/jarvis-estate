# Raspberry Pi 500+ — Software Stack (Kali Linux, primary)

**Layout (HgX, 2026-11-05 ~15:47 ET): Kali Linux runs EVERYTHING, all the time, from the 2TB Samsung 990 PRO (replacing the 256GB). Raspberry Pi OS stays on the 64GB microSD card as backup/rescue only. Boot order: NVMe first, SD as fallback.**

Hardware: 2.4GHz quad-core Cortex-A76 ARM64, 16GB RAM, 2TB NVMe (speed capped by the single PCIe lane: ~500MB/s Gen2, ~900MB/s Gen3), dual micro-HDMI (dual 4Kp60), 40-pin GPIO (flat, horizontal).

## 1. The base — Kali Linux ARM64
- **Kali Linux ARM64** (kali-linux-arm64) — full `kali-linux-large` metapackage fits easily on 2TB
- **XFCE desktop** (Kali default — light, fast on this chip; GNOME available but heavier)
- **apt + Debian ARM64 repos** — thousands of packages, all native ARM64
- **Docker (ARM64)** — isolated tool containers, reproducible lab environments
- **git, GitHub CLI** — the repo workflow, same as the Acer
- **VS Code (ARM64 build)** — the editor; **Node.js, Python 3, Go, Rust toolchains** — all ARM64 native

## 2. The REA core — reverse engineering
- **Ghidra** (Java, ARM64) — the disassembler/decompiler; 16GB RAM holds whole firmware images
- **radare2 / Rizin** (ARM64) — the fast binary analysis pair
- **REA agents (rea-agents)** — the same reverse-engineering agents as on the Acer; Node-based, runs on ARM
- **GDB multiarch (gdb-multiarch)** — debug ARM binaries on the device, and others via QEMU
- **QEMU (qemu-user, qemu-system-arm)** — run and emulate ARM/MIPS firmware images without the hardware
- **Binwalk, firmwalker** — firmware extraction and analysis
- **binutils (strings, readelf, objdump), checksec, pwntools** — the daily binary toolkit
- **Frida (ARM64)** — dynamic instrumentation: hook and watch apps running on real devices
- **angr (Python, ARM64)** — symbolic execution for the hard binaries (slower than on the Acer, but works)

## 3. The network + attack stack
- **nmap, masscan** — map the home network, find every device and open port
- **Wireshark / tshark, tcpdump** — watch what the locks, cameras and TV actually say on the wire
- **Metasploit Framework** (Ruby, ARM64) — works; slower to start than on the Acer, fully usable
- **Burp Suite Community** (Java, ARM64) — web proxy for testing device web interfaces
- **sqlmap, nikto, gobuster, ffuf** — web testing; Go binaries ship ARM64
- **Hydra, John the Ripper** — CPU password testing
- **hashcat — CPU ONLY** — no GPU compute on the Pi (VideoCore VII has no usable OpenCL for hashcat); heavy cracking stays on the Acer's RTX 2060
- **Aircrack-ng suite** — WiFi testing; onboard WiFi monitor mode is fiddly (nexmon patches) — a USB Alfa adapter is the reliable route (not in the current order)
- **sqlmap, netcat, socat, curl** — the plumbing

## 4. The Jarvis layer — the machine's jobs
- **Jarvis dashboard** (his own software, Node/Python web app) — served from the 500+, shown on the 7" LCD and/or dual 4K screens
- **NFS server (nfs-kernel-server) + TFTP/DHCP** — serves the Apple TV 3's Kali rootfs over Ethernet and netboots targets
- **Pi-hole + Unbound** — house-wide DNS ad-blocking, every device in the house
- **Home Assistant (ARM64, Docker)** — the smart-home takeover hub: locks, Samsung TV, Lorex cameras (ONVIF)
- **Jellyfin (ARM64)** — media server / media centre
- **Kodi** — the TV interface when it is a media box
- **RetroPie / RetroArch** — retro gaming when the work is done
- **Ollama (ARM64)** — SMALL Qwen models only, CPU-only (no GPU compute on the Pi). Verified 2026-11-05 against Pi 5 benchmarks (same chip): **Qwen2.5-3B ~5 tok/s** (~2GB weights, best quality that fits), **Qwen2.5-1.5B ~8 tok/s** (the fast one), **Qwen3-0.6B** (tiniest, fastest). **7B is below 1 tok/s — skip it; the Acer does the big ones.** Abliterated (uncensored) picks: `richardyoung/qwen2.5-3b-instruct-abliterated` (Ollama, Q4_K_M ~1.9GB, daily driver), `huihui-ai/Qwen2.5-1.5B-Instruct-abliterated` (GGUF, fast), `huihui-ai/Qwen2.5-Coder-1.5B-Instruct-abliterated` (code helper). llama.cpp is 10–20% faster than Ollama on this chip. Keep context small (2K–4K). Role (HgX, 2026-11-05 ~15:53 ET): NOT a chat companion, NOT for long reasoning, NOT for big code — it is **REA's engine**. REA agents call it via Ollama's OpenAI-compatible API (localhost:11434) for short, sharp jobs: naming functions, reading disassembly, summarising firmware behaviour, drafting Ghidra scripts, tool-calling the next step. The 3B abliterated is the pick because it is the smallest that reliably calls tools and follows instructions, and uncensored matters — a censored model would refuse to look at the firmware being taken apart. 1.5B is the fast spare. Hard reasoning / big code goes back to the Acer's big models.

## 5. The hardware-interfacing stack — the GPIO and the bench tools
- **flashrom** (with Bus Pirate support) — read/write flash chips straight off the board
- **OpenOCD** — JTAG/SWD debugging via the Debug Probe / Pico
- **avrdude, Arduino CLI, picotool** — flash the Arduino Uno and the Pico dongles
- **minicom / screen / picocom** — serial consoles over the Waveshare USB-to-serial converter
- **sigrok / PulseView** — logic analysis with the Logic Sniffer (and the Bus Pirate as an analyzer)
- **i2c-tools, RPi.GPIO / gpiozero / pigpio** — drive the 40-pin header from Python: UART consoles, I2C sensors, SPI flash, PWM motors
- **esptool** — flash ESP32 boards (smart-home devices, sensors)

## 6. What does NOT run here (honest limits)
- **IDA Pro** — x86 only, does not run on ARM Linux
- **hashcat GPU cracking** — no CUDA/OpenCL compute; CPU-only, slow
- **Big local LLMs** — CPU-only, slow; small models only
- **x86-only tools** — box86/box64 can run some, with a performance penalty; not a promise
- **Windows tools** — no (QEMU x86 emulation exists and is very slow)

## 7. The services running all the time
Kali on the 2TB drive, always on: Jarvis dashboard + NFS/TFTP for the ATV3 campaign, Pi-hole DNS for the house, Home Assistant for the locks/TV/Lorex, Jellyfin media, SSH over Ethernet. Pi OS on the 64GB card is the rescue system only — it boots only if the NVMe ever fails.
