# Bridge unit

This unit has LoRa radio to communicate with Mast unit and WiFi interface to communicate with other Ham Radio software.

## Arduino Build

- **Board**: [Heltec WiFi LoRa 32(V2)](https://resource.heltec.cn/download/package_heltec_esp32_index.json)

## Files

- `bridge-uini.ino`: The main program
- `html_page.h`: Simple html page for switching antenas and set the Mast and Bridge transmit power. (using raw DOM interface)
- `arduino_secrets.TEMPLATE.h`: Example file for setting the WiFi SSID and Password. Copy this file to `arduino_secrets.h` and set the your SSID and PASSWORD.