from __future__ import annotations

import json

from PySide6.QtCore import QObject, Property, Signal, Slot

from core.app_controller import AppController
from core.logging_setup import get_logger
from ui.radio_status import RadioStatus
from ui.ws_status import WsStatus


class QmlBridge(QObject):
    statusChanged = Signal()
    busyChanged = Signal()

    def __init__(self, controller: AppController) -> None:
        super().__init__()
        self._controller = controller
        self._status = "Disconnected"
        self._busy = False
        self._logger = get_logger(self.__class__.__name__)
        self._ws_status = WsStatus()
        self._radio_status = RadioStatus()
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
        self._set_busy(True)
        self._controller.send_text(message)

    def _get_status(self) -> str:
        return self._status

    def _set_status(self, value: str) -> None:
        if self._status == value:
            return
        self._status = value
        self.statusChanged.emit()

    status = Property(str, _get_status, _set_status, notify=statusChanged)

    def _get_busy(self) -> bool:
        return self._busy

    def _set_busy(self, value: bool) -> None:
        if self._busy == value:
            return
        self._busy = value
        self.busyChanged.emit()

    busy = Property(bool, _get_busy, _set_busy, notify=busyChanged)

    def _handle_ws_message(self, message: str) -> None:
        try:
            data = json.loads(message)
        except json.JSONDecodeError as exc:
            self._logger.warning("Invalid JSON message: %s", exc)
            return
        if isinstance(data, dict):
            self._ws_status.update_from_dict(data)
            self._set_busy(False)

    def _handle_ws_error(self, error: str) -> None:
        self._logger.warning("WebSocket error: %s", error)
        self._set_busy(False)

    def _handle_ws_disconnected(self) -> None:
        self._set_busy(False)

    def _handle_ws_send_failed(self, reason: str) -> None:
        self._logger.warning("WebSocket send failed: %s", reason)
        self._set_busy(False)

    @Property(QObject, constant=True)
    def wsStatus(self) -> WsStatus:
        return self._ws_status

    def _handle_udp_info(self, info) -> None:
        self._radio_status.update_from_radio_info(info)

    @Property(QObject, constant=True)
    def radioStatus(self) -> RadioStatus:
        return self._radio_status
