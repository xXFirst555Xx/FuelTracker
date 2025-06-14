"""Service handling persistence of entries using SQLModel."""

from pathlib import Path
from typing import List

from sqlmodel import Session, SQLModel, create_engine, select

from ..models import FuelEntry


class StorageService:
    def __init__(self, db_path: str | Path = "fuel.db") -> None:
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        SQLModel.metadata.create_all(self.engine)

    def add_entry(self, entry: FuelEntry) -> None:
        with Session(self.engine) as session:
            session.add(entry)
            session.commit()

    def list_entries(self) -> List[FuelEntry]:
        with Session(self.engine) as session:
            statement = select(FuelEntry)
            return list(session.exec(statement))
