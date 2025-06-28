"""Objects referenced to avoid vulture false positives."""

from src.controllers import main_controller, undo_commands
from src.services import (
    exporter,
    importer,
    report_service,
    storage_service,
)
from src import settings
from src.repositories import fuel_entry_repo
from src.models import fuel_entry as models_fuel_entry
import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - types only
    _tlu: Any
    _tc: Any
else:
    _tlu = object()
    _tc = object()

_m0001 = importlib.import_module("fueltracker.migrations.versions.0001_initial")
_m0002 = importlib.import_module("fueltracker.migrations.versions.0002_add_budgets")
_m0003 = importlib.import_module("fueltracker.migrations.versions.0003_add_maintenances")
_m0004 = importlib.import_module("fueltracker.migrations.versions.0004_add_fuel_prices")
_m0005 = importlib.import_module("fueltracker.migrations.versions.0005_add_fuel_type_to_fuelentry")
_m0006 = importlib.import_module("fueltracker.migrations.versions.0006_add_indexes")
_m0007 = importlib.import_module("fueltracker.migrations.versions.0007_add_fuelprice_index")
_m0008 = importlib.import_module("fueltracker.migrations.versions.0008_add_budget_index")

# Reference attribute to avoid vulture false positive
_dummy_axid = exporter.LineChart().y_axis.axId

_ = (
    # --- Attributes/Methods from main_controller.py that are used by Qt ---
    main_controller.closeEvent,
    main_controller._load_prices,
    main_controller._notify_due_maintenance,
    # --- Methods from undo_commands.py that are used by QUndoStack ---
    undo_commands.AddEntryCommand.undo,
    undo_commands.AddEntryCommand.redo,
    undo_commands.DeleteEntryCommand.undo,
    undo_commands.DeleteEntryCommand.redo,
    undo_commands.AddVehicleCommand.undo,
    undo_commands.AddVehicleCommand.redo,
    undo_commands.DeleteVehicleCommand.undo,
    undo_commands.DeleteVehicleCommand.redo,
    undo_commands.UpdateVehicleCommand.undo,
    undo_commands.UpdateVehicleCommand.redo,
    # --- Methods that might be used by UI or future features ---
    exporter.monthly_excel,
    exporter.monthly_pdf,
    importer.import_csv,
    report_service.generate_report,
    report_service.export_csv,
    report_service.export_pdf,
    report_service.export_excel,
    report_service.weekly_breakdown,
    report_service.vehicle_type_benchmarks,
    storage_service.get_entries_by_vehicle,
    storage_service.list_entries,
    storage_service.update_entry,
    fuel_entry_repo.last_entry,
    models_fuel_entry.FuelEntry.calc_metrics,
    # --- Variables used by Pydantic ---
    settings.model_config,
    # --- Test helpers referenced dynamically ---
    _tlu.DummyUpdater.check_for_update,
    _tlu.DummyUpdater.download_and_extract,
    _tlu.DummyApp.processEvents,
    _tlu.DummySplash.finish,
    _tlu.DummyBar.setRange,
    _tlu.qt_widgets.QProgressBar,
    _tlu.qt_widgets.QSplashScreen,
    _tlu.qt_gui.QPixmap,
    _tc.pytest_sessionstart,
    _tc.pytest_sessionfinish,
    _tc.pytest_configure,
    _tc._cleanup_db,
    # --- Alembic migration metadata ---
    _m0001.down_revision,
    _m0001.branch_labels,
    _m0001.depends_on,
    _m0001.downgrade,
    _m0002.down_revision,
    _m0002.branch_labels,
    _m0002.depends_on,
    _m0002.downgrade,
    _m0003.down_revision,
    _m0003.branch_labels,
    _m0003.depends_on,
    _m0003.downgrade,
    _m0004.down_revision,
    _m0004.branch_labels,
    _m0004.depends_on,
    _m0004.downgrade,
    _m0005.down_revision,
    _m0005.branch_labels,
    _m0005.depends_on,
    _m0005.downgrade,
    _m0006.down_revision,
    _m0006.branch_labels,
    _m0006.depends_on,
    _m0006.downgrade,
    _m0007.down_revision,
    _m0007.branch_labels,
    _m0007.depends_on,
    _m0007.downgrade,
    _m0008.down_revision,
    _m0008.branch_labels,
    _m0008.depends_on,
    _m0008.downgrade,
    _dummy_axid,
)

__all__ = ["_"]
