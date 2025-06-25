"""ชุดเครื่องมือสำหรับทำงานกับไฟล์ UI ของ Qt Designer"""

from pathlib import Path
import sys
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QApplication

# Provide Qt5-style reexports for Qt6 compatibility
if not hasattr(QtWidgets, "QAction"):
    QtWidgets.QAction = QtGui.QAction
if not hasattr(QtWidgets, "QStandardItemModel"):
    QtWidgets.QStandardItemModel = QtGui.QStandardItemModel
if not hasattr(QtWidgets, "QStandardItem"):
    QtWidgets.QStandardItem = QtGui.QStandardItem

from .main_window import MainWindow
from .dialogs import (
    AddEntryDialog,
    AddVehicleDialog,
    AddMaintenanceDialog,
    ImportCsvDialog,
    AboutDialog,
)
from ..constants import FUEL_TYPE_TH

BASE_PATH = Path(__file__).resolve().parent


def asset_path(*parts: str) -> Path:
    """คืนเส้นทางไฟล์ asset แบบสมบูรณ์

    ใช้ได้ทั้งตอนรันจากโค้ดและแพ็กเกจด้วย PyInstaller
    """
    root = Path(getattr(sys, "_MEIPASS", BASE_PATH.parents[1]))
    return root.joinpath("assets", *parts)


# Allow Qt to resolve ``icons:`` paths inside .ui files.
QDir.addSearchPath("icons", str(asset_path("icons")))


def supports_shadow() -> bool:
    """Return True if the current Qt platform supports drop shadows."""
    return QApplication.platformName() not in {"offscreen", "minimal"}


def load_add_entry_dialog() -> AddEntryDialog:
    """ตัวช่วยโหลดกล่องโต้ตอบเพิ่มข้อมูลการเติมน้ำมัน"""
    dialog = AddEntryDialog()
    dialog.fuelTypeComboBox.clear()
    for key, name in FUEL_TYPE_TH.items():
        dialog.fuelTypeComboBox.addItem(name, key)
    return dialog


def load_add_vehicle_dialog() -> AddVehicleDialog:
    """ตัวช่วยโหลดกล่องโต้ตอบเพิ่มยานพาหนะ"""
    return AddVehicleDialog()


def load_about_dialog() -> AboutDialog:
    """ตัวช่วยโหลดกล่องโต้ตอบเกี่ยวกับโปรแกรม"""
    return AboutDialog()


__all__ = [
    "MainWindow",
    "AddEntryDialog",
    "AddVehicleDialog",
    "AddMaintenanceDialog",
    "ImportCsvDialog",
    "AboutDialog",
    "asset_path",
    "load_add_entry_dialog",
    "load_add_vehicle_dialog",
    "load_about_dialog",
    "supports_shadow",
]
