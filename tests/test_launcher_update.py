import os
import zipfile
from pathlib import Path

import launcher

class DummyUpdater:
    def __init__(self):
        self.download_dir = Path(launcher.APP_DIR)
        self.extract_dir = self.download_dir / "extract"
        self.extract_dir.mkdir(parents=True, exist_ok=True)
        self.new_archive_meta = type("Meta", (), {"version": "0.2.0"})()
        self.archive = self.download_dir / "FuelTracker-0.2.0-win64.zip"
        with zipfile.ZipFile(self.archive, "w") as zf:
            zf.writestr("FuelTracker.exe", b"")

    def check_for_update(self):
        return self.new_archive_meta

    def download_and_extract(self, progress):
        with zipfile.ZipFile(self.archive) as zf:
            zf.extractall(self.extract_dir)
        return self.extract_dir, self.new_archive_meta.version


def test_update_install(monkeypatch, tmp_path):
    monkeypatch.setattr(launcher, "APP_DIR", tmp_path)
    monkeypatch.setattr(launcher, "AppUpdater", DummyUpdater)
    launcher.install_version("0.1.0", tmp_path)
    assert (tmp_path / "current").exists()
    result = launcher.main.__wrapped__ if hasattr(launcher.main, "__wrapped__") else launcher.main
    result()  # run update flow
    assert (tmp_path / "FuelTracker-0.2.0-win64.zip").exists()
    assert (tmp_path / "0.2.0" / "FuelTracker.exe").exists()
    assert (tmp_path / "current").resolve().name == "0.2.0"
