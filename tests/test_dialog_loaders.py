from PySide6.QtWidgets import QApplication, QDialog
from src.views import (
    load_add_entry_dialog,
    AddMaintenanceDialog,
    ImportCsvDialog,
    asset_path,
    supports_shadow,
)
from src.constants import FUEL_TYPE_TH


def test_load_add_entry_dialog_populates_combo(qapp):
    dialog = load_add_entry_dialog()
    combo = dialog.fuelTypeComboBox
    items = [combo.itemData(i) for i in range(combo.count())]
    assert items == list(FUEL_TYPE_TH.keys())


def test_add_maintenance_dialog_instantiates(qapp):
    dialog = AddMaintenanceDialog()
    assert isinstance(dialog, QDialog)


def test_import_csv_dialog_instantiates(qapp):
    dialog = ImportCsvDialog()
    assert isinstance(dialog, QDialog)


def test_asset_path_returns_existing_icon():
    assert asset_path("icons", "home.svg").is_file()


def test_supports_shadow(monkeypatch, qapp):
    monkeypatch.setattr(QApplication, "platformName", lambda: "offscreen")
    assert not supports_shadow()
    monkeypatch.setattr(QApplication, "platformName", lambda: "windows")
    assert supports_shadow()
