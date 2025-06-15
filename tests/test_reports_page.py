from src.controllers.main_controller import MainController


def test_refresh_updates_summary(qtbot, tmp_path):
    ctrl = MainController(db_path=tmp_path / "t.db")
    page = ctrl.reports_page
    qtbot.addWidget(page)
    with qtbot.waitSignal(page.refresh_requested, timeout=2000):
        page.refresh_button.click()
    assert "km" in page.cards["distance"].value_label.text()
