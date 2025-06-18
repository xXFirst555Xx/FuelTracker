from typing import Callable, cast

from PySide6.QtWidgets import QDialog, QWidget
from .ui_add_entry_dialog import Ui_AddEntryDialog

class AddEntryDialog(QDialog, Ui_AddEntryDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        cast(Callable[[QDialog], None], self.setupUi)(self)
