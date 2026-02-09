#include <Arduino.h>
#include "LoRaWan-Arduino.h"
#include <SPI.h>
#include <Wire.h>

// --- ASETUKSET ---
#define RF_FREQUENCY 868000000
#define TX_OUTPUT_POWER 2
#define LORA_SPREADING_FACTOR 9
#define LORA_BANDWIDTH 0
#define LORA_CODINGRATE 1
#define LORA_PREAMBLE_LENGTH 8

#define MCP_ADDR 0x20
#define IODIRA 0x00
#define IODIRB 0x01
#define GPIOA 0x12
#define GPIOB 0x13

#define I2C_SUCCESS 0
#define COMMAND_SUCCESS 0
#define COMMAND_UNREGOCNIZED 1
#define COMMAND_INVALID_RIG 2
#define COMMAND_INVALID_ANTENNA 3
#define COMMAND_ANTENNA_CONFLICT 4
#define COMMAND_PWR_OUT_OF_RANGE 5
#define HEARTBEAT_TIMEOUT 20000
#define FLASH_DURATION 250
#define INVALID_ANTENNA 0xff

// --- MUUTTUJAT ---
uint8_t antA = 0;
uint8_t antB = 0;
uint8_t commandStatus = 0;
uint8_t i2cStatus = 0;
int16_t rssi;
int8_t snr;

unsigned long lastHeartbeatReceived = 0;
unsigned long lastBlueFlash = 0;

static RadioEvents_t RadioEvents;

uint8_t setMcp(uint8_t reg, uint8_t antNum) {
  // Lasketaan bittimaski: 1 -> 0x02, 2 -> 0x03, 3 -> 0x04... 0 -> 0x00
  uint8_t mask = (antNum > 0) ? (1 << antNum) : 0;

  Wire.beginTransmission(MCP_ADDR);
  Wire.write(reg);
  Wire.write(mask);
  return Wire.endTransmission();
}

void sendResponse() {
  uint8_t response[7];
  response[0] = (antA == 0) ? '-' : antA + '0';  // Arvo '0'-'6' (- = OFF, '1' = Ant1, jne.)
  response[1] = (antB == 0) ? '-' : antB + '0';  // Arvo '0'-'6'
  response[2] = commandStatus + '0';             // status of last command
  response[3] = i2cStatus + '0';
  response[4] = (rssi >> 8) & 0xff;
  response[5] = rssi & 0xff;
  response[6] = snr;

  Radio.Send(response, sizeof(response));
  Serial.print("Sanoma kuittaus ");
  for (int i = 0; i < sizeof(response); i++)
    Serial.printf("%02X ", response[i]); 
  Serial.println();

}

inline uint8_t parseAnt(uint8_t ant) {
  return (ant == '-')                 ? 0
         : (ant >= '1' && ant <= '6') ? ant - '0'
                                      : INVALID_ANTENNA;
}

void txConfig(int pwr) {
  Radio.SetTxConfig(
    MODEM_LORA,             // Radio modem to be used [0: FSK, 1: LoRa]
    pwr,                    // Sets the output power [dBm]
    0,                      // Sets the frequency deviation (FSK only) FSK : [Hz] LoRa: 0
    LORA_BANDWIDTH,         // Sets the bandwidth (LoRa only) FSK : 0 LoRa: [0: 125 kHz, 1: 250 kHz, 2: 500 kHz, 3: Reserved]
    LORA_SPREADING_FACTOR,  // Sets the Datarate FSK : 600..300000 bits/s LoRa: [6: 64, 7: 128, 8: 256, 9: 512, 10: 1024, 11: 2048, 12: 4096 chips]
    LORA_CODINGRATE,        // Sets the coding rate (LoRa only) FSK : N/A ( set to 0 ) LoRa: [1: 4/5, 2: 4/6, 3: 4/7, 4: 4/8]
    LORA_PREAMBLE_LENGTH,   // Sets the preamble length FSK : Number of bytes LoRa: Length in symbols (the hardware adds 4 more symbols)
    false,                  // Fixed length packets [0: variable, 1: fixed]
    true,                   // Enables disables the CRC [0: OFF, 1: ON]
    0,                      // Enables disables the intra-packet frequency hopping FSK : N/A ( set to 0 ) LoRa: [0: OFF, 1: ON]
    0,                      // Number of symbols between each hop FSK : N/A ( set to 0 ) LoRa: Number of symbols
    false,                  // Inverts IQ signals (LoRa only) FSK : N/A ( set to 0 ) LoRa: [0: not inverted, 1: inverted]
    3000                    // Transmission timeout [ms]
  );  
}

