#!/usr/bin/env python3
"""
flipper_jarvis.py  --  Laptop-side helper that bridges a Flipper Zero to Jarvis.

Part of the Jarvis Field Kit. Talks to the Flipper over its USB serial CLI,
pulls capture files off the Flipper SD card, hands them to the Jarvis
orchestrator for decoding/cataloging, and stores the normalized results.

STRICT SCOPE: this helper is for HgX's OWN devices, cards, remotes, and network
only -- cataloging and automating his own gear. It does not target anyone else's
hardware. Sub-GHz/NFC actions are read/catalog of his own captures; any emulate/
replay is only ever of devices he owns.

NOTHING here is run or installed by the scaffolding build. To use later:
    python -m venv .venv && .venv\Scripts\activate
    pip install pyserial
    python flipper_jarvis.py --list

The Flipper exposes a line-oriented CLI over USB serial (default 115200). This
helper wraps a few safe, read/catalog-oriented commands. Anything uncertain
about exact CLI syntax across firmware versions is marked TODO -- verify against
`help` on the device.
"""

import argparse
import json
import os
import time
import logging

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
FLIPPER_PORT    = os.environ.get("JV_FLIPPER_COM", "COM6")  # Flipper COM port from env (Device Manager)
FLIPPER_BAUD    = 115200                        # Flipper CLI default
ORCH_URL        = "http://127.0.0.1:8080"       # local Jarvis orchestrator
# Read-only catalog route: DOCUMENTED, NOT YET in orchestrator.py (needs HgX). Until it exists,
# catalog_with_jarvis() stores the raw capture only. Never point this at tool-capable /jarvis.
ORCH_CATALOG    = os.environ.get("JV_FLIPPER_CATALOG_ROUTE", "/catalog")
CATALOG_DIR     = r"C:\Jarvis\projects\watch-offgrid\flipper-kit\catalog"  # local store
ALLOW_TX        = False   # compile-time-style flag: receive/scan only by default
TX_VERBS        = ("subghz tx", "subghz tx_from_file", "ir tx", "nfc emulate",
                   "rfid emulate", "ikey emulate", "loader open BadUsb", "badusb")
SD_ROOTS        = ["/ext/subghz", "/ext/nfc", "/ext/infrared", "/ext/lfrfid", "/ext/ibutton"]
CLI_PROMPT      = ">: "                          # Flipper CLI prompt

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("flipper-jarvis")


class FlipperCLI:
    """Thin wrapper over the Flipper Zero USB serial CLI."""

    def __init__(self, port=FLIPPER_PORT, baud=FLIPPER_BAUD):
        import serial  # pip install pyserial
        self.ser = serial.Serial(port, baud, timeout=2)
        time.sleep(0.3)
        self._drain()

    def _drain(self):
        self.ser.reset_input_buffer()

    def cmd(self, line, settle=0.4):
        """Send one CLI command, return the text response up to the next prompt."""
        # Receive/scan only. Transmit/replay/emulate CLI verbs are refused unless
        # ALLOW_TX is flipped in source (OFF by default; HgX + own devices only).
        if not ALLOW_TX and line.strip().split(" ")[0:2] and any(
                line.strip().startswith(v) for v in TX_VERBS):
            raise PermissionError("TX disabled (ALLOW_TX=False): %r" % line.split(" ")[0])
        self.ser.write((line + "\r\n").encode())
        time.sleep(settle)
        out = b""
        # Read until we see the prompt again or the serial goes quiet.
        deadline = time.time() + 5
        while time.time() < deadline:
            chunk = self.ser.read(4096)
            if chunk:
                out += chunk
                if out.rstrip().endswith(CLI_PROMPT.strip().encode()):
                    break
            else:
                break
        text = out.decode("utf-8", "replace")
        # Strip the echoed command and the trailing prompt.
        return text

    def device_info(self):
        # `device_info` or `info` depending on firmware. TODO: confirm on device.
        return self.cmd("device_info")

    def storage_list(self, path):
        # Flipper CLI: `storage list /ext/subghz`
        return self.cmd("storage list %s" % path)

    def storage_read(self, path):
        # Flipper CLI: `storage read /ext/subghz/foo.sub` -> prints file contents.
        # TODO: for binary-ish files prefer qFlipper or `storage read_chunks`.
        return self.cmd("storage read %s" % path, settle=0.6)

    def close(self):
        try:
            self.ser.close()
        except Exception:  # noqa
            pass


# ----------------------------------------------------------------------------
# Pull captures off the SD and catalog them
# ----------------------------------------------------------------------------
def list_captures(cli):
    """Enumerate HgX's own saved captures across the known SD folders."""
    found = {}
    for root in SD_ROOTS:
        listing = cli.storage_list(root)
        log.info("== %s ==\n%s", root, listing)
        found[root] = listing   # TODO: parse names into a clean list
    return found


def pull_and_catalog(cli, sd_path):
    """
    Read one capture file off the Flipper SD, save a local copy, and hand it to
    Jarvis for decoding/cataloging.
    """
    os.makedirs(CATALOG_DIR, exist_ok=True)
    body = cli.storage_read(sd_path)
    local = os.path.join(CATALOG_DIR, os.path.basename(sd_path))
    with open(local, "w", encoding="utf-8") as f:
        f.write(body)
    log.info("saved %s (%d bytes)", local, len(body))

    meta = catalog_with_jarvis(os.path.basename(sd_path), body)
    # Store the normalized catalog record next to the raw file.
    with open(local + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return meta


def catalog_with_jarvis(name, body):
    """
    Ask the orchestrator to decode/label a capture (e.g. identify a .sub protocol,
    an NFC card type, an IR remote). Returns a dict record.

    ASSUMPTION / TODO: orchestrator accepts POST JSON {"kind":"flipper_capture",
    "name":..., "content":...} at ORCH_URL+ORCH_CATALOG and returns a JSON record.
    Adjust to the real contract. Offline-only decode logic could live here too.
    """
    import urllib.request
    payload = json.dumps({"kind": "flipper_capture", "name": name,
                          "content": body[:8000]}).encode()
    req = urllib.request.Request(ORCH_URL + ORCH_CATALOG, data=payload,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa
        log.warning("catalog call failed (%s); storing raw only", e)
        return {"name": name, "cataloged": False, "note": "orchestrator unreachable"}


# ----------------------------------------------------------------------------
# NOTE on the ESP32 Marauder board (own-airspace recon only)
# ----------------------------------------------------------------------------
# The ESP32 Wi-Fi board also exposes a serial CLI. A sibling helper (TODO:
# esp32_marauder.py) would run the RECON/monitor commands only -- e.g. list
# access points + stations on HgX's own network -- parse the output, and feed the
# device inventory to the Jarvis network-watchdog so new/unknown devices get
# flagged. Active attack commands (deauth/beacon spam) are intentionally NOT
# wrapped here. Keep it defensive and on his own airspace.


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Flipper <-> Jarvis helper (own devices only)")
    ap.add_argument("--list", action="store_true", help="list captures on the Flipper SD")
    ap.add_argument("--pull", metavar="SD_PATH", help="pull+catalog one capture, e.g. /ext/subghz/foo.sub")
    ap.add_argument("--info", action="store_true", help="print Flipper device info")
    args = ap.parse_args()

    cli = FlipperCLI()
    try:
        if args.info:
            print(cli.device_info())
        if args.list:
            list_captures(cli)
        if args.pull:
            print(json.dumps(pull_and_catalog(cli, args.pull), indent=2))
    finally:
        cli.close()


if __name__ == "__main__":
    main()
