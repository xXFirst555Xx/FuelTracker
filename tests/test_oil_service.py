from decimal import Decimal

from PySide6.QtWidgets import QDialog
from sqlmodel import Session, select

import requests

from src.services.oil_service import fetch_latest
from src.models import FuelPrice, Vehicle
from src.controllers.main_controller import MainController
from src.views import load_add_entry_dialog

SAMPLE = {
    "date": "2024-06-01",
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
}


def fake_get(url: str):
    class R:
        def raise_for_status(self) -> None:
            pass

        def json(self):
            return SAMPLE

    return R()


def test_fetch_latest(monkeypatch, in_memory_storage):
    monkeypatch.setattr(requests, "get", fake_get)
    with Session(in_memory_storage.engine) as s:
        fetch_latest(s)
        rows = s.exec(select(FuelPrice)).all()
        assert len(rows) == 12


def test_autofill_liters(qapp, monkeypatch, tmp_path):
    ctrl = MainController(db_path=tmp_path / "t.db")
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

    def fake_exec(self: QDialog):
        self.amountEdit.setText("100")
        self.amountEdit.editingFinished.emit()
        return QDialog.Rejected

    monkeypatch.setattr(dialog, "exec", fake_exec)

    ctrl.open_add_entry_dialog()
    assert dialog.litersEdit.text() == "2.00"
