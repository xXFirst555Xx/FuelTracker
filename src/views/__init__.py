"""Utilities for working with Qt Designer UI files."""

from pathlib import Path
import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QDialog, QDialogButtonBox
from PySide6.QtCore import QFile, QDir

BASE_PATH = Path(__file__).resolve().parent


def asset_path(*parts: str) -> Path:
    """Return absolute path to an asset file.

    Works both from source and when packaged with PyInstaller.
    """
    root = Path(getattr(sys, "_MEIPASS", BASE_PATH.parents[1]))
    return root.joinpath("assets", *parts)


# Allow Qt to resolve ``icons:`` paths inside .ui files.
QDir.addSearchPath("icons", str(asset_path("icons")))


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

    if isinstance(widget, QDialog):
        button_box = widget.findChild(QDialogButtonBox, "buttonBox")
        if button_box is not None:
            button_box.accepted.connect(widget.accept)
            button_box.rejected.connect(widget.reject)

    return widget


def load_add_entry_dialog() -> QDialog:
    """Convenience loader for the Add Entry dialog."""
    return load_ui("dialogs/add_entry_dialog")  # type: ignore


def load_add_vehicle_dialog() -> QDialog:
    """Convenience loader for the Add Vehicle dialog."""
    return load_ui("dialogs/add_vehicle_dialog")  # type: ignore
