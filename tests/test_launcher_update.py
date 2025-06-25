import zipfile
from pathlib import Path

import sys
import types
import importlib


def _patch_pyside(monkeypatch):
    """Provide minimal PySide6 stubs used by the launcher."""

    qt_widgets = types.ModuleType("QtWidgets")
    qt_widgets.QApplication = object
    qt_widgets.QProgressBar = object
    qt_widgets.QSplashScreen = object

    qt_gui = types.ModuleType("QtGui")
    qt_gui.QPixmap = object

    monkeypatch.setitem(sys.modules, "PySide6", types.ModuleType("PySide6"))
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", qt_widgets)
    monkeypatch.setitem(sys.modules, "PySide6.QtGui", qt_gui)


import launcher  # noqa: E402


class DummyUpdater:
    def __init__(self):
        self.download_dir = Path(launcher.APP_DIR)
        self.extract_dir = self.download_dir / "extract"
        self.extract_dir.mkdir(parents=True, exist_ok=True)
        from packaging.version import Version

        self.new_archive_meta = type("Meta", (), {"version": Version("0.2.0")})()
        self.archive = self.download_dir / "FuelTracker-0.2.0-win64.zip"
        with zipfile.ZipFile(self.archive, "w") as zf:
            zf.writestr("FuelTracker.exe", b"")

    def check_for_update(self):
        return self.new_archive_meta

    def download_and_extract(self, _progress):
        with zipfile.ZipFile(self.archive) as zf:
            zf.extractall(self.extract_dir)
        return self.extract_dir, self.new_archive_meta.version


def test_update_install(monkeypatch, tmp_path):
    _patch_pyside(monkeypatch)

    importlib.reload(launcher)

    monkeypatch.setattr(launcher, "APP_DIR", tmp_path)
    monkeypatch.setattr(launcher, "LOG_FILE", tmp_path / "launcher.log")
    monkeypatch.setattr(launcher, "read_current_version", lambda: "0.1.0")

    class DummyApp:
        def processEvents(self):
            pass

    class DummySplash:
        def finish(self, _):
            pass

    class DummyBar:
        def setRange(self, *_args):
            pass

        def setValue(self, *_args):
            pass

    monkeypatch.setattr(
        launcher,
        "show_splash",
        lambda: (DummyApp(), DummySplash(), DummyBar()),
    )
    monkeypatch.setattr(launcher, "run_app", lambda: None)
    monkeypatch.setattr(launcher, "AppUpdater", DummyUpdater)
    launcher.install_version("0.1.0", tmp_path)
    assert (tmp_path / "current").exists()
    result = (
        launcher.main.__wrapped__
        if hasattr(launcher.main, "__wrapped__")
        else launcher.main
    )
    result()  # run update flow
    assert (tmp_path / "FuelTracker-0.2.0-win64.zip").exists()
    assert (tmp_path / "0.2.0" / "FuelTracker.exe").exists()
    current = tmp_path / "current"
    if current.is_symlink():
        assert current.resolve().name == "0.2.0"
    else:
        assert (tmp_path / "current_version").read_text().strip() == "0.2.0"
