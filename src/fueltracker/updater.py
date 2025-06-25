from __future__ import annotations

import logging

from PySide6.QtWidgets import QMessageBox, QWidget
from tufup.client import Client

from threading import Thread
import time
import os

from src.settings import data_dir

logger = logging.getLogger(__name__)

APP_NAME = "FuelTracker"
UPDATE_URL = "https://raw.githubusercontent.com/org/fueltracker-updates/main/"


_update_thread: Thread | None = None


def _update_loop(interval: int) -> None:
    # Avoid contacting update servers when running under pytest
    if os.getenv("PYTEST_RUNNING"):
        return

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
    while True:
        try:
            meta = client.check_for_updates()
            if meta and meta.version > client.current_version:
                client.download_and_apply_update()
        except Exception as exc:  # pragma: no cover - best effort logging
            logger.error("การตรวจสอบอัปเดตเบื้องหลังล้มเหลว: %s", exc)
        time.sleep(interval)


def start_async(interval_hours: int = 24) -> None:
    """Start background update checking."""
    global _update_thread
    if os.getenv("PYTEST_RUNNING"):
        return
    if interval_hours <= 0:
        return
    if _update_thread and _update_thread.is_alive():
        return
    _update_thread = Thread(
        target=_update_loop,
        args=(int(interval_hours * 3600),),
        daemon=True,
    )
    _update_thread.start()


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
            "ตรวจสอบการอัปเดต",
            "คุณกำลังใช้เวอร์ชันล่าสุดอยู่แล้ว",
        )
        return
    reply = QMessageBox.question(
        parent,
        "มีการอัปเดตใหม่",
        f"มีเวอร์ชัน {meta.version} ให้ใช้งาน ติดตั้งตอนนี้หรือไม่?",
    )
    if reply == QMessageBox.StandardButton.Yes:
        client.download_and_apply_update()
