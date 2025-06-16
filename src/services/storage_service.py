"""บริการจัดการการบันทึกข้อมูลด้วย SQLModel"""

from pathlib import Path
from datetime import datetime
from typing import List, Optional
import os
import shutil
from getpass import getpass

try:
    from pysqlcipher3 import dbapi2 as sqlcipher  # type: ignore

    _SQLCIPHER_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - fallback when dependency missing
    import sqlite3 as sqlcipher

    _SQLCIPHER_AVAILABLE = False

from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.engine import Engine

from ..models import FuelEntry, Vehicle, Budget, Maintenance, FuelPrice
from .validators import validate_entry


def _is_plain_sqlite(path: Path) -> bool:
    with open(path, "rb") as fh:
        header = fh.read(16)
    return header.startswith(b"SQLite format 3")


def _migrate_plain_to_encrypted(path: Path, password: str) -> None:
    if not _SQLCIPHER_AVAILABLE:
        return

    tmp = path.with_suffix(".tmp")
    conn = sqlcipher.connect(str(tmp))
    conn.execute(f"PRAGMA key='{password}';")
    conn.execute(f"ATTACH DATABASE '{path}' AS plaintext KEY '';")
    conn.execute("SELECT sqlcipher_export('main', 'plaintext');")
    conn.execute("DETACH DATABASE plaintext;")
    conn.close()
    os.replace(tmp, path)


class _ConnProxy:
    def __init__(self, conn: sqlcipher.Connection) -> None:
        self._conn = conn

    def __getattr__(self, name: str):
        return getattr(self._conn, name)

    def create_function(self, name, num_params, func, deterministic=None):
        if deterministic is not None:
            self._conn.create_function(
                name, num_params, func, deterministic=deterministic
            )
        else:
            self._conn.create_function(name, num_params, func)


