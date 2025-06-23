from __future__ import annotations

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from appdirs import user_data_dir


def data_dir() -> Path:
    """Return the per-user data directory for FuelTracker."""
    return Path(user_data_dir("FuelTracker"))


class Settings(BaseSettings):
    """Application environment settings."""

    db_path: Path = Field(default_factory=lambda: data_dir() / "fuel.db")
    ft_theme: str = Field(default="system")
    ft_db_password: str | None = None
    ft_cloud_dir: Path | None = None
    appdata: Path | None = Field(default=None, validation_alias="APPDATA")

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, env_prefix=""
    )
