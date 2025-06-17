from src.config import AppConfig
from src.controllers.main_controller import MainController
from PySide6.QtCore import QTimer


def test_controller_reads_preferences(qapp, tmp_path, monkeypatch):
    cfg_path = tmp_path / "conf.json"
    AppConfig(default_station="bcp", update_hours=6, theme="dark").save(cfg_path)
    calls = {}

    def fake_single_shot(ms, cb):
        calls["ms"] = ms

    def fake_invoke(obj, func, conn):
        calls["invoked"] = True

    monkeypatch.setattr(QTimer, "singleShot", fake_single_shot)
    monkeypatch.setattr(MainController, "_load_prices", lambda self: None)
    monkeypatch.setattr(
        "src.controllers.main_controller.QMetaObject.invokeMethod",
        lambda obj, func, conn: fake_invoke(obj, func, conn),
    )

    ctrl = MainController(db_path=tmp_path / "t.db", config_path=cfg_path)
    monkeypatch.setattr(ctrl.thread_pool, "start", lambda job: job.run())
    monkeypatch.setattr(
        "src.controllers.main_controller.fetch_latest",
        lambda s, station: calls.setdefault("station", station),
    )
    ctrl._schedule_price_update()

    assert calls["ms"] == 6 * 3_600_000
    assert calls["station"] == "bcp"
    assert calls.get("invoked")
    assert ctrl.config.theme == "dark"
