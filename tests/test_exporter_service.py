from datetime import date
from pathlib import Path

from src.models import FuelEntry, Vehicle
from src.services import StorageService
from src.services.exporter import Exporter


def test_exporter_creates_files(
    tmp_path: Path, in_memory_storage: StorageService
) -> None:
    storage = in_memory_storage
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 5, 1),
            vehicle_id=1,
            odo_before=0,
            odo_after=100,
            amount_spent=50,
            liters=20,
        )
    )
    exporter = Exporter(storage)
    csv_path = tmp_path / "out.csv"
    pdf_path = tmp_path / "out.pdf"
    xls_path = tmp_path / "out.xlsx"
    exporter.monthly_csv(5, 2024, csv_path)
    exporter.monthly_pdf(5, 2024, pdf_path)
    exporter.monthly_excel(5, 2024, xls_path)
    assert csv_path.exists()
    assert pdf_path.exists()
    assert xls_path.exists()
    assert pdf_path.stat().st_size > 0
