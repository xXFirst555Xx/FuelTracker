"""ชุดเครื่องมือสำหรับทำงานกับไฟล์ UI ของ Qt Designer"""

from pathlib import Path
import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QDialog, QDialogButtonBox, QListWidget
from PySide6.QtCore import QFile, QDir, Qt
from typing import cast

from .main_window import MainWindow
from .dialogs import (
    AddEntryDialog,
    AddVehicleDialog,
    AddMaintenanceDialog,
    ImportCsvDialog,
    AboutDialog,
)

BASE_PATH = Path(__file__).resolve().parent


def asset_path(*parts: str) -> Path:
    """คืนเส้นทางไฟล์ asset แบบสมบูรณ์

    ใช้ได้ทั้งตอนรันจากโค้ดและแพ็กเกจด้วย PyInstaller
    """
    root = Path(getattr(sys, "_MEIPASS", BASE_PATH.parents[1]))
    return root.joinpath("assets", *parts)


# Allow Qt to resolve ``icons:`` paths inside .ui files.
QDir.addSearchPath("icons", str(asset_path("icons")))


def load_ui(name: str) -> QWidget:
    """โหลดไฟล์ ``.ui`` จากไดเรกทอรี views"""
    ui_path = BASE_PATH / f"{name}.ui"
    if not ui_path.exists():
        raise FileNotFoundError(ui_path)

    file = QFile(str(ui_path))
    file.open(QFile.ReadOnly)  # type: ignore[attr-defined]
    loader = QUiLoader()
    widget = loader.load(file)
    file.close()


    if isinstance(widget, QDialog):
        button_box = widget.findChild(QDialogButtonBox, "buttonBox")
        if button_box is not None:
            button_box.accepted.connect(widget.accept)
            button_box.rejected.connect(widget.reject)

    # Ensure list widget items are selectable
    for lw in widget.findChildren(QListWidget):
        for i in range(lw.count()):
            item = lw.item(i)
            item.setFlags(
                item.flags()
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
            )

    return widget


def load_add_entry_dialog() -> AddEntryDialog:
    """ตัวช่วยโหลดกล่องโต้ตอบเพิ่มข้อมูลการเติมน้ำมัน"""
    return AddEntryDialog()


def load_add_vehicle_dialog() -> QDialog:
    """ตัวช่วยโหลดกล่องโต้ตอบเพิ่มยานพาหนะ"""
    return cast(QDialog, load_ui("dialogs/add_vehicle_dialog"))


def load_about_dialog() -> QDialog:
    """ตัวช่วยโหลดกล่องโต้ตอบเกี่ยวกับโปรแกรม"""
    return cast(QDialog, load_ui("dialogs/about_dialog"))


def load_add_maintenance_dialog() -> QDialog:
    """ตัวช่วยโหลดกล่องโต้ตอบเพิ่มงานบำรุงรักษา"""
    return cast(QDialog, load_ui("dialogs/add_maintenance_dialog"))


def load_import_csv_dialog() -> QDialog:
    """ตัวช่วยโหลดกล่องโต้ตอบนำเข้าข้อมูลจาก CSV"""
    return cast(QDialog, load_ui("dialogs/import_csv_dialog"))


__all__ = [
    "MainWindow",
    "AddEntryDialog",
    "AddVehicleDialog",
    "AddMaintenanceDialog",
    "ImportCsvDialog",
    "AboutDialog",
    "asset_path",
    "load_ui",
    "load_add_entry_dialog",
    "load_add_vehicle_dialog",
    "load_about_dialog",
    "load_add_maintenance_dialog",
    "load_import_csv_dialog",
]
