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
from PySide6.QtGui import (
    QDoubleValidator,
    QUndoStack,
    QCloseEvent,
    QShortcut,
    QKeySequence,
)
from PySide6.QtCore import (
    Qt,
    QMetaObject,  # noqa: F401 - used for monkeypatching in tests
    QObject,
    Signal,
    QEvent,
    QRunnable,
    QThreadPool,
    QTimer,
    QPropertyAnimation,
    QPoint,
    QParallelAnimationGroup,
    QSettings,
    QByteArray,
    QDate,
    Slot,
)
from shiboken6 import isValid
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QSystemTrayIcon

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from win10toast import ToastNotifier
else:
    try:
        from win10toast import ToastNotifier  # type: ignore[import-not-found]
    except Exception:  # pragma: no cover - optional on non-Windows systems

        class ToastNotifier:
            def __init__(self, *_, **__):
                pass

            def show_toast(self, *_, **__):
                pass


from pathlib import Path
import logging
logger = logging.getLogger(__name__)
import os
import sys
from datetime import datetime
import requests

from ..settings import Settings

from sqlmodel import Session, select

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from ..models import FuelEntry, Vehicle, Maintenance, FuelPrice
from ..services import (
    ReportService,
    StorageService,
    Exporter,
    Importer,
    ThemeManager,
    TrayIconManager,
)
from ..services.oil_service import fetch_latest, get_price as _get_price
from ..config import AppConfig
from .undo_commands import (
    AddEntryCommand,
    DeleteEntryCommand,
    AddVehicleCommand,
    DeleteVehicleCommand,
    UpdateVehicleCommand,
)
from ..views import (
    MainWindow,
    AddVehicleDialog,
    AboutDialog,
    AddMaintenanceDialog,
    ImportCsvDialog,
    load_add_entry_dialog,
)
from ..views.reports_page import ReportsPage
from ..hotkey import GlobalHotkey

DEFAULT_FUEL_TYPE = "e20"


def get_price(*args, **kwargs):
    """Wrapper to access :func:`src.services.oil_service.get_price`."""
    return _get_price(*args, **kwargs)


class StatsDock(QDockWidget):
    """วิดเจ็ตแบบ Dock แสดงสถิติแบบเรียลไทม์ของยานพาหนะ"""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__("สถิติ", parent)
        # ADDED: ensure unique object name for saveState
        self.setObjectName("statsDock")
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
        # ADDED: ensure unique object name for saveState
        self.setObjectName("maintenanceDock")
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
        # ADDED: ensure unique object name for saveState
        self.setObjectName("oilPricesDock")
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["วันที่", "ประเภทเชื้อเพลิง", "ราคา"])
        self.figure = Figure(figsize=(4, 3))
        # ``FigureCanvasQTAgg`` comes from ``matplotlib`` which is not fully typed
        self.canvas = FigureCanvasQTAgg(self.figure)  # type: ignore[no-untyped-call]
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.table)
        layout.addWidget(self.canvas)
        self.setWidget(widget)


