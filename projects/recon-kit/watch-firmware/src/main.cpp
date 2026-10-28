/*
 * Jarvis Off-Grid Watch Node  --  LILYGO T-Watch-S3 (SX1280 2.4 GHz)
 * Option B custom firmware SKELETON. Code-complete (UI, touch, haptics, HMAC LoRa, bearer, /health, AUTH); never compiled - PlatformIO not installed (needs HgX OK). RF params need on-hardware tuning. It is
 * NOT guaranteed to compile as-is until the display/touch library is wired in.
 *
 * What it does when finished:
 *   - Inits the ST7789 display + capacitive touch + SX1280 LoRa via RadioLib.
 *   - Shows a simple UI: link status, a few canned commands, and a text line.
 *   - On tap of a canned command, builds a JV1 frame (see PROTOCOL.md) and
 *     transmits it over LoRa to the laptop gateway node.
 *   - Receives reply frames, reassembles, shows them, and buzzes the motor.
 *
 * VERIFIED T-Watch-S3 pins (from espressif arduino-esp32 variant pins_arduino.h):
 *   Display ST7789: CS 12, DC 38, MOSI 13, SCK 18, RST -1, BL 45  (240x240)
 *   Touch: INT 16, I2C SDA 39, SCL 40
 *   LoRa SX1280: CS 5, RST 8, BUSY 7, IRQ/DIO1 9, SCK 3, MISO 4, MOSI 1
 *   Shared sensor/PMU/haptic I2C: SDA 10, SCL 11 (AXP2101, DRV2605, BMA423, PCF8563)
 */

#include <Arduino.h>
#include <RadioLib.h>
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ---- Recon Kit (glasses vision) ----
// Wi-Fi fast path: POST laptop-ingest /look directly. Credentials are NOT in
// source: they come from build flags (-DJV_WIFI_SSID=... in a local, gitignored
// secrets.ini) so nothing secret lands in this repo.
#ifndef JV_WIFI_SSID
#define JV_WIFI_SSID ""
#endif
#ifndef JV_WIFI_PASS
#define JV_WIFI_PASS ""
#endif
#ifndef JV_INGEST_URL
#define JV_INGEST_URL ""   // set via secrets.ini, e.g. http://<laptop-lan-ip>:8767/look (LAN bind needs approval)
#endif
#ifndef JV_INGEST_TOKEN
#error "JV_INGEST_TOKEN is REQUIRED: per-device bearer (one of laptop JV_INGEST_TOKENS) via -DJV_INGEST_TOKEN=\"...\" in secrets.ini"
#endif
#ifndef JV_HEALTH_URL
#define JV_HEALTH_URL ""   // e.g. http://<laptop-ip>:8767/health (LAN first; Tailscale IP if set as JV_HEALTH_URL_TS)
#endif
#ifndef JV_HEALTH_URL_TS
#define JV_HEALTH_URL_TS ""
#endif
#ifndef JV_INGEST_URL_TS
#define JV_INGEST_URL_TS ""
#endif
#include <TFT_eSPI.h>      // configured entirely by build_flags in platformio.ini (no User_Setup edits)
#define RECON_PREFIX "RC:"
#ifndef JV_LORA_KEY
#error "JV_LORA_KEY is REQUIRED (SAF): set -DJV_LORA_KEY=\"...\" in the gitignored secrets.ini"
#endif
static_assert(sizeof(JV_LORA_KEY) > 16, "JV_LORA_KEY must be at least 16 characters (SAF)");
#include "mbedtls/md.h"
#include <Preferences.h>

// Anti-replay counters (persisted in NVS): frame = JV1|id|t|seq|tot|payload|ctr|mac|crc
Preferences jvPrefs;
uint32_t txCtr = 0, rxCtr = 0;
void ctrLoad() { jvPrefs.begin("jvlora", false); txCtr = jvPrefs.getUInt("tx", 0) + 64; rxCtr = jvPrefs.getUInt("rx", 0);
                 jvPrefs.putUInt("tx", txCtr); }   // +64 jump: counter never reuses after an unsaved reboot
uint32_t ctrNextTx() { txCtr++; if ((txCtr & 63) == 0) jvPrefs.putUInt("tx", txCtr); return txCtr; }

