import os
import sys
from datetime import date
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QCloseEvent
from src.controllers import MainController
from src.models import Vehicle, FuelEntry


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


def test_tray_tooltip_updates(qapp, tmp_path, monkeypatch):
    ctrl = MainController(db_path=tmp_path / "t.db")
    storage = ctrl.storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=1,
            odo_before=0.0,
            odo_after=10.0,
            amount_spent=50.0,
            liters=5.0,
        )
    )
    ctrl._selected_vehicle_id = 1
    tip = {}
    monkeypatch.setattr(ctrl.tray_icon, "setToolTip", lambda t: tip.setdefault("v", t))
    ctrl._update_tray_tooltip()
    assert tip.get("v")


def test_hotkey_invokes_dialog(qapp, tmp_path, monkeypatch):
    ctrl = MainController(db_path=tmp_path / "t.db")
    called = {}
    monkeypatch.setattr(ctrl, "open_add_entry_dialog", lambda: called.setdefault("ok", True))
    ctrl.window.hide()
    visible = {}
    monkeypatch.setattr(ctrl.window, "show", lambda: visible.setdefault("v", True))
    ctrl._on_hotkey()
    assert called.get("ok")
    assert visible.get("v")


def test_cleanup_unregisters_hotkey(qapp, tmp_path):
    ctrl = MainController(db_path=tmp_path / "t.db")
    # Hotkeys are enabled by default, so a GlobalHotkey instance should exist
    assert ctrl.global_hotkey is not None
    ctrl.cleanup()
    assert ctrl.global_hotkey is None
