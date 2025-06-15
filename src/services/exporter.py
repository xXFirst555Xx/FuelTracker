from __future__ import annotations

from pathlib import Path
from typing import List
import csv
from reportlab.pdfgen import canvas

from ..models import FuelEntry
from .storage_service import StorageService


class Exporter:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    def _entries(self, month: int, year: int) -> List[FuelEntry]:
        entries = self.storage.list_entries()
        return [
            e
            for e in entries
            if e.entry_date.year == year and e.entry_date.month == month
        ]

    def monthly_csv(self, month: int, year: int, path: Path) -> None:
        entries = self._entries(month, year)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                [
                    "date",
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
                        e.odo_before,
                        e.odo_after,
                        dist,
                        e.liters,
                        e.amount_spent,
                    ]
                )

    def monthly_pdf(self, month: int, year: int, path: Path) -> None:
        entries = self._entries(month, year)
        c = canvas.Canvas(str(path))
        c.drawString(50, 800, f"Fuel report {year}-{month:02d}")
        y = 780
        for e in entries:
            dist = e.odo_after - e.odo_before if e.odo_after is not None else 0
            line = f"{e.entry_date} - {dist} km, {e.liters or 0} L, THB {e.amount_spent or 0}"
            c.drawString(50, y, line)
            y -= 20
        c.save()
