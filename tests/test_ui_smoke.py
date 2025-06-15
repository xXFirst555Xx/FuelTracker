import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow


def test_mainwindow_launch(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from fueltracker.main import run

    # prevent blocking by skipping the event loop
    monkeypatch.setattr(QApplication, "exec", lambda self: 0)
    monkeypatch.setattr(sys, "exit", lambda *a, **kw: None)
    shown = []
    monkeypatch.setattr(QMainWindow, "show", lambda self: shown.append(True))

    run()
    assert shown
