from __future__ import annotations

from datetime import date
from typing import Optional

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
