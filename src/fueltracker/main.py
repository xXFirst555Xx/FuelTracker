"""Application entry points."""

from __future__ import annotations

import sys
import logging
from PySide6.QtWidgets import QApplication


def run() -> None:
    """Launch the FuelTracker UI."""
    logging.basicConfig(level=logging.INFO)
    app = QApplication.instance() or QApplication(sys.argv)
    from .ui.main_window import MainWindow

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
