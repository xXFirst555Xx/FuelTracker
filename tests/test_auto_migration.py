from alembic.config import Config
from alembic import command
from fueltracker.main import ALEMBIC_INI, run


def test_auto_migration(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db}")
    command.upgrade(cfg, "0001")

    monkeypatch.setenv("DB_PATH", str(db))
    run(["--check"])

    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db}")
    command.upgrade(cfg, "head")
    from sqlalchemy import inspect, create_engine

    engine = create_engine(f"sqlite:///{db}")
    insp = inspect(engine)
    cols = [c["name"] for c in insp.get_columns("fuelentry")]
    assert "fuel_type" in cols
