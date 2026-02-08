from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys

BASE_VERSION = "1.0.0"


def _git_short_hash(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or None
    except Exception:
        return None


def _read_embedded_hash(repo_root: Path) -> str | None:
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "version.txt")
    candidates.append(repo_root / "version.txt")

    for path in candidates:
        try:
            if path.is_file():
                value = path.read_text(encoding="utf-8").strip()
                return value or None
        except Exception:
            continue
    return None


def get_version() -> str:
    env_hash = os.getenv("APP_GIT_COMMIT")
    if env_hash:
        return f"{BASE_VERSION}+{env_hash}"

    repo_root = Path(__file__).resolve().parents[2]
    embedded_hash = _read_embedded_hash(repo_root)
    if embedded_hash:
        return f"{BASE_VERSION}+{embedded_hash}"

    short_hash = _git_short_hash(repo_root)
    if not short_hash:
        return f"{BASE_VERSION}+unknown"
    return f"{BASE_VERSION}+{short_hash}"
