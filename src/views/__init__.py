"""Utilities for working with Qt Designer UI files."""

from pathlib import Path
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QDialog
from PySide6.QtCore import QFile

BASE_PATH = Path(__file__).resolve().parent


def load_ui(name: str) -> QWidget:
    """Load a Qt Designer ``.ui`` file from the views directory."""
    ui_path = BASE_PATH / f"{name}.ui"
    if not ui_path.exists():
        raise FileNotFoundError(ui_path)

    file = QFile(str(ui_path))
    file.open(QFile.ReadOnly)
    loader = QUiLoader()
    widget = loader.load(file)
    file.close()
    return widget


def load_add_entry_dialog() -> QDialog:
    """Convenience loader for the Add Entry dialog."""
    return load_ui("dialogs/add_entry_dialog")  # type: ignore


def load_add_vehicle_dialog() -> QDialog:
    """Convenience loader for the Add Vehicle dialog."""
    return load_ui("dialogs/add_vehicle_dialog")  # type: ignore
