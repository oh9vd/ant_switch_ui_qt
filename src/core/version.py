from __future__ import annotations

from pathlib import Path
import os
import subprocess

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


def get_version() -> str:
    env_hash = os.getenv("APP_GIT_COMMIT")
    if env_hash:
        return f"{BASE_VERSION}+{env_hash}"

    repo_root = Path(__file__).resolve().parents[2]
    short_hash = _git_short_hash(repo_root)
    if not short_hash:
        return f"{BASE_VERSION}+unknown"
    return f"{BASE_VERSION}+{short_hash}"
