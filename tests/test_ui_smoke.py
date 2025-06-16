import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QCloseEvent
from src.controllers import MainController


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


def test_close_hides_window(qapp, tmp_path, monkeypatch):
    ctrl = MainController(db_path=tmp_path / "t.db")
    window = ctrl.window
    monkeypatch.setattr(ctrl.tray_icon, "isVisible", lambda: True)
    ctrl.config.hide_on_close = True
    hidden = {}
    monkeypatch.setattr(window, "hide", lambda: hidden.setdefault("h", True))
    event = QCloseEvent()
    window.closeEvent(event)
    assert not event.isAccepted()
    assert hidden.get("h")
