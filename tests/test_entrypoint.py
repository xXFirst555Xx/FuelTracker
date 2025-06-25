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


import builtins
import sys
import pytest


def test_run_requires_pyside(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "db.sqlite"))
    for key in list(sys.modules):
        if key.startswith("PySide6"):
            monkeypatch.delitem(sys.modules, key, raising=False)
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("PySide6"):
            raise ImportError
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(SystemExit) as exc:
        run(["--check"])
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "PySide6 is required" in out