class StorageService:
    def __init__(
        self,
        db_path: str | Path = "fuel.db",
        engine: Engine | None = None,
        password: str | None = None,
    ) -> None:
        """เริ่มต้นบริการจัดเก็บข้อมูล

        พารามิเตอร์
        ----------
        db_path: str | Path
            เส้นทางไปยังไฟล์ฐานข้อมูล SQLite ไม่ใช้ถ้ากำหนด ``engine``
        engine: Engine | None
            ออบเจ็กต์ Engine ที่เตรียมไว้ (ไม่บังคับ)
        """

        if engine is not None:
            self.engine = engine
            self._db_path = Path(engine.url.database) if engine.url.database else None
        else:
            db_path = Path(db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            if password is None:
                if _SQLCIPHER_AVAILABLE:
                    password = os.environ.get("FT_DB_PASSWORD") or getpass(
                        "DB password: "
                    )
                else:
                    password = ""
            self._password = password

            if password and db_path.exists() and _is_plain_sqlite(db_path):
                _migrate_plain_to_encrypted(db_path, password)

            def _connect() -> sqlcipher.Connection:
                raw = sqlcipher.connect(str(db_path))
                if _SQLCIPHER_AVAILABLE:
                    raw.execute(f"PRAGMA key='{password}';")
                return _ConnProxy(raw)

            self.engine = create_engine(
                "sqlite://",
                creator=_connect,
                connect_args={"check_same_thread": False},
            )
            self._db_path = db_path

        SQLModel.metadata.create_all(
            self.engine,
            tables=[
                FuelEntry.__table__,
                Vehicle.__table__,
                Budget.__table__,
                Maintenance.__table__,
                FuelPrice.__table__,
            ],
        )

    def add_entry(self, entry: FuelEntry) -> None:
        validate_entry(entry)
        with Session(self.engine) as session:
            # If there is an older entry for the same vehicle without
            # ``odo_after`` set, fill it with the new ``odo_before`` value.
            statement = (
                select(FuelEntry)
                .where(
                    FuelEntry.vehicle_id == entry.vehicle_id,
                    FuelEntry.odo_after.is_(None),
                )
                .order_by(FuelEntry.entry_date.desc(), FuelEntry.id.desc())
            )
            prev = session.exec(statement).first()
            if prev is not None:
                prev.odo_after = entry.odo_before
                session.add(prev)

            session.add(entry)
            session.commit()
            session.refresh(entry)

    def add_vehicle(self, vehicle: Vehicle) -> None:
        with Session(self.engine) as session:
            session.add(vehicle)
            session.commit()
            session.refresh(vehicle)

    def list_entries(self) -> List[FuelEntry]:
        with Session(self.engine) as session:
            statement = select(FuelEntry)
            return list(session.exec(statement))

    def list_vehicles(self) -> List[Vehicle]:
        with Session(self.engine) as session:
            statement = select(Vehicle)
            return list(session.exec(statement))

    def get_vehicle(self, vehicle_id: int) -> Optional[Vehicle]:
        """ดึงข้อมูลยานพาหนะตามรหัส"""
        with Session(self.engine) as session:
            return session.get(Vehicle, vehicle_id)

    def update_vehicle(self, vehicle: Vehicle) -> None:
        """บันทึกการแก้ไขข้อมูลยานพาหนะ"""
        with Session(self.engine) as session:
            session.add(vehicle)
            session.commit()
            session.refresh(vehicle)

    def delete_vehicle(self, vehicle_id: int) -> None:
        """ลบยานพาหนะออกจากฐานข้อมูล"""
        with Session(self.engine) as session:
            obj = session.get(Vehicle, vehicle_id)
            if obj:
                session.delete(obj)
                session.commit()

    def get_entries_by_vehicle(self, vehicle_id: int) -> List[FuelEntry]:
        """คืนรายการทั้งหมดของยานพาหนะที่กำหนด"""
        with Session(self.engine) as session:
            statement = select(FuelEntry).where(FuelEntry.vehicle_id == vehicle_id)
            return list(session.exec(statement))

    def get_entry(self, entry_id: int) -> Optional[FuelEntry]:
        """ดึงข้อมูลการเติมน้ำมันตามรหัส"""
        with Session(self.engine) as session:
            return session.get(FuelEntry, entry_id)

    def update_entry(self, entry: FuelEntry) -> None:
        """บันทึกการแก้ไขข้อมูลการเติมน้ำมัน"""
        validate_entry(entry)
        with Session(self.engine) as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)

    def delete_entry(self, entry_id: int) -> None:
        """ลบข้อมูลการเติมน้ำมันออกจากฐานข้อมูล"""
        with Session(self.engine) as session:
            obj = session.get(FuelEntry, entry_id)
            if obj:
                session.delete(obj)
                session.commit()

    # ------------------------------------------------------------------
    # Maintenance helpers
    # ------------------------------------------------------------------

    def add_maintenance(self, task: Maintenance) -> None:
        with Session(self.engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)

    def list_maintenances(self, vehicle_id: int | None = None) -> List[Maintenance]:
        with Session(self.engine) as session:
            stmt = select(Maintenance)
            if vehicle_id is not None:
                stmt = stmt.where(Maintenance.vehicle_id == vehicle_id)
            return list(session.exec(stmt))

    def get_maintenance(self, task_id: int) -> Maintenance | None:
        with Session(self.engine) as session:
            return session.get(Maintenance, task_id)

    def update_maintenance(self, task: Maintenance) -> None:
        with Session(self.engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)

    def mark_maintenance_done(self, task_id: int, done: bool = True) -> None:
        with Session(self.engine) as session:
            task = session.get(Maintenance, task_id)
            if task is None:
                return
            task.is_done = done
            session.add(task)
            session.commit()
            session.refresh(task)

    def delete_maintenance(self, task_id: int) -> None:
        with Session(self.engine) as session:
            obj = session.get(Maintenance, task_id)
            if obj:
                session.delete(obj)
                session.commit()

    def list_due_maintenances(
        self,
        vehicle_id: int,
        odo: float | None = None,
        date_: datetime | None = None,
    ) -> List[Maintenance]:
        with Session(self.engine) as session:
            stmt = select(Maintenance).where(
                Maintenance.vehicle_id == vehicle_id,
                Maintenance.is_done.is_(False),
            )
            res = []
            for m in session.exec(stmt):
                if m.due_odo is not None and odo is not None and odo >= m.due_odo:
                    res.append(m)
                elif (
                    m.due_date is not None and date_ is not None and date_ >= m.due_date
                ):
                    res.append(m)
            return res

    # ------------------------------------------------------------------
    # Budget helpers
    # ------------------------------------------------------------------

    def set_budget(self, vehicle_id: int, amount: float) -> None:
        """ตั้งงบประมาณรายเดือนของยานพาหนะ"""
        with Session(self.engine) as session:
            budget = session.exec(
                select(Budget).where(Budget.vehicle_id == vehicle_id)
            ).first()
            if budget is None:
                budget = Budget(vehicle_id=vehicle_id, amount=amount)
            else:
                budget.amount = amount
            session.add(budget)
            session.commit()

    def get_budget(self, vehicle_id: int) -> Optional[float]:
        with Session(self.engine) as session:
            budget = session.exec(
                select(Budget.amount).where(Budget.vehicle_id == vehicle_id)
            ).first()
            return float(budget) if budget is not None else None

    def get_total_spent(self, vehicle_id: int, year: int, month: int) -> float:
        with Session(self.engine) as session:
            statement = select(FuelEntry.amount_spent).where(
                FuelEntry.vehicle_id == vehicle_id,
                FuelEntry.entry_date.between(
                    f"{year}-{month:02d}-01", f"{year}-{month:02d}-31"
                ),
                FuelEntry.amount_spent.is_not(None),
            )
            amounts = [a for a in session.exec(statement) if a is not None]
            return float(sum(amounts))

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def auto_backup(
        self,
        now: datetime | None = None,
        backup_dir: Path | None = None,
    ) -> Path:
        """คัดลอกไฟล์ฐานข้อมูลไปยังที่สำรองโดยมีเวลาในชื่อไฟล์

        คืนค่าที่ตั้งไฟล์สำรองที่สร้างขึ้น
        """

        if self._db_path is None:
            raise RuntimeError("StorageService is not file-based")

        now = now or datetime.now()
        backup_dir = Path(backup_dir or Path.home() / ".fueltracker" / "backups")
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / now.strftime("%y-%m-%d_%H%M.db")
        shutil.copy2(self._db_path, backup_path)

        backups = [p for p in backup_dir.glob("*.db") if p != self._db_path]
        backups.sort()
        if len(backups) > 30:
            for old in backups[: len(backups) - 30]:
                old.unlink()

        return backup_path

    def sync_to_cloud(self, backup_dir: Path, cloud_dir: Path) -> None:
        """คัดลอกโฟลเดอร์สำรองขึ้นพื้นที่ซิงก์คลาวด์"""
        cloud_dir.mkdir(parents=True, exist_ok=True)
        for file in backup_dir.glob("*.db"):
            shutil.copy2(file, cloud_dir / file.name)
