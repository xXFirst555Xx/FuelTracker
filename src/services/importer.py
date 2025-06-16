from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List
import csv

from ..models import FuelEntry
from .storage_service import StorageService


class Importer:
    """Simple CSV importer for fuel entries."""

    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    def read_csv(self, path: Path) -> List[FuelEntry]:
        """Read entries from a CSV file without inserting them."""
        entries: List[FuelEntry] = []
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                try:
                    entry_date = date.fromisoformat(row.get("date", ""))
                    odo_before = float(row.get("odo_before", 0) or 0)
                except (ValueError, KeyError):
                    continue
                odo_after = row.get("odo_after") or None
                try:
                    odo_after_val = float(odo_after) if odo_after else None
                except ValueError:
                    odo_after_val = None
                liters = row.get("liters") or None
                try:
                    liters_val = float(liters) if liters else None
                except ValueError:
                    liters_val = None
                amount = row.get("amount_spent") or None
                try:
                    amount_val = float(amount) if amount else None
                except ValueError:
                    amount_val = None
                entry = FuelEntry(
                    entry_date=entry_date,
                    vehicle_id=0,  # updated by ``import_csv``
                    odo_before=odo_before,
                    odo_after=odo_after_val,
                    amount_spent=amount_val,
                    liters=liters_val,
                )
                entries.append(entry)
        return entries

    def import_csv(self, path: Path, vehicle_id: int) -> List[FuelEntry]:
        """Import entries from a CSV file for the given vehicle."""
        entries = self.read_csv(path)
        for e in entries:
            e.vehicle_id = vehicle_id
            self.storage.add_entry(e)
        return entries
