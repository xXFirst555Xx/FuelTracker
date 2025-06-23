from typing import Callable, cast

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow
from .ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        cast(Callable[[QMainWindow], None], self.setupUi)(self)
        self._setup_menus()

    def _setup_menus(self) -> None:
        help_menu = self.menuBar().addMenu("Help")
        self.check_updates_action = QAction("Check for Updates…", self)
        help_menu.addAction(self.check_updates_action)
        self.check_updates_action.triggered.connect(self.on_check_updates)

    @Slot()
    def on_check_updates(self) -> None:
        from ..fueltracker import updater

        updater.prompt_and_update(self)
