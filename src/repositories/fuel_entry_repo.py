from __future__ import annotations

from sqlmodel import Session, select
from sqlalchemy.engine import Engine
from typing import Any, cast

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
                .order_by(cast(Any, FuelEntry.entry_date).desc(), cast(Any, FuelEntry.id).desc())
            )
            return sess.exec(stmt).first()

    def last_entries(self, vehicle_id: int, limit: int = 3) -> list[FuelEntry]:
        """Return up to ``limit`` most recent entries for a vehicle."""
        with Session(self.engine) as sess:
            stmt = (
                select(FuelEntry)
                .where(FuelEntry.vehicle_id == vehicle_id)
                .order_by(cast(Any, FuelEntry.entry_date).desc(), cast(Any, FuelEntry.id).desc())
                .limit(limit)
            )
            return list(sess.exec(stmt))

    def add(self, entry: FuelEntry) -> FuelEntry:
        with Session(self.engine) as sess:
            sess.add(entry)
            sess.commit()
            # FIX: prevent hang
            sess.flush()
            if entry.id is not None:
                sess.refresh(entry)
            return entry
