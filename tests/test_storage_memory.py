from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from src.services import StorageService


def test_db_path_none_for_memory_engine() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    storage = StorageService(engine=engine)
    assert storage._db_path is None


def test_db_path_none_for_file_memory_engine() -> None:
    engine = create_engine(
        "sqlite:///file:memdb_test?mode=memory&cache=shared",
        connect_args={"check_same_thread": False, "uri": True},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    storage = StorageService(engine=engine)
    assert storage._db_path is None