// Truncated HMAC-SHA256 (8 hex) - mirrors jarvis_lora_bridge.frame_mac().
String frameMac(const String& body) {
  uint8_t out[32];
  const mbedtls_md_info_t* info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
  mbedtls_md_hmac(info, (const uint8_t*)JV_LORA_KEY, strlen(JV_LORA_KEY),
                  (const uint8_t*)body.c_str(), body.length(), out);
  char hex[9];
  snprintf(hex, sizeof(hex), "%02x%02x%02x%02x", out[0], out[1], out[2], out[3]);
  return String(hex);
}
bool macOn() { return true; }   // signing is mandatory

// Pending command (idempotent by msgid): retransmit until ACK/reply, 3 tries.
String pendId = "", pendFrame = "";
uint8_t pendTries = 0;
uint32_t pendAt = 0;
const uint32_t RETRY_MS[] = { 4000, 8000, 16000 };

// ---- LoRa SX1280 pins (T-Watch-S3) ----
#define PIN_LORA_CS    5
#define PIN_LORA_RST   8
#define PIN_LORA_BUSY  7
#define PIN_LORA_IRQ   9   // DIO1
#define PIN_LORA_SCK   3
#define PIN_LORA_MISO  4
#define PIN_LORA_MOSI  1

// ---- Display pins (ST7789) ----
#define PIN_TFT_CS    12
#define PIN_TFT_DC    38
#define PIN_TFT_MOSI  13
#define PIN_TFT_SCK   18
#define PIN_TFT_RST   -1
#define PIN_TFT_BL    45

// ---- Touch / shared I2C ----
#define PIN_TP_INT    16
#define PIN_TP_SDA    39
#define PIN_TP_SCL    40
#define PIN_SENS_SDA  10   // AXP2101 + DRV2605 + BMA423 + PCF8563
#define PIN_SENS_SCL  11

// ---- Protocol (mirror PROTOCOL.md) ----
#define JV_MAGIC   "JV1"
#define MAX_FRAME  200

// SX1280 uses a dedicated SPI bus on these pins. RadioLib Module:
//   new Module(cs, irq/dio1, rst, busy)
SX1280 radio = new Module(PIN_LORA_CS, PIN_LORA_IRQ, PIN_LORA_RST, PIN_LORA_BUSY);

// Canned commands shown on the UI.
const char* CANNED[] = { "recon", "status report", "recon:read the label", "who is home" };
const int   NUM_CANNED = sizeof(CANNED) / sizeof(CANNED[0]);

volatile bool rxFlag = false;
void setRxFlag() { rxFlag = true; }   // DIO1 ISR

uint16_t crc16_ccitt(const uint8_t* data, size_t len) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < len; i++) {
    crc ^= (uint16_t)data[i] << 8;
    for (int b = 0; b < 8; b++)
      crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : (crc << 1);
  }
  return crc;
}

String buildFrame(const String& msgid, char type, int seq, int total, const String& payload) {
  String body = String(JV_MAGIC) + "|" + msgid + "|" + String(type) + "|" +
                String(seq) + "|" + String(total) + "|" + payload;
  if (macOn()) { body += "|" + String(ctrNextTx(), HEX); body += "|" + frameMac(body); }
  uint16_t crc = crc16_ccitt((const uint8_t*)body.c_str(), body.length());
  char crcs[6];
  snprintf(crcs, sizeof(crcs), "%04x", crc);
  return body + "|" + String(crcs);
}

String nextMsgId() {                 // tiny rolling base36 id
  static uint32_t n = 0;
  n = (n + 1) % 1296;                // 36*36
  char buf[4];
  itoa((int)n, buf, 36);              // real base36 per PROTOCOL.md
  return String(buf);
}

#include <Adafruit_DRV2605.h>
Adafruit_DRV2605 drv;
bool drvOk = false;
void buzz(uint16_t ms) {                 // DRV2605 on SENS bus (0x5A): short click vs long buzz
  if (!drvOk) return;
  drv.setWaveform(0, ms >= 300 ? 47 : ms >= 100 ? 1 : 10); drv.setWaveform(1, 0); drv.go();
}

