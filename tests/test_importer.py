from datetime import date
from pathlib import Path
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from src.models import FuelEntry, Vehicle
from src.services import StorageService, Exporter
from src.services.importer import Importer


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
        Vehicle(name="Car", vehicle_type="sedan", license_plate="A", tank_capacity_liters=40)
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
        Vehicle(name="Car", vehicle_type="sedan", license_plate="A", tank_capacity_liters=40)
    )
    importer = Importer(dst_storage)
    entries = importer.import_csv(csv_path, 1)

    saved = dst_storage.list_entries()
    assert len(saved) == len(entries) == 1
    assert saved[0].odo_after == 100
    assert saved[0].liters == 20

