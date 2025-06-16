from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from typing import Any
from alembic import context
from sqlmodel import SQLModel
from pathlib import Path
import sys

# Ensure models are imported so SQLModel metadata is populated
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from src import models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception:
        # Fallback if logging configuration is not defined in alembic.ini
        pass

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section: dict[str, Any] = config.get_section(config.config_ini_section) or {}
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
