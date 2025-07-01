import pytest
from PySide6.QtWidgets import QDialog, QMessageBox

from src.models import Vehicle
from src.views import load_add_vehicle_dialog
from src.controllers.undo_commands import (
    AddVehicleCommand,
    UpdateVehicleCommand,
    DeleteVehicleCommand,
)


# ---------------------------------------------------------------------------
# open_add_vehicle_dialog
# ---------------------------------------------------------------------------

def test_add_vehicle_valid(qtbot, main_controller, monkeypatch):
    ctrl = main_controller
    dialog = load_add_vehicle_dialog()
    qtbot.addWidget(dialog)

    monkeypatch.setattr(
        "src.controllers.main_controller.AddVehicleDialog",
        lambda *_a, **_k: dialog,
    )

    def fake_exec():
        dialog.nameLineEdit.setText("Car")
        dialog.typeLineEdit.setText("Sedan")
        dialog.plateLineEdit.setText("AB-123")
        dialog.capacityLineEdit.setText("50")
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(dialog, "exec", fake_exec)

    ctrl.open_add_vehicle_dialog()

    vehicles = ctrl.storage.list_vehicles()
    assert len(vehicles) == 1
    assert ctrl.undo_stack.count() == 1
    assert isinstance(ctrl.undo_stack.command(0), AddVehicleCommand)


def test_add_vehicle_missing_fields(qtbot, main_controller, monkeypatch):
    ctrl = main_controller
    dialog = load_add_vehicle_dialog()
    qtbot.addWidget(dialog)

    monkeypatch.setattr(
        "src.controllers.main_controller.AddVehicleDialog",
        lambda *_a, **_k: dialog,
    )

    warned = {}
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *a, **k: warned.setdefault("warn", True),
    )

    def fake_exec():
        dialog.nameLineEdit.setText("")
        dialog.typeLineEdit.setText("Sedan")
        dialog.plateLineEdit.setText("AB-123")
        dialog.capacityLineEdit.setText("50")
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(dialog, "exec", fake_exec)

    ctrl.open_add_vehicle_dialog()

    assert warned.get("warn")
    assert ctrl.undo_stack.count() == 0
    assert ctrl.storage.list_vehicles() == []


# ---------------------------------------------------------------------------
# open_edit_vehicle_dialog
# ---------------------------------------------------------------------------

def _setup_vehicle(ctrl):
    v = Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    ctrl.storage.add_vehicle(v)
    ctrl.refresh_vehicle_list()
    ctrl.window.vehicleListWidget.setCurrentRow(0)
    return v


def test_edit_vehicle_invalid_capacity(qtbot, main_controller, monkeypatch):
    ctrl = main_controller
    _setup_vehicle(ctrl)
    dialog = load_add_vehicle_dialog()
    qtbot.addWidget(dialog)

    monkeypatch.setattr(
        "src.controllers.main_controller.AddVehicleDialog",
        lambda *_a, **_k: dialog,
    )

    warned = {}
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *a, **k: warned.setdefault("warn", True),
    )

    def fake_exec():
        dialog.capacityLineEdit.setText("abc")
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(dialog, "exec", fake_exec)

    ctrl.open_edit_vehicle_dialog()

    assert warned.get("warn")
    assert ctrl.undo_stack.count() == 0
    v = ctrl.storage.get_vehicle(1)
    assert v.tank_capacity_liters == 1


def test_edit_vehicle_valid(qtbot, main_controller, monkeypatch):
    ctrl = main_controller
    _setup_vehicle(ctrl)
    dialog = load_add_vehicle_dialog()
    qtbot.addWidget(dialog)

    monkeypatch.setattr(
        "src.controllers.main_controller.AddVehicleDialog",
        lambda *_a, **_k: dialog,
    )

    def fake_exec():
        dialog.nameLineEdit.setText("New")
        dialog.typeLineEdit.setText("Truck")
        dialog.plateLineEdit.setText("CD-456")
        dialog.capacityLineEdit.setText("2")
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(dialog, "exec", fake_exec)

    ctrl.open_edit_vehicle_dialog()

    v = ctrl.storage.get_vehicle(1)
    assert v.name == "New"
    assert ctrl.undo_stack.count() == 1
    assert isinstance(ctrl.undo_stack.command(0), UpdateVehicleCommand)


# ---------------------------------------------------------------------------
# delete_selected_vehicle
# ---------------------------------------------------------------------------

def test_delete_vehicle_yes(qtbot, main_controller, monkeypatch):
    ctrl = main_controller
    _setup_vehicle(ctrl)

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *a, **k: QMessageBox.StandardButton.Yes,
    )

    ctrl.delete_selected_vehicle()

    assert ctrl.storage.list_vehicles() == []
    assert ctrl.undo_stack.count() == 1
    assert isinstance(ctrl.undo_stack.command(0), DeleteVehicleCommand)


def test_delete_vehicle_no(qtbot, main_controller, monkeypatch):
    ctrl = main_controller
    _setup_vehicle(ctrl)

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *a, **k: QMessageBox.StandardButton.No,
    )

    ctrl.delete_selected_vehicle()

    assert len(ctrl.storage.list_vehicles()) == 1
    assert ctrl.undo_stack.count() == 0

