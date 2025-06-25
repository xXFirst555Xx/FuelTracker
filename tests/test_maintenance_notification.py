from datetime import date
from PySide6.QtWidgets import QMessageBox

from src.controllers import main_controller as main_module
from src.models import Vehicle, Maintenance


def test_maintenance_notification(main_controller, monkeypatch):
    ctrl = main_controller
    storage = ctrl.storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    storage.add_maintenance(Maintenance(vehicle_id=1, name="Oil", due_odo=100))
    notified = {}
    monkeypatch.setattr(
        QMessageBox, "information", lambda *a, **k: notified.setdefault("n", True)
    )
    show = {}
    original = main_module.os.name
    monkeypatch.setattr(main_module.os, "name", "nt", raising=False)
    monkeypatch.setattr(
        main_module.ToastNotifier,
        "show_toast",
        lambda *a, **k: show.setdefault("t", True),
    )
    ctrl._notify_due_maintenance(1, 120, date.today())
    monkeypatch.setattr(main_module.os, "name", original, raising=False)
    assert notified.get("n")
    assert show.get("t")
