from datetime import date

from PySide6.QtGui import QUndoStack

from src.controllers.undo_commands import (
    AddVehicleCommand,
    DeleteVehicleCommand,
    UpdateVehicleCommand,
)
from src.models import Vehicle
from src.services import StorageService


def test_add_vehicle_command(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vehicle = Vehicle(
        name="v",
        vehicle_type="t",
        license_plate="x",
        tank_capacity_liters=1,
    )
    stack = QUndoStack()
    stack.push(AddVehicleCommand(storage, vehicle))
    assert len(storage.list_vehicles()) == 1
    stack.undo()
    assert storage.list_vehicles() == []
    stack.redo()
    assert len(storage.list_vehicles()) == 1


def test_delete_vehicle_command(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    v = Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    storage.add_vehicle(v)
    stack = QUndoStack()
    stack.push(DeleteVehicleCommand(storage, v.id))
    assert storage.list_vehicles() == []
    stack.undo()
    assert len(storage.list_vehicles()) == 1


def test_update_vehicle_command(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    v = Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    storage.add_vehicle(v)
    before = Vehicle.model_validate(v)
    v.name = "vv"
    stack = QUndoStack()
    stack.push(UpdateVehicleCommand(storage, v, before))
    assert storage.get_vehicle(v.id).name == "vv"
    stack.undo()
    assert storage.get_vehicle(v.id).name == "v"
    stack.redo()
    assert storage.get_vehicle(v.id).name == "vv"
