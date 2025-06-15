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
    QLabel,
    QVBoxLayout,
    QWidget,
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

from ..models import FuelEntry, Vehicle, FuelPrice
from ..services import ReportService, StorageService
from ..services.oil_service import fetch_latest, get_price
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
)

DEFAULT_STATION = "ptt"
DEFAULT_FUEL_TYPE = "e20"


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


class MaintenanceDock(QDockWidget):
    """Dockable widget listing upcoming maintenance tasks."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__("Maintenance", parent)
        self.list_widget = QListWidget()
        self.setWidget(self.list_widget)


class OilPricesDock(QDockWidget):
    """Dock displaying stored oil prices."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__("Oil Prices", parent)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["date", "fuel_type", "price"])
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
    ) -> None:
        super().__init__()
        self.storage = StorageService(db_path)
        self._dark_mode = dark_mode
        self._theme_override = theme.lower() if theme else None
        self.report_service = ReportService(self.storage)
        self.window: QMainWindow = load_ui("main_window")  # type: ignore
        self.undo_stack = QUndoStack(self.window)
        self.sync_enabled = False
        self.cloud_path: Path | None = None
        self._selected_vehicle_id = None
        self.stats_dock = StatsDock(self.window)
        self.maint_dock = MaintenanceDock(self.window)
        self.oil_dock = OilPricesDock(self.window)
        self.window.addDockWidget(Qt.RightDockWidgetArea, self.stats_dock)
        self.window.addDockWidget(Qt.RightDockWidgetArea, self.maint_dock)
        self.window.addDockWidget(Qt.RightDockWidgetArea, self.oil_dock)
        self.thread_pool = QThreadPool.globalInstance()
        self._price_timer_started = False
        self.window.installEventFilter(self)
        self.entry_changed.connect(self._update_stats_panel)
        self.entry_changed.connect(self._refresh_maintenance_panel)
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
        if hasattr(w, "editVehicleButton"):
            w.editVehicleButton.clicked.connect(self.open_edit_vehicle_dialog)
        if hasattr(w, "deleteVehicleButton"):
            w.deleteVehicleButton.clicked.connect(self.delete_selected_vehicle)
        if hasattr(w, "backButton"):
            w.backButton.clicked.connect(self.show_dashboard)
        if hasattr(w, "aboutButton"):
            w.aboutButton.clicked.connect(self.open_about_dialog)
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
                "Budget exceeded",
                "This month's fuel spending exceeded the set budget.",
            )
            if os.name == "nt":
                try:
                    ToastNotifier().show_toast(
                        "FuelTracker",
                        "Budget exceeded",
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
            "Maintenance due",
            f"Tasks due: {names}",
        )

    def _setup_style(self) -> None:
        """Apply application stylesheet based on the selected theme."""
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
                qss_path = Path(__file__).resolve().parents[2] / "assets" / "qss" / qss_file
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
        if QMessageBox.question(
            self.window,
            "ยืนยัน",
            "ลบยานพาหนะที่เลือกหรือไม่?",
        ) != QMessageBox.StandardButton.Yes:
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
            with Session(self.storage.engine) as sess:
                price = get_price(
                    sess, DEFAULT_FUEL_TYPE, DEFAULT_STATION, date.today()
                )
                if price is None:
                    price = get_price(
                        sess,
                        DEFAULT_FUEL_TYPE,
                        DEFAULT_STATION,
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

    def open_about_dialog(self) -> None:
        dialog = load_about_dialog()
        dialog.exec()

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
    # Oil price scheduler
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
            def run(inner_self) -> None:  # type: ignore[override]
                with Session(self.storage.engine) as sess:
                    fetch_latest(sess)
                    self._load_prices()

        self.thread_pool.start(Job())
        QTimer.singleShot(86_400_000, self._schedule_price_update)

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
            self.oil_dock.table.setItem(idx, 1, QTableWidgetItem(r.fuel_type))
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

    def shutdown(self) -> None:
        backup = self.storage.auto_backup()
        if self.sync_enabled and self.cloud_path is not None:
            self.storage.sync_to_cloud(backup.parent, self.cloud_path)
