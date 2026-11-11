# Kali on iPad — the plan (HgX approved 2026-11-06 ~14:03 ET)

**STATUS 2026-11-07 ~00:10 ET — PARKED, downloads done, build NOT
started.** Parked on HgX's order 2026-11-06 22:02 ET. Downloads DONE on
the Acer (`~/Downloads/`): UTM.ipa v5.0.8 (150,556,413 bytes), Kali
**2026.3** ARM64 installer ISO (4,051,513,344 bytes, SHA256
`c4a7f9bf3a0ff07c8263fe9e9b0edba0cc3d9b408f1d8f06c066df0afce23072`,
matches the official 2026.3 SHA256SUMS), StikDebug v3.2.0 (16,818,331
bytes). Still to fetch: iloader (from https://sidestore.io/ in a
browser), LocalDevVPN v1.3.0 (App Store, on the iPad). **Use Kali
2026.3, not the 2025.4 named in Step 3 below** — the plan was written
before the download, and 2026.3 is what was fetched and verified.
iPhone/iPad dashboard playback is PARKED under the same order. The rest
of this plan stands as written.

**The iPad:** iPad Pro 11" 3rd gen (M1), model A2459, 1TB, 16GB RAM, iPadOS 26.6.2, 433 GB free.
**The verdict:** TrollStore is IMPOSSIBLE (26.6.2 >> 17.0 ceiling). Route = SideStore + UTM.ipa (JIT via StikDebug) + Kali ARM64.
**The goal:** pocket REA lab + Jarvis — Ghidra, rea-agents, little Qwen (3B) in the VM; Acer's 9B/27B brains over Tailscale.

## Step 0 — Home, internet on
- iPad off Airplane Mode, on home Wi-Fi.
- The Acer is the one-time setup computer (iloader runs on Linux).

## Step 1 — SideStore (one-time computer setup)
- On the Acer: download **iloader** (Windows/Mac/Linux desktop app). Plug the iPad in by USB-C, sign in with an Apple ID (a secondary one is recommended — the certificate is tied to it), pick the device, install **SideStore (Stable)** — current build **0.7.0-alpha** (Sep 15, 2026). Do NOT use 0.6.4 (sign-in broken).
- iloader places the **pairing file** on the iPad (needed again after a reset or a big iPadOS update).
- On the iPad: Settings > General > VPN & Device Management → Trust the profile under the Apple ID. Settings > Privacy & Security → turn on **Developer Mode** (iOS 16+), let it restart.
- From the App Store: install **LocalDevVPN** (v1.3.0). Open it, tap Connect, allow the VPN configuration.
- Open SideStore > My Apps, refresh SideStore itself.
- **Free Apple ID limits:** apps expire after **7 days** (refresh on-device via SideStore + LocalDevVPN), and the **3-app limit** applies — SideStore + UTM + StikDebug = exactly 3. A paid developer account ($99/yr) lifts both limits; LiveContainer is the free workaround for more apps (later, if wanted).
- **Known iPadOS 26.4+ quirk:** Apple changed how the local connection is validated. If VPN/signing errors appear, reinstall SideStore with iloader — that is the documented fix.

