import tomllib
from pathlib import Path, Path as _P

from fueltracker.main import run


def test_console_script() -> None:
    data = tomllib.loads(Path("pyproject.toml").read_text())
    scripts = data["project"]["scripts"]
    assert scripts["fueltracker"] == "fueltracker.main:run"
    assert scripts["fueltracker-launcher"] == "launcher:main"


def test_backup_command(monkeypatch):
    called = {}

    class Dummy:
        def __init__(self):
            pass

        def auto_backup(self):
            called["b"] = True

    import src.services as services
    monkeypatch.setattr(services, "StorageService", Dummy)

    run(["backup"])

    assert called.get("b")


def test_sync_command(monkeypatch, tmp_path):
    called = {}

    class Dummy:
        def __init__(self):
            pass

        def sync_to_cloud(self, backup_dir, cloud_dir):
            called["args"] = (backup_dir, cloud_dir)

    import src.services as services
    monkeypatch.setattr(services, "StorageService", Dummy)
    monkeypatch.setenv("FT_CLOUD_DIR", str(tmp_path))
    monkeypatch.setattr(_P, "home", lambda: tmp_path)

    run(["sync"])

    assert called.get("args") == (
        tmp_path / ".fueltracker" / "backups",
        tmp_path,
    )
