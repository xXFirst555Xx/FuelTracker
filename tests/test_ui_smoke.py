import sys
import os
from datetime import date
from pathlib import Path
import sqlite3
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QCloseEvent
from src.models import Vehicle, FuelEntry

if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
    import pytest

    pytest.skip("ui tests disabled in headless mode", allow_module_level=True)


def test_mainwindow_launch(monkeypatch):
    from fueltracker.main import run

    # prevent blocking by skipping the event loop
    monkeypatch.setattr(QApplication, "exec", lambda self: 0)
    monkeypatch.setattr(sys, "exit", lambda *a, **_kw: None)
    shown = []
    monkeypatch.setattr(QMainWindow, "show", lambda self: shown.append(True))

    run()
    assert shown


def test_close_hides_window(main_controller, monkeypatch):
    ctrl = main_controller
    window = ctrl.window
    monkeypatch.setattr(ctrl.tray_icon, "isVisible", lambda: True)
    ctrl.config.hide_on_close = True
    hidden = {}
    monkeypatch.setattr(window, "hide", lambda: hidden.setdefault("h", True))
    event = QCloseEvent()
    window.closeEvent(event)
    assert not event.isAccepted()
    assert hidden.get("h")


def test_tray_tooltip_updates(main_controller, monkeypatch):
    ctrl = main_controller
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


def test_hotkey_invokes_dialog(main_controller, monkeypatch):
    ctrl = main_controller
    called = {}
    monkeypatch.setattr(
        ctrl, "open_add_entry_dialog", lambda: called.setdefault("ok", True)
    )
    ctrl.window.hide()
    visible = {}
    monkeypatch.setattr(ctrl.window, "show", lambda: visible.setdefault("v", True))
    ctrl._on_hotkey()
    assert called.get("ok")
    assert visible.get("v")


def test_cleanup_unregisters_hotkey(main_controller):
    ctrl = main_controller
    # Hotkeys are enabled by default, so a GlobalHotkey instance should exist
    assert ctrl.global_hotkey is not None
    ctrl.cleanup()
    assert ctrl.global_hotkey is None


def test_cleanup_handles_missing_db(main_controller, monkeypatch):
    ctrl = main_controller

    def fail_backup() -> Path:
        raise sqlite3.DatabaseError("fail")

    monkeypatch.setattr(ctrl.storage, "auto_backup", fail_backup)
    called: list[tuple[Path, Path]] = []
    monkeypatch.setattr(ctrl.storage, "sync_to_cloud", lambda *a: called.append(a))

    ctrl.cleanup()
    assert not called
