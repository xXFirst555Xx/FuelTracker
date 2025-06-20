from decimal import Decimal
import requests

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QTimer
from sqlmodel import Session, select

from src.services import oil_service

from src.services.oil_service import fetch_latest
import os
from src.models import FuelPrice, Vehicle
from src.controllers.main_controller import MainController
from src.views import load_add_entry_dialog

SAMPLE = {
    "status": "success",
    "response": {
        "date": "1 มิถุนายน 2567",
        "stations": {
            "ptt": {
                "g95": {"name_th": "G95", "price": 50},
                "g91": {"name_th": "G91", "price": 48},
                "e20": {"name_th": "E20", "price": 44},
                "e85": {"name_th": "E85", "price": 40},
                "diesel": {"name_th": "Diesel", "price": 32},
                "b7": {"name_th": "B7", "price": 33},
            },
            "bcp": {
                "g95": {"name_th": "G95", "price": 49},
                "g91": {"name_th": "G91", "price": 47},
                "e20": {"name_th": "E20", "price": 43},
                "e85": {"name_th": "E85", "price": 39},
                "diesel": {"name_th": "Diesel", "price": 31},
                "b7": {"name_th": "B7", "price": 32},
            },
        },
    },
}


called: dict[str, str] = {}

def fake_get(url: str, timeout: int | None = None):
    called["url"] = url

    class R:
        def raise_for_status(self) -> None:
            pass

        def json(self):
            return SAMPLE

    return R()


def test_fetch_latest(monkeypatch, in_memory_storage):
    monkeypatch.setattr(oil_service._HTTP_SESSION, "get", fake_get)
    with Session(in_memory_storage.engine) as s:
        fetch_latest(s, api_base="http://test/api")
        rows = s.exec(select(FuelPrice)).all()
        assert len(rows) == 12
        assert called["url"].startswith("http://test/api")


def test_fetch_latest_env(monkeypatch, in_memory_storage):
    monkeypatch.setattr(oil_service._HTTP_SESSION, "get", fake_get)
    monkeypatch.setenv("OIL_API_BASE", "http://env/api")
    called.clear()
    with Session(in_memory_storage.engine) as s:
        fetch_latest(s)
        assert called["url"].startswith("http://env/api")


def test_autofill_liters(main_controller, monkeypatch):
    ctrl = main_controller
    ctrl.storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )

    dialog = load_add_entry_dialog()

    def fake_load():
        return dialog

    monkeypatch.setattr(
        "src.controllers.main_controller.load_add_entry_dialog", fake_load
    )
    monkeypatch.setattr(
        "src.controllers.main_controller.get_price", lambda *a, **k: Decimal("50")
    )

    def fake_exec():
        return QDialog.Rejected

    monkeypatch.setattr(dialog, "exec", fake_exec)

    ctrl.open_add_entry_dialog()
    assert not dialog.litersEdit.isEnabled()
    assert not dialog.odoAfterEdit.isEnabled()


def test_price_update_handles_error(main_controller, monkeypatch):
    ctrl = main_controller

    monkeypatch.setattr(ctrl.thread_pool, "start", lambda job: job.run())
    called = {}

    def fake_single_shot(*a, **k):
        called["scheduled"] = True

    monkeypatch.setattr(QTimer, "singleShot", fake_single_shot)
    monkeypatch.setattr(MainController, "_load_prices", lambda self: None)
    monkeypatch.setattr(
        "src.controllers.main_controller.QMetaObject.invokeMethod",
        lambda *a, **k: called.setdefault("invoked", True),
    )

    def raise_error(*_a, **_k):
        raise requests.RequestException("fail")

    monkeypatch.setattr(oil_service._HTTP_SESSION, "get", lambda *a, **k: raise_error())

    ctrl._schedule_price_update()
    assert called.get("scheduled")
