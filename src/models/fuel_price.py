from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


class FuelPrice(SQLModel, table=True):
    """Daily fuel price for a given station and fuel type."""

    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    station: str
    fuel_type: str
    name_th: str
    price: Decimal
