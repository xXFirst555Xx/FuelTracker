from datetime import date

from PySide6.QtWidgets import QMessageBox

from src.models import Vehicle, FuelEntry


def test_budget_save_updates_storage(main_controller, monkeypatch):
    ctrl = main_controller
    storage = ctrl.storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    ctrl.refresh_vehicle_list()
    # select first vehicle
    ctrl.window.budgetVehicleComboBox.setCurrentIndex(0)
    ctrl.window.budgetEdit.setText("120")
    warned = {}
    monkeypatch.setattr(
        QMessageBox, "warning", lambda *a, **k: warned.setdefault("w", True)
    )
    ctrl._save_budget()
    assert storage.get_budget(1) == 120.0
    warned.clear()
    ctrl.storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=1,
            odo_before=0,
            odo_after=10,
            amount_spent=200,
            liters=10,
        )
    )
    ctrl._check_budget(1, date.today())
    assert warned.get("w")
