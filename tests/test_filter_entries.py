from datetime import date, timedelta
from PySide6.QtCore import QDate
from src.models import FuelEntry, Vehicle, Maintenance
from src.services import StorageService


def test_filter_entries(main_controller, monkeypatch):
    ctrl = main_controller
    storage = ctrl.storage
    storage.add_vehicle(
        Vehicle(
            name="Car A", vehicle_type="t", license_plate="a", tank_capacity_liters=1
        )
    )
    storage.add_vehicle(
        Vehicle(
            name="Car B", vehicle_type="t", license_plate="b", tank_capacity_liters=1
        )
    )

    storage.add_entry(
        FuelEntry(
            entry_date=date.today() - timedelta(days=1),
            vehicle_id=1,
            odo_before=0,
            odo_after=10,
            amount_spent=5.0,
            liters=1.0,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=2,
            odo_before=0,
            odo_after=20,
            amount_spent=10.0,
            liters=2.0,
        )
    )

    ctrl.window.searchLineEdit.setText("Car B")
    ctrl.window.startDateEdit.setDate(QDate.currentDate())

    entries = ctrl.filter_entries()
    assert len(entries) == 1
    assert entries[0].vehicle_id == 2


def test_list_entries_filtered(tmp_path):
    storage = StorageService(db_path=tmp_path / "t.db")
    storage.add_vehicle(
        Vehicle(name="A", vehicle_type="t", license_plate="a", tank_capacity_liters=1)
    )
    storage.add_vehicle(
        Vehicle(name="B", vehicle_type="t", license_plate="b", tank_capacity_liters=1)
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=1,
            odo_before=0,
            odo_after=10,
            amount_spent=5.0,
            liters=1.0,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=2,
            odo_before=0,
            odo_after=20,
            amount_spent=10.0,
            liters=2.0,
        )
    )

    res = storage.list_entries_filtered("B", date.today())
    assert len(res) == 1
    assert res[0].vehicle_id == 2


def test_last_entry_tooltip_and_maintenance(main_controller, monkeypatch):
    ctrl = main_controller
    storage = ctrl.storage
    storage.add_vehicle(
        Vehicle(name="Car", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )

    storage.add_entry(
        FuelEntry(
            entry_date=date.today() - timedelta(days=1),
            vehicle_id=1,
            odo_before=0,
            odo_after=50,
            amount_spent=5.0,
            liters=1.0,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=1,
            odo_before=50,
            odo_after=100,
            amount_spent=10.0,
            liters=2.0,
        )
    )
    storage.add_maintenance(Maintenance(vehicle_id=1, name="Oil", due_odo=90))

    ctrl._selected_vehicle_id = 1
    tip = {}
    monkeypatch.setattr(ctrl.tray_icon, "setToolTip", lambda t: tip.setdefault("v", t))
    ctrl._update_tray_tooltip()
    assert str(date.today()) in tip.get("v", "")

    ctrl._refresh_maintenance_panel()
    lw = ctrl.maint_dock.list_widget
    assert lw.count() == 1
    assert "Oil" in lw.item(0).text()
