"""Dialog for scheduling vehicle maintenance."""

from typing import Callable, cast

from PySide6.QtWidgets import QDialog, QWidget
from .ui_add_maintenance_dialog import Ui_AddMaintenanceDialog


class AddMaintenanceDialog(QDialog, Ui_AddMaintenanceDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        cast(Callable[[QDialog], None], self.setupUi)(self)
