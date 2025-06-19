from datetime import date
import pytest
from src.models import FuelEntry, Vehicle
from src.services import StorageService


def test_invalid_odometer(tmp_path):
    storage = StorageService(db_path=tmp_path / "fuel.db")
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=100.0,
        odo_after=50.0,
        amount_spent=10.0,
        liters=1.0,
    )
    with pytest.raises(ValueError):
        storage.add_entry(entry)


def test_liters_requires_amount(tmp_path):
    storage = StorageService(db_path=tmp_path / "fuel.db")
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=0.0,
        odo_after=50.0,
        amount_spent=None,
        liters=5.0,
    )
    with pytest.raises(ValueError):
        storage.add_entry(entry)
