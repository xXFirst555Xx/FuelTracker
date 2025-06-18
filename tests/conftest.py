import sys
from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from PySide6.QtWidgets import QApplication

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
def main_controller(qapp, tmp_path):
    """Return a MainController using a temporary database."""
    ctrl = MainController(db_path=tmp_path / "t.db")
    yield ctrl
    ctrl.cleanup()
