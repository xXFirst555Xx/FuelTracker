from __future__ import annotations

from datetime import date
from typing import Dict, Optional

from sqlmodel import Field, SQLModel


class FuelEntry(SQLModel, table=True):
    """Model representing a single refueling entry."""

    id: Optional[int] = Field(default=None, primary_key=True)
    entry_date: date
    distance: float  # kilometers travelled since last entry
    liters: float
    price: float  # total price for this refuel

    def calc_metrics(self) -> Dict[str, Optional[float]]:
        """Calculate simple metrics based on entry data."""
        metrics: Dict[str, Optional[float]] = {
            "price_per_liter": None,
            "liters_per_100km": None,
            "cost_per_km": None,
        }

        if self.liters > 0:
            metrics["price_per_liter"] = self.price / self.liters
        if self.distance > 0:
            metrics["liters_per_100km"] = (self.liters / self.distance) * 100
            metrics["cost_per_km"] = self.price / self.distance
        return metrics
