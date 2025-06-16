"""คอนโทรลเลอร์หลักเชื่อมต่อ GUI กับบริการและโมเดล"""

from datetime import date
from decimal import Decimal

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidgetItem,
    QListWidget,
    QMessageBox,
    QDialog,
    QDockWidget,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)
from PySide6.QtGui import QDoubleValidator, QUndoStack
from PySide6.QtCore import Qt, QObject, Signal, QEvent, QRunnable, QThreadPool, QTimer
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

try:
    from win10toast import ToastNotifier
except Exception:  # pragma: no cover - optional on non-Windows systems

    class ToastNotifier:
        def __init__(self, *_, **__):
            pass

        def show_toast(self, *_, **__):
            pass


from pathlib import Path
import os
from datetime import timedelta

from sqlmodel import Session, select

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from ..models import FuelEntry, Vehicle, Maintenance, FuelPrice
from ..services import ReportService, StorageService, Exporter, Importer
from ..services.oil_service import fetch_latest, get_price
from ..config import AppConfig
from .undo_commands import (
    AddEntryCommand,
    DeleteEntryCommand,
    AddVehicleCommand,
    DeleteVehicleCommand,
    UpdateVehicleCommand,
)
from ..views import (
    load_ui,
    load_add_entry_dialog,
    load_add_vehicle_dialog,
    load_about_dialog,
    load_add_maintenance_dialog,
    load_import_csv_dialog,
)
from ..views.reports_page import ReportsPage

DEFAULT_STATION = "ptt"
DEFAULT_FUEL_TYPE = "e20"


class StatsDock(QDockWidget):
    """วิดเจ็ตแบบ Dock แสดงสถิติแบบเรียลไทม์ของยานพาหนะ"""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__("สถิติ", parent)
        self.kml_label = QLabel("km/L: -")
        self.cost_label = QLabel("฿/km: -")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.kml_label)
        layout.addWidget(self.cost_label)
        self.setWidget(widget)


class MaintenanceDock(QDockWidget):
    """วิดเจ็ตแบบ Dock แสดงรายการงานบำรุงรักษาที่จะมาถึง"""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__("บำรุงรักษา", parent)
        self.list_widget = QListWidget()
        self.add_button = QPushButton("เพิ่ม")
        self.edit_button = QPushButton("แก้ไข")
        self.done_button = QPushButton("เสร็จ")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.list_widget)
        row = QHBoxLayout()
        row.addWidget(self.add_button)
        row.addWidget(self.edit_button)
        row.addWidget(self.done_button)
        layout.addLayout(row)
        self.setWidget(widget)


