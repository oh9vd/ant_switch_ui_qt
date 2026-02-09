from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable


def configure_logging(level: str, console: bool = True, file_path: str | None = None) -> None:
    handlers: list[logging.Handler] = []

    if console:
        handlers.append(logging.StreamHandler())

    if file_path:
        path = Path(file_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(path, encoding="utf-8"))

    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers or None,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
