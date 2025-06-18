from PySide6.QtWidgets import QDialog
from .ui_add_vehicle_dialog import Ui_AddVehicleDialog

class AddVehicleDialog(QDialog, Ui_AddVehicleDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
