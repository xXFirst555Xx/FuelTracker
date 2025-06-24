from datetime import date

from src.models import FuelEntry, Vehicle
from src.services import StorageService


def test_vehicle_crud(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vehicle = Vehicle(
        name="Test Car",
        vehicle_type="sedan",
        license_plate="TEST123",
        tank_capacity_liters=50.0,
    )
    storage.add_vehicle(vehicle)
    assert vehicle.id is not None

    fetched = storage.get_vehicle(vehicle.id)
    assert fetched is not None
    assert fetched.name == "Test Car"

    vehicle.name = "Updated"
    storage.update_vehicle(vehicle)
    updated = storage.get_vehicle(vehicle.id)
    assert updated is not None
    assert updated.name == "Updated"

    storage.delete_vehicle(vehicle.id)
    assert storage.get_vehicle(vehicle.id) is None
    assert storage.list_vehicles() == []


def test_entry_crud_and_filter(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vehicle = Vehicle(
        name="Filter Car",
        vehicle_type="hatch",
        license_plate="FLT111",
        tank_capacity_liters=40.0,
    )
    storage.add_vehicle(vehicle)
    assert vehicle.id is not None

    e1 = FuelEntry(
        entry_date=date.today(),
        vehicle_id=vehicle.id,
        odo_before=0.0,
        odo_after=100.0,
        amount_spent=20.0,
        liters=10.0,
    )
    storage.add_entry(e1)

    e2 = FuelEntry(
        entry_date=date.today(),
        vehicle_id=vehicle.id,
        odo_before=100.0,
        odo_after=150.0,
        amount_spent=15.0,
        liters=5.0,
    )
    storage.add_entry(e2)

    entries = storage.get_entries_by_vehicle(vehicle.id)
    assert len(entries) == 2

    e1.amount_spent = 25.0
    storage.update_entry(e1)
    fetched = storage.get_entry(e1.id)
    assert fetched is not None
    assert fetched.amount_spent == 25.0

    storage.delete_entry(e2.id)
    entries_after = storage.get_entries_by_vehicle(vehicle.id)
    assert len(entries_after) == 1
    assert entries_after[0].id == e1.id


def test_init_nested_path(tmp_path) -> None:
    nested_path = tmp_path / "nested" / "dir" / "fuel.db"
    StorageService(db_path=nested_path)
    assert nested_path.exists()


def test_get_vehicle_stats(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vehicle = Vehicle(
        name="Stats Car",
        vehicle_type="suv",
        license_plate="STAT123",
        tank_capacity_liters=60.0,
    )
    storage.add_vehicle(vehicle)

    entries = [
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=vehicle.id,
            odo_before=0,
            odo_after=100,
            amount_spent=50,
            liters=20,
        ),
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=vehicle.id,
            odo_before=100,
            odo_after=200,
            amount_spent=40,
            liters=15,
        ),
    ]
    for e in entries:
        storage.add_entry(e)

    manual_distance = 0.0
    manual_liters = 0.0
    manual_price = 0.0
    for e in storage.get_entries_by_vehicle(vehicle.id):
        if e.odo_after is None:
            continue
        manual_distance += e.odo_after - e.odo_before
        if e.liters:
            manual_liters += e.liters
        if e.amount_spent:
            manual_price += e.amount_spent

    dist, liters, price = storage.get_vehicle_stats(vehicle.id)

    assert dist == manual_distance
    assert liters == manual_liters
    assert price == manual_price


def test_vehicle_monthly_stats(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 1),
            vehicle_id=1,
            odo_before=0,
            odo_after=100,
            amount_spent=20,
            liters=10,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 15),
            vehicle_id=1,
            odo_before=100,
            odo_after=None,
            amount_spent=10,
            liters=5,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 2, 1),
            vehicle_id=1,
            odo_before=100,
            odo_after=200,
            amount_spent=16,
            liters=8,
        )
    )

    dist, liters, price = storage.vehicle_monthly_stats(1, 2024, 1)

    assert dist == 100.0
    assert liters == 15.0
    assert price == 30.0
