#include <ArduinoJson.h>
#include <Preferences.h>
#include <RadioLib.h>
#include <U8g2lib.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <WiFi.h>
#include <Wire.h>

#include "arduino_secrets.h"
#include "html_page.h"

#define PING_INTERVAL 5000

// --- SETTINGS ---
const char* ssid = SSID;
const char* password = PASSWORD;

Preferences preferences;

// Heltec V2 LoRa (SX1276) pins: NSS=18, DIO0=26, NRST=14, DIO1=35
SX1276 radio = new Module(18, 26, 14, 35);

// Heltec V2 OLED pins: SCL=15, SDA=4, Reset=16
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, 16, 15, 4);

WebSocketsServer webSocket = WebSocketsServer(81);
WebServer server(80);

String statusA = "-";
String statusB = "-";

unsigned long lastPingTime = 0;
bool isRadioBusy = false;  // allows only one request at a time to the mast unit

int currentTxPower = 2;  // Global variable for transmit power

// --- DISPLAY UPDATE ---
void updateDisplay() {
  u8g2.clearBuffer();

  // Title and IP
  u8g2.setFont(u8g2_font_6x10_tf);
  u8g2.drawStr(0, 10, "OH8KVA 2x6 MATRIX");
  u8g2.drawStr(0, 22, ("IP: " + WiFi.localIP().toString()).c_str());
  u8g2.drawHLine(0, 26, 128);  // Divider line

  // RIG A column
  u8g2.setFont(u8g2_font_6x10_tf);
  u8g2.drawStr(5, 40, "RIG A");
  u8g2.setFont(u8g2_font_ncenB14_tr);
  u8g2.drawStr(15, 60, statusA.c_str());

  // Vertical divider between rigs
  u8g2.drawVLine(64, 30, 34);

  // RIG B column
  u8g2.setFont(u8g2_font_6x10_tf);
  u8g2.drawStr(75, 40, "RIG B");
  u8g2.setFont(u8g2_font_ncenB14_tr);
  u8g2.drawStr(85, 60, statusB.c_str());

  u8g2.sendBuffer();
}

void handleMastoResponse(const uint8_t* rxData) {
  // 1. Parse binary data (bytes 0-6)
  statusA = String((char)rxData[0]);
  statusB = String((char)rxData[1]);
  int cmdStatus = rxData[2] - '0';
  int i2cStatus = rxData[3] - '0';
  int16_t mastRssi = (int16_t)((rxData[4] << 8) | rxData[5]);
  int8_t mastSnr = (int8_t)rxData[6];

  // 2. Update OLED display immediately
  updateDisplay();

  // 3. Build JSON for browsers
  JsonDocument doc;
  doc["a"] = statusA;
  doc["b"] = statusB;
  doc["cmds"] = cmdStatus;
  doc["i2cs"] = i2cStatus;
  doc["rssi"] = mastRssi;
  doc["snr"] = mastSnr;
  doc["lrssi"] = radio.getRSSI();
  doc["pwr"] = currentTxPower;

  String json;
  serializeJson(doc, json);
  webSocket.broadcastTXT(json);
}

bool sendToMasto(String cmd) {
  isRadioBusy = true;

  // Check if the command is just a number (02, 10, 17...)
  if (cmd.length() == 2 && isDigit(cmd[0]) && isDigit(cmd[1])) {
    int pwr = cmd.toInt();
    if (pwr >= 2 && pwr <= 17) {
      if (pwr != currentTxPower) {
        currentTxPower = pwr;
        radio.setOutputPower(currentTxPower);

        // Save permanently
        preferences.putInt("txPower", currentTxPower);
        Serial.print("Teho päivitetty ja tallennettu: ");
        Serial.println(currentTxPower);
      }
    }
  }

  // 1. Transmit
  if (radio.transmit(cmd) != RADIOLIB_ERR_NONE) {
    isRadioBusy = false;
    return false;
  }

  // 2. Receive
  uint8_t rxData[7];
  if (radio.receive(rxData, 7) == RADIOLIB_ERR_NONE) {
    handleMastoResponse(rxData);
    isRadioBusy = false;
    return true;
  }

  // 3. Error case: no response received (timeout or CRC error)
  statusA = "NC";
  statusB = "NC";
  updateDisplay();
  webSocket.broadcastTXT("{\"error\":\"Masto Offline\"}");

  isRadioBusy = false;
  return false;
}

void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload,
                    size_t length) {
  if (type == WStype_TEXT && !isRadioBusy) {
    sendToMasto((char*)payload);
  }
}

void initMastoPwr() {
  char pwrCmd[3];
  sprintf(pwrCmd, "%02d", currentTxPower);
  sendToMasto(String(pwrCmd));
}

void setup() {
  Serial.begin(115200);

  // OLED init
  u8g2.begin();
  u8g2.setFont(u8g2_font_6x10_tf);
  u8g2.clearBuffer();
  u8g2.drawStr(0, 12, "Reading settings...");
  u8g2.sendBuffer();

  // Open "settings" section (false = read/write mode)
  preferences.begin("settings", false);

  // Read power, default is 2 if nothing is saved
  currentTxPower = preferences.getInt("txPower", 2);
  Serial.print("Startup. Using power: ");
  Serial.println(currentTxPower);

  // WiFi connection
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nIP: " + WiFi.localIP().toString());

  int state = radio.begin(
      868.0,  // Carrier frequency in MHz. Allowed values range from 137.0 MHz
              // to 1020.0 MHz
      125.0,  // link bandwidth in kHz. Allowed values
              // are 7.8, 10.4, 15.6, 20.8, 31.25, 41.7, 62.5, 125, 250 and 500
              // kHz.
      9,      // link spreading factor. Allowed values range from 6 to 12.
      5,      // link coding rate denominator. Allowed values range from 4 to 8.
              // Note that a value of 4 means no coding, is undocumented and not
              // recommended without your own FEC.
      0x12,   // sync word. Can be used to distinguish different networks. Note
              // that value 0x34 is reserved for LoRaWAN networks.
      currentTxPower,  // power Transmission output power in dBm. Allowed values
                       // range from 2 to 17 dBm.
      8,  // preambleLength Length of %LoRa transmission preamble in symbols.
          // The actual preamble length is 4.25 symbols longer than the set
          // number. Allowed values range from 6 to 65535.
      0   // gain Gain of receiver LNA (low-noise amplifier). Can be set to any
          // integer in range 1 to 6 where 1 is the highest gain. Set to 0 to
          // enable automatic gain control (recommended).
  );
  radio.setCRC(true);
  radio.invertIQ(false);

  // HTTP and WebSocket
  server.on("/", []() { server.send(200, "text/html", htmlPage); });
  server.begin();

  webSocket.begin();
  webSocket.onEvent(webSocketEvent);

  delay(100);
  initMastoPwr();

  updateDisplay();
}

void loop() {
  webSocket.loop();
  server.handleClient();

  unsigned long now = millis();
  if (now - lastPingTime > PING_INTERVAL) {
    lastPingTime = now;
    if (!isRadioBusy) sendToMasto("PN");
  }
}