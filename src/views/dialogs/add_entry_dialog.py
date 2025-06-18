from PySide6.QtWidgets import QDialog
from .ui_add_entry_dialog import Ui_AddEntryDialog

class AddEntryDialog(QDialog, Ui_AddEntryDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
