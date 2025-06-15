"""Qt MainWindow loader."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow

from src.views import load_ui


def MainWindow() -> QMainWindow:
    """Return the loaded main window."""
    return load_ui("main_window")  # type: ignore[return-value]
