"""Application entry points."""

from __future__ import annotations

import sys
import logging
import argparse
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt

_controller: "MainController | None" = None


def run(argv: list[str] | None = None) -> None:
    """Launch the FuelTracker UI."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args, _ = parser.parse_known_args(argv)

    logging.basicConfig(level=logging.INFO)
    if args.check:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
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
    sys.exit(app.exec())
