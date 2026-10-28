# laptop-ingest - Jarvis Recon Kit vision service (SPEC)

## Flow
```
Mentra Live --direct SRT:8890 (passphrase) / WHIP:8889 (+UDP 8189 media)--> MediaMTX path "glasses"   (RTMP off)
MediaMTX --rtsp://127.0.0.1:8554/glasses (local only)--> recon_ingest.py (:8767)
recon_ingest.py: ffmpeg grabs 1 JPEG (memory only) -> Ollama moondream/llava :11434
   -> NOT sent to orchestrator /jarvis (agentic; vision text is untrusted). JSON-line metadata log only.
   -> watch: HTTP response (Wi-Fi) or LoRa bridge push :8766 -> JV1 'R' "RC:<text>"
```

## Triggers (all end in POST /look)
| Who | How | source |
|-----|-----|--------|
| Glasses | phone-bridge, "look" / button | `glasses` |
| Watch, Wi-Fi | watch POSTs `http://<laptop-ip>:8767/look` | `watch` |
| Watch, LoRa | `JV1 C "recon[:prompt]"` -> bridge -> `/look` | `lora` |

## Contract
- `POST /look` envelope `{v:1,id,ts,src,kind:"cmd",payload:{prompt}}` -> envelope `{kind:"reply",ack_of,payload:{text,short,ms,status}}`
- `GET /health` -> `{"ok":true,"stream":true|false}`
- Envelope v1 (shared/schema.json) in and out; binds 127.0.0.1 by default; body 4 KB; prompt 300 chars. No cloud fallback (SAF).

## Files
- `mediamtx.yml` - rev2 ingest config: no STUN, no api/metrics/pprof/playback/hls, RTMP off, SRT passphrase, publish from tailnet + specific /32s, read localhost only, no recording, logs C:\JarvisData\mediamtx.
- `start-mediamtx.ps1` - the ONLY way to start MediaMTX: refuses without real >=24-char secrets from gitignored .env. No autostart.
- `recon_ingest.py` - stdlib-only service.

## VRAM note (RTX 2060 ~6 GB)
moondream (~1.7 GB) coexists with qwen3:8b better than llava:7b (~4.5 GB).
Start with moondream.

## Guardrails
Own camera feed only. No frames saved to disk. LAN-only binding check.
Not started by this build - see BUILD-STATUS.md.

