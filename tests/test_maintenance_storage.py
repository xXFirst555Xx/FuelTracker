from datetime import date, timedelta

from src.models import Vehicle, Maintenance
from src.services import StorageService


def test_mark_done(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    task = Maintenance(vehicle_id=1, name="Oil", due_odo=100)
    storage.add_maintenance(task)
    storage.mark_maintenance_done(task.id)
    fetched = storage.get_maintenance(task.id)
    assert fetched is not None
    assert fetched.is_done


def test_list_due_by_odo(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    due = Maintenance(vehicle_id=1, name="Oil", due_odo=100)
    not_due = Maintenance(vehicle_id=1, name="Filter", due_odo=150)
    storage.add_maintenance(due)
    storage.add_maintenance(not_due)

    res = storage.list_due_maintenances(1, odo=120)
    assert [m.id for m in res] == [due.id]


def test_list_due_by_date(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    overdue = Maintenance(
        vehicle_id=1, name="Check", due_date=date.today() - timedelta(days=1)
    )
    future = Maintenance(
        vehicle_id=1, name="Wash", due_date=date.today() + timedelta(days=2)
    )
    storage.add_maintenance(overdue)
    storage.add_maintenance(future)

    res = storage.list_due_maintenances(1, date_=date.today())
    assert [m.id for m in res] == [overdue.id]


def test_list_due_by_either(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    odo_due = Maintenance(vehicle_id=1, name="Oil", due_odo=100)
    date_due = Maintenance(
        vehicle_id=1, name="Check", due_date=date.today() - timedelta(days=1)
    )
    storage.add_maintenance(odo_due)
    storage.add_maintenance(date_due)

    res = storage.list_due_maintenances(1, odo=120, date_=date.today())
    ids = {m.id for m in res}
    assert ids == {odo_due.id, date_due.id}
