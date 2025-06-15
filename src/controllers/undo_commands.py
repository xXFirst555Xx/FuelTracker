from __future__ import annotations

from PySide6.QtGui import QUndoCommand

from ..models import FuelEntry
from ..services import StorageService
from PySide6.QtCore import Signal


class AddEntryCommand(QUndoCommand):
    def __init__(
        self,
        storage: StorageService,
        entry: FuelEntry,
        signal: Signal | None = None,
    ) -> None:
        super().__init__("Add Entry")
        self.storage = storage
        self.entry = entry
        self.signal = signal

    def undo(self) -> None:
        if self.entry.id is not None:
            self.storage.delete_entry(self.entry.id)
        if self.signal is not None:
            try:
                self.signal.emit()
            except RuntimeError:
                pass

    def redo(self) -> None:
        # Recreate entry to ensure a fresh insert when redoing after an undo
        if self.entry.id is not None:
            data = self.entry.model_dump(exclude={"id"})
            self.entry = FuelEntry(**data)
        self.storage.add_entry(self.entry)
        if self.signal is not None:
            try:
                self.signal.emit()
            except RuntimeError:
                pass


class DeleteEntryCommand(QUndoCommand):
    def __init__(
        self,
        storage: StorageService,
        entry_id: int,
        signal: Signal | None = None,
    ) -> None:
        super().__init__("Delete Entry")
        self.storage = storage
        self.signal = signal
        self.entry = storage.get_entry(entry_id)

    def undo(self) -> None:
        if self.entry is not None:
            data = self.entry.model_dump(exclude={"id"})
            self.entry = FuelEntry(**data)
            self.storage.add_entry(self.entry)
        if self.signal is not None:
            try:
                self.signal.emit()
            except RuntimeError:
                pass

    def redo(self) -> None:
        if self.entry is not None and self.entry.id is not None:
            self.storage.delete_entry(self.entry.id)
        if self.signal is not None:
            try:
                self.signal.emit()
            except RuntimeError:
                pass
