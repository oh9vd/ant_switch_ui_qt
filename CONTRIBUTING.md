# Contributing

Thanks for your interest in contributing.

## Ways to help

- Report bugs and provide reproduction steps.
- Suggest features or improvements.
- Submit pull requests for fixes and enhancements.

## Development setup (UI)

1. Create a virtual environment.
   - Windows: `python -m venv .venv` then `.venv\\Scripts\\activate`
   - Linux/macOS: `python -m venv .venv` then `source .venv/bin/activate`
2. Install dependencies: `pip install -r ui/requirements.txt`
3. Run the app: `python ui/src/app/main.py`

## Development setup (firmware)

- Bridge unit: open `lora/bridge-unit/bridge-unit.ino` in Arduino IDE.
- Mast unit: open `lora/mast-unit/mast-unit.ino` in Arduino IDE.
- Create `lora/bridge-unit/arduino_secrets.h` from `arduino_secrets.TEMPLATE.h`.

## Testing

There is no automated test suite yet. Before submitting a PR:

- Run `python -m compileall ui/src`.
- Verify the UI connects to your bridge and responds to status updates.

## Pull request checklist

- Keep changes focused and scoped.
- Update documentation if behavior changes.
- Add or update config examples if needed.

## Code of Conduct

This project follows the code of conduct in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
