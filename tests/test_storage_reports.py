from datetime import date
import pandas as pd

from src.models import Vehicle, FuelEntry
from src.services import StorageService, ReportService
from src.constants import FUEL_TYPE_TH


def _add_vehicle(storage: StorageService) -> int:
    vehicle = Vehicle(
        name="Test", vehicle_type="car", license_plate="TST123", tank_capacity_liters=50.0
    )
    storage.add_vehicle(vehicle)
    assert vehicle.id is not None
    return vehicle.id


def test_monthly_totals(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vid = _add_vehicle(storage)

    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 1),
            vehicle_id=vid,
            odo_before=0,
            odo_after=100,
            liters=20,
            amount_spent=60,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 15),
            vehicle_id=vid,
            odo_before=100,
            odo_after=200,
            liters=30,
            amount_spent=90,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 2, 1),
            vehicle_id=vid,
            odo_before=200,
            odo_after=300,
            liters=40,
            amount_spent=100,
        )
    )

    result = storage.monthly_totals()
    assert result == [
        ("2024-01", 200.0, 50.0, 150.0),
        ("2024-02", 100.0, 40.0, 100.0),
    ]


def test_liters_by_fuel_type(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vid = _add_vehicle(storage)

    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 1),
            vehicle_id=vid,
            fuel_type="gasohol_95",
            odo_before=0,
            odo_after=100,
            liters=10,
            amount_spent=30,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 2),
            vehicle_id=vid,
            fuel_type="gasohol_95",
            odo_before=100,
            odo_after=200,
            liters=5,
            amount_spent=15,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 3),
            vehicle_id=vid,
            fuel_type="diesel",
            odo_before=200,
            odo_after=300,
            liters=8,
            amount_spent=24,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 4),
            vehicle_id=vid,
            fuel_type="diesel",
            odo_before=300,
            odo_after=400,
            liters=None,
            amount_spent=10,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 5),
            vehicle_id=vid,
            fuel_type=None,
            odo_before=400,
            odo_after=500,
            liters=2,
            amount_spent=6,
        )
    )

    result = storage.liters_by_fuel_type()
    assert result == {
        "gasohol_95": 15.0,
        "diesel": 8.0,
        None: 2.0,
    }


def test_last_year_summary(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vid = _add_vehicle(storage)

    # create entries spanning 13 months
    for i in range(13):
        year = 2023 + (i // 12)
        month = (i % 12) + 1
        storage.add_entry(
            FuelEntry(
                entry_date=date(year, month, 1),
                vehicle_id=vid,
                odo_before=i * 100,
                odo_after=i * 100 + 100,
                liters=10,
                amount_spent=20,
            )
        )

    service = ReportService(storage)
    df = service.last_year_summary()

    months = [pd.Period(f"2023-{m:02d}", freq="M") for m in range(2, 13)]
    months.append(pd.Period("2024-01", freq="M"))
    expected = pd.DataFrame(
        {
            "month": months,
            "distance": [100.0] * 12,
            "liters": [10.0] * 12,
            "amount_spent": [20.0] * 12,
            "km_per_l": [10.0] * 12,
        }
    )
    pd.testing.assert_frame_equal(df, expected)


def test_liters_by_type(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vid = _add_vehicle(storage)

    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 1),
            vehicle_id=vid,
            fuel_type="gasohol_95",
            odo_before=0,
            odo_after=100,
            liters=10,
            amount_spent=30,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 2),
            vehicle_id=vid,
            fuel_type="gasohol_95",
            odo_before=100,
            odo_after=200,
            liters=5,
            amount_spent=15,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 3),
            vehicle_id=vid,
            fuel_type="diesel",
            odo_before=200,
            odo_after=300,
            liters=8,
            amount_spent=24,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 5),
            vehicle_id=vid,
            fuel_type=None,
            odo_before=400,
            odo_after=500,
            liters=2,
            amount_spent=6,
        )
    )

    service = ReportService(storage)
    result = service.liters_by_type()
    expected = pd.Series(
        {
            FUEL_TYPE_TH.get("gasohol_95", "gasohol_95"): 15.0,
            FUEL_TYPE_TH.get("diesel", "diesel"): 8.0,
            FUEL_TYPE_TH.get("", ""): 2.0,
        }
    )
    pd.testing.assert_series_equal(result.sort_index(), expected.sort_index())
