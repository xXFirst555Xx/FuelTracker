from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


class ThemeManager:
    """Handle theme and stylesheet application for the Qt app."""

    def __init__(self, app: QApplication) -> None:
        self.app = app

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

        qss_map = {
            "light": "light.qss",
            "dark": "dark.qss",
            "modern": "modern.qss",
            "vivid": "vivid.qss",
        }
        qss_file = qss_map.get(theme)
        if not qss_file:
            return

        try:
            qss_path = Path(__file__).resolve().parents[2] / "assets" / "qss" / qss_file
            with open(qss_path, "r", encoding="utf-8") as fh:
                self.app.setStyleSheet(fh.read())
        except OSError:
            pass
