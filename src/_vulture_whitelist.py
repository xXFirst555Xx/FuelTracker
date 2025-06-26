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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - types only
    _tlu: Any
    _tc: Any
else:
    _tlu = object()
    _tc = object()

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
    _tc._cleanup_db,
    _dummy_axid,
)

__all__ = ["_"]
