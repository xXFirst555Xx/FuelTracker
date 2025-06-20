import sqlalchemy
import pytest
from alembic import command
from alembic.config import Config
from fueltracker.main import ALEMBIC_INI  # type: ignore
from sqlalchemy.engine import Engine
from pathlib import Path


@pytest.fixture()
def engine(tmp_path: Path) -> Engine:
    db = tmp_path / "m.db"
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db}")
    command.upgrade(cfg, "head")
    return sqlalchemy.create_engine(f"sqlite:///{db}")


def test_fuel_type_column(engine: Engine) -> None:
    insp = sqlalchemy.inspect(engine)
    assert "fuel_type" in [c["name"] for c in insp.get_columns("fuelentry")]


def test_indexes_created(engine: Engine) -> None:
    insp = sqlalchemy.inspect(engine)
    fuel_indexes = {idx["name"] for idx in insp.get_indexes("fuelentry")}
    maint_indexes = {idx["name"] for idx in insp.get_indexes("maintenance")}
    price_indexes = {idx["name"] for idx in insp.get_indexes("fuelprice")}
    assert "ix_fuelentry_vehicle_id" in fuel_indexes
    assert "ix_fuelentry_entry_date" in fuel_indexes
    assert "ix_maintenance_vehicle_id" in maint_indexes
    assert "ix_fuelprice_date_station_fuel_type" in price_indexes
