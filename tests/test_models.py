import pytest
from datetime import date
from src.models import FuelEntry


def test_calc_metrics_full():
    entry = FuelEntry(entry_date=date.today(), distance=100.0, liters=50.0, price=100.0)
    metrics = entry.calc_metrics()
    assert metrics["price_per_liter"] == pytest.approx(2.0)
    assert metrics["liters_per_100km"] == pytest.approx(50.0)
    assert metrics["cost_per_km"] == pytest.approx(1.0)


def test_calc_metrics_zero_liters():
    entry = FuelEntry(entry_date=date.today(), distance=100.0, liters=0.0, price=100.0)
    metrics = entry.calc_metrics()
    assert metrics["price_per_liter"] is None
    assert metrics["liters_per_100km"] == pytest.approx(0.0)
    assert metrics["cost_per_km"] == pytest.approx(1.0)


def test_calc_metrics_zero_distance():
    entry = FuelEntry(entry_date=date.today(), distance=0.0, liters=10.0, price=20.0)
    metrics = entry.calc_metrics()
    assert metrics["price_per_liter"] == pytest.approx(2.0)
    assert metrics["liters_per_100km"] is None
    assert metrics["cost_per_km"] is None
