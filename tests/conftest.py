import sys
from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool

# Ensure 'src' package is on the Python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.services import StorageService


@pytest.fixture
def in_memory_storage():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    storage = StorageService(":memory:")
    storage.engine = engine
    return storage
