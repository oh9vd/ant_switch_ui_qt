from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal


class WsStatus(QObject):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._a = ""
        self._b = ""
        self._cmds = 0
        self._i2cs = 0
        self._rssi = 0
        self._snr = 0
        self._lrssi = 0
        self._pwr = 0

    def update_from_dict(self, data: dict) -> None:
        updated = False

        def set_if_changed(attr: str, value) -> None:
            nonlocal updated
            if getattr(self, attr) != value:
                setattr(self, attr, value)
                updated = True

        set_if_changed("_a", str(data.get("a", self._a)))
        set_if_changed("_b", str(data.get("b", self._b)))
        set_if_changed("_cmds", int(data.get("cmds", self._cmds)))
        set_if_changed("_i2cs", int(data.get("i2cs", self._i2cs)))
        set_if_changed("_rssi", int(data.get("rssi", self._rssi)))
        set_if_changed("_snr", int(data.get("snr", self._snr)))
        set_if_changed("_lrssi", int(data.get("lrssi", self._lrssi)))
        set_if_changed("_pwr", int(data.get("pwr", self._pwr)))

        if updated:
            self.changed.emit()

    a = Property(str, lambda self: self._a, notify=changed)
    b = Property(str, lambda self: self._b, notify=changed)
    cmds = Property(int, lambda self: self._cmds, notify=changed)
    i2cs = Property(int, lambda self: self._i2cs, notify=changed)
    rssi = Property(int, lambda self: self._rssi, notify=changed)
    snr = Property(int, lambda self: self._snr, notify=changed)
    lrssi = Property(int, lambda self: self._lrssi, notify=changed)
    pwr = Property(int, lambda self: self._pwr, notify=changed)
