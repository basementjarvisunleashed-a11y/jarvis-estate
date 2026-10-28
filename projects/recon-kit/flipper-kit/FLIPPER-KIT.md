# Flipper Kit — Jarvis Field Kit RF & Wireless Module

Part of the **Jarvis Field Kit** (the legacy R&D project). This module wires
HgX's **Flipper Zero** and his **ESP32 Wi-Fi dev board** (the companion board
running Marauder / ESP32 Wi-Fi firmware) into Jarvis.

> **Scope / ethics — read first.** Everything here is scoped to **HgX's OWN
> devices, cards, remotes, and network**: cataloging and automating his own gear
> and watching his own airspace defensively. This is not for reading, emulating,
> or replaying anyone else's cards, remotes, or networks. Keep it legal and
> defensive. Sub-GHz replay and NFC emulation are only ever used on hardware HgX
> owns and controls (his garage, his gate, his fobs, his tags).

---

## What the Flipper Zero can do with Jarvis (own devices only)

| Capability | What Jarvis does with it | Own-device note |
|------------|--------------------------|-----------------|
| **RFID 125 kHz read & emulate** | Catalog HgX's own access fobs; let the watch/Jarvis trigger an emulate of HIS fob | Only HgX's own tags |
| **NFC read & emulate** | Read & store HgX's own NFC tags/cards; label them in the catalog | Only HgX's own cards |
| **Sub-GHz capture/replay** | Capture + save HIS OWN garage door / gate / RF remotes, then let Jarvis replay to open them on command | Only remotes HgX owns; many modern remotes are rolling-code and won't replay — note that |
| **Infrared universal remote** | Learn HgX's TVs/AC/soundbar; Jarvis drives IR scenes ("movie mode") | His own appliances |
| **BadUSB / HID scripting** | Pre-approved automation macros Jarvis can push to HgX's own machines | His own PCs only |
| **iButton (1-Wire)** | Catalog his own iButton keys | His own keys |
| **GPIO / UART / SPI / I2C** | Bench tool for chip/sensor reverse-engineering in the RE lab | Hardware he owns |

## What the ESP32 Wi-Fi board adds

| Capability | What Jarvis does with it |
|------------|--------------------------|
| **Wi-Fi recon / network mapping (Marauder)** | Enumerate APs + stations **on HgX's own network/airspace**, feed the inventory to the **Jarvis network-watchdog** so new/unknown devices get flagged |
| **Packet/beacon monitoring** | Passive monitoring of his own 2.4 GHz space for rogue APs / evil-twins impersonating his SSID |
| **Signal strength / channel survey** | Map coverage + congestion to tune his own Wi-Fi |

(Active Wi-Fi attack features in Marauder — deauth, beacon spam, etc. — are out
of scope here. This module uses the **recon/monitor** side only, defensively, on
his own network.)

---

## Flagship build — "Jarvis RF & Wireless Security Scout"

A Jarvis-driven scout that continuously inventories HgX's own RF and wireless
environment and flags anything new or rogue:

```
  Flipper Zero  --USB serial CLI-->  flipper-jarvis helper  --->  Jarvis
     - sub-GHz sweeps (own remotes)        (Python on laptop)       orchestrator
     - IR scene control                    - pulls .sub/.nfc/.ir      -> qwen3
     - NFC/RFID own-tag catalog              capture files off SD      cataloging
                                           - normalizes + stores      + alerts
  ESP32 Marauder --USB serial-->  parses AP/station lists  ---^
     - own-airspace Wi-Fi recon

  Output: a living catalog of HgX's own signals + devices. Jarvis diffs each
  scan against the known-good baseline and raises an alert (watch buzz / status
  hub / voice) when a NEW or UNEXPECTED signal or device appears — a rogue AP
  cloning his SSID, an unknown 125kHz fob near the door, an unexpected sub-GHz
  transmitter. Ties straight into the existing Jarvis network-watchdog idea.
```

Everything is **defensive**: it inventories and alerts on his own property; it
does not attack, jam, or impersonate anyone.

---

## Bill of materials (Flipper module)

| Item | Status | Note |
|------|--------|------|
| Flipper Zero | **Owned** | — |
| ESP32 Wi-Fi dev board (Marauder companion) | **Owned** | GPIO or WiFi Dev Board |
| USB-C data cables (Flipper + ESP32) | Likely have | Must be data, not charge-only |
| (Optional) Flipper microSD card (if not already in it) | Check | Stores captures Jarvis pulls |
| (Optional) 2.4 GHz Wi-Fi antenna for the ESP32 board | Optional | If the board has a U.FL/SMA connector; improves recon range |
| (Optional) blank NFC cards / 125kHz T5577 fobs | Optional | To clone HIS OWN tags onto spares |
| (Optional) Flipper GPIO jumper leads | Optional | For chip/sensor RE bench work |

## Safety / legal notes
- Only HgX's own cards, tags, remotes, appliances, machines, and network.
- Rolling-code remotes (most modern garage/car) cannot be simply replayed — the
  helper flags these rather than pretending it worked.
- BadUSB macros run only on HgX's own machines, with his approval each time.
- No jamming, no deauth, no impersonation, no third-party targets.
- No secrets, keys, or card dumps are committed to this repo — captures live on
  the Flipper SD and in HgX's local catalog only.
