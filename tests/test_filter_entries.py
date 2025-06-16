from datetime import date, timedelta
from PySide6.QtCore import QDate
from src.controllers.main_controller import MainController
from src.models import FuelEntry, Vehicle


def test_filter_entries(qapp, tmp_path):
    ctrl = MainController(db_path=tmp_path / "t.db")
    storage = ctrl.storage
    storage.add_vehicle(Vehicle(name="Car A", vehicle_type="t", license_plate="a", tank_capacity_liters=1))
    storage.add_vehicle(Vehicle(name="Car B", vehicle_type="t", license_plate="b", tank_capacity_liters=1))

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
