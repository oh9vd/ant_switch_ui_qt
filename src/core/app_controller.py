from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable, Optional
from urllib.parse import urlparse, urlunparse

from config.settings import AppSettings
from core.logging_setup import get_logger
from core.radio_info import RadioInfo, parse_radio_info
from core.state import AppState
from net.udp_client import UdpClient, UdpConfig
from net.websocket_client import WebSocketClient, WebSocketConfig


@dataclass
class AppController:
    settings: AppSettings
    state: AppState

    def __post_init__(self) -> None:
        self._logger = get_logger(self.__class__.__name__)
        self._ws_message_listener: Optional[Callable[[str], None]] = None
        self._ws_error_listener: Optional[Callable[[str], None]] = None
        self._ws_disconnect_listener: Optional[Callable[[], None]] = None
        self._ws_send_failed_listener: Optional[Callable[[str], None]] = None
        self._udp_info_listener: Optional[Callable[[RadioInfo], None]] = None
        self._ws_a: str = ""
        self._ws_b: str = ""
        ws_url = _build_ws_url(self.settings.ws_url, self.settings.ws_port)
        self.ws_client = WebSocketClient(
            WebSocketConfig(url=ws_url)
        )
        self.ws_client.set_message_handler(self._handle_ws_message)
        self.ws_client.set_error_handler(self._handle_ws_error)
        self.ws_client.set_disconnect_handler(self._handle_ws_disconnected)
        self.ws_client.set_send_failed_handler(self._handle_ws_send_failed)
        self.udp_client = UdpClient(
            UdpConfig(host=self.settings.udp_host, port=self.settings.udp_port)
        )
        self.udp_client.set_message_handler(self._handle_udp_message)

    def start(self) -> None:
        try:
            self.ws_client.connect()
        except Exception as exc:
            self._logger.exception("WebSocket connection failed: %s", exc)

        try:
            self.udp_client.open()
        except Exception as exc:
            self._logger.exception("UDP connection failed: %s", exc)

    def stop(self) -> None:
        self.ws_client.close()
        self.udp_client.close()

    def send_text(self, text: str) -> None:
        try:
            self.ws_client.send(text)
        except Exception as exc:
            self._logger.exception("WebSocket send failed: %s", exc)

    def select_antenna(self, rig: str, value: int) -> bool:
        rig = rig.upper()
        target = "-" if value == 0 else str(value)
        current = self._ws_a if rig == "A" else self._ws_b
        if current == target:
            return False
        command = f"{rig}{'-' if value == 0 else value}"
        self.send_text(command)
        return True

    def set_ws_message_listener(self, listener: Callable[[str], None]) -> None:
        self._ws_message_listener = listener

    def set_ws_error_listener(self, listener: Callable[[str], None]) -> None:
        self._ws_error_listener = listener

    def set_ws_disconnect_listener(self, listener: Callable[[], None]) -> None:
        self._ws_disconnect_listener = listener

    def set_ws_send_failed_listener(self, listener: Callable[[str], None]) -> None:
        self._ws_send_failed_listener = listener

    def set_udp_info_listener(self, listener: Callable[[RadioInfo], None]) -> None:
        self._udp_info_listener = listener

    def _handle_ws_message(self, message: str) -> None:
        self.state.last_message = message
        self._logger.debug("WebSocket message received: %s", message)
        self._update_ws_state(message)
        if self._ws_message_listener:
            self._ws_message_listener(message)

    def _handle_ws_error(self, error: str) -> None:
        self._logger.warning("WebSocket error: %s", error)
        if self._ws_error_listener:
            self._ws_error_listener(error)

    def _handle_ws_disconnected(self) -> None:
        if self._ws_disconnect_listener:
            self._ws_disconnect_listener()

    def _handle_ws_send_failed(self, reason: str) -> None:
        if self._ws_send_failed_listener:
            self._ws_send_failed_listener(reason)

    def _handle_udp_message(self, payload: bytes) -> None:
        try:
            xml_text = payload.decode("utf-8", errors="ignore")
            self.state.radio_info = parse_radio_info(xml_text)
            self._logger.debug("UDP RadioInfo parsed: %s", self.state.radio_info)
            if self._udp_info_listener:
                self._udp_info_listener(self.state.radio_info)
        except Exception as exc:
            self._logger.exception("Failed to parse UDP XML: %s", exc)

    def _update_ws_state(self, message: str) -> None:
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return
        if not isinstance(data, dict):
            return
        if "a" in data:
            self._ws_a = str(data.get("a"))
        if "b" in data:
            self._ws_b = str(data.get("b"))


def _build_ws_url(raw_url: str, port: int) -> str:
    parsed = urlparse(raw_url)
    scheme = parsed.scheme or "ws"
    if scheme == "http":
        scheme = "ws"
    elif scheme == "https":
        scheme = "wss"

    hostname = parsed.hostname or raw_url
    if hostname and ":" in hostname and hostname.startswith("["):
        hostname = hostname.strip("[]")

    netloc = hostname or "127.0.0.1"
    if parsed.port is not None:
        netloc = f"{netloc}:{parsed.port}"
    else:
        netloc = f"{netloc}:{port}"

    path = parsed.path or "/"
    return urlunparse((scheme, netloc, path, "", "", ""))
