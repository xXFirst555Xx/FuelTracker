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
