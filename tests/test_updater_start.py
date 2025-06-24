import sys
from PySide6.QtWidgets import QApplication, QMainWindow

from src.fueltracker import main
from src.fueltracker import updater


def test_run_starts_background_updater(monkeypatch):
    # Prevent Qt event loop from blocking and exit calls from stopping the test
    monkeypatch.setattr(QApplication, "exec", lambda self: 0)
    monkeypatch.setattr(sys, "exit", lambda *a, **k: None)
    monkeypatch.setattr(QMainWindow, "show", lambda self: None)

    started = {}

    class DummyThread:
        def __init__(self, *a, **k):
            pass

        def start(self):
            started["t"] = True

        def is_alive(self):  # pragma: no cover - not used but avoids AttributeError
            return False

    monkeypatch.setattr(updater, "Thread", DummyThread)

    main.run([])

    assert started.get("t")
