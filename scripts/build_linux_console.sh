#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
CFG_BACKUP="$PROJECT_ROOT/config.backup.json"

if [[ -f "dist/remote_switch_console/config.json" ]]; then
  cp -f "dist/remote_switch_console/config.json" "$CFG_BACKUP"
fi

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

pyinstaller --clean --noconfirm remote_switch_console.spec

if [[ -f "$CFG_BACKUP" ]]; then
  mkdir -p "dist/remote_switch_console"
  cp -f "$CFG_BACKUP" "dist/remote_switch_console/config.json"
  rm -f "$CFG_BACKUP"
fi
