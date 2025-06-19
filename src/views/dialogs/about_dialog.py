from typing import Callable, cast

from PySide6.QtWidgets import QDialog, QWidget
from .ui_about_dialog import Ui_AboutDialog

class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        cast(Callable[[QDialog], None], self.setupUi)(self)
        if hasattr(self, "buttonBox"):
            self.buttonBox.accepted.connect(self.accept)
            self.buttonBox.rejected.connect(self.reject)
