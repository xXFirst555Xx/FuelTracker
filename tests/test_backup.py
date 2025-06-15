from datetime import datetime, timedelta

from src.services import StorageService
from src.models import Vehicle


def test_backup_rotation(tmp_path):
    db = tmp_path / "fuel.db"
    storage = StorageService(db_path=db)
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    now = datetime(2024, 1, 1, 0, 0)
    for i in range(35):
        storage.auto_backup(now=now + timedelta(minutes=i), backup_dir=tmp_path)
    backups = sorted(p for p in tmp_path.glob("*.db") if p.name != "fuel.db")
    assert len(backups) == 30
    first = backups[0].stem
    assert first == (now + timedelta(minutes=5)).strftime("%y-%m-%d_%H%M")
