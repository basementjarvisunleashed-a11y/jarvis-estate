# PiShop.ca — REA Lab Shopping List (consolidated)

**Status 2026-11-07: the REA bench list — a SEPARATE project from the
Pi 500+ rig order (see `local-jarvis/pi500/`). Summarised and authorised
up to $500; not confirmed placed. Nothing ordered.**

All prices CAD, verified on pishop.ca 2026-11-05, in stock. Nothing ordered.
Soldering iron listed ONCE. Two 32GB microSD cards kept (one for Kali/Pi images, one for firmware dumps).

## The keys — getting into the boxes
| Item | Qty | Price | What it is for |
|---|---|---|---|
| Raspberry Pi Pico (Non-Wireless), RP2040 — in cart | 1 | $5.65 | The checkm8-a5 dongle for the Apple TV 3 (A1427). Original RP2040 only — never Pico 2. https://www.pishop.ca/product/raspberry-pi-pico-non-wireless/ |
| Raspberry Pi Pico (Non-Wireless), RP2040 — spare | 1 | $5.65 | Spare dongle; a dead Pico must never stall the project. https://www.pishop.ca/product/raspberry-pi-pico-non-wireless/ |
| Arduino Compatible USB Host Shield | 1 | $23.95 | The Arduino-road checkm8-a5 dongle (pairs with an Uno). Verify MAX3421E printed on the board on arrival. https://www.pishop.ca/product/arduino-compatible-usb-host-shield/ |
| USB to Micro-USB cable, 45cm ×2 | 2 | $5.90 | Data-capable cables: one Pico↔Acer, one Apple TV DFU. https://www.pishop.ca/product/usb-cable-a-to-micro-b-45cm-black/ |
| USB Console Stub — serial adapter, 3.3V | 1 | $6.45 | Cheap USB-to-TTL serial console for Pi, Pico and embedded targets. https://www.pishop.ca/product/usb-console-stub-serial-adaptor-for-raspberry-pi/ |
| Waveshare USB-to-RS232/RS485/TTL isolated converter (FT232RL) | 1 | $33.95 | One box for every serial job: TTL UART consoles on the Samsung TV, Lorex cameras and smart locks, plus true DB9 RS-232 for the Sony laptop's era of gear. Isolated — a miswired target cannot fry the Acer. https://www.pishop.ca/product/usb-to-rs232-rs485-ttl-industrial-isolated-converter/ |
| Raspberry Pi Debug Probe | 1 | $16.95 | SWD + UART in one kit, for Pico/ARM targets and as a second UART. https://www.pishop.ca/product/raspberry-pi-debug-probe/ |
| FTDI Serial TTL-232 USB Type-C cable, 5V/3.3V, 1m | 1 | $30.95 | A more convenient UART cable than the Waveshare box's screw terminals. https://www.pishop.ca/product/ftdi-serial-ttl-232-usb-type-c-cable-5v-power-3-3v-logic/ |

