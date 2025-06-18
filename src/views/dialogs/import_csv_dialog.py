from typing import Callable, cast

from PySide6.QtWidgets import QDialog, QWidget
from .ui_import_csv_dialog import Ui_ImportCsvDialog

class ImportCsvDialog(QDialog, Ui_ImportCsvDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        cast(Callable[[QDialog], None], self.setupUi)(self)