// ---- Display / UI (ST7789 240x240 via TFT_eSPI, FT6336 touch @0x38 raw I2C) ----
TFT_eSPI tft;
TwoWire touchWire = TwoWire(1);
enum Link : uint8_t { LINK_NONE, LINK_WIFI, LINK_TS, LINK_LORA, LINK_AUTH };
Link link = LINK_NONE;
String uiLine = "";
bool uiDirty = true;
const char* linkName(Link l) {
  switch (l) { case LINK_WIFI: return "WIFI"; case LINK_TS: return "TAILNET"; case LINK_LORA: return "LORA";
               case LINK_AUTH: return "AUTH"; default: return "OFFLINE"; }
}
void uiDrawStatus(const char* line) { uiLine = line; uiDirty = true; Serial.print("[UI] "); Serial.println(line); }
void uiRender() {                    // called from loop(); redraws only when dirty
  if (!uiDirty) return; uiDirty = false;
  tft.fillScreen(TFT_BLACK);
  uint16_t lc = link == LINK_AUTH ? TFT_RED : link == LINK_LORA ? TFT_ORANGE : link == LINK_NONE ? TFT_DARKGREY : TFT_GREEN;
  tft.fillRoundRect(4, 4, 232, 26, 6, lc);
  tft.setTextColor(TFT_BLACK, lc); tft.setTextSize(2); tft.setCursor(12, 10); tft.print(linkName(link));
  if (link == LINK_AUTH) { tft.setTextSize(1); tft.setCursor(120, 14); tft.print("check token"); }
  tft.setTextColor(TFT_WHITE, TFT_BLACK); tft.setTextSize(1); tft.setCursor(6, 38);
  tft.print(uiLine.substring(0, 200));          // wraps automatically
  for (int i = 0; i < NUM_CANNED; i++) {        // 2x2 canned buttons, bottom half
    int x = 4 + (i % 2) * 118, y = 124 + (i / 2) * 56;
    tft.drawRoundRect(x, y, 114, 52, 8, TFT_CYAN); tft.setCursor(x + 6, y + 22); tft.print(CANNED[i]);
  }
}
int touchedButton() {                // FT6336: reg 0x02 = touch count, 0x03.. = XH XL YH YL
  static uint32_t last = 0;
  if (millis() - last < 350) return -1;          // debounce
  touchWire.beginTransmission(0x38); touchWire.write(0x02);
  if (touchWire.endTransmission(false) != 0 || touchWire.requestFrom(0x38, 5) != 5) return -1;
  uint8_t n = touchWire.read(), xh = touchWire.read(), xl = touchWire.read(), yh = touchWire.read(), yl = touchWire.read();
  if ((n & 0x0F) == 0) return -1;
  int x = ((xh & 0x0F) << 8) | xl, y = ((yh & 0x0F) << 8) | yl;
  if (y < 124) return -1;
  last = millis();
  int i = (x >= 120 ? 1 : 0) + (y >= 180 ? 2 : 0);
  return i < NUM_CANNED ? i : -1;
}
void showResult(const String& msgid, const String& text) {
  if (text.startsWith(RECON_PREFIX)) {
    // Recon card: distinct triple buzz + "EYES" header so HgX knows it is vision.
    uiDrawStatus(("[EYES " + msgid + "] " + text.substring(3)).c_str());
    buzz(60); delay(80); buzz(60); delay(80); buzz(60);
  } else {
    uiDrawStatus(text.c_str());
    buzz(120);
  }
}

// Endpoint choice by GET /health only: LAN, then Tailscale. 401/403 => AUTH (fail closed, NO LoRa failover).
// Returns: 1 = picked (url set), 0 = network unreachable (LoRa failover allowed), -1 = AUTH.
int pickWifiEndpoint(String& lookUrl) {
  if (WiFi.status() != WL_CONNECTED) return 0;
  const char* health[] = { JV_HEALTH_URL, JV_HEALTH_URL_TS };
  const char* look[]   = { JV_INGEST_URL, JV_INGEST_URL_TS };
  for (int i = 0; i < 2; i++) {
    if (strlen(health[i]) == 0 || strlen(look[i]) == 0) continue;
    HTTPClient h; h.setTimeout(6000);
    if (!h.begin(health[i])) continue;
    h.addHeader("Authorization", String("Bearer ") + JV_INGEST_TOKEN);
    int c = h.GET(); h.end();
    if (c == 401 || c == 403) return -1;
    if (c == 200) { lookUrl = look[i]; link = i == 0 ? LINK_WIFI : LINK_TS; uiDirty = true; return 1; }
  }
  return 0;                                       // network errors only -> LoRa
}

