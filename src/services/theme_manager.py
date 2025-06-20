from __future__ import annotations

from pathlib import Path
from typing import Optional, TypedDict

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Qt



class _ThemeArgs(TypedDict, total=False):
    theme_override: Optional[str]
    env_theme: Optional[str]
    config_theme: Optional[str]
    dark_mode_override: Optional[bool]


class ThemeManager(QObject):
    """Handle theme and stylesheet application for the Qt app."""

    palette_changed = Signal()

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self._last_args: _ThemeArgs = {}
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

        self._last_args = {
            "theme_override": theme_override,
            "env_theme": env_theme,
            "config_theme": config_theme,
            "dark_mode_override": dark_mode_override,
        }

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

        self.current_theme = theme

        if theme == "system":
            scheme = self.app.styleHints().colorScheme()
            theme = "dark" if scheme == Qt.ColorScheme.Dark else "light"

        qss_file = self._theme_to_file(theme)
        if not qss_file:
            return

        try:
            qss_path = (
                Path(__file__).resolve().parents[2] / "assets" / "qss" / qss_file
            )
            with qss_path.open("r", encoding="utf-8") as fh:
                self.app.setStyleSheet(fh.read())
        except OSError:
            pass

    def reapply_theme(self) -> None:
        """Reapply the last requested theme."""

        self.apply_theme(
            theme_override=self._last_args.get("theme_override"),
            env_theme=self._last_args.get("env_theme"),
            config_theme=self._last_args.get("config_theme"),
            dark_mode_override=self._last_args.get("dark_mode_override"),
        )

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
        self.palette_changed.emit()
