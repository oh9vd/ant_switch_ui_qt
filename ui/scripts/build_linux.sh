#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
CFG_BACKUP="$PROJECT_ROOT/config.backup.json"
DIST_BASE="$PROJECT_ROOT/dist/linux"
DIST_APP="$DIST_BASE/remote_switch"

if [[ -f "$DIST_APP/config.json" ]]; then
  cp -f "$DIST_APP/config.json" "$CFG_BACKUP"
fi

mkdir -p "$DIST_BASE"

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

export APP_GIT_COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf "%s" "$APP_GIT_COMMIT" > version.txt

pyinstaller --clean --noconfirm --distpath "$DIST_BASE" --workpath "$PROJECT_ROOT/build/linux" remote_switch.spec

rm -f version.txt

if [[ -f "$CFG_BACKUP" ]]; then
  mkdir -p "$DIST_APP"
  cp -f "$CFG_BACKUP" "$DIST_APP/config.json"
  rm -f "$CFG_BACKUP"
fi

ARCHIVE_BASE="$DIST_BASE/remote_switch-${APP_GIT_COMMIT}-linux"
if [[ -d "$DIST_APP" ]]; then
  if command -v 7z >/dev/null 2>&1; then
    7z a -t7z "$ARCHIVE_BASE.7z" "$DIST_APP" >/dev/null
  fi
  if command -v tar >/dev/null 2>&1 && command -v gzip >/dev/null 2>&1; then
    tar -czf "$ARCHIVE_BASE.tar.gz" -C "$DIST_BASE" "remote_switch"
  fi
fi
