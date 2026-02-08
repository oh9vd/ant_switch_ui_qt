from __future__ import annotations

import json

from PySide6.QtCore import QObject, Property, Signal, Slot

from core.app_controller import AppController
from core.logging_setup import get_logger
from core.radio_info import Rig, RadioInfo
from ui.radio_status import RadioStatus
from ui.ws_status import WsStatus


class QmlBridge(QObject):
    statusChanged = Signal()
    statusMessageChanged = Signal()
    busyChanged = Signal()
    autoAChanged = Signal()
    autoBChanged = Signal()

    def __init__(self, controller: AppController) -> None:
        super().__init__()
        self._controller = controller
        self._status = "Disconnected"
        self._status_message = "Disconnected"
        self._busy = False
        self._auto_a = False
        self._auto_b = False
        self._logger = get_logger(self.__class__.__name__)
        self._ws_status = WsStatus()
        self._radio_status = RadioStatus()
        self._auto_rules = controller.settings.auto_rules
        self._controller.set_ws_message_listener(self._handle_ws_message)
        self._controller.set_ws_error_listener(self._handle_ws_error)
        self._controller.set_ws_disconnect_listener(self._handle_ws_disconnected)
        self._controller.set_ws_send_failed_listener(self._handle_ws_send_failed)
        self._controller.set_udp_info_listener(self._handle_udp_info)

    @Slot(str)
    def sendText(self, text: str) -> None:
        message = text.strip()
        if not message:
            return
        self._controller.send_text(message)

    @Slot(str, int)
    def selectAntenna(self, rig: str, value: int) -> None:
        self._select_antenna_internal(rig, value)

    def _get_status(self) -> str:
        return self._status

    def _set_status(self, value: str) -> None:
        if self._status == value:
            return
        self._status = value
        self.statusChanged.emit()

    status = Property(str, _get_status, _set_status, notify=statusChanged)

    def _get_status_message(self) -> str:
        return self._status_message

    def _set_status_message(self, value: str) -> None:
        if self._status_message == value:
            return
        self._status_message = value
        self.statusMessageChanged.emit()

    statusMessage = Property(str, _get_status_message, _set_status_message, notify=statusMessageChanged)

    def _get_busy(self) -> bool:
        return self._busy

    def _set_busy(self, value: bool) -> None:
        if self._busy == value:
            return
        self._busy = value
        self.busyChanged.emit()

    busy = Property(bool, _get_busy, _set_busy, notify=busyChanged)

    def _get_auto_a(self) -> bool:
        return self._auto_a

    def _set_auto_a(self, value: bool) -> None:
        if self._auto_a == value:
            return
        self._auto_a = value
        self.autoAChanged.emit()

    autoA = Property(bool, _get_auto_a, _set_auto_a, notify=autoAChanged)

    def _get_auto_b(self) -> bool:
        return self._auto_b

    def _set_auto_b(self, value: bool) -> None:
        if self._auto_b == value:
            return
        self._auto_b = value
        self.autoBChanged.emit()

    autoB = Property(bool, _get_auto_b, _set_auto_b, notify=autoBChanged)

    def _handle_ws_message(self, message: str) -> None:
        try:
            data = json.loads(message)
        except json.JSONDecodeError as exc:
            self._logger.warning("Invalid JSON message: %s", exc)
            return
        if isinstance(data, dict):
            self._ws_status.update_from_dict(data)
            self._set_busy(False)
            self._set_status_message("OK")

    def _handle_ws_error(self, error: str) -> None:
        self._logger.warning("WebSocket error: %s", error)
        self._set_busy(False)
        self._set_status_message(error)

    def _handle_ws_disconnected(self) -> None:
        self._set_busy(False)
        self._set_status_message("Disconnected")

    def _handle_ws_send_failed(self, reason: str) -> None:
        self._logger.warning("WebSocket send failed: %s", reason)
        self._set_busy(False)
        self._set_status_message(f"Send failed: {reason}")

    @Property(QObject, constant=True)
    def wsStatus(self) -> WsStatus:
        return self._ws_status

    def _handle_udp_info(self, info) -> None:
        self._radio_status.update_from_radio_info(info)
        if isinstance(info, RadioInfo):
            self._apply_auto_rule(info)

    @Property(QObject, constant=True)
    def radioStatus(self) -> RadioStatus:
        return self._radio_status

    def _apply_auto_rule(self, info: RadioInfo) -> None:
        if self._busy:
            return
        if info.radio == Rig.A and not self._auto_a:
            return
        if info.radio == Rig.B and not self._auto_b:
            return

        rule = self._select_rule(info.radio,info.freq)
        if rule is None:
            return

        primary = int(rule.get("primaryAntenna", 0))
        secondary = int(rule.get("secondaryAntenna", 0))
        selected = primary

        other = self._current_antenna(Rig.B if info.radio == Rig.A else Rig.A)
        if other == str(primary):
            selected = secondary

        current = self._current_antenna(info.radio)
        if current == str(selected):
            return

        self._select_antenna_internal(info.radio.value, selected)

    def _select_rule(self, rig: Rig, freq_khz: int) -> dict | None:
        for rule in self._auto_rules:
            if str(rule.get("rig", "")).upper() != rig.value:
                continue
            min_freq = int(rule.get("minFrequency", 0))
            max_freq = int(rule.get("maxFrequency", 0))
            if min_freq <= freq_khz < max_freq:
                return rule
        return None

    def _current_antenna(self, rig: Rig) -> str:
        return self._ws_status.a if rig == Rig.A else self._ws_status.b

    def _select_antenna_internal(self, rig: str, value: int) -> None:
        rig = rig.upper()
        target = "-" if value == 0 else str(value)
        current = self._ws_status.a if rig == "A" else self._ws_status.b
        if current == target:
            return
        command = f"{rig}{'-' if value == 0 else value}"
        self._set_status_message(f"Sending command: {command}")
        self._set_busy(True)
        self._controller.send_text(command)
