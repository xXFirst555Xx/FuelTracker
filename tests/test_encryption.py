import sqlite3
import pytest

from src.models import Vehicle
from src.services import StorageService


def test_encrypted_db_unreadable(tmp_path):
    db = tmp_path / "fuel.db"
    storage = StorageService(db_path=db, password="secret")
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    conn = sqlite3.connect(db)
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("select * from vehicle").fetchall()
