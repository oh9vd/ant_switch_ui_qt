from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from PySide6.QtNetwork import QHostAddress, QUdpSocket

from core.logging_setup import get_logger


@dataclass
class UdpConfig:
    host: str
    port: int
    enabled: bool = True


class UdpClient:
    def __init__(self, config: UdpConfig) -> None:
        self._config = config
        self._socket: QUdpSocket | None = None
        self._on_message: Optional[Callable[[bytes], None]] = None
        self._logger = get_logger(self.__class__.__name__)

    def set_message_handler(self, handler: Callable[[bytes], None]) -> None:
        self._on_message = handler

    def open(self) -> None:
        if not self._config.enabled:
            return
        if self._socket is None:
            self._socket = QUdpSocket()
            self._socket.readyRead.connect(self._handle_ready_read)
        address = QHostAddress(self._config.host)
        if not self._socket.bind(address, self._config.port):
            self._logger.error("UDP bind failed: %s:%s", self._config.host, self._config.port)
        else:
            self._logger.info("UDP listening on %s:%s", self._config.host, self._config.port)

    def send(self, payload: bytes) -> None:
        self._logger.debug("UDP send ignored (listen-only mode)")

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()

    def _handle_ready_read(self) -> None:
        if self._socket is None:
            return
        while self._socket.hasPendingDatagrams():
            datagram = self._socket.receiveDatagram()
            data = bytes(datagram.data())
            self._logger.debug(
                "UDP datagram received from %s:%s (%d bytes)",
                datagram.senderAddress().toString(),
                datagram.senderPort(),
                len(data),
            )
            if self._on_message:
                self._on_message(data)