class MainController(QObject):
    entry_changed = Signal()
    export_finished = Signal(Path, Path)
    """โค้ดเชื่อมระหว่างวิดเจ็ต Qt กับบริการของแอป"""

    def __init__(
        self,
        db_path: str | Path | None = None,
        dark_mode: bool | None = None,
        theme: str | None = None,
        config_path: str | Path | None = None,
    ) -> None:
        super().__init__()
        self.env = Settings()
        self.config_path = Path(config_path) if config_path else None
        self.config = AppConfig.load(self.config_path)
        self.storage = StorageService(db_path or self.env.db_path)
        self._dark_mode = dark_mode
        self._theme_override = theme.lower() if theme else None
        self.report_service = ReportService(self.storage)
        self.exporter = Exporter(self.storage)
        self.importer = Importer(self.storage)
        self.window: MainWindow = MainWindow()
        self.global_hotkey: GlobalHotkey | None = None
        self.settings = QSettings("FuelTracker", "MainWindow")
        geom = self.settings.value("windowGeometry")
        if isinstance(geom, (QByteArray, bytes, bytearray, memoryview)):
            self.window.restoreGeometry(geom)
        state = self.settings.value("windowState")
        if isinstance(state, (QByteArray, bytes, bytearray, memoryview)):
            self.window.restoreState(state)
        self.undo_stack = QUndoStack(self.window)
        self.sync_enabled = False
        self.cloud_path: Path | None = (
            Path(self.env.ft_cloud_dir) if self.env.ft_cloud_dir else None
        )
        self._selected_vehicle_id = None
        self.stats_dock = StatsDock(self.window)
        self.maint_dock = MaintenanceDock(self.window)
        self.oil_dock = OilPricesDock(self.window)
        self.window.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, self.stats_dock
        )
        self.window.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, self.maint_dock
        )
        self.window.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, self.oil_dock
        )
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
        if hasattr(self.window, "themeComboBox"):
            idx = self.window.themeComboBox.findText(
                self.config.theme, Qt.MatchFlag.MatchFixedString
            )
            if idx >= 0:
                self.window.themeComboBox.setCurrentIndex(idx)
        self.thread_pool = QThreadPool.globalInstance()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._price_timer_started = False
        self.window.installEventFilter(self)
        app = QApplication.instance()
        self.theme_manager = ThemeManager(app) if app else None
        if app:
            app.aboutToQuit.connect(self.cleanup)
            app.aboutToQuit.connect(self.shutdown)
            if self.theme_manager is not None:
                self.theme_manager.palette_changed.connect(self._on_palette_changed)
        self.entry_changed.connect(self._update_stats_panel)
        self.entry_changed.connect(self._refresh_maintenance_panel)
        self._setup_style()
        self._connect_signals()
        self.tray_manager = TrayIconManager(
            self.window,
            self.window.show,
            self.window.hide,
            self.open_add_entry_dialog,
            self._tray_quit,
        )
        self.tray_manager.show()
        self._setup_hotkey()
        self.window.closeEvent = self._close_event  # type: ignore[method-assign]
        if hasattr(self.window, "budgetEdit"):
            self.window.budgetEdit.setValidator(QDoubleValidator(0.0, 1e9, 2))
        self.refresh_vehicle_list()
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.dashboardPage)

    @property
    def tray_icon(self) -> QSystemTrayIcon:
        """Return the underlying system tray icon."""
        return self.tray_manager.tray_icon

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
        if hasattr(w, "themeComboBox"):
            w.themeComboBox.currentTextChanged.connect(self._theme_changed)
        if hasattr(w, "budgetVehicleComboBox"):
            w.budgetVehicleComboBox.currentIndexChanged.connect(
                self._budget_vehicle_changed
            )
        if hasattr(w, "saveBudgetButton"):
            w.saveBudgetButton.clicked.connect(self._save_budget)
        if hasattr(w, "vehicleListWidget"):
            w.vehicleListWidget.itemSelectionChanged.connect(self._vehicle_changed)
        if hasattr(w, "searchLineEdit"):
            w.searchLineEdit.textChanged.connect(self.filter_entries)
        if hasattr(w, "startDateEdit"):
            w.startDateEdit.dateChanged.connect(self.filter_entries)
        if hasattr(w, "sidebarList"):
            w.sidebarList.currentRowChanged.connect(self._switch_page)
        if hasattr(self, "reports_page"):
            self.reports_page.export_button.clicked.connect(self.export_report)
            self.reports_page.refresh_button.clicked.connect(self.reports_page.refresh)
            self.export_finished.connect(
                lambda c, p: QMessageBox.information(
                    self.window, self.tr("เสร็จสิ้น"), self.tr("ส่งออกรายงานแล้ว")
                )
            )
        self.maint_dock.add_button.clicked.connect(self.open_add_maintenance_dialog)
        self.maint_dock.edit_button.clicked.connect(self.open_edit_maintenance_dialog)
        self.maint_dock.done_button.clicked.connect(self.mark_selected_maintenance_done)
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+N"), w)
        self.shortcut_new.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_new.activated.connect(self.open_add_entry_dialog)
        self.shortcut_about = QShortcut(QKeySequence("F1"), w)
        self.shortcut_about.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_about.activated.connect(self.open_about_dialog)
        if hasattr(w, "hotkeyCheckBox"):
            w.hotkeyCheckBox.toggled.connect(self._toggle_hotkey)
        if hasattr(w, "startupShortcutButton"):
            w.startupShortcutButton.clicked.connect(self._toggle_startup_shortcut)

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

    def _theme_changed(self, name: str) -> None:
        self.config.theme = name.lower()
        self.config.save(self.config_path)
        self._setup_style()

    def _toggle_startup_shortcut(self) -> None:
        if os.name != "nt":
            QMessageBox.information(self.window, "ไม่รองรับ", "ใช้ได้เฉพาะบน Windows")
            return
        startup_base = self.env.appdata or ""
        startup = (
            Path(startup_base)
            / "Microsoft"
            / "Windows"
            / "Start Menu"
            / "Programs"
            / "Startup"
        )
        shortcut = startup / "FuelTracker.cmd"
        if shortcut.exists():
            shortcut.unlink()
            QMessageBox.information(
                self.window, "ปิดการทำงานอัตโนมัติ", "ลบทางลัดเริ่มอัตโนมัติแล้ว"
            )
        else:
            startup.mkdir(parents=True, exist_ok=True)
            cmd = (
                f'@echo off\r\n"{sys.executable}" -m fueltracker --start-minimized\r\n'
            )
            shortcut.write_text(cmd, encoding="utf-8")
            QMessageBox.information(self.window, "ตั้งค่าเรียบร้อย", "สร้างทางลัดเริ่มอัตโนมัติแล้ว")

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
            self._selected_vehicle_id = item.data(Qt.ItemDataRole.UserRole)
        else:
            self._selected_vehicle_id = None
        self._update_stats_panel()

    def _update_stats_panel(self) -> None:
        vid = self._selected_vehicle_id
        if vid is None:
            self.stats_dock.kml_label.setText("km/L: -")
            self.stats_dock.cost_label.setText("฿/km: -")
            return
        total_distance, total_liters, total_price = self.storage.get_vehicle_stats(vid)
        kmpl = total_distance / total_liters if total_liters else 0.0
        cost = total_price / total_distance if total_distance else 0.0
        self.stats_dock.kml_label.setText(f"km/L: {kmpl:.2f}")
        self.stats_dock.cost_label.setText(f"฿/km: {cost:.2f}")
        self._update_tray_tooltip()

    def _update_tray_tooltip(self) -> None:
        """Update system tray tooltip with a short summary of the last entry."""
        if not getattr(self, "tray_manager", None):
            return
        vid = self._selected_vehicle_id
        if vid is None:
            self.tray_manager.set_tooltip("")
            return
        last = self.storage.get_last_entry(vid)
        if not last:
            self.tray_manager.set_tooltip("")
            return
        parts = [str(last.entry_date)]
        if last.odo_after is not None:
            dist = last.odo_after - last.odo_before
            parts.append(f"{dist:g} km")
        if last.amount_spent is not None:
            parts.append(f"฿{last.amount_spent:g}")
        self.tray_manager.set_tooltip(" - ".join(parts))

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
            if getattr(self, "tray_manager", None):
                self.tray_manager.show_message("FuelTracker", "เกินงบประมาณ")

    def _refresh_maintenance_panel(self) -> None:
        vid = self._selected_vehicle_id
        if vid is None:
            self.maint_dock.list_widget.clear()
            return
        tasks = self.storage.list_maintenances(vid)
        self.maint_dock.list_widget.clear()
        last = self.storage.get_last_entry(vid)
        current_odo = last.odo_after if last and last.odo_after is not None else None
        for t in tasks:
            text = t.name
            if not t.is_done:
                if t.due_odo is not None:
                    text += f" @ {t.due_odo}km"
                if t.due_date is not None:
                    text += f" by {t.due_date}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, t.id)
            if (
                current_odo is not None
                and t.due_odo is not None
                and current_odo >= t.due_odo
            ) or (t.due_date is not None and t.due_date <= date.today()):
                item.setForeground(Qt.red)
            self.maint_dock.list_widget.addItem(item)

    def _notify_due_maintenance(self, vehicle_id: int, odo: float, when: date) -> None:
        when_dt = datetime.combine(when, datetime.min.time())
        due = self.storage.list_due_maintenances(vehicle_id, odo=odo, date_=when_dt)
        if not due:
            return
        names = ", ".join(d.name for d in due)
        QMessageBox.information(
            self.window,
            "ถึงกำหนดบำรุงรักษา",
            f"งานที่ถึงกำหนด: {names}",
        )
        if os.name == "nt":
            try:
                ToastNotifier().show_toast(
                    "FuelTracker",
                    f"ถึงกำหนดบำรุงรักษา: {names}",
                    threaded=True,
                )
            except Exception:
                pass

    def _on_palette_changed(self, *_: object) -> None:
        """Refresh stylesheet when the application's palette changes."""
        self._setup_style()

    def _setup_style(self) -> None:
        """ปรับสไตล์ชีตของแอปตามธีมที่เลือก"""
        if not self.theme_manager:
            return

        self.theme_manager.apply_theme(
            theme_override=self._theme_override,
            env_theme=self.env.ft_theme,
            config_theme=self.config.theme,
            dark_mode_override=self._dark_mode,
        )


    def _tray_quit(self) -> None:
        self.shutdown()
        app = QApplication.instance()
        if app:
            app.quit()

    def _setup_hotkey(self) -> None:
        if not hasattr(self.window, "hotkeyCheckBox"):
            return
        self.window.hotkeyCheckBox.setChecked(self.config.global_hotkey_enabled)
        if self.config.global_hotkey_enabled:
            self._register_hotkey()

    def _register_hotkey(self) -> None:
        self._unregister_hotkey()
        self.global_hotkey = GlobalHotkey(self.config.hotkey)
        self.global_hotkey.triggered.connect(self._on_hotkey)
        self.global_hotkey.start()

    def _unregister_hotkey(self) -> None:
        if self.global_hotkey:
            self.global_hotkey.stop()
            self.global_hotkey = None

    def _toggle_hotkey(self, checked: bool) -> None:
        self.config.global_hotkey_enabled = checked
        self.config.save(self.config_path)
        if checked:
            self._register_hotkey()
        else:
            self._unregister_hotkey()

    def _on_hotkey(self) -> None:
        if not self.window.isVisible():
            self.window.show()
        self.open_add_entry_dialog()

    def _switch_page(self, index: int) -> None:
        if not hasattr(self.window, "stackedWidget"):
            return
        stack = self.window.stackedWidget
        if index < 0 or index >= stack.count():
            return
        current_idx = stack.currentIndex()
        if current_idx == index:
            return

        current_widget = stack.currentWidget()
        next_widget = stack.widget(index)
        width = stack.frameRect().width()
        direction = 1 if index > current_idx else -1

        # Position the incoming widget just outside of view
        next_widget.move(direction * width, 0)
        next_widget.show()

        anim_old = QPropertyAnimation(current_widget, b"pos", stack)
        anim_old.setDuration(300)
        anim_old.setStartValue(current_widget.pos())
        anim_old.setEndValue(QPoint(-direction * width, 0))

        anim_new = QPropertyAnimation(next_widget, b"pos", stack)
        anim_new.setDuration(300)
        anim_new.setStartValue(next_widget.pos())
        anim_new.setEndValue(QPoint(0, 0))

        group = QParallelAnimationGroup(stack)
        group.addAnimation(anim_old)
        group.addAnimation(anim_new)

        def _finalize() -> None:
            stack.setCurrentIndex(index)
            current_widget.move(0, 0)

        group.finished.connect(_finalize)
        group.start()

    def refresh_vehicle_list(self) -> None:
        if hasattr(self.window, "vehicleListWidget"):
            list_widget = self.window.vehicleListWidget
            list_widget.clear()
            for vehicle in self.storage.list_vehicles():
                item = QListWidgetItem(vehicle.name)
                item.setData(Qt.ItemDataRole.UserRole, vehicle.id)
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
        dialog = AddVehicleDialog(self.window)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)
        dialog.capacityLineEdit.setValidator(QDoubleValidator(0.0, 1e6, 2))
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
        vid = item.data(Qt.ItemDataRole.UserRole)
        vehicle = self.storage.get_vehicle(vid)
        if vehicle is None:
            return
        before = Vehicle.model_validate(vehicle)
        dialog = AddVehicleDialog(self.window)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)
        dialog.setWindowTitle("แก้ไขยานพาหนะ")
        dialog.capacityLineEdit.setValidator(QDoubleValidator(0.0, 1e6, 2))
        dialog.nameLineEdit.setText(vehicle.name)
        dialog.typeLineEdit.setText(vehicle.vehicle_type)
        dialog.plateLineEdit.setText(vehicle.license_plate)
        dialog.capacityLineEdit.setText(str(vehicle.tank_capacity_liters))
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
        vid = item.data(Qt.ItemDataRole.UserRole)
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
        dialog.setParent(self.window)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)
        today = date.today()
        dialog.dateEdit.setDate(QDate(today.year, today.month, today.day))

        dialog.odoBeforeEdit.setValidator(QDoubleValidator(0.0, 1e9, 2))
        dialog.amountEdit.setValidator(QDoubleValidator(0.0, 1e9, 2))

        # Disable fields managed automatically
        dialog.odoAfterEdit.setEnabled(False)
        dialog.litersEdit.setEnabled(False)
        dialog.autoFillCheckBox.setEnabled(False)

        def _prefill() -> None:
            vid = dialog.vehicleComboBox.currentData()
            if vid is None:
                return
            last = self.storage.get_last_entry(vid)
            if last is not None and last.odo_after is not None:
                dialog.odoBeforeEdit.setText(str(last.odo_after))
            else:
                dialog.odoBeforeEdit.clear()
            dialog.amountEdit.clear()

        for v in self.storage.list_vehicles():
            dialog.vehicleComboBox.addItem(v.name, v.id)
        _prefill()
        dialog.vehicleComboBox.currentIndexChanged.connect(_prefill)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            vehicle_id = dialog.vehicleComboBox.currentData()
            try:
                amount_text = dialog.amountEdit.text().strip()
                entry = FuelEntry(
                    entry_date=dialog.dateEdit.date().toPython(),
                    vehicle_id=vehicle_id,
                    odo_before=float(dialog.odoBeforeEdit.text()),
                    odo_after=None,
                    amount_spent=float(amount_text) if amount_text else None,
                    liters=None,
                )
            except ValueError:
                QMessageBox.warning(dialog, "ข้อผิดพลาด", "ข้อมูลตัวเลขไม่ถูกต้อง")
                return
            try:
                cmd = AddEntryCommand(
                    self.storage, entry, cast(Signal, self.entry_changed)
                )
                self.undo_stack.push(cmd)
            except ValueError as exc:
                QMessageBox.warning(dialog, "การตรวจสอบ", str(exc))
                return
            self._check_budget(entry.vehicle_id, entry.entry_date)

    def open_import_csv_dialog(self) -> None:
        if not self.storage.list_vehicles():
            QMessageBox.warning(self.window, "ไม่พบยานพาหนะ", "กรุณาเพิ่มยานพาหนะก่อน")
            return
        dialog = ImportCsvDialog(self.window)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)
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

        if dialog.exec() == QDialog.DialogCode.Accepted and entries:
            vehicle_id = dialog.vehicleComboBox.currentData()
            for e in entries:
                e.vehicle_id = vehicle_id
                self.storage.add_entry(e)
            self.entry_changed.emit()
            self._update_tray_tooltip()

    def open_about_dialog(self) -> None:
        dialog = AboutDialog(self.window)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.exec()

    def open_add_maintenance_dialog(self) -> None:
        if not self.storage.list_vehicles():
            QMessageBox.warning(self.window, "ไม่พบยานพาหนะ", "กรุณาเพิ่มยานพาหนะก่อน")
            return
        dialog = AddMaintenanceDialog(self.window)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)
        today = date.today()
        dialog.dateEdit.setDate(QDate(today.year, today.month, today.day))
        dialog.odoLineEdit.setValidator(QDoubleValidator(0.0, 1e9, 0))
        for v in self.storage.list_vehicles():
            dialog.vehicleComboBox.addItem(v.name, v.id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
                due_date=cast(date, dialog.dateEdit.date().toPython()),
                note=dialog.noteLineEdit.text().strip() or None,
            )
            self.storage.add_maintenance(task)
            self._refresh_maintenance_panel()

    def open_edit_maintenance_dialog(self) -> None:
        item = self.maint_dock.list_widget.currentItem()
        if item is None:
            QMessageBox.warning(self.window, "ไม่พบงาน", "กรุณาเลือกรายการ")
            return
        task_id = item.data(Qt.ItemDataRole.UserRole)
        task = self.storage.get_maintenance(task_id)
        if task is None:
            return
        dialog = AddMaintenanceDialog(self.window)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)
        dialog.setWindowTitle("แก้ไขงานบำรุงรักษา")
        today = date.today()
        if task.due_date:
            dialog.dateEdit.setDate(QDate(task.due_date.year, task.due_date.month, task.due_date.day))
        else:
            dialog.dateEdit.setDate(QDate(today.year, today.month, today.day))
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
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
            task.due_date = cast(date, dialog.dateEdit.date().toPython())
            task.note = dialog.noteLineEdit.text().strip() or None
            self.storage.update_maintenance(task)
            self._refresh_maintenance_panel()

    def mark_selected_maintenance_done(self) -> None:
        item = self.maint_dock.list_widget.currentItem()
        if item is None:
            QMessageBox.warning(self.window, "ไม่พบงาน", "กรุณาเลือกรายการ")
            return
        task_id = item.data(Qt.ItemDataRole.UserRole)
        self.storage.mark_maintenance_done(task_id, True)
        self._refresh_maintenance_panel()

    def export_report(self) -> None:
        today = date.today()
        csv_path_str, _ = QFileDialog.getSaveFileName(
            self.window,
            self.tr("เลือกที่บันทึกไฟล์ CSV"),
            "report.csv",
            "CSV Files (*.csv)",
        )
        if not csv_path_str:
            return

        pdf_path_str, _ = QFileDialog.getSaveFileName(
            self.window,
            self.tr("เลือกที่บันทึกไฟล์ PDF"),
            "report.pdf",
            "PDF Files (*.pdf)",
        )
        if not pdf_path_str:
            return

        out_csv = Path(csv_path_str)
        out_pdf = Path(pdf_path_str)

        def job() -> None:
            self.exporter.monthly_csv(today.month, today.year, out_csv)
            self.exporter.monthly_pdf(today.month, today.year, out_pdf)
            self.export_finished.emit(out_csv, out_pdf)

        self.executor.submit(job)

    # ------------------------------------------------------------------
    # Page switching
    # ------------------------------------------------------------------
    def show_dashboard(self) -> None:
        if hasattr(self.window, "stackedWidget"):
            self.window.stackedWidget.setCurrentWidget(self.window.dashboardPage)

    # ------------------------------------------------------------------
    # ตัวจัดตารางราคาน้ำมัน
    # ------------------------------------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if (
            getattr(self, "window", None) is not None
            and obj is self.window
            and event.type() == QEvent.Type.Show
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

            def run(self) -> None:
                try:
                    with Session(self.controller.storage.engine) as sess:
                        fetch_latest(sess, self.controller.config.default_station)
                        if isValid(self.controller):
                            # ``invokeMethod`` expects the member name as a
                            # Python ``str`` in newer PySide versions. Using a
                            # ``bytes`` object causes a ``ValueError`` which in
                            # turn fails the test suite.  Cast to ``Any`` is
                            # kept for mypy compatibility.
                            cast(Any, QMetaObject).invokeMethod(
                                self.controller,
                                "_load_prices",
                                Qt.ConnectionType.QueuedConnection,
                            )
                except requests.RequestException as exc:  # pragma: no cover - network
                    logger.error("Failed to update oil prices: %s", exc)
                    if os.name == "nt":
                        try:
                            ToastNotifier().show_toast(
                                "FuelTracker",
                                "ไม่สามารถอัปเดตราคาน้ำมันได้",
                                threaded=True,
                            )
                        except Exception:
                            pass

        self.thread_pool.start(Job(self))
        interval_ms = self.config.update_hours * 3_600_000
        QTimer.singleShot(interval_ms, self._schedule_price_update)

    @Slot()
    def _load_prices(self) -> None:
        with Session(self.storage.engine) as session:
            rows = session.exec(
                select(FuelPrice).order_by(cast(Any, FuelPrice.date).desc()).limit(90 * 6)
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
            ax.plot(cast(Any, [d for d, _ in points]), [float(p) for _, p in points])
        cast(Any, self.oil_dock.canvas).draw_idle()

    def filter_entries(self) -> list[FuelEntry]:
        """Filter entries based on search text and start date."""
        text = None
        start = None
        if hasattr(self.window, "searchLineEdit"):
            t = self.window.searchLineEdit.text().strip()
            if t:
                text = t
        if hasattr(self.window, "startDateEdit"):
            start = cast(date, self.window.startDateEdit.date().toPython())
        entries = self.storage.list_entries_filtered(text, start)
        if hasattr(self.window, "vehicleListWidget"):
            lw = self.window.vehicleListWidget
            lw.clear()
            for e in entries:
                dist = e.odo_after - e.odo_before if e.odo_after is not None else 0
                item = QListWidgetItem(f"{e.entry_date} - {dist} km")
                item.setData(Qt.ItemDataRole.UserRole, e.id)
                lw.addItem(item)
        return entries

    # ------------------------------------------------------------------
    # Data modification helpers
    # ------------------------------------------------------------------

    def delete_entry(self, entry_id: int) -> None:
        cmd = DeleteEntryCommand(
            self.storage, entry_id, cast(Signal, self.entry_changed)
        )
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
        try:
            self.settings.setValue("windowGeometry", self.window.saveGeometry())
            self.settings.setValue("windowState", self.window.saveState())
        except RuntimeError:
            # Window already destroyed
            pass
        self._unregister_hotkey()
        self.executor.shutdown(wait=False)

    def __del__(self) -> None:  # pragma: no cover - defensive
        """Ensure resources are released if cleanup was not called."""
        try:
            self.cleanup()
        except Exception:
            pass

    def shutdown(self) -> None:
        backup = self.storage.auto_backup()
        if self.sync_enabled and self.cloud_path is not None:
            self.storage.sync_to_cloud(backup.parent, self.cloud_path)

    def _close_event(self, event: QCloseEvent) -> None:
        if (
            getattr(self, "tray_manager", None)
            and self.tray_manager.is_visible()
            and self.config.hide_on_close
        ):
            event.ignore()
            self.window.hide()
        else:
            event.accept()
