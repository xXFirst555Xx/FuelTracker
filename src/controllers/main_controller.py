"""คอนโทรลเลอร์หลักเชื่อมต่อ GUI กับบริการและโมเดล"""

from datetime import date

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidgetItem,
    QMessageBox,
    QDialog,
    QDockWidget,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt, QObject, Signal
from pathlib import Path
import os

from ..models import FuelEntry, Vehicle
from ..services import ReportService, StorageService
from ..views import (
    load_ui,
    load_add_entry_dialog,
    load_add_vehicle_dialog,
)


class StatsDock(QDockWidget):
    """Dockable widget showing live statistics for a vehicle."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__("Statistics", parent)
        self.kml_label = QLabel("km/L: -")
        self.cost_label = QLabel("฿/km: -")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.kml_label)
        layout.addWidget(self.cost_label)
        self.setWidget(widget)


class MainController(QObject):
    entry_changed = Signal()
    """โค้ดเชื่อมระหว่างวิดเจ็ต Qt กับบริการของแอป"""

    def __init__(
        self,
        db_path: str | Path = "fuel.db",
        dark_mode: bool | None = None,
        theme: str | None = None,
    ) -> None:
        super().__init__()
        self.storage = StorageService(db_path)
        self._dark_mode = dark_mode
        self._theme_override = theme.lower() if theme else None
        self.report_service = ReportService(self.storage)
        self.window: QMainWindow = load_ui("main_window")  # type: ignore
        self._selected_vehicle_id = None
        self.stats_dock = StatsDock(self.window)
        self.window.addDockWidget(Qt.RightDockWidgetArea, self.stats_dock)
        self.entry_changed.connect(self._update_stats_panel)
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
        self._update_stats_panel()

    def _update_stats_panel(self) -> None:
        vid = self._selected_vehicle_id
        if vid is None:
            self.stats_dock.kml_label.setText("km/L: -")
            self.stats_dock.cost_label.setText("฿/km: -")
            return
        entries = self.storage.get_entries_by_vehicle(vid)
        total_distance = 0.0
        total_liters = 0.0
        total_price = 0.0
        for e in entries:
            if e.odo_after is None:
                continue
            total_distance += e.odo_after - e.odo_before
            if e.liters:
                total_liters += e.liters
            if e.amount_spent:
                total_price += e.amount_spent
        kmpl = total_distance / total_liters if total_liters else 0.0
        cost = total_price / total_distance if total_distance else 0.0
        self.stats_dock.kml_label.setText(f"km/L: {kmpl:.2f}")
        self.stats_dock.cost_label.setText(f"฿/km: {cost:.2f}")

    def _setup_style(self) -> None:
        """โหลดธีม QSS ของแอป"""
        app = QApplication.instance()
        if not app:
            return
        if self._theme_override is not None:
            theme = self._theme_override
        elif self._dark_mode is None:
            theme = None
        else:
            theme = "dark" if self._dark_mode else "light"

        if theme is None:
            args = app.arguments()
            for i, arg in enumerate(args):
                if arg.startswith("--theme="):
                    theme = arg.split("=", 1)[1].lower()
                    break
                if arg == "--theme" and i + 1 < len(args):
                    theme = args[i + 1].lower()
                    break

        if theme is None:
            theme = os.getenv("FT_THEME", "light").lower()

        base = Path(__file__).resolve().parents[2] / "assets" / "qss"
        if theme == "dark":
            candidates = ["dark.qss", "theme_dark.qss"]
        elif theme == "modern":
            candidates = ["modern.qss"]
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
                    liters=(
                        float(dialog.litersEdit.text())
                        if dialog.litersEdit.text()
                        else None
                    ),
                )
            except ValueError:
                QMessageBox.warning(dialog, "ข้อผิดพลาด", "ข้อมูลตัวเลขไม่ถูกต้อง")
                return
            try:
                self.storage.add_entry(entry)
            except ValueError as exc:
                QMessageBox.warning(dialog, "การตรวจสอบ", str(exc))
                return
            self.entry_changed.emit()

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

    # ------------------------------------------------------------------
    # Data modification helpers
    # ------------------------------------------------------------------

    def delete_entry(self, entry_id: int) -> None:
        self.storage.delete_entry(entry_id)
        self.entry_changed.emit()
