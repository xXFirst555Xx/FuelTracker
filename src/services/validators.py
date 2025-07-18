from __future__ import annotations

from ..models import FuelEntry


def validate_entry(entry: FuelEntry) -> None:
    """ตรวจสอบ :class:`FuelEntry` ก่อนบันทึก"""
    if entry.odo_after is not None and entry.odo_after < entry.odo_before:
        raise ValueError("ค่าเลขไมล์หลังเติมต้องมากกว่าหรือเท่ากับก่อนเติม")
    # ``liters`` cannot be stored without a corresponding ``amount_spent`` value.
    # When adding a new refuel entry the liters are calculated later, so
    # ``amount_spent`` may be provided without ``liters``.
    if entry.liters is not None and entry.amount_spent is None:
        raise ValueError("ต้องระบุจำนวนเงินเมื่อระบุจำนวนลิตร")
