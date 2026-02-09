# Remote Switch (LoRa and WbSocket)

Remote antenna switch system for two rigs and up to six antennas. This repo contains:

- LoRa bridge firmware (Heltec V2) and mast unit firmware (RAK11300).
- A Qt UI (PySide6) that controls the bridge over WebSocket.

## Repository layout

- `lora/bridge-unit` - Heltec V2 LoRa + WiFi bridge firmware.
- `lora/mast-unit` - RAK11300 mast controller firmware.
- `ui` - Qt UI application (PySide6) and build scripts.

## Quickstart (UI)

1. Create a virtual environment.
   - Windows: `python -m venv .venv` then `.venv\Scripts\activate`
   - Linux/macOS: `python -m venv .venv` then `source .venv/bin/activate`
2. Install dependencies: `pip install -r ui/requirements.txt`
3. Run the app: `python ui/src/app/main.py`

## Configuration

The UI reads settings from `ui/config.json`. See [ui/README.md](ui/README.md) for the full config schema and examples.

## Building the UI

Use the build scripts in `ui/scripts`.

- Windows: `ui/scripts/build_windows.cmd`
- Linux: `ui/scripts/build_linux.sh`

## Firmware

Open the `.ino` files in Arduino IDE:

- `lora/bridge-unit/bridge-unit.ino`
- `lora/mast-unit/mast-unit.ino`

Copy `lora/bridge-unit/arduino_secrets.TEMPLATE.h` to `arduino_secrets.h` and fill in your credentials.

## Documentation

Detailed architecture, message formats, and UI internals are documented in [ui/README.md](ui/README.md).

## License

MIT. See [LICENSE](LICENSE).
