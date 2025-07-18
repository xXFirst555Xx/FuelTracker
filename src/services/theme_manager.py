from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Qt


class ThemeManager(QObject):
    """Handle theme and stylesheet application for the Qt app."""

    palette_changed = Signal()

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self._qss_cache: dict[str, str] = {}
        self._applying = False
        if hasattr(app, "paletteChanged"):
            app.paletteChanged.connect(self._on_palette_changed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def apply_theme(
        self,
        theme_override: Optional[str] = None,
        env_theme: Optional[str] = None,
        config_theme: Optional[str] = None,
        dark_mode_override: Optional[bool] = None,
    ) -> None:
        """Apply the appropriate QSS based on the given themes."""

        if not isinstance(self.app, QApplication):
            return

        self._applying = True

        theme = theme_override
        if theme is None:
            for arg in self.app.arguments():
                if arg.startswith("--theme="):
                    theme = arg.split("=", 1)[1]
                    break

        theme = (theme or env_theme or config_theme or "system").lower()

        if dark_mode_override is not None:
            theme = "dark" if dark_mode_override else "light"

        if theme == "system":
            scheme = self.app.styleHints().colorScheme()
            theme = "dark" if scheme == Qt.ColorScheme.Dark else "light"

        qss_file = self._theme_to_file(theme)
        if not qss_file:
            return

        try:
            if theme not in self._qss_cache:
                qss_path = (
                    Path(__file__).resolve().parents[2] / "assets" / "qss" / qss_file
                )
                with qss_path.open("r", encoding="utf-8") as fh:
                    self._qss_cache[theme] = fh.read()
            self.app.setStyleSheet(self._qss_cache[theme])
        except OSError:
            pass
        finally:
            self._applying = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _theme_to_file(theme: str) -> Optional[str]:
        qss_map = {
            "light": "light.qss",
            "dark": "dark.qss",
            "modern": "modern.qss",
            "vivid": "vivid.qss",
        }
        return qss_map.get(theme)

    def _on_palette_changed(self, *_: object) -> None:
        if self._applying:
            return
        self.palette_changed.emit()
