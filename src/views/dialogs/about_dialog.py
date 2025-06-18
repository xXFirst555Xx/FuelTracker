from PySide6.QtWidgets import QDialog
from .ui_about_dialog import Ui_AboutDialog

class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
