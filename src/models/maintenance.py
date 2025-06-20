from __future__ import annotations

from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import Index


class Maintenance(SQLModel, table=True):
    """งานบำรุงรักษาที่กำหนดไว้ของยานพาหนะ"""

    id: Optional[int] = Field(default=None, primary_key=True)
    vehicle_id: int
    name: str
    due_odo: Optional[int] = None
    due_date: Optional[date] = None
    note: Optional[str] = None
    is_done: bool = False

    __table_args__ = (
        Index("ix_maintenance_vehicle_id", "vehicle_id"),
    )
