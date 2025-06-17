from src.repositories import FuelEntryRepository
from src.models import FuelEntry
from datetime import date


def test_last_entry(in_memory_storage):
    repo = FuelEntryRepository(in_memory_storage.engine)
    entry1 = FuelEntry(entry_date=date.today(), vehicle_id=1, odo_before=0, odo_after=10, liters=5.0, amount_spent=100.0)
    repo.add(entry1)
    latest = repo.last_entry(1)
    assert latest is not None
    assert latest.id == entry1.id
