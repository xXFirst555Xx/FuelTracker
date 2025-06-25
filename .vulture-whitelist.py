"""Objects referenced to avoid vulture false positives."""

from src.controllers import main_controller, undo_commands
from src.services import (
    exporter,
    importer,
    report_service,
    storage_service,
)
from src import settings
import tests.test_launcher_update
import tests.conftest

# Reference attribute to avoid vulture false positive
_dummy_axid = exporter.LineChart().y_axis.axId

_ = (
    # --- Attributes/Methods from main_controller.py that are used by Qt ---
    main_controller.closeEvent,
    main_controller._load_prices,
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
    importer.import_csv,
    report_service.generate_report,
    report_service.export_csv,
    report_service.export_pdf,
    report_service.export_excel,
    report_service.weekly_breakdown,
    report_service.vehicle_type_benchmarks,
    storage_service.get_entries_by_vehicle,
    storage_service.update_entry,
    # --- Variables used by Pydantic ---
    settings.model_config,
    # --- Test helpers referenced dynamically ---
    tests.test_launcher_update.DummyUpdater.check_for_update,
    tests.test_launcher_update.DummyUpdater.download_and_extract,
    tests.test_launcher_update.DummyApp.processEvents,
    tests.test_launcher_update.DummySplash.finish,
    tests.test_launcher_update.DummyBar.setRange,
    tests.test_launcher_update.qt_widgets.QProgressBar,
    tests.test_launcher_update.qt_widgets.QSplashScreen,
    tests.test_launcher_update.qt_gui.QPixmap,
    tests.conftest.pytest_sessionstart,
    tests.conftest._cleanup_db,
    _dummy_axid,
)

__all__ = ["_"]
