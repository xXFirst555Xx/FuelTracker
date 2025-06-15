from datetime import date
from PySide6.QtGui import QUndoStack
from PySide6.QtCore import QObject, Signal

from src.controllers.undo_commands import AddEntryCommand, DeleteEntryCommand
from src.models import FuelEntry, Vehicle
from src.services import StorageService


class Dummy(QObject):
    sig = Signal()


def test_add_and_undo_redo(in_memory_storage: StorageService):
    storage = in_memory_storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=0.0,
        odo_after=10.0,
        amount_spent=5.0,
        liters=1.0,
    )
    stack = QUndoStack()
    cmd = AddEntryCommand(storage, entry, Dummy().sig)
    stack.push(cmd)
    assert len(storage.list_entries()) == 1
    stack.undo()
    assert storage.list_entries() == []
    stack.redo()
    assert len(storage.list_entries()) == 1


def test_delete_and_undo_redo(in_memory_storage: StorageService):
    storage = in_memory_storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=0.0,
        odo_after=10.0,
        amount_spent=5.0,
        liters=1.0,
    )
    storage.add_entry(entry)
    stack = QUndoStack()
    cmd = DeleteEntryCommand(storage, entry.id, Dummy().sig)
    stack.push(cmd)
    assert storage.list_entries() == []
    stack.undo()
    assert len(storage.list_entries()) == 1
