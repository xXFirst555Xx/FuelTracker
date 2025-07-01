# ruff: noqa: E402
from pathlib import Path
import warnings

from matplotlib import font_manager

from reportlab.pdfbase import pdfmetrics

from src.services.export_service import ExportService

warnings.filterwarnings("ignore", category=DeprecationWarning, module="PyPDF2")

def test_build_pdf_fallback_on_canvas_error(tmp_path: Path, monkeypatch, in_memory_storage):
    service = ExportService(in_memory_storage)

    # Avoid real font loading
    monkeypatch.setattr(ExportService, "_get_font", lambda self: "Helvetica")

    def raise_canvas(*_a, **_k):
        raise Exception("boom")

    monkeypatch.setattr("src.services.export_service.Canvas", raise_canvas)

    out = tmp_path / "out.pdf"
    service._build_pdf(out, [])

    assert out.exists() and out.stat().st_size > 0


def test_get_font_returns_helvetica_on_ttfont_error(monkeypatch, in_memory_storage):
    service = ExportService(in_memory_storage)

    monkeypatch.setattr(font_manager, "findfont", lambda *a, **k: __file__)

    def raise_ttfont(*_a, **_k):
        raise Exception("bad font")

    monkeypatch.setattr("src.services.export_service.TTFont", raise_ttfont)
    monkeypatch.setattr(pdfmetrics, "registerFont", lambda *a, **k: None)

    assert service._get_font() == "Helvetica"
