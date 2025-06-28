from datetime import datetime, timedelta

from pathlib import Path
from typing import Any
import gzip
import sqlite3
import time

import pytest
from PySide6.QtCore import QTimer
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from src.services import StorageService
from src.controllers.main_controller import MainController
from src.services.storage_service import _SQLCIPHER_AVAILABLE
from src.models import Vehicle


def test_backup_rotation(tmp_path, monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *_args, **_kwargs: None)
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
            conn = sqlite3.connect(backup)
            try:
                conn.execute("SELECT name FROM sqlite_master").fetchall()
            finally:
                conn.close()

            for _ in range(5):
                try:
                    backup.unlink()
                    break
                except PermissionError:
                    time.sleep(0.1)
            else:
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


def test_compressed_backup(tmp_path):
    db = tmp_path / "fuel.db"
    storage = StorageService(db_path=db)
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )

    gz = storage.auto_backup(backup_dir=tmp_path, compress=True)
    assert gz.suffix == ".gz"
    tmp = tmp_path / "unpacked.db"
    with gzip.open(gz, "rb") as fh:
        tmp.write_bytes(fh.read())

    with sqlite3.connect(tmp) as conn:
        conn.execute("SELECT name FROM sqlite_master").fetchall()


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

    MainController()

    assert count["n"] == 1
    assert calls["ms"] == 86_400_000

    # simulate timer trigger
    calls["cb"]()
    assert count["n"] == 2


def test_daily_backup_handles_error(qapp, monkeypatch):
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

    def fail_backup() -> Path:
        raise sqlite3.DatabaseError("fail")

    monkeypatch.setattr(storage, "auto_backup", fail_backup)
    sync_calls: list[tuple[Path, Path]] = []
    monkeypatch.setattr(storage, "sync_to_cloud", lambda *a: sync_calls.append(a))

    MainController()

    assert calls["ms"] == 86_400_000
    assert not sync_calls

    # simulate timer trigger; should not raise
    calls["cb"]()
    assert not sync_calls
