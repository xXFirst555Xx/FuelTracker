import sqlalchemy
from src.services import StorageService


def test_indexes_created_in_memory(in_memory_storage: StorageService) -> None:
    engine = in_memory_storage.engine
    insp = sqlalchemy.inspect(engine)
    fuel_indexes = {idx["name"] for idx in insp.get_indexes("fuelentry")}
    maint_indexes = {idx["name"] for idx in insp.get_indexes("maintenance")}
    budget_indexes = {idx["name"] for idx in insp.get_indexes("budget")}
    price_indexes = {idx["name"] for idx in insp.get_indexes("fuelprice")}
    assert "ix_fuelentry_vehicle_id" in fuel_indexes
    assert "ix_fuelentry_entry_date" in fuel_indexes
    assert "ix_maintenance_vehicle_id" in maint_indexes
    assert "ix_budget_vehicle_id" in budget_indexes
    assert "ix_fuelprice_date_station_fuel_type" in price_indexes
