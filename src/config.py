import json
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_PATH = Path.home() / ".fueltracker" / "config.json"


@dataclass
class AppConfig:
    """User preferences for FuelTracker."""

    default_station: str = "ptt"
    update_hours: int = 24

    @classmethod
    def load(cls, path: Path | None = None) -> "AppConfig":
        path = path or CONFIG_PATH
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return cls(
                default_station=data.get("default_station", "ptt"),
                update_hours=int(data.get("update_hours", 24)),
            )
        except Exception:
            return cls()

    def save(self, path: Path | None = None) -> None:
        path = path or CONFIG_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, ensure_ascii=False, indent=2)
