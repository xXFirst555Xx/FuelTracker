from datetime import date

import pytest

from src.models import FuelEntry
from src.services.storage_service import StorageService
from src.services.validators import validate_entry


@pytest.mark.parametrize(
    "odo_before, odo_after, amount_spent, liters, message",
    [
        (200.0, 100.0, 50.0, 5.0, "ค่าเลขไมล์หลังเติมต้องมากกว่าหรือเท่ากับก่อนเติม"),
        (0.0, 50.0, None, 5.0, "ต้องระบุจำนวนเงินเมื่อระบุจำนวนลิตร"),
    ],
)
def test_invalid_entries_raise(
    odo_before: float,
    odo_after: float | None,
    amount_spent: float | None,
    liters: float | None,
    message: str,
    in_memory_storage: StorageService,
) -> None:
    """Ensure invalid entries fail validation both directly and via storage."""
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=odo_before,
        odo_after=odo_after,
        amount_spent=amount_spent,
        liters=liters,
    )

    with pytest.raises(ValueError, match=message):
        validate_entry(entry)

    with pytest.raises(ValueError, match=message):
        in_memory_storage.add_entry(entry)


def test_valid_entry_passes():
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=100.0,
        odo_after=150.0,
        amount_spent=20.0,
        liters=2.0,
    )
    # Should not raise any errors
    validate_entry(entry)
