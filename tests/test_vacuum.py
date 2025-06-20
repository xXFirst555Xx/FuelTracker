from datetime import date
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from src.models import FuelEntry, Vehicle
from src.services import StorageService


def _new_storage(threshold: int) -> StorageService:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return StorageService(engine=engine, vacuum_threshold=threshold)


def _add_vehicle(storage: StorageService) -> None:
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )


def _add_entry(storage: StorageService, odo_before: float, odo_after: float) -> None:
    storage.add_entry(
        FuelEntry(
            entry_date=date(2024, 1, int(odo_after / 100)),
            vehicle_id=1,
            odo_before=odo_before,
            odo_after=odo_after,
            amount_spent=50.0,
            liters=5.0,
        )
    )


def test_vacuum_called_after_threshold(monkeypatch) -> None:
    storage = _new_storage(2)
    _add_vehicle(storage)

    calls = {"n": 0}

    def fake_vacuum() -> None:
        calls["n"] += 1

    monkeypatch.setattr(storage, "vacuum", fake_vacuum)

    _add_entry(storage, 0, 100)
    assert calls["n"] == 0
    _add_entry(storage, 100, 200)
    assert calls["n"] == 1


def test_vacuum_executes_sql(monkeypatch) -> None:
    storage = _new_storage(1)
    _add_vehicle(storage)

    executed: list[str] = []
    real_connect = storage.engine.connect

    def connect():
        conn = real_connect()
        real_exec = conn.exec_driver_sql

        def exec_driver_sql(sql: str, *a, **k):
            executed.append(sql)
            return real_exec(sql, *a, **k)

        conn.exec_driver_sql = exec_driver_sql  # type: ignore[assignment]
        return conn

    monkeypatch.setattr(storage.engine, "connect", connect)

    _add_entry(storage, 0, 100)

    assert any(sql.strip().upper().startswith("VACUUM") for sql in executed)

