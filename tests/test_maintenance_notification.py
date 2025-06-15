from datetime import date
from PySide6.QtWidgets import QMessageBox

from src.controllers.main_controller import MainController
from src.models import Vehicle, Maintenance


def test_maintenance_notification(qapp, tmp_path, monkeypatch):
    ctrl = MainController(db_path=tmp_path / "t.db")
    storage = ctrl.storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    storage.add_maintenance(Maintenance(vehicle_id=1, name="Oil", due_odo=100))
    notified = {}
    monkeypatch.setattr(
        QMessageBox, "information", lambda *a, **k: notified.setdefault("n", True)
    )
    ctrl._notify_due_maintenance(1, 120, date.today())
    assert notified.get("n")
