import pytest
from datetime import date
from src.models import FuelEntry


def test_calc_metrics_full():
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=1000.0,
        odo_after=1100.0,
        amount_spent=50.0,
        liters=10.0,
    )
    metrics = entry.calc_metrics()
    assert metrics["distance"] == pytest.approx(100.0)
    assert metrics["cost_per_km"] == pytest.approx(0.5)
    assert metrics["fuel_efficiency_km_l"] == pytest.approx(10.0)


def test_calc_metrics_no_liters():
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=200.0,
        odo_after=300.0,
        amount_spent=25.0,
        liters=None,
    )
    metrics = entry.calc_metrics()
    assert metrics["distance"] == pytest.approx(100.0)
    assert metrics["cost_per_km"] == pytest.approx(0.25)
    assert metrics["fuel_efficiency_km_l"] is None


def test_calc_metrics_zero_distance():
    entry = FuelEntry(
        entry_date=date.today(),
        vehicle_id=1,
        odo_before=500.0,
        odo_after=500.0,
        amount_spent=20.0,
        liters=10.0,
    )
    metrics = entry.calc_metrics()
    assert metrics["distance"] == pytest.approx(0.0)
    assert metrics["cost_per_km"] is None
    assert metrics["fuel_efficiency_km_l"] is None
