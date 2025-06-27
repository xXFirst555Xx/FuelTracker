"""เลเยอร์บริการของ FuelTracker"""

from .report_service import ReportService
from .storage_service import StorageService
from .exporter import Exporter
from .export_service import ExportService
from .importer import Importer
from .oil_service import (
    fetch_latest,
    get_price,
    purge_old_prices,
    update_missing_liters,
)
try:
    from .theme_manager import ThemeManager
except Exception:  # pragma: no cover - optional dependency
    ThemeManager = None  # type: ignore[misc]

try:
    from .tray_icon_manager import TrayIconManager
except Exception:  # pragma: no cover - optional dependency
    TrayIconManager = None  # type: ignore[misc]

__all__ = [
    "ReportService",
    "StorageService",
    "Exporter",
    "ExportService",
    "Importer",
    "fetch_latest",
    "get_price",
    "purge_old_prices",
    "update_missing_liters",
]

if ThemeManager is not None:
    __all__.append("ThemeManager")
if TrayIconManager is not None:
    __all__.append("TrayIconManager")
