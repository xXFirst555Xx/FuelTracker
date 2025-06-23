from __future__ import annotations

from pathlib import Path
from typing import List
import csv
import shutil

from ..models import FuelEntry
from .storage_service import StorageService
from .export_service import ExportService


class Exporter:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage
        self.export_service = ExportService(storage)

    def _entries(self, month: int, year: int) -> List[FuelEntry]:
        return self.storage.list_entries_for_month(year, month)

    def monthly_csv(self, month: int, year: int, path: Path) -> None:
        entries = self._entries(month, year)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                [
                    "date",
                    "fuel_type",
                    "odo_before",
                    "odo_after",
                    "distance",
                    "liters",
                    "amount_spent",
                ]
            )
            for e in entries:
                dist = e.odo_after - e.odo_before if e.odo_after is not None else ""
                writer.writerow(
                    [
                        e.entry_date.isoformat(),
                        e.fuel_type or "",
                        e.odo_before,
                        e.odo_after,
                        dist,
                        e.liters,
                        e.amount_spent,
                    ]
                )

    def monthly_pdf(self, month: int, year: int, path: Path) -> None:
        """Create a monthly PDF report via :class:`ExportService`."""
        tmp = self.export_service.export_monthly_pdf(f"{year}-{month:02d}", None)
        shutil.copy(tmp, path)

    def monthly_excel(self, month: int, year: int, path: Path) -> None:
        """Create a monthly Excel report via :class:`ExportService`."""
        tmp = self.export_service.export_monthly_xlsx(f"{year}-{month:02d}")
        shutil.copy(tmp, path)
