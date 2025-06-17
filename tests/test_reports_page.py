from src.controllers.main_controller import MainController
from src.models import Vehicle
from src.services.report_service import ReportService
import pandas as pd


def test_refresh_updates_summary(qtbot, tmp_path):
    ctrl = MainController(db_path=tmp_path / "t.db")
    page = ctrl.reports_page
    qtbot.addWidget(page)
    with qtbot.waitSignal(page.refresh_requested, timeout=2000):
        page.refresh_button.click()
    assert "km" in page.cards["distance"].value_label.text()


def test_monthly_tab_populates(qtbot, tmp_path):
    ctrl = MainController(db_path=tmp_path / "t.db")
    page = ctrl.reports_page
    qtbot.addWidget(page)
    with qtbot.waitSignal(page.refresh_requested, timeout=2000):
        page.refresh_button.click()
    assert page.monthly_layout.count() > 0


def test_refresh_clears_worker(qtbot, tmp_path):
    ctrl = MainController(db_path=tmp_path / "t.db")
    page = ctrl.reports_page
    qtbot.addWidget(page)
    with qtbot.waitSignal(page.refresh_requested, timeout=2000):
        page.refresh_button.click()
    qtbot.waitUntil(lambda: page._worker is None, timeout=2000)


def test_vehicle_selection_updates_monthly(qtbot, tmp_path, monkeypatch):
    ctrl = MainController(db_path=tmp_path / "t.db")
    storage = ctrl.storage
    storage.add_vehicle(
        Vehicle(name="v1", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    storage.add_vehicle(
        Vehicle(name="v2", vehicle_type="t", license_plate="y", tank_capacity_liters=1)
    )
    page = ctrl.reports_page
    page.vehicle_combo.blockSignals(True)
    page.vehicle_combo.clear()
    for v in storage.list_vehicles():
        page.vehicle_combo.addItem(v.name, v.id)
    page.vehicle_combo.blockSignals(False)
    qtbot.addWidget(page)

    called = {}

    def fake_monthly(self, month, vid):
        called["vid"] = vid
        return pd.DataFrame()

    monkeypatch.setattr(
        ctrl.report_service,
        "_monthly_df",
        fake_monthly.__get__(ctrl.report_service, ReportService),
    )

    with qtbot.waitSignal(page.refresh_requested, timeout=2000):
        page.vehicle_combo.setCurrentIndex(1)

    assert called.get("vid") == 2
