# Option A — Off-Grid Jarvis over STOCK Meshtastic (fastest demo)

The T-Watch-S3 already ships with Meshtastic (SX1280 2.4 G build). Meshtastic
already gives you framing, addressing, retries, and encryption, plus a **Python
serial API** on the laptop. So the fastest working off-grid demo reuses the
stock firmware and only adds the laptop bridge. **No flashing of the watch.**

## Pieces you need

1. **The watch** — stock Meshtastic (already there). It is your field node.
2. **A 2nd SX1280 2.4 GHz Meshtastic node** wired to the laptop over USB — the
   **gateway**. A LILYGO T3-S3 (SX1280 revision) flashed with Meshtastic, or a
   second T-Watch-S3 (SX1280). **Same band (2.4 GHz SX1280) on both** or they
   cannot hear each other.
3. **Laptop bridge** — `laptop-gateway/jarvis_lora_bridge.py` with `MODE =
   "MESHTASTIC"`, which uses the `meshtastic` Python library instead of raw
   serial.

## One-time setup

- Make sure both radios are on the **same Meshtastic channel** (same channel
  name + PSK) and the same region/modem preset so they talk. Set this in the
  Meshtastic phone app or `meshtastic` CLI. (Keep the channel PSK out of this
  repo.)
- Flash the gateway node with Meshtastic if it is not already (use the official
  web flasher / CLI). Do this with HgX present.

## Laptop install (later, with approval — not run in this build)

```
cd C:\Jarvis\projects\watch-offgrid\laptop-gateway
python -m venv .venv
.venv\Scripts\activate
pip install meshtastic pypubsub
# set SERIAL_PORT to the gateway's COM port, MODE = "MESHTASTIC"
python jarvis_lora_bridge.py
```

## How it works

The bridge subscribes to `meshtastic.receive`. When a text message
(`decoded.portnum == "TEXT_MESSAGE_APP"`) arrives, it reads `decoded.text`,
forwards it to the orchestrator (`ask_jarvis`), shortens the reply, and calls
`interface.sendText(reply)`. Meshtastic chunks/ACKs/encrypts for you.

```python
import meshtastic.serial_interface
from pubsub import pub

def on_receive(packet, interface):
    dec = packet.get("decoded", {})
    if dec.get("portnum") != "TEXT_MESSAGE_APP":
        return
    text = dec.get("text")
    if text:
        interface.sendText(shorten(ask_jarvis(text)))

pub.subscribe(on_receive, "meshtastic.receive")
iface = meshtastic.serial_interface.SerialInterface(devPath="COM5")
```

## Sending from the watch (off-grid)

On the stock watch firmware you send Meshtastic text messages via the watch's
canned-message UI, the Meshtastic phone app paired to the watch, or a Bluetooth
keyboard. Each text you send reaches the gateway, which hands it to Jarvis; the
reply comes back as a Meshtastic text and shows on the watch.

## Pros / cons recap

- **Pros:** fastest path to a real off-grid demo; encryption + ACK + mesh
  routing are free; a second Meshtastic node "just works" as the gateway.
- **Cons:** you live inside Meshtastic's text/UI model on the watch (canned
  text / app / keyboard) rather than a bespoke Jarvis wrist UI; message format
  is theirs, not our compact `PROTOCOL.md`.

## Addressing (optional refinement)
- Send Jarvis messages on a **dedicated channel** or to the **gateway's node id**
  so normal mesh chatter doesn't trigger qwen3. `sendText(..., destinationId=...)`
  targets a specific node. TODO: pick the addressing scheme when you set it up.
