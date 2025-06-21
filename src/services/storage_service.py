"""บริการจัดการการบันทึกข้อมูลด้วย SQLModel"""

from pathlib import Path
from datetime import datetime, date
from typing import List, Optional, Any, Callable, cast
import os
import shutil
import gzip
from getpass import getpass
from decimal import Decimal
from contextlib import closing

from ..settings import Settings

try:
    from pysqlcipher3 import dbapi2 as sqlcipher

    _SQLCIPHER_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - fallback when dependency missing
    import sqlite3 as sqlcipher

    _SQLCIPHER_AVAILABLE = False

from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy import func, or_

from ..models import FuelEntry, Vehicle, Budget, Maintenance, FuelPrice
from .validators import validate_entry
from .oil_service import get_price

# ---------------------------------------------------------------------------
# Database table collection
# ---------------------------------------------------------------------------
ALL_TABLES = (
    cast(Any, FuelEntry).__table__,
    cast(Any, Vehicle).__table__,
    cast(Any, Budget).__table__,
    cast(Any, Maintenance).__table__,
    cast(Any, FuelPrice).__table__,
)


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

    # FIX: mypy clean
    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)

    # FIX: mypy clean
    def create_function(
        self,
        name: str,
        num_params: int,
        func: Callable[..., Any],
        deterministic: bool | None = None,
    ) -> None:
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
        vacuum_threshold: int = 100,
        default_station: str = "ptt",
    ) -> None:
        """เริ่มต้นบริการจัดเก็บข้อมูล

        พารามิเตอร์
        ----------
        db_path: str | Path
            เส้นทางไปยังไฟล์ฐานข้อมูล SQLite ไม่ใช้ถ้ากำหนด ``engine``
        engine: Engine | None
            ออบเจ็กต์ Engine ที่เตรียมไว้ (ไม่บังคับ)
        vacuum_threshold:
            เรียก :meth:`vacuum` หลังจากเพิ่มข้อมูลด้วย :meth:`add_entry`
            ครบจำนวนครั้งที่กำหนด ค่าเริ่มต้น ``100``
        default_station:
            สถานีบริการน้ำมันเริ่มต้นสำหรับคำสั่งคำนวณอัตโนมัติ
        """

        self._vacuum_threshold = vacuum_threshold
        self.default_station = default_station
        self._entry_counter = 0

        if engine is not None:
            self.engine = engine
            self._db_path = Path(engine.url.database) if engine.url.database else None
            self._password = password or ""
            SQLModel.metadata.create_all(self.engine, tables=list(ALL_TABLES))
        else:
            db_path = Path(db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            if password is None:
                if _SQLCIPHER_AVAILABLE:
                    env = Settings()
                    password = env.ft_db_password or getpass("DB password: ")
                else:
                    password = ""
            if password and db_path.exists() and _is_plain_sqlite(db_path):
                _migrate_plain_to_encrypted(db_path, password)

            self._password = password or ""

            def _connect() -> sqlcipher.Connection:
                raw = sqlcipher.connect(str(db_path))
                if _SQLCIPHER_AVAILABLE:
                    raw.execute(f"PRAGMA key='{password}';")
                return _ConnProxy(raw)

            exists_before = db_path.exists()
            self.engine = create_engine(
                "sqlite://",
                creator=_connect,
                connect_args={"check_same_thread": False},
            )
            self._db_path = db_path

            if not exists_before:
                SQLModel.metadata.create_all(self.engine, tables=list(ALL_TABLES))

    def add_entry(self, entry: FuelEntry) -> None:
        """Add a refuel entry and finalize the previous incomplete one.

        Parameters
        ----------
        entry:
            The :class:`~src.models.FuelEntry` instance to be persisted. If
            ``liters`` is ``None`` but ``amount_spent`` is provided, the method
            will attempt to infer the missing value from stored fuel prices.

        Returns
        -------
        None
            The entry is written to the database. After the call ``entry.id``
            will be populated with the assigned primary key.
        """

        validate_entry(entry)
        with Session(self.engine) as session:
            # ------------------------------------------------------------------
            # Find the latest entry for this vehicle that hasn't recorded an
            # ``odo_after`` yet. This represents a previous refuel awaiting the
            # next odometer reading to know the distance driven.
            # ------------------------------------------------------------------
            stmt = (
                select(FuelEntry)
                .where(
                    FuelEntry.vehicle_id == entry.vehicle_id,
                    cast(Any, FuelEntry.odo_after).is_(None),
                )
                .order_by(
                    cast(Any, FuelEntry.entry_date).desc(),
                    cast(Any, FuelEntry.id).desc(),
                )
            )
            prev = session.exec(stmt).first()
            if prev is not None:
                # Update the previous entry so that its ``odo_after`` matches the
                # odometer reading before this new refuel.
                prev.odo_after = entry.odo_before

                # If the previous entry recorded spending but not liters, derive
                # the liters from the historical fuel price at that date.
                if prev.amount_spent is not None and prev.liters is None:
                    price = get_price(
                        session,
                        prev.fuel_type or "e20",
                        self.default_station,
                        prev.entry_date,
                    )
                    if price is not None:
                        prev.liters = float(
                            (Decimal(str(prev.amount_spent)) / price).quantize(
                                Decimal("0.01")
                            )
                        )
                session.add(prev)

            # ------------------------------------------------------------------
            # Auto-calculate liters for the current entry when only the amount
            # spent is provided. The calculation uses the fuel price for the
            # entry date and the service's default station.
            # ------------------------------------------------------------------
            if entry.amount_spent is not None and entry.liters is None:
                price = get_price(
                    session,
                    entry.fuel_type or "e20",
                    self.default_station,
                    entry.entry_date,
                )
                if price is not None:
                    entry.liters = float(
                        (Decimal(str(entry.amount_spent)) / price).quantize(
                            Decimal("0.01")
                        )
                    )

            session.add(entry)
            session.commit()

            # FIX: prevent hang when entry.id is None
            session.flush()
            if entry.id is not None:
                session.refresh(entry)

        self._entry_counter += 1
        if self._entry_counter >= self._vacuum_threshold:
            self.vacuum()
            self._entry_counter = 0

    def add_vehicle(self, vehicle: Vehicle) -> None:
        with Session(self.engine) as session:
            session.add(vehicle)
            session.commit()
            # FIX: prevent hang when vehicle.id is None
            session.flush()
            if vehicle.id is not None:
                session.refresh(vehicle)

    def list_entries(self) -> List[FuelEntry]:
        with Session(self.engine) as session:
            statement = select(FuelEntry)
            return list(session.exec(statement))

    def list_entries_filtered(
        self, text: str | None = None, start: date | None = None
    ) -> list[FuelEntry]:
        """Return entries filtered by vehicle name and start date."""
        with Session(self.engine) as session:
            stmt = select(FuelEntry)
            if text:
                stmt = stmt.join(
                    Vehicle,
                    cast(Any, FuelEntry.vehicle_id == Vehicle.id),
                ).where(func.lower(Vehicle.name).contains(text.lower()))
            if start:
                stmt = stmt.where(FuelEntry.entry_date >= start)
            return list(session.exec(stmt))

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
            # FIX: prevent hang when vehicle.id is None
            session.flush()
            if vehicle.id is not None:
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

    def get_last_entry(self, vehicle_id: int) -> FuelEntry | None:
        """Return the most recent entry for the given vehicle."""
        with Session(self.engine) as session:
            stmt = (
                select(FuelEntry)
                .where(FuelEntry.vehicle_id == vehicle_id)
                .order_by(
                    cast(Any, FuelEntry.entry_date).desc(),
                    cast(Any, FuelEntry.id).desc(),
                )
            )
            return session.exec(stmt).first()

    def get_vehicle_stats(self, vehicle_id: int) -> tuple[float, float, float]:
        """Calculate aggregate stats for a vehicle."""
        with Session(self.engine) as session:
            stmt = select(
                func.sum(cast(Any, FuelEntry.odo_after) - FuelEntry.odo_before),
                func.sum(FuelEntry.liters),
                func.sum(FuelEntry.amount_spent),
            ).where(
                FuelEntry.vehicle_id == vehicle_id,
                cast(Any, FuelEntry.odo_after).is_not(None),
            )
            totals = session.exec(stmt).one()
            dist = float(totals[0] or 0.0)
            liters = float(totals[1] or 0.0)
            price = float(totals[2] or 0.0)
            return dist, liters, price

    def get_overall_totals(self) -> tuple[float, float, float]:
        """Return overall distance, liters and amount spent across all vehicles."""
        with Session(self.engine) as session:
            dist, liters = session.exec(
                select(
                    func.sum(cast(Any, FuelEntry.odo_after) - FuelEntry.odo_before),
                    func.sum(FuelEntry.liters),
                ).where(cast(Any, FuelEntry.odo_after).is_not(None))
            ).one()
            price = session.exec(select(func.sum(FuelEntry.amount_spent))).one()
            return (
                float(dist or 0.0),
                float(liters or 0.0),
                float(price or 0.0),
            )

    def list_entries_for_month(
        self, year: int, month: int, vehicle_id: int | None = None
    ) -> List[FuelEntry]:
        """Return entries within the given month optionally filtered by vehicle."""
        with Session(self.engine) as session:
            stmt = select(FuelEntry).where(
                cast(Any, FuelEntry.entry_date).between(
                    f"{year}-{month:02d}-01", f"{year}-{month:02d}-31"
                )
            )
            if vehicle_id is not None:
                stmt = stmt.where(FuelEntry.vehicle_id == vehicle_id)
            return list(session.exec(stmt))

    def monthly_totals(self) -> list[tuple[str, float, float, float]]:
        """Return aggregated totals grouped by month."""
        month = func.strftime("%Y-%m", FuelEntry.entry_date)
        with Session(self.engine) as session:
            stmt = (
                select(
                    month.label("month"),
                    func.sum(cast(Any, FuelEntry.odo_after) - FuelEntry.odo_before),
                    func.sum(FuelEntry.liters),
                    func.sum(FuelEntry.amount_spent),
                )
                .where(
                    cast(Any, FuelEntry.odo_after).is_not(None),
                    cast(Any, FuelEntry.liters).is_not(None),
                )
                .group_by(month)
                .order_by(month)
            )
            res = []
            for m, d, liters_val, amount_val in session.exec(stmt):
                res.append(
                    (
                        m,
                        float(d or 0.0),
                        float(liters_val or 0.0),
                        float(amount_val or 0.0),
                    )
                )
            return res

    def liters_by_fuel_type(self) -> dict[str | None, float]:
        """Return total liters grouped by fuel type."""
        with Session(self.engine) as session:
            stmt = (
                select(FuelEntry.fuel_type, func.sum(FuelEntry.liters))
                .where(cast(Any, FuelEntry.liters).is_not(None))
                .group_by(FuelEntry.fuel_type)
            )
            return {
                fuel_type: float(total_liters or 0.0)
                for fuel_type, total_liters in session.exec(stmt)
            }

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
            # FIX: prevent hang when entry.id is None
            session.flush()
            if entry.id is not None:
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
            # FIX: prevent hang
            session.flush()
            if task.id is not None:
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
            # FIX: prevent hang
            session.flush()
            if task.id is not None:
                session.refresh(task)

    def mark_maintenance_done(self, task_id: int, done: bool = True) -> None:
        with Session(self.engine) as session:
            task = session.get(Maintenance, task_id)
            if task is None:
                return
            task.is_done = done
            session.add(task)
            session.commit()
            # FIX: prevent hang
            session.flush()
            if task.id is not None:
                session.refresh(task)

    def list_due_maintenances(
        self,
        vehicle_id: int,
        odo: float | None = None,
        date_: datetime | None = None,
    ) -> List[Maintenance]:
        with Session(self.engine) as session:
            if odo is None and date_ is None:
                return []

            conditions = [
                Maintenance.vehicle_id == vehicle_id,
                cast(Any, Maintenance.is_done).is_(False),
            ]

            odo_cond = (
                (
                    cast(Any, Maintenance.due_odo).is_not(None)
                    & (cast(Any, Maintenance.due_odo) <= odo)
                )
                if odo is not None
                else None
            )

            date_cond = (
                (
                    cast(Any, Maintenance.due_date).is_not(None)
                    & (cast(Any, Maintenance.due_date) <= date_)
                )
                if date_ is not None
                else None
            )

            if odo_cond is not None and date_cond is not None:
                conditions.append(or_(odo_cond, date_cond))
            elif odo_cond is not None:
                conditions.append(odo_cond)
            elif date_cond is not None:
                conditions.append(date_cond)

            stmt = select(Maintenance).where(*conditions)
            return list(session.exec(stmt))

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
            stmt = select(func.sum(FuelEntry.amount_spent)).where(
                FuelEntry.vehicle_id == vehicle_id,
                cast(Any, FuelEntry.entry_date).between(
                    f"{year}-{month:02d}-01", f"{year}-{month:02d}-31"
                ),
                cast(Any, FuelEntry.amount_spent).is_not(None),
            )
            total = session.exec(stmt).first()
            return float(total or 0.0)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def auto_backup(
        self,
        now: datetime | None = None,
        backup_dir: Path | None = None,
        encrypted: bool = False,
        compress: bool = False,
        max_backups: int = 30,
    ) -> Path:
        """คัดลอกไฟล์ฐานข้อมูลไปยังที่สำรองโดยมีเวลาในชื่อไฟล์

        คืนค่าที่ตั้งไฟล์สำรองที่สร้างขึ้น

        Parameters
        ----------
        encrypted:
            ถ้า ``True`` และมี SQLCipher จะเข้ารหัสไฟล์สำรองด้วยรหัสผ่านเดียวกัน
        compress:
            ถ้า ``True`` จะบีบอัดไฟล์สำรองด้วย gzip แล้วเพิ่ม ``.gz`` ต่อท้ายชื่อไฟล์
        max_backups:
            จำนวนไฟล์สำรองสูงสุดที่จะเก็บไว้ก่อนลบของเก่า ค่าเริ่มต้น ``30``
        """

        if self._db_path is None:
            raise RuntimeError("StorageService is not file-based")

        now = now or datetime.now()
        backup_dir = Path(backup_dir or Path.home() / ".fueltracker" / "backups")
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / now.strftime("%y-%m-%d_%H%M.db")

        with (
            closing(
                cast(sqlcipher.Connection, self.engine.raw_connection())
            ) as source_conn,
            closing(sqlcipher.connect(str(backup_path))) as dest_conn,
        ):
            if encrypted and _SQLCIPHER_AVAILABLE and self._password:
                dest_conn.execute(f"PRAGMA key='{self._password}';")
            source_conn.backup(dest_conn)

        if compress:
            gz_path = backup_path.with_suffix(backup_path.suffix + ".gz")
            with open(backup_path, "rb") as fh, gzip.open(gz_path, "wb") as out:
                shutil.copyfileobj(fh, out)
            backup_path.unlink()
            backup_path = gz_path

        backups = [p for p in backup_dir.glob("*.db*") if p != self._db_path]
        backups.sort()
        if len(backups) > max_backups:
            for old in backups[: len(backups) - max_backups]:
                old.unlink()

        return backup_path

    def sync_to_cloud(self, backup_dir: Path, cloud_dir: Path) -> None:
        """คัดลอกโฟลเดอร์สำรองขึ้นพื้นที่ซิงก์คลาวด์"""
        cloud_dir.mkdir(parents=True, exist_ok=True)
        for file in backup_dir.glob("*.db"):
            shutil.copy2(file, cloud_dir / file.name)

    def vacuum(self) -> None:
        """ลดขนาดฐานข้อมูลด้วยคำสั่ง ``VACUUM``."""
        with self.engine.connect() as conn:
            conn.exec_driver_sql("VACUUM")