class OilPricesDock(QDockWidget):
    """Dock แสดงราคาน้ำมันที่บันทึกไว้."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__("ราคาน้ำมัน", parent)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["วันที่", "ประเภทเชื้อเพลิง", "ราคา"])
        self.figure = Figure(figsize=(4, 3))
        self.canvas = FigureCanvasQTAgg(self.figure)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.table)
        layout.addWidget(self.canvas)
        self.setWidget(widget)


class MainController(QObject):
    entry_changed = Signal()
    """โค้ดเชื่อมระหว่างวิดเจ็ต Qt กับบริการของแอป"""

    def __init__(
        self,
        db_path: str | Path = "fuel.db",
        dark_mode: bool | None = None,
        theme: str | None = None,
        config_path: str | Path | None = None,
    ) -> None:
        super().__init__()
        self.config_path = Path(config_path) if config_path else None
        self.config = AppConfig.load(self.config_path)
        self.storage = StorageService(db_path)
        self._dark_mode = dark_mode
        self._theme_override = theme.lower() if theme else None
        self.report_service = ReportService(self.storage)
        self.exporter = Exporter(self.storage)
        self.importer = Importer(self.storage)
        self.window: QMainWindow = load_ui("main_window")  # type: ignore
        self.undo_stack = QUndoStack(self.window)
        self.sync_enabled = False
        env_cloud = os.getenv("FT_CLOUD_DIR")
        self.cloud_path: Path | None = Path(env_cloud) if env_cloud else None
        self._selected_vehicle_id = None
        self.stats_dock = StatsDock(self.window)
        self.maint_dock = MaintenanceDock(self.window)
        self.oil_dock = OilPricesDock(self.window)
        self.window.addDockWidget(Qt.RightDockWidgetArea, self.stats_dock)
        self.window.addDockWidget(Qt.RightDockWidgetArea, self.maint_dock)
        self.window.addDockWidget(Qt.RightDockWidgetArea, self.oil_dock)
        if hasattr(self.window, "reportsContainer"):
            self.reports_page = ReportsPage(self.report_service, self.window)
            self.window.reportsLayout.replaceWidget(
                self.window.reportsContainer, self.reports_page
            )
            self.window.reportsContainer.deleteLater()
        if hasattr(self.window, "syncCheckBox"):
            self.window.syncCheckBox.setChecked(self.sync_enabled)
        if hasattr(self.window, "cloudPathEdit") and self.cloud_path:
            self.window.cloudPathEdit.setText(str(self.cloud_path))
        if hasattr(self.window, "stationComboBox"):
            self.window.stationComboBox.clear()
            self.window.stationComboBox.addItems(["PTT", "BCP"])
            idx = self.window.stationComboBox.findText(
                self.config.default_station.upper()
            )
            if idx >= 0:
                self.window.stationComboBox.setCurrentIndex(idx)
        if hasattr(self.window, "updateIntervalSpinBox"):
            self.window.updateIntervalSpinBox.setValue(self.config.update_hours)
        self.thread_pool = QThreadPool.globalInstance()
        self._price_timer_started = False
        self.window.installEventFilter(self)
        app = QApplication.instance()
        if app:
            app.aboutToQuit.connect(self.cleanup)
        self.entry_changed.connect(self._update_stats_panel)
        self.entry_changed.connect(self._refresh_maintenance_panel)
        self._setup_style()
        self._connect_signals()
        if hasattr(self.window, "budgetEdit"):
            self.window.budgetEdit.setValidator(QDoubleValidator(0.0, 1e9, 2))
        self.refresh_vehicle_list()
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.dashboardPage)

    def _connect_signals(self) -> None:
        w = self.window
        if hasattr(w, "addEntryButton"):
            w.addEntryButton.clicked.connect(self.open_add_entry_dialog)
        if hasattr(w, "importCSVButton"):
            w.importCSVButton.clicked.connect(self.open_import_csv_dialog)
        if hasattr(w, "addVehicleButton"):
            w.addVehicleButton.clicked.connect(self.open_add_vehicle_dialog)
        if hasattr(w, "editVehicleButton"):
            w.editVehicleButton.clicked.connect(self.open_edit_vehicle_dialog)
        if hasattr(w, "deleteVehicleButton"):
            w.deleteVehicleButton.clicked.connect(self.delete_selected_vehicle)
        if hasattr(w, "backButton"):
            w.backButton.clicked.connect(self.show_dashboard)
        if hasattr(w, "aboutButton"):
            w.aboutButton.clicked.connect(self.open_about_dialog)
        if hasattr(w, "syncCheckBox"):
            w.syncCheckBox.toggled.connect(self._toggle_sync)
        if hasattr(w, "browseCloudButton"):
            w.browseCloudButton.clicked.connect(self._browse_cloud_path)
        if hasattr(w, "stationComboBox"):
            w.stationComboBox.currentTextChanged.connect(self._station_changed)
        if hasattr(w, "updateIntervalSpinBox"):
            w.updateIntervalSpinBox.valueChanged.connect(self._interval_changed)
        if hasattr(w, "budgetVehicleComboBox"):
            w.budgetVehicleComboBox.currentIndexChanged.connect(
                self._budget_vehicle_changed
            )
        if hasattr(w, "saveBudgetButton"):
            w.saveBudgetButton.clicked.connect(self._save_budget)
        if hasattr(w, "vehicleListWidget"):
            w.vehicleListWidget.itemSelectionChanged.connect(self._vehicle_changed)
        if hasattr(w, "sidebarList"):
            w.sidebarList.currentRowChanged.connect(self._switch_page)
        if hasattr(self, "reports_page"):
            self.reports_page.export_button.clicked.connect(self.export_report)
            self.reports_page.refresh_button.clicked.connect(self.reports_page.refresh)
        self.maint_dock.add_button.clicked.connect(self.open_add_maintenance_dialog)
        self.maint_dock.edit_button.clicked.connect(self.open_edit_maintenance_dialog)
        self.maint_dock.done_button.clicked.connect(self.mark_selected_maintenance_done)

    def _toggle_sync(self, checked: bool) -> None:
        self.sync_enabled = checked

    def _browse_cloud_path(self) -> None:
        path = QFileDialog.getExistingDirectory(self.window, self.tr("เลือกโฟลเดอร์ซิงก์"))
        if path:
            self.cloud_path = Path(path)
            if hasattr(self.window, "cloudPathEdit"):
                self.window.cloudPathEdit.setText(path)

    def _station_changed(self, name: str) -> None:
        self.config.default_station = name.lower()
        self.config.save(self.config_path)

    def _interval_changed(self, hours: int) -> None:
        self.config.update_hours = int(hours)
        self.config.save(self.config_path)

    def _budget_vehicle_changed(self) -> None:
        if not hasattr(self.window, "budgetVehicleComboBox"):
            return
        vid = self.window.budgetVehicleComboBox.currentData()
        if vid is None or not hasattr(self.window, "budgetEdit"):
            return
        budget = self.storage.get_budget(vid)
        self.window.budgetEdit.setText("" if budget is None else str(budget))

    def _save_budget(self) -> None:
        if not (
            hasattr(self.window, "budgetVehicleComboBox")
            and hasattr(self.window, "budgetEdit")
        ):
            return
        vid = self.window.budgetVehicleComboBox.currentData()
        if vid is None:
            return
        try:
            amount = float(self.window.budgetEdit.text())
        except ValueError:
            QMessageBox.warning(self.window, "ข้อผิดพลาด", "ข้อมูลตัวเลขไม่ถูกต้อง")
            return
        self.storage.set_budget(vid, amount)
        self._check_budget(vid, date.today())

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

    def _check_budget(self, vehicle_id: int, entry_date: date) -> None:
        budget = self.storage.get_budget(vehicle_id)
        if budget is None:
            return
        total = self.storage.get_total_spent(
            vehicle_id, entry_date.year, entry_date.month
        )
        if total > budget:
            QMessageBox.warning(
                self.window,
                "เกินงบประมาณ",
                "ค่าใช้จ่ายค่าน้ำมันเดือนนี้เกินงบที่ตั้งไว้",
            )
            if os.name == "nt":
                try:
                    ToastNotifier().show_toast(
                        "FuelTracker",
                        "เกินงบประมาณ",
                        threaded=True,
                    )
                except Exception:
                    pass

    def _refresh_maintenance_panel(self) -> None:
        vid = self._selected_vehicle_id
        if vid is None:
            self.maint_dock.list_widget.clear()
            return
        tasks = self.storage.list_maintenances(vid)
        self.maint_dock.list_widget.clear()
        entries = self.storage.get_entries_by_vehicle(vid)
        current_odo = (
            entries[-1].odo_after
            if entries and entries[-1].odo_after is not None
            else None
        )
        for t in tasks:
            text = t.name
            if not t.is_done:
                if t.due_odo is not None:
                    text += f" @ {t.due_odo}km"
                if t.due_date is not None:
                    text += f" by {t.due_date}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, t.id)
            if (
                current_odo is not None
                and t.due_odo is not None
                and current_odo >= t.due_odo
            ) or (t.due_date is not None and t.due_date <= date.today()):
                item.setForeground(Qt.red)
            self.maint_dock.list_widget.addItem(item)

    def _notify_due_maintenance(self, vehicle_id: int, odo: float, when: date) -> None:
        due = self.storage.list_due_maintenances(vehicle_id, odo=odo, date_=when)
        if not due:
            return
        names = ", ".join(d.name for d in due)
        QMessageBox.information(
            self.window,
            "ถึงกำหนดบำรุงรักษา",
            f"งานที่ถึงกำหนด: {names}",
        )

    def _setup_style(self) -> None:
        """ปรับสไตล์ชีตของแอปตามธีมที่เลือก"""
        app = QApplication.instance()
        if not app:
            return

        theme = self._theme_override
        if theme is None:
            for arg in app.arguments():
                if arg.startswith("--theme="):
                    theme = arg.split("=", 1)[1]
                    break
        theme = (theme or os.getenv("FT_THEME", "system")).lower()
        if self._dark_mode is not None:
            theme = "dark" if self._dark_mode else "light"
        if theme == "system":
            scheme = app.styleHints().colorScheme()
            theme = "dark" if scheme == Qt.ColorScheme.Dark else "light"

        qss_map = {
            "light": "theme.qss",
            "dark": "theme_dark.qss",
            "modern": "modern.qss",
        }
        qss_file = qss_map.get(theme)
        if qss_file:
            try:
                qss_path = (
                    Path(__file__).resolve().parents[2] / "assets" / "qss" / qss_file
                )
                with open(qss_path, "r", encoding="utf-8") as fh:
                    app.setStyleSheet(fh.read())
            except OSError:
                pass

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
        if hasattr(self.window, "vehicleListWidget"):
            list_widget = self.window.vehicleListWidget
            list_widget.clear()
            for vehicle in self.storage.list_vehicles():
                item = QListWidgetItem(vehicle.name)
                item.setData(Qt.UserRole, vehicle.id)
                list_widget.addItem(item)
        if hasattr(self.window, "budgetVehicleComboBox"):
            combo = self.window.budgetVehicleComboBox
            combo.clear()
            for v in self.storage.list_vehicles():
                combo.addItem(v.name, v.id)
            self._budget_vehicle_changed()

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
            cmd = AddVehicleCommand(self.storage, vehicle)
            self.undo_stack.push(cmd)
            self.refresh_vehicle_list()

    def open_edit_vehicle_dialog(self) -> None:
        item = self.window.vehicleListWidget.currentItem()
        if item is None:
            QMessageBox.warning(self.window, "ไม่พบยานพาหนะ", "กรุณาเลือกยานพาหนะ")
            return
        vid = item.data(Qt.UserRole)
        vehicle = self.storage.get_vehicle(vid)
        if vehicle is None:
            return
        before = Vehicle.model_validate(vehicle)
        dialog = load_add_vehicle_dialog()
        dialog.setWindowTitle("แก้ไขยานพาหนะ")
        dialog.capacityLineEdit.setValidator(QDoubleValidator(0.0, 1e6, 2))
        dialog.nameLineEdit.setText(vehicle.name)
        dialog.typeLineEdit.setText(vehicle.vehicle_type)
        dialog.plateLineEdit.setText(vehicle.license_plate)
        dialog.capacityLineEdit.setText(str(vehicle.tank_capacity_liters))
        if dialog.exec() == QDialog.Accepted:
            vehicle.name = dialog.nameLineEdit.text().strip()
            vehicle.vehicle_type = dialog.typeLineEdit.text().strip()
            vehicle.license_plate = dialog.plateLineEdit.text().strip()
            try:
                vehicle.tank_capacity_liters = float(dialog.capacityLineEdit.text())
            except ValueError:
                QMessageBox.warning(dialog, "ข้อผิดพลาด", "ข้อมูลตัวเลขไม่ถูกต้อง")
                return
            cmd = UpdateVehicleCommand(self.storage, vehicle, before)
            self.undo_stack.push(cmd)
            self.refresh_vehicle_list()

    def delete_selected_vehicle(self) -> None:
        item = self.window.vehicleListWidget.currentItem()
        if item is None:
            QMessageBox.warning(self.window, "ไม่พบยานพาหนะ", "กรุณาเลือกรายการ")
            return
        vid = item.data(Qt.UserRole)
        if (
            QMessageBox.question(
                self.window,
                "ยืนยัน",
                "ลบยานพาหนะที่เลือกหรือไม่?",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        cmd = DeleteVehicleCommand(self.storage, vid)
        self.undo_stack.push(cmd)
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

        def _auto_calc() -> None:
            if dialog.litersEdit.text():
                return
            amt_text = dialog.amountEdit.text()
            if not amt_text:
                return
            station = self.config.default_station
            with Session(self.storage.engine) as sess:
                price = get_price(sess, DEFAULT_FUEL_TYPE, station, date.today())
                if price is None:
                    price = get_price(
                        sess,
                        DEFAULT_FUEL_TYPE,
                        station,
                        date.today() - timedelta(days=1),
                    )
            if price is None:
                return
            liters = Decimal(amt_text) / price
            dialog.litersEdit.setText(f"{liters.quantize(Decimal('0.01'))}")

        dialog.amountEdit.editingFinished.connect(_auto_calc)
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
                cmd = AddEntryCommand(self.storage, entry, self.entry_changed)
                self.undo_stack.push(cmd)
            except ValueError as exc:
                QMessageBox.warning(dialog, "การตรวจสอบ", str(exc))
                return
            self._check_budget(entry.vehicle_id, entry.entry_date)
            if entry.odo_after is not None:
                self._notify_due_maintenance(
                    entry.vehicle_id, entry.odo_after, entry.entry_date
                )

    def open_import_csv_dialog(self) -> None:
        if not self.storage.list_vehicles():
            QMessageBox.warning(self.window, "ไม่พบยานพาหนะ", "กรุณาเพิ่มยานพาหนะก่อน")
            return
        dialog = load_import_csv_dialog()
        for v in self.storage.list_vehicles():
            dialog.vehicleComboBox.addItem(v.name, v.id)

        entries: list[FuelEntry] = []

        def _load_file() -> None:
            path, _ = QFileDialog.getOpenFileName(
                dialog, self.tr("เลือกไฟล์ CSV"), "", "CSV Files (*.csv)"
            )
            if path:
                dialog.fileLineEdit.setText(path)
                entries.clear()
                entries.extend(self.importer.read_csv(Path(path)))
                table = dialog.previewTable
                headers = [
                    "date",
                    "odo_before",
                    "odo_after",
                    "distance",
                    "liters",
                    "amount_spent",
                ]
                table.setColumnCount(len(headers))
                table.setHorizontalHeaderLabels(headers)
                table.setRowCount(len(entries))
                for r, e in enumerate(entries):
                    dist = e.odo_after - e.odo_before if e.odo_after is not None else ""
                    values = [
                        e.entry_date.isoformat(),
                        str(e.odo_before),
                        "" if e.odo_after is None else str(e.odo_after),
                        "" if dist == "" else str(dist),
                        "" if e.liters is None else str(e.liters),
                        "" if e.amount_spent is None else str(e.amount_spent),
                    ]
                    for c, val in enumerate(values):
                        table.setItem(r, c, QTableWidgetItem(val))

        dialog.browseButton.clicked.connect(_load_file)

        if dialog.exec() == QDialog.Accepted and entries:
            vehicle_id = dialog.vehicleComboBox.currentData()
            for e in entries:
                e.vehicle_id = vehicle_id
                self.storage.add_entry(e)
            self.entry_changed.emit()

    def open_about_dialog(self) -> None:
        dialog = load_about_dialog()
        dialog.exec()

    def open_add_maintenance_dialog(self) -> None:
        if not self.storage.list_vehicles():
            QMessageBox.warning(self.window, "ไม่พบยานพาหนะ", "กรุณาเพิ่มยานพาหนะก่อน")
            return
        dialog = load_add_maintenance_dialog()
        dialog.dateEdit.setDate(date.today())
        dialog.odoLineEdit.setValidator(QDoubleValidator(0.0, 1e9, 0))
        for v in self.storage.list_vehicles():
            dialog.vehicleComboBox.addItem(v.name, v.id)
        if dialog.exec() == QDialog.Accepted:
            try:
                odo = (
                    int(dialog.odoLineEdit.text())
                    if dialog.odoLineEdit.text()
                    else None
                )
            except ValueError:
                QMessageBox.warning(dialog, "ข้อผิดพลาด", "ข้อมูลตัวเลขไม่ถูกต้อง")
                return
            task = Maintenance(
                vehicle_id=dialog.vehicleComboBox.currentData(),
                name=dialog.nameLineEdit.text().strip(),
                due_odo=odo,
                due_date=(
                    dialog.dateEdit.date().toPython()
                    if dialog.dateEdit.date()
                    else None
                ),
                note=dialog.noteLineEdit.text().strip() or None,
            )
            self.storage.add_maintenance(task)
            self._refresh_maintenance_panel()

    def open_edit_maintenance_dialog(self) -> None:
        item = self.maint_dock.list_widget.currentItem()
        if item is None:
            QMessageBox.warning(self.window, "ไม่พบงาน", "กรุณาเลือกรายการ")
            return
        task_id = item.data(Qt.UserRole)
        task = self.storage.get_maintenance(task_id)
        if task is None:
            return
        dialog = load_add_maintenance_dialog()
        dialog.setWindowTitle("แก้ไขงานบำรุงรักษา")
        dialog.dateEdit.setDate(task.due_date or date.today())
        dialog.odoLineEdit.setValidator(QDoubleValidator(0.0, 1e9, 0))
        dialog.nameLineEdit.setText(task.name)
        dialog.odoLineEdit.setText(
            str(task.due_odo) if task.due_odo is not None else ""
        )
        dialog.noteLineEdit.setText(task.note or "")
        for v in self.storage.list_vehicles():
            dialog.vehicleComboBox.addItem(v.name, v.id)
            if v.id == task.vehicle_id:
                dialog.vehicleComboBox.setCurrentIndex(
                    dialog.vehicleComboBox.count() - 1
                )
        if dialog.exec() == QDialog.Accepted:
            try:
                odo = (
                    int(dialog.odoLineEdit.text())
                    if dialog.odoLineEdit.text()
                    else None
                )
            except ValueError:
                QMessageBox.warning(dialog, "ข้อผิดพลาด", "ข้อมูลตัวเลขไม่ถูกต้อง")
                return
            task.vehicle_id = dialog.vehicleComboBox.currentData()
            task.name = dialog.nameLineEdit.text().strip()
            task.due_odo = odo
            task.due_date = (
                dialog.dateEdit.date().toPython() if dialog.dateEdit.date() else None
            )
            task.note = dialog.noteLineEdit.text().strip() or None
            self.storage.update_maintenance(task)
            self._refresh_maintenance_panel()

    def mark_selected_maintenance_done(self) -> None:
        item = self.maint_dock.list_widget.currentItem()
        if item is None:
            QMessageBox.warning(self.window, "ไม่พบงาน", "กรุณาเลือกรายการ")
            return
        task_id = item.data(Qt.UserRole)
        self.storage.mark_maintenance_done(task_id, True)
        self._refresh_maintenance_panel()

    def export_report(self) -> None:
        out_csv = Path("report.csv")
        out_pdf = Path("report.pdf")
        today = date.today()
        self.exporter.monthly_csv(today.month, today.year, out_csv)
        self.exporter.monthly_pdf(today.month, today.year, out_pdf)

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
        if hasattr(self, "reports_page"):
            self.reports_page.refresh()
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.reportsPage)

    def show_settings_page(self) -> None:
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.settingsPage)

    # ------------------------------------------------------------------
    # ตัวจัดตารางราคาน้ำมัน
    # ------------------------------------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if (
            obj is self.window
            and event.type() == QEvent.Show
            and not self._price_timer_started
        ):
            self._price_timer_started = True
            self._schedule_price_update()
        return super().eventFilter(obj, event)

    def _schedule_price_update(self) -> None:

        class Job(QRunnable):
            def __init__(self, controller: "MainController") -> None:
                super().__init__()
                self.controller = controller

            def run(self) -> None:  # type: ignore[override]
                with Session(self.controller.storage.engine) as sess:
                    fetch_latest(sess, self.controller.config.default_station)
                    self.controller._load_prices()

        self.thread_pool.start(Job(self))
        interval_ms = self.config.update_hours * 3_600_000
        QTimer.singleShot(interval_ms, self._schedule_price_update)

    def _load_prices(self) -> None:
        with Session(self.storage.engine) as session:
            rows = session.exec(
                select(FuelPrice).order_by(FuelPrice.date.desc()).limit(90 * 6)
            ).all()
        self.oil_dock.table.setRowCount(len(rows))
        self.oil_dock.figure.clear()
        ax = self.oil_dock.figure.add_subplot(111)
        by_type: dict[str, list[tuple[date, Decimal]]] = {}
        for idx, r in enumerate(rows):
            self.oil_dock.table.setItem(idx, 0, QTableWidgetItem(r.date.isoformat()))
            self.oil_dock.table.setItem(idx, 1, QTableWidgetItem(r.name_th))
            self.oil_dock.table.setItem(idx, 2, QTableWidgetItem(str(r.price)))
            by_type.setdefault(r.fuel_type, []).append((r.date, r.price))
        fuel = next(iter(by_type)) if by_type else None
        if fuel:
            points = sorted(by_type[fuel], key=lambda t: t[0])[-90:]
            ax.plot([d for d, _ in points], [float(p) for _, p in points])
        self.oil_dock.canvas.draw_idle()

    # ------------------------------------------------------------------
    # Data modification helpers
    # ------------------------------------------------------------------

    def delete_entry(self, entry_id: int) -> None:
        cmd = DeleteEntryCommand(self.storage, entry_id, self.entry_changed)
        self.undo_stack.push(cmd)

    def delete_vehicle(self, vehicle_id: int) -> None:
        cmd = DeleteVehicleCommand(self.storage, vehicle_id)
        self.undo_stack.push(cmd)

    def cleanup(self) -> None:
        if hasattr(self.window, "removeEventFilter"):
            try:
                self.window.removeEventFilter(self)
            except RuntimeError:
                pass

    def shutdown(self) -> None:
        backup = self.storage.auto_backup()
        if self.sync_enabled and self.cloud_path is not None:
            self.storage.sync_to_cloud(backup.parent, self.cloud_path)
