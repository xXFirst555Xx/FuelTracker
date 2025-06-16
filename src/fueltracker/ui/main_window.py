"""ตัวโหลด Qt MainWindow"""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow

from src.views import load_ui


def MainWindow() -> QMainWindow:
    """คืนค่าหน้าต่างหลักที่โหลดแล้ว"""
    return load_ui("main_window")  # type: ignore[return-value]