## The bench — working on the boards
| Item | Qty | Price | What it is for |
|---|---|---|---|
| Half-size 400-pin breadboard ×2 | 2 | $7.90 | Prototyping base for Pico/Arduino bench work. https://www.pishop.ca/product/half-size-400-pin-electronics-diy-breadboard/ |
| Male-to-female jumper cables ×40 ×3 | 3 | $8.85 | Pico/Arduino headers → breadboard; UART/SPI/I2C hookups. https://www.pishop.ca/product/diy-jumper-wires-for-raspberry-pi-30cm/ |
| Female-to-female jumper cables ×40 | 1 | $2.95 | Header-to-header links (debug probe to target board). https://www.pishop.ca/product/40-x-jumper-cable-for-arduino-20cm/ |
| Bus Pirate v3.6 Universal Serial Interface | 1 | $39.95 | UART/SPI/I2C/JTAG, bus sniffing, low-speed logic analyzer, flashrom/OpenOCD support — directly useful for firmware dumping. https://www.pishop.ca/product/bus-pirate-v3-6-universal-serial-interface/ |
| Open Workbench Logic Sniffer | 1 | $69.95 | 16-channel, up to 200Msps logic analyzer for sniffing SPI/I2C/UART on TVs, cameras, locks. Probe cable NOT included — needs a further purchase before use. https://www.pishop.ca/product/open-workbench-logic-sniffer/ |
| Hakko RED 503 soldering iron, 60W (ONCE) | 1 | $20.95 | Header pins, UART pad work, repairs on DVD players / TV / camera boards. Solder NOT included — buy a small tube elsewhere. https://www.pishop.ca/product/hakko-red-503-soldering-iron/ |
| Raspberry Pi Pico Header Set | 1 | $2.45 | Lets the spare Pico plug into a breadboard (needs the iron above). https://www.pishop.ca/product/raspberry-pi-pico-header-set/ |
| USB 2.0 powered hub, 7 ports + 5V 2A supply | 1 | $42.18 | Keeps the Acer's ports free with Pico, converter, analyzer and drives all live at once. https://www.pishop.ca/product/usb-2-0-powered-hub-7-ports-with-5v-2a-power-supply/ |

## Storage, power & cables
| Item | Qty | Price | What it is for |
|---|---|---|---|
| SanDisk Ultra microSDHC 32GB, Class 10, BLANK ×2 | 2 | $55.90 | Card 1: Kali/Pi ARM images. Card 2: firmware dumps. 32GB ships FAT32 — no reformatting. https://www.pishop.ca/product/sandisk-ultra-microsdhc-32gb-class-10-blank/ |
| Raspberry Pi 27W USB-C Power Supply, 5.1V/5A | 1 | $16.95 | Powers a future Pi 5 and anything 5V on the bench. https://www.pishop.ca/product/raspberry-pi-27w-usb-c-power-supply-black-us/ |
| SparkFun 4-in-1 Multi-USB Cable, USB-C host | 1 | $22.95 | One 6ft cable, four ends: USB-C (Switch, Androids), micro-B (Pico, Apple TV), mini-B (old DVD players/cameras), USB-B (feeds the Waveshare converter, which ships without a cable). https://www.pishop.ca/product/4-in-1-multi-usb-cable-usb-c-host/ |
| 5ft Cat6 Ethernet cable ×2 | 2 | $3.90 | SSH/NFS lifeline to the Apple TV after entry, plus a spare. https://www.pishop.ca/product/5ft-cat6-ethernet-cable-black/ |
| 7ft Cat6 Ethernet cable ×2 | 2 | $5.90 | Longer bench runs for the Samsung TV and Lorex NVR/cameras. https://www.pishop.ca/product/7ft-cat6-ethernet-cable/ |

## Totals
- Items: **$340.15** (core) — **$430.23** (with Debug Probe, FTDI cable, powered hub)
- + shipping $13.92 → $354.07 / $444.15
- + HST 13% → **grand total $400.10 core / $501.89 with everything**

## Still needed from elsewhere (NOT PiShop)
- **Arduino Uno** — PiShop has none in stock. Canada Robotix: compatible Uno $15.99 / genuine $35.99 (prices from earlier research, re-verify at checkout).
- **Lightning cable** (iPhones/iPads) — PiShop does not sell one. Apple / Best Buy / Amazon.
- **Solder** — small tube; not included with the Hakko iron.
- **Logic Sniffer probe cable** — not included with the Sniffer; buy before it is usable.
- **Raspberry Pi 5** — separate future purchase, not in this order: 4GB $156.85 / 8GB $249.50 at PiShop. The 27W supply and microSD in this order already cover its power and storage.
- **64GB microSD upgrade (optional swap):** Official Raspberry Pi 64GB A2 V30 BLANK, $45.95 — swap for one 32GB card (+$18.00) for headroom for several Kali images at once.
