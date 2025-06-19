from typing import Callable, cast

from PySide6.QtWidgets import QDialog, QWidget
from .ui_add_vehicle_dialog import Ui_AddVehicleDialog

class AddVehicleDialog(QDialog, Ui_AddVehicleDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        cast(Callable[[QDialog], None], self.setupUi)(self)
        # ensure standard dialog buttons behave as expected
        if hasattr(self, "buttonBox"):
            self.buttonBox.accepted.connect(self.accept)
            self.buttonBox.rejected.connect(self.reject)
