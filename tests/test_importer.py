from datetime import date
from pathlib import Path
import csv
from sqlalchemy import event
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

from src.models import FuelEntry, Vehicle
from src.services import StorageService, Exporter
from src.services.importer import Importer
from src.controllers.main_controller import MainController
from src.views import load_add_entry_dialog
from PySide6.QtWidgets import QDialog


def _new_storage():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return StorageService(engine=engine)


def test_importer_roundtrip(tmp_path: Path):
    src_storage = _new_storage()
    src_storage.add_vehicle(
        Vehicle(
            name="Car", vehicle_type="sedan", license_plate="A", tank_capacity_liters=40
        )
    )
    src_storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 6, 1),
            vehicle_id=1,
            odo_before=0,
            odo_after=100,
            liters=20,
            amount_spent=50,
        )
    )
    exporter = Exporter(src_storage)
    csv_path = tmp_path / "data.csv"
    exporter.monthly_csv(6, 2024, csv_path)

    dst_storage = _new_storage()
    dst_storage.add_vehicle(
        Vehicle(
            name="Car", vehicle_type="sedan", license_plate="A", tank_capacity_liters=40
        )
    )
    importer = Importer(dst_storage)
    entries = importer.import_csv(csv_path, 1)

    saved = dst_storage.list_entries()
    assert len(saved) == len(entries) == 1
    assert saved[0].odo_after == 100
    assert saved[0].liters == 20


def test_import_many_single_transaction(tmp_path: Path):
    storage = _new_storage()
    storage.add_vehicle(
        Vehicle(
            name="Car", vehicle_type="sedan", license_plate="A", tank_capacity_liters=40
        )
    )

    csv_path = tmp_path / "data.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "date",
                "odo_before",
                "odo_after",
                "liters",
                "amount_spent",
            ]
        )
        writer.writerow(["2024-06-01", "0", "100", "20", "50"])
        writer.writerow(["2024-06-02", "100", "200", "20", "50"])

    importer = Importer(storage)

    commit_count = 0

    def count_commit(session):
        nonlocal commit_count
        commit_count += 1

    event.listen(Session, "after_commit", count_commit)
    start = commit_count
    entries = importer.import_csv(csv_path, 1)
    event.remove(Session, "after_commit", count_commit)

    assert len(entries) == 2
    assert commit_count - start == 1


def test_prefill_odometer(qapp, tmp_path, monkeypatch):
    ctrl = MainController(db_path=tmp_path / "t.db")
    storage = ctrl.storage
    storage.add_vehicle(
        Vehicle(
            name="Car", vehicle_type="sedan", license_plate="A", tank_capacity_liters=40
        )
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 6, 1),
            vehicle_id=1,
            odo_before=0,
            odo_after=500,
            liters=20,
            amount_spent=50,
        )
    )

    dialog = load_add_entry_dialog()

    def fake_load():
        return dialog

    monkeypatch.setattr(
        "src.controllers.main_controller.load_add_entry_dialog", fake_load
    )

    def fake_exec():
        assert float(dialog.odoBeforeEdit.text()) == 500.0
        assert float(dialog.odoAfterEdit.text()) == 500.0
        return QDialog.Rejected

    monkeypatch.setattr(dialog, "exec", fake_exec)

    ctrl.open_add_entry_dialog()
