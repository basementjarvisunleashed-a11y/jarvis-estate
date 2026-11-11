# Raspberry Pi 500+ — Accessories: The Complete Sweep

All prices CAD, verified on pishop.ca 2026-11-05, in stock unless noted. **STATUS 2026-11-05 ~15:56 ET: ORDERED — his secretary placed the order, already paid, on its way for delivery. HgX orders it himself (not Jarvis).**
Items already in the other PiShop order (27W PSU, SanDisk 32GB, Pico, Bus Pirate, etc.) are flagged, not duplicated.

## NVMe verdict (one line)
**ONE M.2 slot — the 256GB drive can be REPLACED with a bigger NVMe, but a second internal NVMe cannot be added; a second drive must live outside over USB 3.0 (enclosure), microSD, or the network.**
HgX's pick: Samsung 990 PRO 2TB (Amazon.ca $649.99) — M.2 2280, fits the slot; speed capped by the Pi's single PCIe lane (~500MB/s Gen2, ~900MB/s Gen3), far below the drive's 7,450MB/s rating. Non-heatsink version is the right pick for fit inside the keyboard case.

## Kit & power
| Item | Price | Stock | Why |
|---|---|---|---|
| Raspberry Pi 500+ Desktop Kit (US layout) | $609.00 | In stock | THE BUY: 500+ + PSU + Mouse 2 Black + Beginner's Guide + 1× micro-HDMI 1m cable. Only $35 more than unit-only; the PSU ($16.95) + mouse ($11.45) + cable ($6.95) bought separately cost $35.35 — the kit is cheaper AND includes the guide. https://www.pishop.ca/product/raspberry-pi-500-us-kit/ |
| Raspberry Pi 500+ Unit Only (US layout) | $574.00 | In stock | Bare unit, no accessories. For reference — the kit above beats it. https://www.pishop.ca/product/raspberry-pi-500-us-unit-only/ |
| Raspberry Pi 27W USB-C Power Supply, Black US | $16.95 | In stock | 5V/5A — the 500+'s required power. ALREADY in the other order — do not buy twice. https://www.pishop.ca/product/raspberry-pi-27w-usb-c-power-supply-black-us/ |

## Storage
| Item | Price | Stock | Why |
|---|---|---|---|
| Raspberry Pi NVMe SSD 256GB / 512GB / 1TB | $98.75 / $159.95 / $178.95 | Out of stock | Official Pi drives — but M.2 **2230**, wrong length for the 500+'s 2280 slot (would need an adapter PiShop doesn't sell). Out of stock anyway. |
| Waveshare NX M2 NVME 2280 256GB | $120.50 | Out of stock | True 2280 — WOULD fit the slot directly — but out of stock. |
| Waveshare NX M2 NVME 2280 128GB | $80.95 | In stock | True 2280, fits — but terrible value ($80.95 for 128GB). Listed for completeness; not recommended. |
| Official Raspberry Pi microSD 64GB A2 V30, BLANK | $45.95 | In stock | Second boot/storage option in the microSD slot — a Kali image on card, Pi OS on SSD, or vice versa. https://www.pishop.ca/product/official-raspberry-pi-microsd-card-a2-v30-64gb/ |

**Bottom line on storage:** PiShop is a bad place to buy the replacement NVMe right now — every official Pi SSD is the wrong length (2230) and out of stock, and the only true-2280 drive in stock is a bad deal. Buy a standard M.2 2280 NVMe elsewhere (Amazon.ca / Best Buy / Canada Computers).

## Second drive (USB — the "extra NVMe" answer)
| Item | Price | Stock | Why |
|---|---|---|---|
| USB NVMe enclosure | — | Not sold by PiShop | PiShop's "nvme enclosure" search returns no enclosure at all. Buy elsewhere — Amazon.ca lists the Plugable USBC-NVME tool-free enclosure at $69.95; Best Buy marketplace has dual-protocol (NVMe+SATA) enclosures. |

## Display & cables
| Item | Price | Stock | Why |
|---|---|---|---|
| Micro-HDMI to Standard HDMI (A/M), 1m, Black — official, 4Kp60 | $6.95 | In stock | The cable the 500+ needs to reach a TV/monitor. Buy 2 for dual 4K (kit includes 1, so kit route needs 1 more). https://www.pishop.ca/product/micro-hdmi-to-standard-hdmi-a-m-1m-cable-black/ |
| Micro-HDMI to Standard HDMI (A/M), 2m, Black | $8.95 | Unconfirmed | Longer run for the second screen. |
| Micro-HDMI to Standard HDMI, 3ft | $5.95 | Unconfirmed | Short run. |
| Micro HDMI to Standard HDMI Adapter, 235mm, White | $4.95 | Unconfirmed | Lets you use any full-size HDMI cable you already own. |
| Micro HDMI Male to HDMI Female Adapter Cable | $3.45 | Unconfirmed | Cheapest way to reuse an existing HDMI cable. |
| 7" HDMI LCD (C) Display, 1024×600, IPS, capacitive touch | $62.95 | In stock | Portable second screen over plain HDMI (touch via USB). Optional — the bench's little dashboard screen. https://www.pishop.ca/product/7inch-hdmi-lcd-c-display-1024x600-ips/ |

