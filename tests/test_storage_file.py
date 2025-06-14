from datetime import date

from src.models import Vehicle, FuelEntry
from src.services import StorageService


def test_file_storage_crud(tmp_path):
    db_path = tmp_path / "fuel.db"
    storage = StorageService(db_path=db_path)

    vehicle = Vehicle(
        name="File Car",
        vehicle_type="sedan",
        license_plate="FILE123",
        tank_capacity_liters=55.0,
    )
    storage.add_vehicle(vehicle)
    assert vehicle.id is not None

    fetched = storage.get_vehicle(vehicle.id)
    assert fetched is not None
    assert fetched.name == "File Car"

    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=vehicle.id,
        odo_before=0.0,
        odo_after=100.0,
        amount_spent=50.0,
        liters=20.0,
    )
    storage.add_entry(entry)
    assert entry.id is not None

    entries = storage.get_entries_by_vehicle(vehicle.id)
    assert len(entries) == 1

    entry.amount_spent = 55.0
    storage.update_entry(entry)
    updated = storage.get_entry(entry.id)
    assert updated is not None
    assert updated.amount_spent == 55.0

    storage.delete_entry(entry.id)
    assert storage.get_entries_by_vehicle(vehicle.id) == []

    storage.delete_vehicle(vehicle.id)
    assert storage.list_vehicles() == []

    assert db_path.exists()
