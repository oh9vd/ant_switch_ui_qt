from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class AppSettings:
    theme: str
    ui_mode: str
    rig_a_name: str
    rig_b_name: str
    antennas: dict[str, str]
    ws_url: str
    ws_port: int
    udp_host: str
    udp_port: int
    log_level: str
    log_file: str | None
    log_console: bool
    auto_rules: list[dict[str, int | str]]


DEFAULTS_PATH = Path(__file__).with_name("defaults.json")


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_settings(overrides_path: Path | None = None) -> AppSettings:
    defaults = _load_json(DEFAULTS_PATH)
    overrides = _load_json(overrides_path) if overrides_path else {}
    merged: Dict[str, Any] = {**defaults}

    def deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in update.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                base[key] = deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    merged = deep_merge(merged, overrides)

    app_cfg = merged.get("app", {})
    log_cfg = merged.get("logging", {})
    ws_cfg = merged.get("wsConnection", {})
    udp_cfg = merged.get("udpConnection", {})
    rigs_cfg = merged.get("rigs", {})
    antennas_cfg = merged.get("antennas", {})
    auto_cfg = merged.get("autoSwitch", {})

    return AppSettings(
        theme=str(app_cfg.get("theme", "light")),
        ui_mode=str(app_cfg.get("ui", "qml")),
        rig_a_name=str(rigs_cfg.get("rigAName", "A")),
        rig_b_name=str(rigs_cfg.get("rigBName", "B")),
        antennas={
            "ant0Name": str(antennas_cfg.get("ant0Name", "OFF")),
            "ant1Name": str(antennas_cfg.get("ant1Name", "1")),
            "ant2Name": str(antennas_cfg.get("ant2Name", "2")),
            "ant3Name": str(antennas_cfg.get("ant3Name", "3")),
            "ant4Name": str(antennas_cfg.get("ant4Name", "4")),
            "ant5Name": str(antennas_cfg.get("ant5Name", "5")),
            "ant6Name": str(antennas_cfg.get("ant6Name", "6")),
        },
        ws_url=str(ws_cfg.get("url", "http://127.0.0.1/")),
        ws_port=int(ws_cfg.get("port", 81)),
        udp_host=str(udp_cfg.get("host", "127.0.0.1")),
        udp_port=int(udp_cfg.get("port", 9000)),
        log_level=str(log_cfg.get("level", "INFO")),
        log_file=log_cfg.get("file"),
        log_console=bool(log_cfg.get("console", True)),
        auto_rules=list(auto_cfg.get("antennaRules", [])),
    )