## Step 2 — UTM (v5.0.8)
- In SideStore: My Apps > + > pick **UTM.ipa** (143.58 MB, from UTM's official GitHub releases v5.0.8). SideStore signs and installs it.
- **JIT via StikDebug** (v3.2.0, works on iPadOS 17.4+ incl. 26): install StikDebug (from the AltStore source, or sideload its IPA via SideStore). Import the **same pairing file** iloader made. LocalDevVPN ON. Open StikDebug > Enable JIT > select UTM — UTM launches with JIT.
- JIT is per-launch: enable it each time UTM starts (StikDebug, or AltStore's long-press "Enable JIT" if using AltStore Classic).
- **Note:** UTM is on StikDebug's supported list for iPadOS 26.6. No hypervisor, no USB — JIT only. That is the ceiling on this iPad.

## Step 3 — Kali ARM64 in UTM
- **Get the ISO:** `kali-linux-2025.4-installer-arm64.iso` (~4 GB) from kali.org (Installer Images → Apple Silicon ARM64). Best fetched on the Acer, copied to the USB-C drive, plugged into the iPad — UTM reads the ISO from Files. (Or download directly on the iPad over Wi-Fi.)
- **New VM in UTM:** Emulate (TCG + JIT — no hypervisor on this build), architecture **ARM64 / aarch64**, machine `virt`, **4 CPU cores, 8 GB RAM** (iPadOS keeps the other 8 GB), **40 GB drive**, boot from the ISO.
- Install Kali (Xfce). When done, eject the ISO. Install the SPICE guest tools in Kali (`spice-vdagent`, `qemu-guest-agent`) for clipboard + shared folder + resolution.

## Step 4 — The stack inside Kali (same as the Pi 500+ rig)
- **Ollama ARM64** + `richardyoung/qwen2.5-3b-instruct-abliterated` (Q4_K_M, ~1.9 GB) — REA's engine. (7B is below 1 tok/s on this class of chip — skip. llama.cpp is 10–20% faster than Ollama if we want it later.)
- **REA:** `npm i -g rea-agents` (rea-agents@6.7.0) + **Ghidra** (Java, ARM64) + radare2/Rizin, gdb-multiarch, QEMU, Binwalk, Frida, angr.
- **Network tools:** nmap, Metasploit, Burp, Wireshark, sqlmap, gobuster, ffuf, Hydra, John.
- **Jarvis layer:** the dashboard server (Python stdlib, runs anywhere) + Tailscale on the iPad (iOS app — joins the tailnet) so the VM reaches the Acer's router over Tailscale (find the address with `tailscale ip -4` on the Acer) and the 9B/27B brains.

## Step 5 — First tests (at home, one at a time)
1. Kali boots, desktop up, internet works in the VM.
2. `nmap` a scan of the home network.
3. REA analyzes a binary (`rea analyze /bin/ls --provider ghidra`) and the little Qwen summarises it.
4. From the VM, reach the Acer's router over Tailscale (the 9B answers).
5. Voice loop: speaker test first (Piper in the VM), then the mic — UTM's own iOS docs confirm the iPad's built-in mic (or a headset mic) becomes the VM's microphone via SPICE audio, and UTM 5.0.8 fixed mic quality. Latency/quality for Whisper is the unproven part — test it, do not assume it.

## Honest limits (do not forget)
- **NO Wi-Fi monitor mode** — virtual NIC only; no USB passthrough for an Alfa adapter.
- **NO GPU cracking** — CPU-only hashcat.
- **NO USB devices in the VM.**
- **Battery** drains faster with an 8 GB VM running.
- **Do NOT give the VM more than 8 GB** — an iPad Pro has crashed with too much RAM in a VM; 8 GB for Kali, 8 GB for iPadOS.
- **No hypervisor** — JIT emulation, not native speed. Heavy builds will be slower.
- Free Apple ID: 7-day refresh + 3-app limit (see Step 1).

## Files / links
- UTM releases: https://github.com/utmapp/UTM/releases/tag/v5.0.8
- Kali: https://www.kali.org/get-kali/ (Installer Images → Apple Silicon ARM64)
- SideStore guide: https://libshortcut.com/blog/install-ipa-with-sidestore/
- StikDebug: https://stikdebug.org/ (JIT docs: https://github.com/sidestore/sidestore-docs/blob/HEAD/docs/advanced/jit.mdx)

## Top 10 — real things to do with the iPad Pro once Kali + Jarvis + Qwen run on it (HgX, 2026-11-06 ~14:56 ET)
1. **Map any network you sit on** — café, office, hotel, home. nmap the network in minutes: every device, every open port, every service.
2. **Tear apart firmware in the wild** — any firmware image (router, IoT gadget, the Apple TV IPSW) through Ghidra + REA + the little Qwen; it names the functions and explains the code. REA on the train, at work, anywhere.
3. **Command the whole estate from work** — Tailscale into the Acer, the Pi 500+, the dashboard. Check the brains, check REA jobs, check the dashboard — from your desk, on cellular.
4. **Audit your own house** — Burp and nmap against your own gear: the router, the cameras, the smart locks, the TV. Find the open doors in your own home before anyone else does. Your house, your rules.
5. **A full dev machine in your bag** — write code (Python, Go, Rust), commit to Git, push to the repo — from a café, a plane, a car.
6. **Show it off — "Hey Jarvis" in front of anyone** — talk to the iPad, it talks back, runs commands, analyzes a binary on the spot. Guests, colleagues — everybody is operator approved.
7. **An AI brain with no internet** — on a plane, in a dead zone: the little Qwen answers, explains code, drafts scripts. No cloud, nothing leaves the device.
8. **Test your own web services** — Burp Suite against your own sites and apps: intercept, inspect, test.
9. **A classroom in a tablet** — teach REA, demo the Apple TV teardown, demo Jarvis. The iPad is the screen, Kali is the engine, Jarvis is the voice.
10. **The travel cyberdeck** — the whole lab in a tablet that fits in a bag, on cellular. On a trip, in a hotel, at a client site — the lab travels with you. No laptop needed.

NOT on the list (honest): no Wi-Fi monitor mode, no GPU cracking, no USB device work — the VM has a virtual NIC, not the real radio.
