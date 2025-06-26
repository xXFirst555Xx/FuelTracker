"""FuelTracker package root – global compatibility shims."""

from importlib import import_module

try:
    # Ensure PySide6 is importable in headless CI
    QtWidgets = import_module("PySide6.QtWidgets")
    if not hasattr(QtWidgets, "QStackedLayout"):
        from PySide6.QtWidgets import QStackedLayout  # noqa: F401

        QtWidgets.QStackedLayout = QStackedLayout
except ModuleNotFoundError:
    # PySide6 not available during some static analysis; ignore.
    pass