// Wi-Fi fast path for recon. Returns true if handled (incl. AUTH, which must NOT fall back to LoRa).
bool reconOverWifi(const String& id, const String& cmd) {
  String url;
  int pick = pickWifiEndpoint(url);
  if (pick < 0) { link = LINK_AUTH; uiDrawStatus("AUTH - ingest refused token"); buzz(400); return true; }
  if (pick == 0) return false;                    // network -> LoRa
  String prompt = cmd.indexOf(':') > 0 ? cmd.substring(cmd.indexOf(':') + 1) : "";
  prompt.replace("\\", " "); prompt.replace("\"", "'");
  HTTPClient http;
  http.setTimeout(45000);                         // caller budget 45 s > ingest 30 s (nested)
  if (!http.begin(url)) return false;
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", String("Bearer ") + JV_INGEST_TOKEN);
  uiDrawStatus("recon: looking...");
  int code = http.POST("{\"v\":1,\"id\":\"" + id + "\",\"ts\":" + String(millis() / 1000) +
                       ",\"src\":\"watch\",\"kind\":\"cmd\",\"payload\":{\"prompt\":\"" + prompt + "\"}}");
  if (code == 401 || code == 403) { http.end(); link = LINK_AUTH; uiDrawStatus("AUTH - ingest refused token"); buzz(400); return true; }
  if (code <= 0) { http.end(); return false; }    // transport error -> LoRa
  if (code != 200) { http.end(); uiDrawStatus(("recon error " + String(code)).c_str()); return true; }  // server error: report, no failover
  String body = http.getString();
  http.end();
  int k = body.indexOf("\"short\":\"");
  if (k < 0) k = body.indexOf("\"text\":\""), k = k < 0 ? -1 : k - 1;
  String txt = k < 0 ? String("no result") : body.substring(k + 9, body.indexOf('"', k + 9));
  showResult(id, String(RECON_PREFIX) + txt);
  return true;
}
void sendCommand(const String& text) {
  String id = nextMsgId();
  if (text.startsWith("recon") && reconOverWifi(id, text)) return;   // home: fast path
  // (Chunk if text > frame budget; canned commands are short, so assume 1.)
  String frame = buildFrame(id, 'C', 0, 1, text);
  int st = radio.transmit(frame);
  if (st == RADIOLIB_ERR_NONE) {
    if (link != LINK_AUTH) link = LINK_LORA;
    pendId = id; pendFrame = frame; pendTries = 0; pendAt = millis();
    uiDrawStatus(("PENDING " + id + ": " + text).c_str());   // shown until ack
    buzz(40);
  } else {
    uiDrawStatus(("TX err " + String(st)).c_str());
  }
  radio.startReceive();              // back to RX to await the reply
}

// Reassembly of a chunked reply (single logical message at a time for now).
String rxMsgId = "";
int    rxTotal = 0;
String rxParts[8];                   // TODO: size for your max reply chunks
int    rxHave = 0;

