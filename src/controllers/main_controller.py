"""Main controller connecting the GUI with services and models."""

from datetime import date

from PySide6.QtWidgets import QMainWindow

from ..models import FuelEntry
from ..services import ReportService, StorageService
from ..views import load_ui


class MainController:
    """Glue code between Qt widgets and application services."""

    def __init__(self) -> None:
        self.storage = StorageService()
        self.report_service = ReportService(self.storage)
        # Load UI designed in Qt Designer
        self.window: QMainWindow = load_ui("main_window")  # type: ignore
        self._connect_signals()

    def _connect_signals(self) -> None:
        if hasattr(self.window, "addButton"):
            self.window.addButton.clicked.connect(self.add_dummy_entry)
        if hasattr(self.window, "reportButton"):
            self.window.reportButton.clicked.connect(self.show_report)

    # ---- slots ----
    def add_dummy_entry(self) -> None:
        """Create a dummy entry and store it."""
        entry = FuelEntry(entry_date=date.today(), distance=100.0, liters=10.0, price=20.0)
        self.storage.add_entry(entry)

    def show_report(self) -> None:
        stats = self.report_service.calc_overall_stats()
        print("Report", stats)
