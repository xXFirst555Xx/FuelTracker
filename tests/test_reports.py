from datetime import date, timedelta
import logging
import pytest
from src.models import FuelEntry
from src.services import ReportService
from fpdf import FPDF


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


def test_generate_report_output(caplog, in_memory_storage):
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
    with caplog.at_level(logging.INFO):
        service.generate_report()
    assert "total_distance" in caplog.text
    assert "avg_consumption" in caplog.text


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


def test_export_excel(tmp_path, in_memory_storage):
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
    xls_path = tmp_path / "report.xlsx"
    service.export_excel(date(2024, 5, 1), 1, xls_path)
    assert xls_path.exists()


def test_export_pdf_cleanup_on_error(tmp_path, in_memory_storage, monkeypatch):
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

    def fail_output(self, *args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(FPDF, "output", fail_output)

    with pytest.raises(RuntimeError):
        service.export_pdf(date(2024, 5, 1), 1, pdf_path)

    chart_file = pdf_path.with_suffix(".png")
    assert not chart_file.exists()


def test_calc_overall_stats_large(in_memory_storage):
    storage = in_memory_storage
    total_distance = 0.0
    total_liters = 0.0
    total_price = 0.0
    day = date(2024, 1, 1)
    for i in range(50):
        e = FuelEntry(
            entry_date=day + timedelta(days=i),
            vehicle_id=1,
            odo_before=i * 10.0,
            odo_after=(i + 1) * 10.0,
            amount_spent=20.0,
            liters=5.0,
        )
        storage.add_entry(e)
        total_distance += 10.0
        total_liters += 5.0
        total_price += 20.0

    for i in range(10):
        storage.add_entry(
            FuelEntry(
                entry_date=day + timedelta(days=100 + i),
                vehicle_id=1,
                odo_before=0,
                odo_after=None,
                amount_spent=30.0,
                liters=3.0,
            )
        )
        total_price += 30.0

    service = ReportService(storage)
    stats = service.calc_overall_stats()
    assert stats["total_distance"] == total_distance
    # all but the last distance-only entry have odo_after filled to 0 by
    # add_entry(), so their liters count toward the total
    total_liters += 9 * 3.0
    assert stats["total_liters"] == total_liters
    assert stats["total_price"] == total_price


def test_monthly_summary_large(in_memory_storage):
    storage = in_memory_storage
    start = date(2023, 1, 1)
    entries = []
    for m in range(1, 13):
        for i in range(3):
            d = start.replace(month=m, day=i + 1)
            e = FuelEntry(
                entry_date=d,
                vehicle_id=1,
                odo_before=i * 100 + (m - 1) * 1000,
                odo_after=i * 100 + (m - 1) * 1000 + 100,
                liters=10.0,
                amount_spent=25.0,
            )
            storage.add_entry(e)
            entries.append(e)

    service = ReportService(storage)
    result = service.monthly_summary()

    import pandas as pd

    data = []
    for e in entries:
        dist = e.odo_after - e.odo_before
        data.append({"date": e.entry_date, "distance": dist, "liters": e.liters})
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    expected = df.groupby("month")[["distance", "liters"]].sum().sort_index()
    expected["km_per_l"] = expected["distance"] / expected["liters"]
    expected = expected.reset_index()

    pd.testing.assert_frame_equal(result, expected)
