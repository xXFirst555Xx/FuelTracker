import sys
from PySide6.QtWidgets import QApplication, QMainWindow

from src.fueltracker import main
from src.fueltracker import updater
from src.config import AppConfig


def test_run_starts_background_updater(monkeypatch):
    # Prevent Qt event loop from blocking and exit calls from stopping the test
    monkeypatch.setattr(QApplication, "exec", lambda self: 0)
    monkeypatch.setattr(sys, "exit", lambda *a, **k: None)
    monkeypatch.setattr(QMainWindow, "show", lambda self: None)
    monkeypatch.setattr(
        "src.config.AppConfig.load", lambda path=None: AppConfig(update_hours=24)
    )

    started = {}

    class DummyThread:
        def __init__(self, *a, **k):
            pass

        def start(self):
            started["t"] = True

        def is_alive(self):  # pragma: no cover - not used but avoids AttributeError
            return False

    monkeypatch.setattr(updater, "Thread", DummyThread)

    # Allow updater.start_async() to run during this test
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "")

    main.run([])

    assert started.get("t")


def test_run_skips_updater_when_disabled(monkeypatch):
    monkeypatch.setattr(QApplication, "exec", lambda self: 0)
    monkeypatch.setattr(sys, "exit", lambda *a, **k: None)
    monkeypatch.setattr(QMainWindow, "show", lambda self: None)

    monkeypatch.setattr(
        "src.config.AppConfig.load", lambda path=None: AppConfig(update_hours=0)
    )

    called = {}

    def fake_start(interval):
        called["i"] = interval

    monkeypatch.setattr(updater, "start_async", fake_start)

    main.run([])

    assert "i" not in called
