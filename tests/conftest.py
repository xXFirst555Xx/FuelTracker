import sys
from pathlib import Path

import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from alembic.config import Config
from alembic import command
from PySide6.QtWidgets import QApplication

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"

# Ensure 'src' package is on the Python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.services import StorageService  # noqa: E402
from src.controllers.main_controller import MainController  # noqa: E402


@pytest.fixture
def in_memory_storage():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    storage = StorageService(engine=engine)
    return storage


@pytest.fixture
def migrated_db_session():
    """Return a Session connected to a migrated in-memory database."""
    engine = create_engine(
        "sqlite:///file:memdb1?mode=memory&cache=shared",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    keeper = engine.connect()
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", str(engine.url))
    command.upgrade(cfg, "head")
    with Session(engine) as session:
        yield session
    # Clear data after each test to avoid cross-test contamination
    with Session(engine) as cleanup:
        for table in reversed(SQLModel.metadata.sorted_tables):
            cleanup.execute(table.delete())
        cleanup.commit()
    keeper.close()
    engine.dispose()


@pytest.fixture(scope="session")
def qapp():
    """Provide a QApplication instance for UI tests."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def main_controller(qapp, migrated_db_session, monkeypatch):
    """Return a MainController bound to the migrated in-memory database."""

    engine = migrated_db_session.get_bind()

    def _storage_service(*_args, **_kwargs):
        return StorageService(engine=engine)

    monkeypatch.setattr(
        "src.controllers.main_controller.StorageService", _storage_service
    )

    ctrl = MainController()
    yield ctrl
    # ADDED: Ensure the window is closed after each test to trigger proper cleanup
    ctrl.window.close() 
    ctrl.cleanup()
