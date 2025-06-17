from __future__ import annotations

from sqlmodel import Session, select
from sqlalchemy.engine import Engine

from ..models import FuelEntry


class FuelEntryRepository:
    """Repository for ``FuelEntry`` records."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def last_entry(self, vehicle_id: int) -> FuelEntry | None:
        with Session(self.engine) as sess:
            stmt = (
                select(FuelEntry)
                .where(FuelEntry.vehicle_id == vehicle_id)
                .order_by(FuelEntry.entry_date.desc(), FuelEntry.id.desc())
            )
            return sess.exec(stmt).first()

    def add(self, entry: FuelEntry) -> FuelEntry:
        with Session(self.engine) as sess:
            sess.add(entry)
            sess.commit()
            sess.refresh(entry)
            return entry
