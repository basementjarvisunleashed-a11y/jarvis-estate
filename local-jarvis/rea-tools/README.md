# REA tools — the bench record

The 15 REA tools, all installed 2026-11-07, plus BLA 3.2.3 (the
counter-REA defense, not a REA tool).

## The 15 tools

| # | Tool | Version | Note |
|---|---|---|---|
| 1 | Detect-It-Easy | 4.0.0 | |
| 2 | capa | v10.0.0 | |
| 3 | ImHex | 1.38.1 | |
| 4 | LIEF | 0.16.2 | |
| 5 | Ghidra | 12.1.4 (apt) + 12.2 (upstream) | Two copies; `ghidra-data` 10.5 lags, minor |
| 6 | GhidraMCP | 2.0 | Port 8081 — GUI verification pending |
| 7 | angr | 10.0.5 | Unicorn disabled |
| 8 | Frida | 17.26.2 | |
| 9 | objection | 1.12.5 | |
| 10 | jadx | 1.5.6 | |
| 11 | Apktool | 3.0.3 | |
| 12 | ILSpy ilspycmd | 11.2.0.10050 | `TERM=dumb` mandatory |
| 13 | asar | 4.3.1 | |
| 14 | mitmproxy | 12.3.1 | |
| 15 | Wireshark | 4.6.9 | |

## Files here

| File | What it is |
|---|---|
| `rea-tool-usage-guide.md` | The teach guide (384 lines, scrubbed) — one section per tool, with the exact commands. |
| `BLA-COUNTER-REA.md` | BLA 3.2.3, the counter-REA defense, with its benchmark and the honest caveat. |

## The registry (on the Acer, not published)

`~/Jarvis/rea-toolset.md` is the record of record: all 15 tools with
versions and locations. It lives on the Acer. If this guide and the
registry disagree, the registry wins — and report the disagreement.

## The C270 close-out

The 15-tool breakdown of the Logitech C270 closed 2026-11-08: 373
functions decompiled, 6,037 packets / 233 MB live pcap, 83.0%
isochronous. Verdict: stock, clean UVC device. Figures in
`../STATE-2026-11-10.md` and `../c270/README.md`; the full
consolidated report lives on the Acer, not yet sent.

---

@basementjarvisu · basementjarvisunleashed@gmail.com