// --- KOMENTOJEN KÄSITTELY ---
void processCommand(uint8_t *payload, uint16_t size) {
  // oletetaan että komento on ok
  commandStatus = COMMAND_SUCCESS;

  if (size != 2) {
    commandStatus = COMMAND_UNREGOCNIZED;
  } else if (isDigit(payload[0]) && isDigit(payload[1])) {
    int pwr = (payload[0] - '0') * 10 + (payload[1] - '0');
    if (pwr < 2 || pwr > 17) {
      commandStatus = COMMAND_PWR_OUT_OF_RANGE;
    } else {
      // Päivitetään RAK:n radion tehoasetus
      txConfig(pwr);
    }
  } else if (payload[0] == 'A') {
    // A ANT
    uint8_t antNum = parseAnt(payload[1]);
    if (antNum == INVALID_ANTENNA) {
      commandStatus = COMMAND_INVALID_ANTENNA;
    } else if (antA != antNum && (antNum != antB || antNum == 0)) {
      i2cStatus = setMcp(GPIOA, antNum);
      if (i2cStatus == I2C_SUCCESS) {
        antA = antNum;
      }
    } else {
      commandStatus = COMMAND_ANTENNA_CONFLICT;
    }
  } else if (payload[0] == 'B') {
    uint8_t antNum = parseAnt(payload[1]);
    if (antNum == INVALID_ANTENNA) {
      commandStatus = COMMAND_INVALID_ANTENNA;
    } else if (antB != antNum && (antNum != antA || antNum == 0)) {
      i2cStatus = setMcp(GPIOB, antNum);
      if (i2cStatus == I2C_SUCCESS) {
        antB = antNum;
      }
    } else {
      commandStatus = COMMAND_ANTENNA_CONFLICT;
    }
  } else if (payload[0] == 'P' && payload[1] == 'N') {
    // PING
  } else {
    commandStatus = COMMAND_UNREGOCNIZED;
  }

  sendResponse();
}

void OnRxDone(uint8_t *payload, uint16_t size, int16_t _rssi, int8_t _snr) {
  digitalWrite(LED_BLUE, HIGH);  // Välähdys alkaa  
  Serial.print("Sanoma saatu ");
  for (int i = 0; i < size; i++)
    Serial.printf("%02X ", payload[i]); 
  Serial.println();
  rssi = _rssi;
  snr = _snr;
  processCommand(payload, size);
  lastBlueFlash = lastHeartbeatReceived = millis();
}

