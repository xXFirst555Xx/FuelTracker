from src.models import Vehicle, Maintenance
from src.services import StorageService


def test_mark_done(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    storage.add_vehicle(Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1))
    task = Maintenance(vehicle_id=1, name="Oil", due_odo=100)
    storage.add_maintenance(task)
    storage.mark_maintenance_done(task.id)
    fetched = storage.get_maintenance(task.id)
    assert fetched is not None
    assert fetched.is_done
