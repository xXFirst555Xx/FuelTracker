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
    storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=1,
            odo_before=0.0,
            odo_after=100.0,
            amount_spent=20.0,
            liters=10.0,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=1,
            odo_before=100.0,
            odo_after=300.0,
            amount_spent=40.0,
            liters=20.0,
        )
    )
    service = ReportService(storage)
    stats = service.calc_overall_stats()
    assert stats["total_distance"] == 300.0
    assert stats["total_liters"] == 30.0
    assert stats["total_price"] == 60.0
    assert stats["avg_consumption"] == pytest.approx((30.0 / 300.0) * 100)
    assert stats["cost_per_km"] == pytest.approx(60.0 / 300.0)


def test_generate_report_output(capsys, in_memory_storage):
    storage = in_memory_storage
    storage.add_entry(
        FuelEntry(
            entry_date=date.today(),
            vehicle_id=1,
            odo_before=0.0,
            odo_after=50.0,
            amount_spent=10.0,
            liters=5.0,
        )
    )
    service = ReportService(storage)
    service.generate_report()
    captured = capsys.readouterr()
    assert "total_distance" in captured.out
    assert "avg_consumption" in captured.out


def test_get_monthly_stats(in_memory_storage):
    storage = in_memory_storage
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 10),
            vehicle_id=1,
            odo_before=0,
            odo_after=100,
            amount_spent=10,
            liters=5,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, 20),
            vehicle_id=1,
            odo_before=100,
            odo_after=200,
            amount_spent=20,
            liters=8,
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 2, 1),
            vehicle_id=1,
            odo_before=200,
            odo_after=300,
            amount_spent=15,
            liters=7,
        )
    )
    service = ReportService(storage)
    stats = service.get_monthly_stats(date(2024, 1, 1), 1)
    assert stats["total_distance"] == 200.0
    assert stats["total_price"] == 30.0
    assert stats["total_liters"] == 13.0
    assert stats["avg_consumption"] == pytest.approx((13.0 / 200.0) * 100)
    assert stats["cost_per_km"] == pytest.approx(30.0 / 200.0)


def test_export_csv(tmp_path, in_memory_storage):
    storage = in_memory_storage
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 5, 1),
            vehicle_id=1,
            odo_before=0,
            odo_after=100,
            amount_spent=50,
            liters=20,
        )
    )
    service = ReportService(storage)
    csv_path = tmp_path / "report.csv"
    service.export_csv(date(2024, 5, 1), 1, csv_path)
    assert csv_path.exists()
    import pandas as pd

    df = pd.read_csv(csv_path)
    assert len(df) == 1
    assert df.loc[0, "distance"] == 100


def test_export_pdf(tmp_path, in_memory_storage):
    storage = in_memory_storage
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 5, 1),
            vehicle_id=1,
            odo_before=0,
            odo_after=100,
            amount_spent=50,
            liters=20,
        )
    )
    service = ReportService(storage)
    pdf_path = tmp_path / "report.pdf"
    service.export_pdf(date(2024, 5, 1), 1, pdf_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
