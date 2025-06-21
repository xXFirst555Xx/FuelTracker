from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import Index


class Budget(SQLModel, table=True):  # type: ignore[misc]
    """งบประมาณรายเดือนของยานพาหนะ"""

    id: Optional[int] = Field(default=None, primary_key=True)
    vehicle_id: int
    amount: float

    __table_args__ = (Index("ix_budget_vehicle_id", "vehicle_id"),)
