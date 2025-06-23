from __future__ import annotations

import logging

from PySide6.QtWidgets import QMessageBox, QWidget
from tufup.client import Client

from ..settings import data_dir

logger = logging.getLogger(__name__)

APP_NAME = "FuelTracker"
UPDATE_URL = "https://raw.githubusercontent.com/org/fueltracker-updates/main/"


def start_async() -> None:
    """Start background update checking."""
    # Existing functionality preserved (defined elsewhere)
    pass


def prompt_and_update(parent: QWidget) -> None:
    """Prompt the user and apply available updates."""
    app_dir = data_dir()
    client = Client(
        app_name=APP_NAME,
        app_install_dir=app_dir,
        current_version="0.1.0",
        metadata_dir=app_dir / "metadata",
        metadata_base_url=f"{UPDATE_URL}metadata/",
        target_dir=app_dir / "targets",
        target_base_url=f"{UPDATE_URL}targets/",
    )
    meta = client.check_for_updates()
    if not meta or meta.version <= client.current_version:
        QMessageBox.information(
            parent,
            "Check for Updates",
            "You are already running the latest version.",
        )
        return
    reply = QMessageBox.question(
        parent,
        "Update Available",
        f"Version {meta.version} is available. Install now?",
    )
    if reply == QMessageBox.StandardButton.Yes:
        client.download_and_apply_update()