## GPIO & HATs (the 500+'s horizontal header)
| Item | Price | Stock | Why |
|---|---|---|---|
| Adafruit CYBERDECK HAT for Raspberry Pi 400 & 500 | $14.95 | In stock | **Made for the 500+.** Turns it into a standalone Kali deck: plug in a display HAT, plus STEMMA/QT plugs for NeoPixels, servos, sensors. The most on-brand accessory on this list for the REA bench. https://www.pishop.ca/product/adafruit-cyberdeck-hat-for-raspberry-pi-400/ |
| Pimoroni Breakout Garden for Raspberry Pi 400 & 500 | $16.95 | In stock | **Made for the 500+.** Right-angle format for the horizontal header; 3 slots (2× I2C, 1× SPI) for solderless sensor/display breakouts. Breakouts sold separately. Note: it obstructs one HDMI connector on the Pi 500. https://www.pishop.ca/product/breakout-garden-for-raspberry-pi-400/ |
| SparkFun Qwiic pHAT Extension for Raspberry Pi 400 & Pi 500 | $8.95 | Out of stock | Reroutes the 40-pin header to vertical so normal HATs can stack right-side up, plus Qwiic I2C ports. Great part — but OOS at PiShop right now. https://www.pishop.ca/product/sparkfun-qwiic-phat-extension-for-raspberry-pi-400/ |
| GPIO Ribbon Cable, 40-pin, 6" | $5.45 | In stock | Breaks the GPIO out to a breadboard or another board. Electrically fits any 40-pin header including the 500+'s; physical clearance on the recessed horizontal header unconfirmed. https://www.pishop.ca/product/gpio-ribbon-cable-for-raspberry-pi-model-abpi-2pi-3-40-pins/ |
| GPIO Hammer Headers (female $4.95 / male $3.95) | — | — | **Do NOT buy.** They hammer onto unpopulated Pi Zero/pHAT holes; the 500+'s header is already populated. |

**What does NOT fit the 500+:** standard Pi 5 HATs — the Raspberry Pi M.2 HAT+, M.2 HAT+ Compact, Pimoroni NVMe Base / NVMe Base Duo, and all Waveshare PCIe-to-M.2 adapters — are Pi 5-board accessories. The 500+ exposes no PCIe, and its GPIO is horizontal and recessed, so none of them mount. Only the three 400/500-specific items above (CYBERDECK, Breakout Garden, Qwiic pHAT) are made for this header.

**Also not applicable:** the 500+ has NO camera (CSI) or display (DSI) ports — the brief's spec table lists neither. Pi Cameras and the Raspberry Pi Touch Display 2 ($86.95, DSI) do **not** work with it. HDMI displays only (like the 7" LCD above).

## Keyboard & keys
| Item | Price | Stock | Why |
|---|---|---|---|
| Key Dampeners for Raspberry Pi 500+ (200 silicone O-rings) | $5.95 | In stock | Sit under each key, soften the clicky Gateron Blues and the typing feel. One kit covers the whole keyboard with spares. https://www.pishop.ca/product/key-dampeners-for-raspberry-pi-500/ |
| Replacement keycap sets | — | Not sold by PiShop | Keycaps ARE swappable (tools included; Cherry MX stems, per Raspberry Pi docs — the switches themselves cannot be replaced). Buy generic low-profile Cherry-MX-stem keycaps elsewhere if wanted. |

## Everything else
| Item | Price | Stock | Why |
|---|---|---|---|
| Raspberry Pi Mouse 2 — Black | $11.45 | In stock | The exact mouse included in the Desktop Kit. Only needed on the unit-only route. https://www.pishop.ca/product/raspberry-pi-mouse-2-black/ |
| Raspberry Pi Mouse 2 — White | $11.45 | In stock | Same mouse, white. |
| Official Raspberry Pi Mouse (black/grey) | $11.95 | In stock | The older official mouse; same job. |
| Sleeve / carry case for the 500+ | — | Not sold by PiShop.ca | No sleeve on PiShop.ca. Alternatives: Adafruit Black Zipper Sleeve Case for Pi 400 & 500 ($14.95 USD, adafruit.com) or the Felt Sleeve Case; The Pi Hut (UK) also sells a 500/400 sleeve. |

## Recommended set & total (CORRECTED 2026-11-05 ~15:26 ET — HgX: the 7" screen IS included in this project; the REA bench list is a SEPARATE project, do not mix them)
**Buy the Desktop Kit route** — it is the better deal:
- Desktop Kit $609.00 + 1× micro-HDMI 1m $6.95 (second display) + Key Dampeners $5.95 + CYBERDECK HAT $14.95 + Breakout Garden $16.95 + GPIO Ribbon Cable $5.45 + microSD 64GB $45.95 + 7" HDMI LCD (C) $62.95 = **$768.15** in items → + HST 13% ($99.86) = **$868.01 before shipping**.
- The unit-only route would cost more and lacks the Beginner's Guide. The kit wins.
- Accessories alone (excluding the 500+ itself): **$159.15** on the kit route.
- Plus, from Amazon.ca: Samsung 990 PRO 2TB $649.99 before tax (~$734 with tax).

## What PiShop does NOT carry (with alternatives)
- **USB NVMe enclosure** — none on PiShop. Amazon.ca: Plugable USBC-NVME, $69.95. Best Buy marketplace: dual-protocol enclosures.
- **Keycap sets** — none on PiShop. Generic low-profile Cherry-MX-stem keycaps from any keyboard retailer.
- **Sleeve/case for the 500+** — none on PiShop.ca. Adafruit zipper sleeve ($14.95 USD) or The Pi Hut sleeve.
- **Qwiic pHAT Extension** — listed but out of stock at PiShop; check back or order from SparkFun/Adafruit directly.
- **Replacement NVMe at a sane price** — PiShop's official Pi SSDs are 2230 + out of stock; the in-stock 2280 is bad value. Buy a standard 2280 NVMe (1TB class) from Amazon.ca / Best Buy / Canada Computers.
