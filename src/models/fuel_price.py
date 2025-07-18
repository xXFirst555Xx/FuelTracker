"""Model storing daily fuel prices for each station and type."""

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import Index


class FuelPrice(SQLModel, table=True):
    """ราคาน้ำมันรายวันของสถานีและประเภทเชื้อเพลิง"""

    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime.date
    station: str
    fuel_type: str
    name_th: str
    price: Decimal

    __table_args__ = (
        Index(
            "ix_fuelprice_date_station_fuel_type",
            "date",
            "station",
            "fuel_type",
        ),
    )
