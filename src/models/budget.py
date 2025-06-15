from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class Budget(SQLModel, table=True):
    """Monthly budget per vehicle."""

    id: Optional[int] = Field(default=None, primary_key=True)
    vehicle_id: int
    amount: float
