"""จุดเริ่มต้นของโปรแกรม"""

from __future__ import annotations

import sys
import logging
import argparse
import os
from pathlib import Path
from typing import TYPE_CHECKING

from alembic.config import Config
from alembic.command import upgrade

from src.settings import Settings

ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from src.controllers.main_controller import MainController

_controller: "MainController | None" = None


def run(argv: list[str] | None = None) -> None:
    """เปิดหน้าต่าง FuelTracker"""
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--start-minimized", action="store_true")
    args, _ = parser.parse_known_args(argv)

    if args.command == "migrate":
        upgrade(Config(ALEMBIC_INI), "head")
        return

    settings = Settings()
    cfg = Config(ALEMBIC_INI)
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{settings.db_path}")
    upgrade(cfg, "head")

    logging.basicConfig(level=logging.INFO)
    if args.check:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QCoreApplication, Qt

    app = QApplication.instance() or QApplication(sys.argv[:1])

    # --- NEW: use MainController instead of bare MainWindow ---
    from src.controllers.main_controller import MainController

    global _controller
    _controller = MainController()
    window = _controller.window
    # ----------------------------------------------------------
    if args.check:
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi, True)
        window.show()
        print("MainWindow OK")
        return

    window.show()
    if args.start_minimized or _controller.config.start_minimized:
        window.hide()
    sys.exit(app.exec())
