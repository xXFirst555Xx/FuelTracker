from datetime import date
from PySide6.QtWidgets import QMessageBox

from src.controllers.main_controller import MainController
from src.models import FuelEntry, Vehicle


def test_budget_warning(qapp, tmp_path, monkeypatch):
    ctrl = MainController(db_path=tmp_path / "t.db")
    storage = ctrl.storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    storage.set_budget(1, 50.0)
    storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=1,
            odo_before=0.0,
            odo_after=10.0,
            amount_spent=30.0,
            liters=2.0,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=1,
            odo_before=10.0,
            odo_after=20.0,
            amount_spent=25.0,
            liters=2.0,
        )
    )
    warned = {}
    monkeypatch.setattr(
        QMessageBox, "warning", lambda *a, **k: warned.setdefault("w", True)
    )
    monkeypatch.setattr("src.controllers.main_controller.ToastNotifier", lambda: None)
    ctrl._check_budget(1, date.today())
    today = date.today()
    assert storage.get_total_spent(1, today.year, today.month) == 55.0
    assert warned.get("w")
