from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from core.logging_setup import get_logger

from PySide6.QtCore import QUrl
from PySide6.QtWebSockets import QWebSocket


@dataclass
class WebSocketConfig:
    url: str
    enabled: bool = True


class WebSocketClient:
    def __init__(self, config: WebSocketConfig) -> None:
        self._config = config
        self._on_message: Optional[Callable[[str], None]] = None
        self._on_error: Optional[Callable[[str], None]] = None
        self._on_disconnect: Optional[Callable[[], None]] = None
        self._on_send_failed: Optional[Callable[[str], None]] = None
        self._logger = get_logger(self.__class__.__name__)
        self._socket: QWebSocket | None = None

    def set_message_handler(self, handler: Callable[[str], None]) -> None:
        self._on_message = handler

    def set_error_handler(self, handler: Callable[[str], None]) -> None:
        self._on_error = handler

    def set_disconnect_handler(self, handler: Callable[[], None]) -> None:
        self._on_disconnect = handler

    def set_send_failed_handler(self, handler: Callable[[str], None]) -> None:
        self._on_send_failed = handler

    def connect(self) -> None:
        if not self._config.enabled:
            return
        if self._socket is None:
            self._socket = QWebSocket()
            self._connect_signal("textMessageReceived", self._handle_text_message)
            self._connect_signal("connected", self._handle_connected)
            self._connect_signal("disconnected", self._handle_disconnected)
            self._connect_signal("errorOccurred", self._handle_error)
        self._logger.info("Opening WebSocket: %s", self._config.url)
        self._socket.open(QUrl(self._config.url))

    def send(self, message: str) -> None:
        if not self._config.enabled:
            return
        if self._socket is not None and self._socket.isValid():
            self._logger.debug("Sending WebSocket message: %s", message)
            self._socket.sendTextMessage(message)
        else:
            self._logger.warning("WebSocket not connected; message not sent")
            if self._on_send_failed:
                self._on_send_failed("not connected")

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()

    def _handle_text_message(self, message: str) -> None:
        self._logger.debug("WebSocket text message received: %s", message)
        if self._on_message:
            self._on_message(message)

    def _handle_connected(self) -> None:
        self._logger.info("WebSocket connected")

    def _handle_disconnected(self) -> None:
        self._logger.info("WebSocket disconnected")
        if self._on_disconnect:
            self._on_disconnect()

    def _handle_error(self, error) -> None:
        message = str(error)
        self._logger.error("WebSocket error: %s", message)
        if self._on_error:
            self._on_error(message)

    def _connect_signal(self, name: str, handler) -> None:
        if self._socket is None:
            return
        signal = getattr(self._socket, name, None)
        if signal is None or not hasattr(signal, "connect"):
            self._logger.warning("WebSocket signal missing: %s", name)
            return
        try:
            signal.connect(handler)
        except Exception as exc:
            self._logger.warning("Failed to connect WebSocket signal %s: %s", name, exc)
