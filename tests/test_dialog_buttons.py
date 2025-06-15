from PySide6.QtWidgets import QDialogButtonBox, QDialog
from src.views import load_add_vehicle_dialog


def test_add_vehicle_dialog_buttons(qapp):
    dialog = load_add_vehicle_dialog()
    box = dialog.findChild(QDialogButtonBox, "buttonBox")
    assert box is not None
    box.accepted.emit()
    assert dialog.result() == QDialog.Accepted
