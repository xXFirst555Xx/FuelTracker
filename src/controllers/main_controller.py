"""Main controller connecting the GUI with services and models."""

from datetime import date

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidgetItem,
    QMessageBox,
    QDialog,
)
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt
from pathlib import Path
import os

from ..models import FuelEntry, Vehicle
from ..services import ReportService, StorageService
from ..views import (
    load_ui,
    load_add_entry_dialog,
    load_add_vehicle_dialog,
)


class MainController:
    """Glue code between Qt widgets and application services."""

    def __init__(self, db_path: str | Path = "fuel.db", dark_mode: bool | None = None) -> None:
        self.storage = StorageService(db_path)
        self._dark_mode = dark_mode
        self.report_service = ReportService(self.storage)
        self.window: QMainWindow = load_ui("main_window")  # type: ignore
        self._selected_vehicle_id = None
        self._setup_style()
        self._connect_signals()
        self.refresh_vehicle_list()
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.dashboardPage)

    def _connect_signals(self) -> None:
        w = self.window
        if hasattr(w, "addEntryButton"):
            w.addEntryButton.clicked.connect(self.open_add_entry_dialog)
        if hasattr(w, "addVehicleButton"):
            w.addVehicleButton.clicked.connect(self.open_add_vehicle_dialog)
        if hasattr(w, "backButton"):
            w.backButton.clicked.connect(self.show_dashboard)
        if hasattr(w, "vehicleListWidget"):
            w.vehicleListWidget.itemSelectionChanged.connect(self._vehicle_changed)
        if hasattr(w, "sidebarList"):
            w.sidebarList.currentRowChanged.connect(self._switch_page)

    def _vehicle_changed(self) -> None:
        item = self.window.vehicleListWidget.currentItem()
        if item:
            self._selected_vehicle_id = item.data(Qt.UserRole)
        else:
            self._selected_vehicle_id = None

    def _setup_style(self) -> None:
        """Load application QSS theme."""
        app = QApplication.instance()
        if not app:
            return
        if self._dark_mode is None:
            theme = os.getenv("FT_THEME", "light").lower()
        else:
            theme = "dark" if self._dark_mode else "light"

        base = Path(__file__).resolve().parents[2] / "assets" / "qss"
        if theme == "dark":
            candidates = ["dark.qss", "theme_dark.qss"]
        else:
            candidates = ["theme.qss"]

        for name in candidates:
            css_path = base / name
            if css_path.exists():
                app.setStyleSheet(css_path.read_text(encoding="utf-8"))
                break


    def _switch_page(self, index: int) -> None:
        if not hasattr(self.window, "stackedWidget"):
            return
        if index == 0:
            self.show_dashboard()
        elif index == 1:
            self.show_add_entry_page()
        elif index == 2:
            self.show_report_page()
        elif index == 3:
            self.show_settings_page()

    def refresh_vehicle_list(self) -> None:
        if not hasattr(self.window, "vehicleListWidget"):
            return
        list_widget = self.window.vehicleListWidget
        list_widget.clear()
        for vehicle in self.storage.list_vehicles():
            item = QListWidgetItem(vehicle.name)
            item.setData(Qt.UserRole, vehicle.id)
            list_widget.addItem(item)

    # ------------------------------------------------------------------
    # Dialog handlers
    # ------------------------------------------------------------------
    def open_add_vehicle_dialog(self) -> None:
        dialog = load_add_vehicle_dialog()
        dialog.capacityLineEdit.setValidator(QDoubleValidator(0.0, 1e6, 2))
        if dialog.exec() == QDialog.Accepted:
            name = dialog.nameLineEdit.text().strip()
            vtype = dialog.typeLineEdit.text().strip()
            plate = dialog.plateLineEdit.text().strip()
            cap_text = dialog.capacityLineEdit.text()
            if not (name and vtype and plate and cap_text):
                QMessageBox.warning(dialog, "การตรวจสอบ", "กรุณากรอกข้อมูลให้ครบถ้วน")
                return
            vehicle = Vehicle(
                name=name,
                vehicle_type=vtype,
                license_plate=plate,
                tank_capacity_liters=float(cap_text),
            )
            self.storage.add_vehicle(vehicle)
            self.refresh_vehicle_list()

    def open_add_entry_dialog(self) -> None:
        if not self.storage.list_vehicles():
            QMessageBox.warning(self.window, "ไม่พบยานพาหนะ", "กรุณาเพิ่มยานพาหนะก่อน")
            return
        dialog = load_add_entry_dialog()
        dialog.dateEdit.setDate(date.today())
        dialog.odoBeforeEdit.setValidator(QDoubleValidator(0.0, 1e9, 2))
        dialog.odoAfterEdit.setValidator(QDoubleValidator(0.0, 1e9, 2))
        dialog.amountEdit.setValidator(QDoubleValidator(0.0, 1e9, 2))
        dialog.litersEdit.setValidator(QDoubleValidator(0.0, 1e9, 2))
        for v in self.storage.list_vehicles():
            dialog.vehicleComboBox.addItem(v.name, v.id)
        if dialog.exec() == QDialog.Accepted:
            vehicle_id = dialog.vehicleComboBox.currentData()
            try:
                entry = FuelEntry(
                    entry_date=dialog.dateEdit.date().toPython(),
                    vehicle_id=vehicle_id,
                    odo_before=float(dialog.odoBeforeEdit.text()),
                    odo_after=float(dialog.odoAfterEdit.text()),
                    amount_spent=float(dialog.amountEdit.text()),
                    liters=float(dialog.litersEdit.text()) if dialog.litersEdit.text() else None,
                )
            except ValueError:
                QMessageBox.warning(dialog, "ข้อผิดพลาด", "ข้อมูลตัวเลขไม่ถูกต้อง")
                return
            self.storage.add_entry(entry)

    # ------------------------------------------------------------------
    # Page switching
    # ------------------------------------------------------------------
    def show_dashboard(self) -> None:
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.dashboardPage)

    def show_add_entry_page(self) -> None:
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.addEntryPage)

    def show_report_page(self) -> None:
        stats = self.report_service.calc_overall_stats()
        if hasattr(self.window, "reportLabel"):
            text = "\n".join(f"{k}: {v}" for k, v in stats.items())
            self.window.reportLabel.setText(text)
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.reportsPage)

    def show_settings_page(self) -> None:
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.settingsPage)
