from datetime import datetime, timedelta

from src.services import StorageService
from src.controllers.main_controller import MainController
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from PySide6.QtCore import QTimer
from pathlib import Path
from typing import Any
import sqlite3
import pytest
from src.services.storage_service import _SQLCIPHER_AVAILABLE
from src.models import Vehicle


def test_backup_rotation(tmp_path):
    db = tmp_path / "fuel.db"
    storage = StorageService(db_path=db)
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )
    now = datetime(2024, 1, 1, 0, 0)
    for i in range(35):
        backup = storage.auto_backup(
            now=now + timedelta(minutes=i), backup_dir=tmp_path, max_backups=30
        )
        if i == 0:
            with sqlite3.connect(backup) as conn:
                conn.execute("SELECT name FROM sqlite_master").fetchall()
            backup.unlink()
    backups = sorted(p for p in tmp_path.glob("*.db") if p.name != "fuel.db")
    assert len(backups) == 30
    first = backups[0].stem
    assert first == (now + timedelta(minutes=5)).strftime("%y-%m-%d_%H%M")


@pytest.mark.skipif(not _SQLCIPHER_AVAILABLE, reason="SQLCipher not available")
def test_encrypted_backup(tmp_path):
    db = tmp_path / "fuel.db"
    storage = StorageService(db_path=db, password="secret")
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )

    plain = storage.auto_backup(backup_dir=tmp_path)
    with sqlite3.connect(plain) as conn:
        conn.execute("SELECT name FROM sqlite_master").fetchall()

    enc = storage.auto_backup(backup_dir=tmp_path, encrypted=True)
    with pytest.raises(sqlite3.DatabaseError):
        sqlite3.connect(enc).execute("SELECT name FROM sqlite_master").fetchall()


def test_daily_backup_timer(qapp, tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    storage = StorageService(engine=engine)

    monkeypatch.setattr("src.hotkey.keyboard", None, raising=False)
    monkeypatch.setattr(
        "src.controllers.main_controller.StorageService", lambda *a, **k: storage
    )

    calls: dict[str, Any] = {}

    def fake_single_shot(ms: int, cb: callable) -> None:
        calls["ms"] = ms
        calls["cb"] = cb

    monkeypatch.setattr(QTimer, "singleShot", fake_single_shot)

    count = {"n": 0}

    def fake_backup() -> Path:
        count["n"] += 1
        return tmp_path / f"b{count['n']}.db"

    monkeypatch.setattr(storage, "auto_backup", fake_backup)

    ctrl = MainController()

    assert count["n"] == 1
    assert calls["ms"] == 86_400_000

    # simulate timer trigger
    calls["cb"]()
    assert count["n"] == 2
