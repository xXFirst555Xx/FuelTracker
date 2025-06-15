from datetime import date

from src.models import FuelEntry, Vehicle
from src.services import StorageService


def test_incomplete_entry_update(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vehicle = Vehicle(name="Car", vehicle_type="sedan", license_plate="A", tank_capacity_liters=40)
    storage.add_vehicle(vehicle)

    e1 = FuelEntry(
        entry_date=date(2024, 1, 1),
        vehicle_id=vehicle.id,
        odo_before=1000.0,
        odo_after=None,
        amount_spent=50.0,
    )
    storage.add_entry(e1)

    # next entry with known odo_before should complete previous entry
    e2 = FuelEntry(
        entry_date=date(2024, 1, 5),
        vehicle_id=vehicle.id,
        odo_before=1100.0,
        odo_after=1200.0,
        amount_spent=60.0,
    )
    storage.add_entry(e2)

    updated = storage.get_entry(e1.id)
    assert updated.odo_after == 1100.0


def test_add_incomplete_without_followup(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vehicle = Vehicle(name="Car", vehicle_type="sedan", license_plate="B", tank_capacity_liters=40)
    storage.add_vehicle(vehicle)

    entry = FuelEntry(
        entry_date=date(2024, 1, 1),
        vehicle_id=vehicle.id,
        odo_before=500.0,
        odo_after=None,
        amount_spent=30.0,
    )
    storage.add_entry(entry)

    # No other entries; metrics should have distance None
    fetched = storage.get_entry(entry.id)
    assert fetched.odo_after is None
    metrics = fetched.calc_metrics()
    assert metrics["distance"] is None

