# LoRa Message Protocol (custom, Option B)

A tiny framed text protocol for the Jarvis off-grid link. Designed to fit inside
one LoRa payload (keep total frame <= ~200 bytes; SX1280 can do more, but small
frames = lower airtime + fewer drops). This spec applies to **Option B (custom
firmware)**. In **Option A (Meshtastic)** the transport framing/ACK/CRC is
handled by Meshtastic itself and you send plain text — see `MESHTASTIC-OPTION.md`.

## Design goals
- Human-debuggable (printable ASCII), compact, resilient to drops.
- Explicit message id + sequence so long replies can be chunked and reassembled.
- A CRC so corrupted frames are discarded.
- ACKs so each side can retry.

## Frame format (ASCII, pipe-delimited)

```
JV1|<msgid>|<type>|<seq>|<total>|<payload>|<crc>
```

| Field   | Meaning |
|---------|---------|
| `JV1`   | Magic + version. Lets us reject junk and bump the version later. |
| `msgid` | 1-4 char base36 id of the *logical* message (a command or a reply). Unique per sender for a while. |
| `type`  | `C`=cmd (watch->laptop), `R`=reply (laptop->watch), `A`=ack, `N`=nack/retry-request, `P`=ping/presence. |
| `seq`   | 0-based chunk index of this frame within the logical message. |
| `total` | Total number of chunks in this logical message. |
| `payload` | The chunk text. For `A`/`N` this is the msgid+seq being (n)acked. Must not contain a raw `|`; escape as `\x7c` if needed. |
| `crc`   | CRC-16/CCITT (hex, 4 chars) over the bytes `JV1|...|<payload>` (everything before the final `|crc`). |

### Example — a command from the watch

```
JV1|7f|C|0|1|status report|3a2c
```

### Example — a two-chunk reply from the laptop

```
JV1|7f|R|0|2|All services up. VRAM 5.1G.|b19d
JV1|7f|R|1|2| Last job finished 2m ago.|04e7
```
(The watch reassembles by `msgid`, orders by `seq`, and knows it has all of them
when it has `total` distinct chunks.)

### Example — an ACK

```
JV1|7f|A|0|1|7f:0|9c11
```

## Rules

1. **Reply msgid mirrors the command msgid** so the watch can match a reply to
   the command it sent.
2. **Chunking:** sender splits payload so each full frame stays <= MAX_FRAME
   bytes (default 200). `total` is the chunk count.
3. **ACK/retry:** receiver ACKs each chunk (`A`). Sender keeps a per-chunk timer
   (default 4 s) and retransmits un-ACKed chunks up to N times (default 3). A
   receiver missing a chunk after a timeout may send `N` with the missing seq.
4. **CRC:** CRC-16/CCITT (poly 0x1021, init 0xFFFF). Drop frames whose CRC
   fails; do not ACK them.
5. **Dedup:** a receiver that already has `(msgid,seq)` re-ACKs but does not
   re-process.
6. **Presence:** `P` frames (payload = node name) every ~60 s let each side show
   link-alive. Optional.
7. **Truncation:** the laptop bridge truncates qwen3 replies to a configurable
   max (default ~400 chars) before chunking so a long answer can't flood the air.

## Reserved / future
- `type=E` error, `type=G` GPS/telemetry push from the watch.
- A compact binary variant (replace the ASCII header with packed bytes) once the
  ASCII version is proven. Marked TODO.

## Notes / assumptions (TODO to verify on hardware)
- MAX_FRAME and the 4 s/3-retry timers are starting guesses; tune against real
  airtime at your chosen SX1280 spreading factor/bandwidth.
- base36 msgid space is small; wrap-around is fine for this low-rate link but
  revisit if traffic grows.

## Recon Kit extension (v1, backward compatible)
- **Command:** `JV1|<id>|C|0|1|recon|crc` or `recon:<prompt>` (e.g. `recon:read the label`).
  The bridge routes it to laptop-ingest `POST /look` (source=lora) instead of qwen3.
- **Result:** normal `R` frames whose payload starts with `RC:` - the watch shows an
  "EYES" card and triple-buzzes. Results are capped at 160 chars (1-2 frames).
- **Unsolicited push:** glasses-triggered looks are pushed via the bridge's local
  `127.0.0.1:8766/push` as `R` frames with the glasses msgid, also prefixed `RC:`.
- **Wi-Fi fast path:** at home the watch POSTs `http://<laptop>:8767/look` directly
  (`{"msgid","source":"watch","prompt"}`) and renders `short` the same way.
- The watch now sends `A` ACKs per chunk.

## Anti-replay (2026-10-28, SAF)
Signing is mandatory. Signed frame: `JV1|msgid|type|seq|total|payload|ctr|mac|crc` - `ctr` = hex monotonic counter per sender (persisted: bridge `C:\JarvisData\lora\counters.json`, watch NVS). MAC = HMAC-SHA256/8 over everything before it, incl. ctr. Receivers drop any ctr <= last seen. Reply chunks are resent (4/8/16 s) until the watch ACKs `msgid:seq`; resends get a fresh ctr.

