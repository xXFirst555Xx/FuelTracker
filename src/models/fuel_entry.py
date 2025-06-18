from __future__ import annotations

from datetime import date
from typing import Dict, Optional

from sqlmodel import Field, SQLModel


class FuelEntry(SQLModel, table=True):  # type: ignore[call-arg]
    """โมเดลแทนข้อมูลการเติมเชื้อเพลิงหนึ่งรายการ"""

    id: Optional[int] = Field(default=None, primary_key=True)
    entry_date: date
    vehicle_id: int
    fuel_type: Optional[str] = None
    odo_before: float
    #: Odometer reading after refueling. ``None`` when user didn't provide it.
    odo_after: Optional[float] = None
    #: Total money spent for the refuel. ``None`` for distance-only entries.
    amount_spent: Optional[float] = None
    #: Liters filled. Must be provided together with ``amount_spent``.
    liters: Optional[float] = None

    def calc_metrics(self) -> Dict[str, Optional[float]]:
        """คำนวณค่าต่าง ๆ เช่น ระยะทางและประสิทธิภาพ"""

        if self.odo_after is None:
            distance = None
        else:
            distance = self.odo_after - self.odo_before
        metrics: Dict[str, Optional[float]] = {
            "distance": distance,
            "cost_per_km": None,
            "fuel_efficiency_km_l": None,
        }

        if distance is not None and distance > 0:
            if self.amount_spent is not None:
                metrics["cost_per_km"] = self.amount_spent / distance
            if self.liters and self.liters > 0:
                metrics["fuel_efficiency_km_l"] = distance / self.liters

        return metrics
