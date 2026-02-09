from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.radio_info import RadioInfo


@dataclass
class AppState:
    connected: bool = False
    last_message: str = ""
    radio_info: Optional[RadioInfo] = None
