import time
from types import MethodType
from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QFileDialog


def test_export_report_runs_async(qtbot, main_controller, tmp_path, monkeypatch):
    ctrl = main_controller
    qtbot.addWidget(ctrl.window)

    # Prevent the QMessageBox connected to the signal from blocking the test
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)

    csv_path = tmp_path / "out.csv"
    pdf_path = tmp_path / "out.pdf"

    def slow_csv(self, month, year, path):
        assert Path(path) == csv_path
        time.sleep(0.2)

    def slow_pdf(self, month, year, path):
        assert Path(path) == pdf_path
        time.sleep(0.2)

    monkeypatch.setattr(
        ctrl.exporter, "monthly_csv", MethodType(slow_csv, ctrl.exporter)
    )
    monkeypatch.setattr(
        ctrl.exporter, "monthly_pdf", MethodType(slow_pdf, ctrl.exporter)
    )

    calls = []

    def fake_get_save_file_name(*_a, **_k):
        if not calls:
            calls.append("csv")
            return str(csv_path), ""
        calls.append("pdf")
        return str(pdf_path), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", fake_get_save_file_name)

    start = time.monotonic()
    ctrl.export_report()
    elapsed = time.monotonic() - start
    assert elapsed < 0.05

    with qtbot.waitSignal(ctrl.export_finished, timeout=2000):
        pass


def test_export_report_failure_shows_error(
    qtbot, main_controller, tmp_path, monkeypatch
):
    ctrl = main_controller
    qtbot.addWidget(ctrl.window)

    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    error_called = {}
    monkeypatch.setattr(
        QMessageBox, "critical", lambda *a, **k: error_called.setdefault("c", True)
    )

    def fail_csv(self, *_a, **_k):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        ctrl.exporter, "monthly_csv", MethodType(fail_csv, ctrl.exporter)
    )
    monkeypatch.setattr(
        ctrl.exporter, "monthly_pdf", MethodType(lambda *a, **k: None, ctrl.exporter)
    )

    csv_path = tmp_path / "out.csv"
    pdf_path = tmp_path / "out.pdf"
    calls = []

    def fake_get_save_file_name(*_a, **_k):
        if not calls:
            calls.append("csv")
            return str(csv_path), ""
        calls.append("pdf")
        return str(pdf_path), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", fake_get_save_file_name)

    with qtbot.waitSignal(ctrl.export_failed, timeout=2000):
        ctrl.export_report()
    assert error_called.get("c")
