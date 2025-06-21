from typing import Callable, cast

from PySide6.QtWidgets import QMainWindow
from .ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        cast(Callable[[QMainWindow], None], self.setupUi)(self)
