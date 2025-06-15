"""Application entry points."""

from __future__ import annotations

import sys
import logging
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt


def run(argv: list[str] | None = None) -> None:
    """Launch the FuelTracker UI."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args, _ = parser.parse_known_args(argv)

    logging.basicConfig(level=logging.INFO)
    app = QApplication.instance() or QApplication(sys.argv[:1])
    from .ui.main_window import MainWindow

    window = MainWindow()
    if args.check:
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi, True)
        window.show()
        print("MainWindow OK")
        return

    window.show()
    sys.exit(app.exec())
