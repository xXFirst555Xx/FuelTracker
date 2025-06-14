"""Service handling persistence of entries using SQLModel."""

from pathlib import Path
from typing import List, Optional

from sqlmodel import Session, SQLModel, create_engine, select

from ..models import FuelEntry, Vehicle


class StorageService:
    def __init__(self, db_path: str | Path = "fuel.db") -> None:
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        SQLModel.metadata.create_all(
            self.engine, tables=[FuelEntry.__table__, Vehicle.__table__]
        )

    def add_entry(self, entry: FuelEntry) -> None:
        with Session(self.engine) as session:
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
        """Retrieve a vehicle by its identifier."""
        with Session(self.engine) as session:
            return session.get(Vehicle, vehicle_id)

    def update_vehicle(self, vehicle: Vehicle) -> None:
        """Persist changes to an existing vehicle."""
        with Session(self.engine) as session:
            session.add(vehicle)
            session.commit()
            session.refresh(vehicle)

    def delete_vehicle(self, vehicle_id: int) -> None:
        """Delete a vehicle from the database."""
        with Session(self.engine) as session:
            obj = session.get(Vehicle, vehicle_id)
            if obj:
                session.delete(obj)
                session.commit()

    def get_entries_by_vehicle(self, vehicle_id: int) -> List[FuelEntry]:
        """Return all entries associated with a vehicle."""
        with Session(self.engine) as session:
            statement = select(FuelEntry).where(FuelEntry.vehicle_id == vehicle_id)
            return list(session.exec(statement))

    def get_entry(self, entry_id: int) -> Optional[FuelEntry]:
        """Retrieve a fuel entry by id."""
        with Session(self.engine) as session:
            return session.get(FuelEntry, entry_id)

    def update_entry(self, entry: FuelEntry) -> None:
        """Persist changes to a fuel entry."""
        with Session(self.engine) as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)

    def delete_entry(self, entry_id: int) -> None:
        """Remove a fuel entry from the database."""
        with Session(self.engine) as session:
            obj = session.get(FuelEntry, entry_id)
            if obj:
                session.delete(obj)
                session.commit()
