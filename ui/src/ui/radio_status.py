from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal

from core.radio_info import RadioInfo, Rig


class RadioStatus(QObject):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._a_freq = 0
        self._b_freq = 0

    def update_from_radio_info(self, info: RadioInfo) -> None:
        updated = False

        if info.radio == Rig.A and self._a_freq != info.freq:
            self._a_freq = info.freq
            updated = True
        elif info.radio == Rig.B and self._b_freq != info.freq:
            self._b_freq = info.freq
            updated = True

        if updated:
            self.changed.emit()

    aFreq = Property(int, lambda self: self._a_freq, notify=changed)
    bFreq = Property(int, lambda self: self._b_freq, notify=changed)
