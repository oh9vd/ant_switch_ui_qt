from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

from core.app_controller import AppController
from core.version import get_version
from ui.qml_bridge import QmlBridge


def _resource_path() -> Path:
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base_dir / "ui" / "qml" / "Main.qml"


def create_qml_engine(controller: AppController) -> QQmlApplicationEngine:
    engine = QQmlApplicationEngine()
    bridge = QmlBridge(controller)
    engine.rootContext().setContextProperty("bridge", bridge)
    engine.rootContext().setContextProperty(
        "appTitle",
        "2x6 Remote Switch Controller",
    )
    engine.rootContext().setContextProperty("wsStatus", bridge.wsStatus)
    engine.rootContext().setContextProperty("radioStatus", bridge.radioStatus)
    antenna_names = controller.settings.antennas
    engine.rootContext().setContextProperty(
        "antennaNames",
        [
            antenna_names.get("ant0Name", "OFF"),
            antenna_names.get("ant1Name", "1"),
            antenna_names.get("ant2Name", "2"),
            antenna_names.get("ant3Name", "3"),
            antenna_names.get("ant4Name", "4"),
            antenna_names.get("ant5Name", "5"),
            antenna_names.get("ant6Name", "6"),
        ],
    )
    engine.rootContext().setContextProperty("rigAName", controller.settings.rig_a_name)
    engine.rootContext().setContextProperty("rigBName", controller.settings.rig_b_name)
    
    engine.rootContext().setContextProperty("appVersion", get_version())

    qml_path = _resource_path()
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    return engine

