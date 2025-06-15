from __future__ import annotations

from datetime import date
from typing import Dict, Optional

from sqlmodel import Field, SQLModel


class FuelEntry(SQLModel, table=True):
    """โมเดลแทนข้อมูลการเติมเชื้อเพลิงหนึ่งรายการ"""

    id: Optional[int] = Field(default=None, primary_key=True)
    entry_date: date
    vehicle_id: int
    odo_before: float
    odo_after: float
    amount_spent: float
    liters: Optional[float] = None

    def calc_metrics(self) -> Dict[str, Optional[float]]:
        """คำนวณค่าต่าง ๆ เช่น ระยะทางและประสิทธิภาพ"""

        distance = self.odo_after - self.odo_before
        metrics: Dict[str, Optional[float]] = {
            "distance": distance,
            "cost_per_km": None,
            "fuel_efficiency_km_l": None,
        }

        if distance > 0:
            metrics["cost_per_km"] = self.amount_spent / distance
            if self.liters and self.liters > 0:
                metrics["fuel_efficiency_km_l"] = distance / self.liters

        return metrics
