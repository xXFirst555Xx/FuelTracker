"""บริการจัดการการบันทึกข้อมูลด้วย SQLModel"""

from pathlib import Path
from datetime import datetime
from typing import List, Optional
import shutil

from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.engine import Engine

from ..models import FuelEntry, Vehicle
from .validators import validate_entry


class StorageService:
    def __init__(
        self, db_path: str | Path = "fuel.db", engine: Engine | None = None
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
            # ``check_same_thread`` must be disabled so a single engine can be
            # shared across threads during testing and normal application use.
            self.engine = create_engine(
                f"sqlite:///{db_path}",
                echo=False,
                connect_args={"check_same_thread": False},
            )
            self._db_path = db_path

        SQLModel.metadata.create_all(
            self.engine, tables=[FuelEntry.__table__, Vehicle.__table__]
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
    # Utilities
    # ------------------------------------------------------------------

    def auto_backup(
        self,
        now: datetime | None = None,
        backup_dir: Path | None = None,
    ) -> Path:
        """Copy the database file to a timestamped backup path.

        Returns the created backup path.
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