void setup() {
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  digitalWrite(LED_GREEN, HIGH);
  Serial.begin(115200);
  while (!Serial && millis() < 3000) delay(10);  // Odota, että USB-yhteys on valmis

  Serial.println("--- MASTO START ---");

  // 1. Alustetaan pinnit heti
  digitalWrite(LED_BLUE, HIGH);

  // RAK11300:n radion kova resetointi
  lora_rak11300_init();

  // 2. I2C (pidetään yksinkertaisena)
  Wire.begin();
  Wire.setClock(100000);
  setMcp(IODIRA, 0x00);
  setMcp(IODIRB, 0x00);
  setMcp(GPIOA, 0);
  setMcp(GPIOB, 0);

  // 3. Radio - Lisätään pieni viive ennen initia
  delay(100);

  RadioEvents.RxDone = OnRxDone;
  RadioEvents.TxDone = []() {
    Radio.Rx(0);
  };
  RadioEvents.RxTimeout = []() {
    Radio.Rx(0);
  };
  RadioEvents.RxError = []() {
    Radio.Rx(0);
  };

  // ALUSTUS
  Radio.Init(&RadioEvents);

  // Annetaan hetki aikaa initin jälkeen ennen konfigurointia
  delay(100);

  Radio.SetChannel(RF_FREQUENCY);

  Radio.SetRxConfig(
    MODEM_LORA,             // modem Radio modem to be used [0: FSK, 1: LoRa]
    LORA_BANDWIDTH,         // bandwidth Sets the bandwidth FSK : >= 2600 and <= 250000 Hz LoRa: [0: 125 kHz, 1: 250 kHz, 2: 500 kHz, 3: Reserved]
    LORA_SPREADING_FACTOR,  // datarate Sets the Datarate FSK : 600..300000 bits/s LoRa: [6: 64, 7: 128, 8: 256, 9: 512, 10: 1024, 11: 2048, 12: 4096 chips]
    LORA_CODINGRATE,        // coderate Sets the coding rate ( LoRa only ) FSK : N/A ( set to 0 ) LoRa: [1: 4/5, 2: 4/6, 3: 4/7, 4: 4/8]
    0,                      // bandwidthAfc Sets the AFC Bandwidth ( FSK only ) FSK : >= 2600 and <= 250000 Hz LoRa: N/A ( set to 0 )
    LORA_PREAMBLE_LENGTH,   // preambleLen Sets the Preamble length ( LoRa only ) FSK : N/A ( set to 0 ) LoRa: Length in symbols ( the hardware adds 4 more symbols )
    0,                      // symbTimeout Sets the RxSingle timeout value FSK : timeout number of bytes LoRa: timeout in symbols
    false,                  //fixLen Fixed length packets [0: variable, 1: fixed]
    0,                      // payloadLen Sets payload length when fixed lenght is used
    true,                   // crcOn Enables/Disables the CRC [0: OFF, 1: ON]
    0,                      // freqHopOn Enables disables the intra-packet frequency hopping [0: OFF, 1: ON] (LoRa only)
    0,                      // hopPeriod Number of symbols bewteen each hop (LoRa only)
    false,                  // iqInverted Inverts IQ signals ( LoRa only ) FSK : N/A ( set to 0 ) LoRa: [0: not inverted, 1: inverted]
    true                    // rxContinuous Sets the reception in continuous mode [false: single mode, true: continuous mode]
  );

  txConfig(TX_OUTPUT_POWER);

  // 4. Onnistuminen!
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, LOW);
  Radio.Rx(0);

  lastHeartbeatReceived = millis();
}

void loop() {
  unsigned long now = millis();

  // --- RADION VAKUUTUS (TÄRKEÄ) ---
  // Pakotetaan radio takaisin RX-tilaan 2 sekunnin välein,
  // jos viestejä ei kuulu. Tämä korjaa jumiutumiset nopeasti.
  static unsigned long lastForceRx = 0;
  if (now - lastHeartbeatReceived > 2000) {  // Jos edellisestä on yli 2s
    if (now - lastForceRx > 2000) {          // Eikä olla juuri pakotettu
      Radio.Rx(0);
      lastForceRx = now;
      Serial.println("Radio pakotettu RX-tilaan"); 
    }
  }

  // --- VIHREÄ LED: Heartbeat-diagnostiikka ---
  if (now - lastHeartbeatReceived > HEARTBEAT_TIMEOUT) {
    // Heartbeat poikki: Vilkkuu 250ms syklissä
    digitalWrite(LED_GREEN, (now / FLASH_DURATION) % 2);
  } else {
    // Heartbeat OK: Jatkuva valo
    digitalWrite(LED_GREEN, HIGH);
  }

  // --- SININEN LED: Vastaanoton välähdys ---
  if (lastBlueFlash > 0 && (now - lastBlueFlash > FLASH_DURATION)) {
    digitalWrite(LED_BLUE, LOW);
    lastBlueFlash = 0;  // Nollataan, jotta ei sammuteta turhaan joka kierroksella
  }
}
