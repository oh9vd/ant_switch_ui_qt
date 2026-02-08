from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from PySide6.QtGui import QGuiApplication, QIcon

from config.settings import load_settings
from core.logging_setup import configure_logging
from core.app_controller import AppController
from core.state import AppState
def _icon_path() -> Path:
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    icon_path = base_dir / "assets" / "app_icon.svg"
    if not icon_path.exists():
        icon_path = Path(__file__).resolve().parents[1] / "assets" / "app_icon.svg"
    return icon_path


from ui.qml_app import create_qml_engine


def main() -> int:
    settings = load_settings(Path("config.json"))
    configure_logging(settings.log_level, settings.log_console, settings.log_file)
    controller = AppController(settings=settings, state=AppState())
    app = QGuiApplication(sys.argv)
    app.setWindowIcon(QIcon(str(_icon_path())))
    engine = create_qml_engine(controller)
    if not engine.rootObjects():
        controller.stop()
        return 1

    controller.start()

    exit_code = app.exec()
    controller.stop()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
