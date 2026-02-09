from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET


class Rig(str, Enum):
    A = "A"
    B = "B"


@dataclass(frozen=True)
class RadioInfo:
    station_name: str
    radio_nr: int
    freq: int
    tx_freq: int
    mode: str
    op_call: str
    is_running: bool
    focus_entry: int
    antenna: int
    rotors: str
    focus_radio_nr: int
    is_stereo: bool
    active_radio_nr: int

    @property
    def radio(self) -> Rig:
        return Rig.A if self.radio_nr == 1 else Rig.B

    @property
    def focus_radio(self) -> Rig:
        return Rig.A if self.focus_radio_nr == 1 else Rig.B

    @property
    def active_radio(self) -> Rig:
        return Rig.A if self.active_radio_nr == 1 else Rig.B


TRUE_VALUES = {"1", "true", "yes", "on"}


def _to_bool(value: str) -> bool:
    return value.strip().lower() in TRUE_VALUES


def parse_radio_info(xml_payload: str) -> RadioInfo:
    root = ET.fromstring(xml_payload)

    def text(name: str, default: str = "") -> str:
        node = root.find(name)
        return node.text.strip() if node is not None and node.text is not None else default

    return RadioInfo(
        station_name=text("StationName"),
        radio_nr=int(text("RadioNr", "0")),
        freq=int(text("Freq", "0"))/100,
        tx_freq=int(text("TXFreq", "0"))/100,
        mode=text("Mode"),
        op_call=text("OpCall"),
        is_running=_to_bool(text("IsRunning", "false")),
        focus_entry=int(text("FocusEntry", "0")),
        antenna=int(text("Antenna", "0")),
        rotors=text("Rotors"),
        focus_radio_nr=int(text("FocusRadioNr", "0")),
        is_stereo=_to_bool(text("IsStereo", "false")),
        active_radio_nr=int(text("ActiveRadioNr", "0")),
    )
