from __future__ import annotations

from typing import List

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from .storage_service import StorageService
from ..models import FuelEntry


# FIX: mypy clean
def _monthly_data(
    entries: List[FuelEntry], year: int
) -> tuple[list[int], list[float], list[float], list[float]]:
    months = list(range(1, 13))
    distance = [0.0 for _ in months]
    liters = [0.0 for _ in months]

    for e in entries:
        if e.entry_date.year != year:
            continue
        idx = e.entry_date.month - 1
        if e.odo_after is not None:
            distance[idx] += e.odo_after - e.odo_before
        if e.liters:
            liters[idx] += e.liters
    km_per_l = [
        (dist / lit) if dist > 0 and lit > 0 else 0.0
        for dist, lit in zip(distance, liters)
    ]
    return months, distance, liters, km_per_l


def monthly_summary(storage: StorageService, year: int) -> Figure:
    """สร้างกราฟสรุปข้อมูลรายเดือนของหนึ่งปี"""
    entries = storage.list_entries()
    months, distance, liters, kmpl = _monthly_data(entries, year)

    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
    axes[0].bar(months, distance)
    axes[0].set_ylabel("กม.")
    axes[1].bar(months, liters)
    axes[1].set_ylabel("ลิตร")
    axes[2].bar(months, kmpl)
    axes[2].set_ylabel("กม./ลิตร")
    axes[2].set_xlabel("เดือน")
    fig.tight_layout()
    return fig


__all__ = ["monthly_summary"]