void handleFrame(const String& line) {
  // Expect: JV1|msgid|type|seq|total|payload|crc
  if (!line.startsWith(JV_MAGIC "|")) return;
  int lastBar = line.lastIndexOf('|');
  if (lastBar < 0) return;
  String body = line.substring(0, lastBar);
  String crcs = line.substring(lastBar + 1);
  uint16_t want = (uint16_t)strtol(crcs.c_str(), nullptr, 16);
  if (crc16_ccitt((const uint8_t*)body.c_str(), body.length()) != want) return; // drop
  if (macOn()) {                                   // fail closed on bad/missing MAC
    int mb = body.lastIndexOf('|');
    if (mb < 0 || body.substring(mb + 1) != frameMac(body.substring(0, mb))) return;
    body = body.substring(0, mb);
    int cb = body.lastIndexOf('|');                // monotonic counter -> replay window
    if (cb < 0) return;
    uint32_t c = strtoul(body.substring(cb + 1).c_str(), nullptr, 16);
    if (c <= rxCtr) return;                          // replayed / stale -> drop
    rxCtr = c; jvPrefs.putUInt("rx", rxCtr);
    body = body.substring(0, cb);
  }

  // split body into 6 fields
  String f[6]; int idx = 0, start = 0;
  for (int i = 0; i < body.length() && idx < 6; i++) {
    if (body[i] == '|') { f[idx++] = body.substring(start, i); start = i + 1; }
  }
  f[idx] = body.substring(start);     // payload (last; may contain nothing special)

  String msgid = f[1]; char type = f[2][0];
  int seq = f[3].toInt(); int total = f[4].toInt(); String payload = f[5];

  if ((type == 'A' || type == 'R') && msgid == pendId) pendId = "";   // acked
  if (type == 'R') {
    if (msgid != rxMsgId) { rxMsgId = msgid; rxTotal = total; rxHave = 0;
                            for (int i = 0; i < 8; i++) rxParts[i] = ""; }
    if (seq < 8 && rxParts[seq] == "") { rxParts[seq] = payload; rxHave++; }
    if (rxHave >= rxTotal) {
      String full = "";
      for (int i = 0; i < rxTotal && i < 8; i++) full += rxParts[i];
      showResult(msgid, full);        // recon card or normal reply
      rxMsgId = "";
    }
    // ACK each chunk per PROTOCOL.md (payload "msgid:seq").
    radio.transmit(buildFrame(msgid, 'A', seq, total, msgid + ":" + String(seq)));
    radio.startReceive();
  }
}

void setup() {
  Serial.begin(115200);

  // SPI bus for the SX1280.
  SPI.begin(PIN_LORA_SCK, PIN_LORA_MISO, PIN_LORA_MOSI, PIN_LORA_CS);

  // SX1280 is 2.4 GHz. Default to 2400.0 MHz; tune BW/SF/CR for range vs speed.
  // begin(freq, bw, sf, cr, syncWord, power, preambleLength)
  ctrLoad();                                     // anti-replay counters from NVS
  int st = radio.begin(2400.0, 812.5, 9, 7);   // TODO: tune these on hardware
  if (st != RADIOLIB_ERR_NONE) {
    Serial.printf("SX1280 begin failed: %d\n", st);
  }
  radio.setPacketReceivedAction(setRxFlag);     // DIO1 -> rxFlag
  radio.startReceive();

  tft.init(); tft.setRotation(0); pinMode(PIN_TFT_BL, OUTPUT); digitalWrite(PIN_TFT_BL, HIGH);
  touchWire.begin(PIN_TP_SDA, PIN_TP_SCL, 400000);
  drvOk = drv.begin(&Wire); if (drvOk) drv.selectLibrary(1);   // AXP2101 rails default-on on T-Watch-S3
  Wire.begin(PIN_SENS_SDA, PIN_SENS_SCL);       // sensor/PMU/haptic bus
  // Home Wi-Fi if configured (non-blocking; LoRa works regardless).
  if (strlen(JV_WIFI_SSID) > 0) { WiFi.mode(WIFI_STA); WiFi.begin(JV_WIFI_SSID, JV_WIFI_PASS); }
  uiDrawStatus("Jarvis Recon Kit ready");
}

void loop() {
  static uint32_t lastHealth = 0;
  if (millis() - lastHealth > 30000 && link != LINK_AUTH) { lastHealth = millis(); String u; int p = pickWifiEndpoint(u);
    if (p < 0) { link = LINK_AUTH; uiDrawStatus("AUTH - ingest refused token"); } else if (p == 0 && link != LINK_LORA) { link = LINK_NONE; uiDirty = true; } }
  int b = touchedButton();
  if (b >= 0) sendCommand(CANNED[b]);
  uiRender();

  if (pendId.length() && millis() - pendAt > RETRY_MS[pendTries < 3 ? pendTries : 2]) {
    if (pendTries >= 3) {
      uiDrawStatus(("FAILED " + pendId + " - no ack").c_str()); buzz(400);   // fail loud
      Serial.printf("{\"event\":\"cmd_failed\",\"id\":\"%s\"}\n", pendId.c_str());
      pendId = "";
    } else {
      radio.transmit(pendFrame); radio.startReceive();
      pendTries++; pendAt = millis();
    }
  }

  if (rxFlag) {
    rxFlag = false;
    String in;
    int st = radio.readData(in);
    if (st == RADIOLIB_ERR_NONE) handleFrame(in);
    radio.startReceive();
  }
  delay(5);
}
