import sys
from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from PySide6.QtWidgets import QApplication

# Ensure 'src' package is on the Python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.services import StorageService  # noqa: E402


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
