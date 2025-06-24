from datetime import date

import pytest

from src.models import FuelEntry
from src.services.validators import validate_entry


def test_odo_after_less_than_before_raises():
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=200.0,
        odo_after=100.0,
        amount_spent=50.0,
        liters=5.0,
    )
    with pytest.raises(ValueError):
        validate_entry(entry)


def test_liters_without_amount_raises():
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=0.0,
        odo_after=50.0,
        amount_spent=None,
        liters=5.0,
    )
    with pytest.raises(ValueError):
        validate_entry(entry)


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
