from datetime import date
import pytest
from src.models import FuelEntry
from src.services import ReportService


def test_calc_overall_stats_empty(in_memory_storage):
    service = ReportService(in_memory_storage)
    stats = service.calc_overall_stats()
    assert stats == {
        "total_distance": 0,
        "total_liters": 0,
        "total_price": 0,
        "avg_consumption": 0.0,
        "cost_per_km": 0.0,
    }


def test_calc_overall_stats(in_memory_storage):
    storage = in_memory_storage
    storage.add_entry(FuelEntry(entry_date=date.today(), distance=100.0, liters=10.0, price=20.0))
    storage.add_entry(FuelEntry(entry_date=date.today(), distance=200.0, liters=20.0, price=40.0))
    service = ReportService(storage)
    stats = service.calc_overall_stats()
    assert stats["total_distance"] == 300.0
    assert stats["total_liters"] == 30.0
    assert stats["total_price"] == 60.0
    assert stats["avg_consumption"] == pytest.approx((30.0 / 300.0) * 100)
    assert stats["cost_per_km"] == pytest.approx(60.0 / 300.0)


def test_generate_report_output(capsys, in_memory_storage):
    storage = in_memory_storage
    storage.add_entry(FuelEntry(entry_date=date.today(), distance=50.0, liters=5.0, price=10.0))
    service = ReportService(storage)
    service.generate_report()
    captured = capsys.readouterr()
    assert "total_distance" in captured.out
    assert "avg_consumption" in captured.out
