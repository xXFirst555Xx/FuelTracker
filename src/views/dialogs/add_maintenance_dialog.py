from PySide6.QtWidgets import QDialog
from .ui_add_maintenance_dialog import Ui_AddMaintenanceDialog

class AddMaintenanceDialog(QDialog, Ui_AddMaintenanceDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
