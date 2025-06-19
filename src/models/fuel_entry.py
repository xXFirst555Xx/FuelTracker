from __future__ import annotations

from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class FuelEntry(SQLModel, table=True):
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

    def calc_metrics(self) -> dict[str, Optional[float]]:
        """Return basic calculated metrics for this entry."""

        distance: Optional[float]
        if self.odo_after is not None:
            distance = self.odo_after - self.odo_before
        else:
            distance = None

        cost_per_km: Optional[float]
        if (
            distance is not None
            and distance > 0
            and self.amount_spent is not None
        ):
            cost_per_km = self.amount_spent / distance
        else:
            cost_per_km = None

        fuel_eff: Optional[float]
        if (
            distance is not None
            and distance > 0
            and self.liters is not None
            and self.liters > 0
        ):
            fuel_eff = distance / self.liters
        else:
            fuel_eff = None

        return {
            "distance": distance,
            "cost_per_km": cost_per_km,
            "fuel_efficiency_km_l": fuel_eff,
        }
