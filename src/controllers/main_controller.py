"""Main controller connecting the GUI with services and models."""

from datetime import date

from PySide6.QtWidgets import (
    QMainWindow,
    QListWidgetItem,
    QMessageBox,
    QDialog,
)
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt
from pathlib import Path

from ..models import FuelEntry, Vehicle
from ..services import ReportService, StorageService
from ..views import (
    load_ui,
    load_add_entry_dialog,
    load_add_vehicle_dialog,
)


class MainController:
    """Glue code between Qt widgets and application services."""

    def __init__(self, db_path: str | Path = "fuel.db") -> None:
        self.storage = StorageService(db_path)
        self.report_service = ReportService(self.storage)
        self.window: QMainWindow = load_ui("main_window")  # type: ignore
        self._selected_vehicle_id = None
        self._connect_signals()
        self.refresh_vehicle_list()
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.entryPage)

    def _connect_signals(self) -> None:
        w = self.window
        if hasattr(w, "addEntryButton"):
            w.addEntryButton.clicked.connect(self.open_add_entry_dialog)
        if hasattr(w, "addVehicleButton"):
            w.addVehicleButton.clicked.connect(self.open_add_vehicle_dialog)
        if hasattr(w, "reportButton"):
            w.reportButton.clicked.connect(self.show_report_page)
        if hasattr(w, "backButton"):
            w.backButton.clicked.connect(self.show_entry_page)
        if hasattr(w, "vehicleListWidget"):
            w.vehicleListWidget.itemSelectionChanged.connect(self._vehicle_changed)

    def _vehicle_changed(self) -> None:
        item = self.window.vehicleListWidget.currentItem()
        if item:
            self._selected_vehicle_id = item.data(Qt.UserRole)
        else:
            self._selected_vehicle_id = None

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
                QMessageBox.warning(dialog, "Validation", "All fields are required.")
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
            QMessageBox.warning(self.window, "No Vehicle", "Please add a vehicle first.")
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
                QMessageBox.warning(dialog, "Validation", "Invalid numeric input.")
                return
            self.storage.add_entry(entry)

    # ------------------------------------------------------------------
    # Page switching
    # ------------------------------------------------------------------
    def show_report_page(self) -> None:
        stats = self.report_service.calc_overall_stats()
        if hasattr(self.window, "reportLabel"):
            text = "\n".join(f"{k}: {v}" for k, v in stats.items())
            self.window.reportLabel.setText(text)
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.reportPage)

    def show_entry_page(self) -> None:
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.entryPage)
