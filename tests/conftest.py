import os
import sys
from pathlib import Path

# Ensure Qt runs in headless mode before importing PySide6
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
import warnings
from sqlmodel import SQLModel, Session, create_engine
from contextlib import contextmanager
from sqlalchemy.pool import StaticPool
from alembic.config import Config
from alembic import command

try:
    from PySide6 import QtWidgets, QtGui
    from PySide6.QtWidgets import QApplication

    # Import an extra Qt class to ensure the real Qt libraries are present
    # (not just stub packages). This guards against environments where only
    # type stubs are installed without the full runtime.
    from PySide6.QtGui import QFont  # noqa: F401

    PYSIDE_AVAILABLE = True
    sys.modules["QtWidgets"] = QtWidgets
except Exception:  # pragma: no cover - platform dependent
    PYSIDE_AVAILABLE = False

# Provide Qt5-style reexports for Qt6 compatibility when PySide6 is available
if PYSIDE_AVAILABLE:
    if not hasattr(QtWidgets, "QAction"):
        QtWidgets.QAction = QtGui.QAction  # type: ignore[attr-defined]
    if not hasattr(QtWidgets, "QStandardItemModel"):
        QtWidgets.QStandardItemModel = QtGui.QStandardItemModel  # type: ignore[attr-defined]
    if not hasattr(QtWidgets, "QStandardItem"):
        QtWidgets.QStandardItem = QtGui.QStandardItem  # type: ignore[attr-defined]

warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"PyPDF2")
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"fpdf\\..*")

A_FIXTURE_MARKER = object()

@pytest.fixture(scope="session")
def worker_id() -> str:
    """Provide default worker id when pytest-xdist is absent."""
    return "master"

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"

# Ensure 'src' package is on the Python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

# Disable global hotkey backend for the entire test session **before** any
# application modules that might load the ``keyboard`` package are imported.
import src.hotkey as _hotkey  # noqa: E402

_hotkey.keyboard = None


def pytest_sessionstart(session):
    """Set up the test session."""
    # Environment already configured for headless Qt
    pass


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
def migrated_db_session(worker_id: str):
    """Return a context manager yielding sessions on a migrated in-memory database."""
    engine = create_engine(
        f"sqlite:///file:memdb_{worker_id}?mode=memory&cache=shared",
        connect_args={"check_same_thread": False, "uri": True},
        poolclass=StaticPool,
    )
    keeper = engine.connect()
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", str(engine.url))
    command.upgrade(cfg, "head")

    @contextmanager
    def get_session() -> Session:
        with Session(engine) as session:
            yield session

    yield get_session

    keeper.close()
    engine.dispose()


@pytest.fixture(autouse=True)
def _cleanup_db(migrated_db_session):
    """Truncate all tables after each test to keep isolation."""
    yield
    with migrated_db_session() as cleanup:
        for table in reversed(SQLModel.metadata.sorted_tables):
            cleanup.execute(table.delete())
        cleanup.commit()


@pytest.fixture(scope="session")
def qapp():
    """Provide a QApplication instance for UI tests."""
    if not PYSIDE_AVAILABLE:
        pytest.skip("PySide6 not available", allow_module_level=True)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def main_controller(qapp, migrated_db_session, monkeypatch):
    """Return a MainController bound to the migrated in-memory database."""

    if not PYSIDE_AVAILABLE:
        pytest.skip("PySide6 not available", allow_module_level=True)

    with migrated_db_session() as tmp:
        engine = tmp.get_bind()

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
