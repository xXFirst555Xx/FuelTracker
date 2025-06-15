from __future__ import annotations

from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Maintenance(SQLModel, table=True):
    """Scheduled maintenance task for a vehicle."""

    id: Optional[int] = Field(default=None, primary_key=True)
    vehicle_id: int
    name: str
    due_odo: Optional[int] = None
    due_date: Optional[date] = None
    note: Optional[str] = None
    is_done: bool = False
