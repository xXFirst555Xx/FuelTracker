from __future__ import annotations

from pathlib import Path
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application environment settings."""

    db_path: Path = Field(default_factory=lambda: Path("fuel.db"))
    ft_theme: str = Field(default="system")
    ft_db_password: str | None = None
    ft_cloud_dir: Path | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""
