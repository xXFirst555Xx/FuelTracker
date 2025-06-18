import time
from types import MethodType
from PySide6.QtWidgets import QMessageBox


def test_export_report_runs_async(qtbot, main_controller, monkeypatch):
    ctrl = main_controller
    qtbot.addWidget(ctrl.window)

    # Prevent the QMessageBox connected to the signal from blocking the test
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)

    def slow_csv(self, month, year, path):
        time.sleep(0.2)

    def slow_pdf(self, month, year, path):
        time.sleep(0.2)

    monkeypatch.setattr(
        ctrl.exporter, "monthly_csv", MethodType(slow_csv, ctrl.exporter)
    )
    monkeypatch.setattr(
        ctrl.exporter, "monthly_pdf", MethodType(slow_pdf, ctrl.exporter)
    )

    start = time.monotonic()
    ctrl.export_report()
    elapsed = time.monotonic() - start
    assert elapsed < 0.05

    with qtbot.waitSignal(ctrl.export_finished, timeout=2000):
        pass
