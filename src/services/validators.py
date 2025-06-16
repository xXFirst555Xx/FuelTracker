from __future__ import annotations

from ..models import FuelEntry


def validate_entry(entry: FuelEntry) -> None:
    """ตรวจสอบ :class:`FuelEntry` ก่อนบันทึก"""
    if entry.odo_after is not None and entry.odo_after < entry.odo_before:
        raise ValueError("odo_after must be >= odo_before")
    if (entry.amount_spent is None) != (entry.liters is None):
        raise ValueError("amount_spent and liters must be given together or neither")
