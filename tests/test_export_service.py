from datetime import date
from pathlib import Path

import matplotlib
from matplotlib import font_manager
import matplotlib.pyplot as plt
import pandas as pd
import warnings
from PyPDF2 import PdfReader
from reportlab.pdfbase import pdfmetrics

from src.models import FuelEntry, Vehicle
from src.services.export_service import ExportService
from src.services.storage_service import StorageService

warnings.filterwarnings("ignore", category=DeprecationWarning, module="PyPDF2")


def _populate(storage: StorageService, count: int = 80) -> None:
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    for i in range(count):
        day = (i % 30) + 1
        storage.add_entry(
            FuelEntry(
                entry_date=date(2024, 1, day),
                vehicle_id=1,
                odo_before=i * 10,
                odo_after=(i + 1) * 10,
                liters=5.0,
                amount_spent=10.0,
            )
        )


def test_export_service_outputs(
    tmp_path: Path, in_memory_storage: StorageService
) -> None:
    storage = in_memory_storage
    _populate(storage)
    service = ExportService(storage)
    pdf_path = service.export_monthly_pdf("2024-01", None)
    xls_path = service.export_monthly_xlsx("2024-01")

    assert pdf_path.exists()
    assert xls_path.exists()

    reader = PdfReader(pdf_path)
    assert len(reader.pages) >= 3
    text = "".join(page.extract_text() or "" for page in reader.pages)
    assert text.strip()

    xls = pd.ExcelFile(xls_path)
    assert len(xls.sheet_names) >= 2

    weekly_sheet = next((s for s in xls.sheet_names if "weekly" in s.lower()), None)
    summary_sheet = next((s for s in xls.sheet_names if "summary" in s.lower()), None)
    assert weekly_sheet is not None
    assert summary_sheet is not None

    df_weekly = pd.read_excel(xls_path, sheet_name=weekly_sheet)
    for col in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        assert col in df_weekly.columns

    df_summary = pd.read_excel(xls_path, sheet_name=summary_sheet)
    assert {"metric", "value"}.issubset(df_summary.columns)
    for field in ["distance", "liters", "km_per_l"]:
        assert field in df_summary["metric"].values

    assert matplotlib.get_backend().lower() == "agg"


def test_cleanup_removes_tmpdirs(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    _populate(storage, count=10)
    service = ExportService(storage)
    pdf_path = service.export_monthly_pdf("2024-01", None)
    xls_path = service.export_monthly_xlsx("2024-01")

    # capture temporary directories before cleanup
    tmp_dirs = [Path(tmp.name) for tmp in service._tmpdirs]
    assert pdf_path.exists()
    assert xls_path.exists()
    assert all(p.exists() for p in tmp_dirs)

    service.cleanup()

    for p in tmp_dirs:
        assert not p.exists()
    assert service._tmpdirs == []


def test_get_font_fallback_when_findfont_fails(monkeypatch, in_memory_storage):
    service = ExportService(in_memory_storage)

    def fake_findfont(name, *args, **kwargs):
        if name == "Noto Sans Thai":
            raise RuntimeError("missing")
        return __file__

    monkeypatch.setattr(font_manager, "findfont", fake_findfont)
    monkeypatch.setattr("src.services.export_service.TTFont", lambda *a, **k: object())
    monkeypatch.setattr(pdfmetrics, "registerFont", lambda *a, **k: None)

    assert service._get_font() == "Tahoma"


def test_get_font_returns_helvetica_on_register_error(monkeypatch, in_memory_storage):
    service = ExportService(in_memory_storage)

    monkeypatch.setattr(font_manager, "findfont", lambda *a, **k: __file__)
    monkeypatch.setattr("src.services.export_service.TTFont", lambda *a, **k: object())

    def raise_reg(*_a, **_k):
        raise Exception("boom")

    monkeypatch.setattr(pdfmetrics, "registerFont", raise_reg)

    assert service._get_font() == "Helvetica"


def test_build_pdf_handles_font_errors(tmp_path, monkeypatch, in_memory_storage):
    service = ExportService(in_memory_storage)

    monkeypatch.setattr(font_manager, "findfont", lambda *a, **k: __file__)
    monkeypatch.setattr("src.services.export_service.TTFont", lambda *a, **k: object())

    def raise_reg(*_a, **_k):
        raise Exception("boom")

    monkeypatch.setattr(pdfmetrics, "registerFont", raise_reg)

    out = tmp_path / "out.pdf"

    service._build_pdf(out, [lambda c, f: c.drawString(10, 10, "x")])

    assert out.exists() and out.stat().st_size > 0


def test_plot_dual_axis_empty_df(monkeypatch, in_memory_storage):
    service = ExportService(in_memory_storage)
    fig = plt.Figure()
    df = pd.DataFrame()

    service._plot_dual_axis(fig, df)

    assert fig.axes  # ensures axes were created without error
