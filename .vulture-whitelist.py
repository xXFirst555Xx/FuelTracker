# Vulture whitelist
# This file tells Vulture to ignore false positives.

# --- Attributes/Methods from main_controller.py that are used by Qt ---
main_controller.closeEvent
main_controller._load_prices

# --- Methods from undo_commands.py that are used by QUndoStack ---
undo_commands.AddEntryCommand.undo
undo_commands.AddEntryCommand.redo
undo_commands.DeleteEntryCommand.undo
undo_commands.DeleteEntryCommand.redo
undo_commands.AddVehicleCommand.undo
undo_commands.AddVehicleCommand.redo
undo_commands.DeleteVehicleCommand.undo
undo_commands.DeleteVehicleCommand.redo
undo_commands.UpdateVehicleCommand.undo
undo_commands.UpdateVehicleCommand.redo

# --- Methods that might be used by UI or future features ---
exporter.monthly_excel
importer.import_csv
report_service.generate_report
report_service.export_csv
report_service.export_pdf
report_service.export_excel
storage_service.get_entries_by_vehicle
storage_service.update_entry

# --- Variables used by Pydantic ---
settings.model_config
