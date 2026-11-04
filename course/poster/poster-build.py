# J.A.R.V.I.S. — OPERATOR PRIME Course Material
# J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System) — public identity, first and prominent.
# Operator: HgX (small). Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.
# DISCLAIMER: NOT an official University of Toronto calendar entry, course code, or accreditation. No approval claimed as verified.
# STATUS: LOCKED v1.0.0 — Poster build script. MIT licence.
# Licence: MIT. © HGX Engineering.

from PIL import Image, ImageDraw, ImageFont
import textwrap
W, H = 1600, 2680
BG = (8, 20, 38); CARD = (18, 41, 77); BORDER = (42, 74, 122)
BLUE = (0, 194, 255); GOLD = (245, 197, 66); WHITE = (255, 255, 255); LIGHT = (215, 230, 255); MUTED = (169, 198, 232)
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def F(p, bold=False): return ImageFont.truetype(BOLD if bold else REG, p)
img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
def rr(box, fill, outline=None, r=18):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=2 if outline else 1)
def center(y, text, font, fill=WHITE):
    w = d.textlength(text, font=font); d.text(((W-w)/2, y), text, font=font, fill=fill); return y + font.size + 8
def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines
def section(y, title):
    d.text((64, y), title, font=F(36, True), fill=BLUE); return y + 58
y = 48
# badge
badge = "CONTROLLED LAB ONLY  •  DEFENSIVE EDUCATION"
bw = d.textlength(badge, font=F(26, True)) + 52
rr([ (W-bw)/2, y, (W+bw)/2, y+54 ], None, BLUE, 27)
d.text(((W-d.textlength(badge, font=F(26, True)))/2, y+12), badge, font=F(26, True), fill=BLUE); y += 78
y = center(y, "THE OPERATOR", F(92, True)); y = center(y-6, "COURSE", F(92, True), BLUE)
for line in ["Kali Everything  •  REA  •  Open Hardware", "SEE  →  DOCUMENT  →  LOG  →  PREVENT"]:
    y = center(y, line, F(32, True), GOLD if "SEE" in line else LIGHT)
y += 10; d.line([(64, y), (W-64, y)], fill=BLUE, width=4); y += 30
# pillars
y = section(y, "THE 3 PILLARS")
cards = [("1. Kali Everything", "Full suite, all families,\nall tools — one laptop,\nthe whole spectrum."),
         ("2. REA Everything", "Reverse-engineer anything,\nlocally. Analyze, inspect,\nprove — then defend."),
         ("3. Grokbot", "Cloud brain, local hands.\nReasoning in the cloud,\nwork on the Acer.")]
cw, gap = 480, 20; x0 = 64
for i, (t, p) in enumerate(cards):
    x = x0 + i*(cw+gap); rr([x, y, x+cw, y+210], CARD, BORDER)
    d.text((x+22, y+18), t, font=F(29, True), fill=WHITE)
    for j, ln in enumerate(p.split("\n")): d.text((x+22, y+66+j*32), ln, font=F(23), fill=LIGHT)
y += 232
# stacks
y = section(y, "THE 10 STACKS — ALL LOCAL-ONLY")
left = ["1. REA — local CLI, local model", "2. Security Audit Skill — sandboxed", "3. Graphify — local knowledge graph", "4. HyperFrames — HTML → video", "5. ComfyUI — local diffusion, offline"]
right = ["6. FreeLLMAPI — router → Ollama", "7. ai-memory — zero-LLM default", "8. Claude Plugins — needs Claude Code", "9. VoiceStudio — voice + lectures", "10. GenOffice — Docs, Sheets, Slides"]
rr([64, y, 784, y+210], CARD, BORDER); rr([816, y, 1536, y+210], CARD, BORDER)
for i, t in enumerate(left): d.text((88, y+16+i*36), t, font=F(24), fill=WHITE)
for i, t in enumerate(right): d.text((840, y+16+i*36), t, font=F(24), fill=WHITE)
y += 232
# hardware
y = section(y, "ALL 20 HARDWARE PIECES")
hl = ["1. Flipper Zero + Starter Kit", "2. Mentra Live Camera Glasses", "3. T-Watch S3 Plus — Meshtastic", "4. HackRF One — SDR", "5. Proxmark3 RDV4 — RFID / NFC", "6. Ubertooth One — Bluetooth", "7. ChipWhisperer-Lite — side-channel", "8. KrakenSDR — direction finding", "9. T-Beam — Meshtastic node", "10. OpenMV Cam — machine vision"]
hr = ["11. GreatFET One — USB bridge", "12. PX4 / ArduPilot Drone Kit", "13. Frigate — motion, local NVR", "14. Near-IR Night Vision", "15. Thermal — MLX90640", "16. SatNOGS Satellite Station", "17. RPLIDAR A1 — 360° scan", "18. RPLIDAR A2 — fast scan", "19. RPLIDAR C1 — compact DTOF", "20. DonkeyCar Rover — self-driving"]
rr([64, y, 784, y+385], CARD, BORDER); rr([816, y, 1536, y+385], CARD, BORDER)
for i, t in enumerate(hl): d.text((88, y+14+i*36), t, font=F(24), fill=WHITE)
for i, t in enumerate(hr): d.text((840, y+14+i*36), t, font=F(24), fill=WHITE)
y += 407
# modules
y = section(y, "THE MODULES  M0 – M13")
ml = ["M0  Lab Rules, Consent, Audit", "M1  Kali + Project 25", "M2  Spectrum — HackRF + Kraken", "M3  Cards — Flipper + Proxmark", "M4  Bluetooth — Ubertooth", "M5  Chips — ChipWhisperer", "M6  Mesh — Watch + T-Beam + Acer"]
mr = ["M7  Vision — Glasses + OpenMV", "M8  Bridge — GreatFET + REA", "M9  Brain / Voice — VoiceStudio", "M10  Capstone — all eleven talking", "M11  Aerial — drone", "M12  Motion + Night — IR, thermal", "M13  Space + Mapping — LiDAR, rover"]
rr([64, y, 784, y+275], CARD, BORDER); rr([816, y, 1536, y+275], CARD, BORDER)
for i, t in enumerate(ml): d.text((88, y+14+i*36), t, font=F(24), fill=WHITE)
for i, t in enumerate(mr): d.text((840, y+14+i*36), t, font=F(24), fill=WHITE)
y += 297
# banner
rr([64, y, 1536, y+118], GOLD, None, 18)
y = center(y+14, "PROJECT 25 — PROVE THE ENTIRE SUITE", F(30, True), BG)
y = center(y-2, "21 family checkpoints  •  Own lab targets only  •  Evidence logged  •  No faked passes", F(22), BG)
y += 18
# footer wrapped
lines = wrap("Your device in this course: M1 iPad Pro with LiDAR — scan, export, measure against ground truth.", F(25, True), 1472)
for ln in lines: y = center(y, ln, F(25, True))
lines = wrap("Own devices only. Consenting adults only. Everything in a controlled lab. Break it in the lab, so you can prevent it in the real world.", F(24), 1472)
for ln in lines: y = center(y, ln, F(24), LIGHT)
lines = wrap("Open source hardware is key: if you can see it, audit it, document it and log it — only then can you prevent it.", F(22), 1472)
for ln in lines: y = center(y, ln, F(22), MUTED)
print("final y", y, "canvas", H)
img.save("/home/hatch/workspace/your_files/course-poster.jpg", quality=92)
print("saved")

# @basementjarvisu · basementjarvisunleashed@gmail.com
