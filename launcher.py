# FuelTracker launcher with secure updates
from __future__ import annotations

import ctypes
import logging
import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable

from packaging.version import Version
from PyQt6.QtWidgets import QApplication, QProgressBar, QSplashScreen
from PyQt6.QtGui import QPixmap
from tufup.client import Client

APP_NAME = "FuelTracker"
PACKAGE = "fueltracker"
CURRENT_VERSION = "0.1.0"
UPDATE_URL = "https://raw.githubusercontent.com/org/fueltracker-updates/main/"
ROOT_KEY_HEX = "6ab4…c3"  # truncated example

LOCALAPPDATA = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
APP_DIR = LOCALAPPDATA / APP_NAME
LOG_FILE = APP_DIR / "launcher.log"
MUTEX_NAME = "FuelTrackerLauncherMutex"


@contextmanager
def single_instance(name: str):
    """Prevent concurrent launcher instances using a Windows mutex."""
    if hasattr(ctypes, "windll"):
        handle = ctypes.windll.kernel32.CreateMutexW(None, False, name)
        if ctypes.GetLastError() == 183:
            sys.exit("Another instance is already running.")
        try:
            yield
        finally:
            ctypes.windll.kernel32.ReleaseMutex(handle)
            ctypes.windll.kernel32.CloseHandle(handle)
    else:
        # Non-Windows platforms: mutex not required
        yield


def setup_logging() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=512 * 1024, backupCount=5, encoding="utf-8"
    )
    logging.basicConfig(level=logging.INFO, handlers=[handler])


def read_current_version() -> str:
    cur = APP_DIR / "current"
    if cur.exists():
        return cur.resolve().name
    return CURRENT_VERSION


class AppUpdater:
    """Wrapper around ``tufup.Client``."""

    def __init__(self) -> None:
        self.metadata_dir = APP_DIR / "metadata"
        self.target_dir = APP_DIR / "targets"
        self.client = Client(
            app_name=APP_NAME,
            app_install_dir=APP_DIR,
            current_version=read_current_version(),
            metadata_dir=self.metadata_dir,
            metadata_base_url=f"{UPDATE_URL}metadata/",
            target_dir=self.target_dir,
            target_base_url=f"{UPDATE_URL}targets/",
        )

    def check_for_update(self):
        return self.client.check_for_updates()

    def download_and_extract(self, progress: Callable[[int, int], None]):
        self.client.download_and_apply_update(
            skip_confirmation=True,
            install=lambda *a, **k: None,
            progress_hook=progress,
        )
        return Path(self.client.extract_dir), self.client.new_archive_meta.version


def install_version(version: str, extracted: Path) -> Path:
    dest = APP_DIR / version
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(extracted, dest)
    current = APP_DIR / "current"
    if current.exists():
        if current.is_symlink() or current.is_file():
            current.unlink()
        else:
            shutil.rmtree(current)
    try:
        current.symlink_to(dest, target_is_directory=True)
    except OSError:
        shutil.copytree(dest, current, dirs_exist_ok=True)
    versions = sorted(
        [p for p in APP_DIR.iterdir() if p.is_dir() and p.name[0].isdigit()],
        key=lambda p: Version(p.name),
        reverse=True,
    )
    for old in versions[2:]:
        shutil.rmtree(old, ignore_errors=True)
    return dest


def run_app() -> None:
    exe = APP_DIR / "current" / f"{APP_NAME}.exe"
    if exe.exists():
        subprocess.Popen([str(exe)])
    else:
        logging.error("Executable not found: %s", exe)


def show_splash():
    app = QApplication.instance() or QApplication(sys.argv[:1])
    icon_path = Path(__file__).with_name("assets/icon.ico")
    splash = QSplashScreen(QPixmap(str(icon_path)))
    splash.show()
    bar = QProgressBar(splash)
    bar.setGeometry(0, splash.pixmap().height() - 25, splash.pixmap().width(), 20)
    bar.setRange(0, 100)
    bar.show()
    return app, splash, bar


def main() -> None:
    setup_logging()
    with single_instance(MUTEX_NAME):
        app, splash, bar = show_splash()

        def update_progress(bytes_downloaded: int, bytes_expected: int) -> None:
            bar.setRange(0, bytes_expected)
            bar.setValue(bytes_downloaded)
            app.processEvents()

        updater = AppUpdater()
        meta = updater.check_for_update()
        if meta and meta.version > Version(read_current_version()):
            logging.info("Updating to %s", meta.version)
            extracted, version = updater.download_and_extract(update_progress)
            install_version(str(version), extracted)
        splash.finish(None)
    run_app()


if __name__ == "__main__":
    main()
