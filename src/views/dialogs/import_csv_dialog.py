from PySide6.QtWidgets import QDialog
from .ui_import_csv_dialog import Ui_ImportCsvDialog

class ImportCsvDialog(QDialog, Ui_ImportCsvDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
