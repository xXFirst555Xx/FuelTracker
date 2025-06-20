from __future__ import annotations

from pathlib import Path
from typing import List
import csv
import pandas as pd
from reportlab.pdfgen import canvas

from ..models import FuelEntry
from .storage_service import StorageService


class Exporter:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

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
        entries = self._entries(month, year)
        c = canvas.Canvas(str(path))
        c.drawString(50, 800, f"Fuel report {year}-{month:02d}")
        y = 780
        for e in entries:
            dist = e.odo_after - e.odo_before if e.odo_after is not None else 0
            line = (
                f"{e.entry_date} - {dist} km, {e.liters or 0} L, THB {e.amount_spent or 0},"
                f" {e.fuel_type or ''}"
            )
            c.drawString(50, y, line)
            y -= 20
        c.save()

    def monthly_excel(self, month: int, year: int, path: Path) -> None:
        entries = self._entries(month, year)
        data = []
        for e in entries:
            dist = e.odo_after - e.odo_before if e.odo_after is not None else None
            data.append(
                {
                    "date": e.entry_date,
                    "fuel_type": e.fuel_type,
                    "odo_before": e.odo_before,
                    "odo_after": e.odo_after,
                    "distance": dist,
                    "liters": e.liters,
                    "amount_spent": e.amount_spent,
                }
            )
        df = pd.DataFrame(data)
        with pd.ExcelWriter(path) as writer:
            df.to_excel(writer, index=False)
