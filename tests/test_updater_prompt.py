from types import SimpleNamespace
from PySide6.QtWidgets import QMessageBox

from src.fueltracker import updater

class DummyParent:
    pass

class DummyClient:
    current_version = "1.0"

    def __init__(self, *args, **kwargs) -> None:
        pass

    def check_for_updates(self):
        return None

    def download_and_apply_update(self):
        raise AssertionError("should not be called")


def test_prompt_no_update(monkeypatch):
    info_called = {}

    class Client(DummyClient):
        def check_for_updates(self):
            return None

    monkeypatch.setattr(updater, "Client", Client)
    from pathlib import Path
    monkeypatch.setattr(updater, "data_dir", lambda: Path("/tmp"))
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: info_called.setdefault("info", True))
    updater.prompt_and_update(DummyParent())
    assert info_called.get("info")


def test_prompt_update_yes(monkeypatch):
    called = {}

    class Client(DummyClient):
        def check_for_updates(self):
            return SimpleNamespace(version="2.0")

        def download_and_apply_update(self):
            called["applied"] = True

    monkeypatch.setattr(updater, "Client", Client)
    from pathlib import Path
    monkeypatch.setattr(updater, "data_dir", lambda: Path("/tmp"))
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)
    updater.prompt_and_update(DummyParent())
    assert called.get("applied")


def test_prompt_update_no(monkeypatch):
    called = {}

    class Client(DummyClient):
        def check_for_updates(self):
            return SimpleNamespace(version="2.0")

        def download_and_apply_update(self):
            called["applied"] = True

    monkeypatch.setattr(updater, "Client", Client)
    from pathlib import Path
    monkeypatch.setattr(updater, "data_dir", lambda: Path("/tmp"))
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.No)
    updater.prompt_and_update(DummyParent())
    assert "applied" not in called
