from decimal import Decimal
from datetime import date, timedelta
import requests

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QTimer
import pytest
from sqlmodel import Session, select

from src.services import oil_service

from src.services.oil_service import fetch_latest
from src.models import FuelPrice, Vehicle, FuelEntry
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


def test_amount_edit_triggers_autofill(main_controller, monkeypatch):
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
        dialog.amountEdit.setText("100")
        dialog.amountEdit.editingFinished.emit()
        return QDialog.Rejected

    monkeypatch.setattr(dialog, "exec", fake_exec)

    ctrl.open_add_entry_dialog()
    assert float(dialog.litersEdit.text()) == pytest.approx(2.0)
    assert not dialog.litersEdit.isEnabled()


def test_autofill_toggle_enables_edit(main_controller, monkeypatch):
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
        dialog.autoFillCheckBox.setChecked(False)
        return QDialog.Rejected

    monkeypatch.setattr(dialog, "exec", fake_exec)

    ctrl.open_add_entry_dialog()
    assert dialog.litersEdit.isEnabled()


def test_missing_price_enables_manual_liters(main_controller, monkeypatch):
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
        "src.controllers.main_controller.get_price", lambda *a, **k: None
    )

    def fake_exec():
        dialog.amountEdit.setText("100")
        dialog.amountEdit.editingFinished.emit()
        return QDialog.Rejected

    monkeypatch.setattr(dialog, "exec", fake_exec)

    ctrl.open_add_entry_dialog()
    assert dialog.litersEdit.isEnabled()


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


def test_purge_old_prices(in_memory_storage):
    with Session(in_memory_storage.engine) as s:
        old_day = date.today() - timedelta(days=40)
        s.add(
            FuelPrice(
                date=old_day,
                station="ptt",
                fuel_type="e20",
                name_th="E20",
                price=Decimal("40"),
            )
        )
        s.add(
            FuelPrice(
                date=date.today(),
                station="ptt",
                fuel_type="e20",
                name_th="E20",
                price=Decimal("41"),
            )
        )
        s.commit()
        oil_service.purge_old_prices(s, days=30)
        rows = s.exec(select(FuelPrice)).all()
        assert len(rows) == 1
        assert rows[0].date == date.today()


def test_fetch_latest_calls_purge(monkeypatch, in_memory_storage):
    monkeypatch.setattr(oil_service._HTTP_SESSION, "get", fake_get)
    called_purge = {}

    def fake_purge(session, days=None):
        called_purge["days"] = days

    monkeypatch.setattr(oil_service, "purge_old_prices", fake_purge)
    monkeypatch.setenv("OIL_PRICE_RETENTION_DAYS", "15")
    with Session(in_memory_storage.engine) as s:
        fetch_latest(s)
    assert called_purge["days"] is None  # fetch_latest passes None so helper reads env


def test_fetch_latest_updates_missing_liters(monkeypatch, in_memory_storage):
    monkeypatch.setattr(oil_service._HTTP_SESSION, "get", fake_get)
    with Session(in_memory_storage.engine) as s:
        s.add(
            Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
        )
        s.commit()
        entry = FuelEntry(
            entry_date=date(2024, 6, 1),
            vehicle_id=1,
            fuel_type="e20",
            odo_before=0.0,
            odo_after=10.0,
            amount_spent=88.0,
            liters=None,
        )
        s.add(entry)
        s.commit()
        fetch_latest(s)
        updated = s.get(FuelEntry, entry.id)
        assert updated is not None
        assert updated.liters == pytest.approx(2.0)


def test_get_price_fallback(in_memory_storage):
    day1 = date(2024, 6, 1)
    day2 = date(2024, 6, 3)
    with Session(in_memory_storage.engine) as s:
        s.add(
            FuelPrice(
                date=day1,
                station="ptt",
                fuel_type="e20",
                name_th="E20",
                price=Decimal("40"),
            )
        )
        s.commit()

        price = oil_service.get_price(s, "e20", "ptt", day2)
        assert price == Decimal("40")

