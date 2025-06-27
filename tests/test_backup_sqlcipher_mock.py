import importlib
import sqlite3
import sys
import types

from src.models import Vehicle


def test_auto_backup_with_mocked_sqlcipher(tmp_path, monkeypatch):
    """Backup with encrypted=True using mocked SQLCipher backend."""

    class FakeConn(sqlite3.Connection):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.filename = a[0] if a else kw.get("database")

        def close(self) -> None:  # type: ignore[override]
            super().close()
            with open(self.filename, "r+b") as fh:
                header = fh.read(16)
                fh.seek(0)
                fh.write(b"XXXX" + header[4:])

    def fake_connect(db: str, *a: object, **kw: object) -> FakeConn:
        kw["factory"] = FakeConn
        return sqlite3.connect(db, *a, **kw)

    fake_dbapi2 = types.ModuleType("dbapi2")
    fake_dbapi2.connect = fake_connect  # type: ignore[attr-defined]
    fake_dbapi2.Connection = FakeConn
    fake_pkg = types.ModuleType("pysqlcipher3")
    fake_pkg.dbapi2 = fake_dbapi2

    monkeypatch.setitem(sys.modules, "pysqlcipher3", fake_pkg)
    monkeypatch.setitem(sys.modules, "pysqlcipher3.dbapi2", fake_dbapi2)

    from src.services import storage_service as ss

    importlib.reload(ss)

    assert ss._SQLCIPHER_AVAILABLE is True

    storage = ss.StorageService(db_path=tmp_path / "fuel.db", password="secret")
    storage.add_vehicle(
        Vehicle(name="v", vehicle_type="t", license_plate="x", tank_capacity_liters=1)
    )

    backup = storage.auto_backup(backup_dir=tmp_path, encrypted=True)

    assert backup.exists()
    with open(backup, "rb") as fh:
        assert not fh.read(16).startswith(b"SQLite format")
