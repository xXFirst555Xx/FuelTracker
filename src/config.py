import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from appdirs import user_config_dir

from .settings import Settings

CONFIG_PATH = Path(user_config_dir("FuelTracker")) / "config.json"


@dataclass
class AppConfig:
    """User preferences for FuelTracker."""

    default_station: str = "ptt"
    update_hours: int = 24  # controls oil price updates and auto checks; 0 disables
    theme: str = "system"
    hide_on_close: bool = os.name == "nt"
    global_hotkey_enabled: bool = True
    hotkey: str = "Ctrl+Shift+N"
    start_minimized: bool = False

    @classmethod
    def load(cls, path: Path | None = None) -> "AppConfig":
        path = path or CONFIG_PATH

        # During test runs avoid picking up a real user configuration file
        # which could interfere with expected defaults.
        if os.getenv("PYTEST_CURRENT_TEST"):
            if path != CONFIG_PATH:
                # Custom path still honoured to allow tests to override settings
                pass
            else:
                return cls(theme=Settings().ft_theme)

        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return cls(
                default_station=data.get("default_station", "ptt"),
                update_hours=int(data.get("update_hours", 24)),
                theme=data.get("theme", Settings().ft_theme),
                hide_on_close=bool(data.get("hide_on_close", os.name == "nt")),
                global_hotkey_enabled=bool(data.get("global_hotkey_enabled", True)),
                hotkey=data.get("hotkey", "Ctrl+Shift+N"),
                start_minimized=bool(data.get("start_minimized", False)),
            )
        except (OSError, json.JSONDecodeError):
            return cls(theme=Settings().ft_theme)

    def save(self, path: Path | None = None) -> None:
        path = path or CONFIG_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, ensure_ascii=False, indent=2)
