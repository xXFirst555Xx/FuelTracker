from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class Vehicle(SQLModel, table=True):  # type: ignore[call-arg]
    """ยานพาหนะที่ลงทะเบียนในระบบ"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    vehicle_type: str
    license_plate: str
    tank_capacity_liters: float
