"""จุดเริ่มต้นของโปรแกรม"""

from __future__ import annotations

import sys
import logging
from rich.logging import RichHandler
import argparse
import os
from pathlib import Path
from typing import TYPE_CHECKING

from alembic.config import Config
from alembic.command import upgrade, stamp
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from src.settings import Settings


ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from src.controllers.main_controller import MainController

_controller: "MainController | None" = None


def _upgrade_to_head(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", "fueltracker:migrations")
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{path}")
    engine = create_engine(f"sqlite:///{path}")
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    expected = {"fuelentry", "vehicle", "budget", "maintenance", "fuelprice"}
    revision = None
    if "alembic_version" in tables:
        with engine.connect() as conn:
            row = conn.execute(text("SELECT version_num FROM alembic_version")).first()
            revision = row[0] if row else None
    if expected.issubset(tables) and (
        revision is None
        or revision != ScriptDirectory.from_config(cfg).get_current_head()
    ):
        stamp(cfg, "head")
    else:
        upgrade(cfg, "head")


def run(argv: list[str] | None = None) -> None:
    """เปิดหน้าต่าง FuelTracker"""
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--start-minimized", action="store_true")
    args, _ = parser.parse_known_args(argv)

    os.environ.setdefault(
        "QT_QPA_FONTDIR", str(Path(__file__).resolve().parents[2] / "fonts")
    )

    env = Settings()

    if args.command == "migrate":
        _upgrade_to_head(env.db_path)
        return
    if args.command == "backup":
        from src.services import StorageService

        path = StorageService().auto_backup()
        print(path)
        return
    if args.command == "sync":
        from src.services import StorageService

        if env.ft_cloud_dir is None:
            raise SystemExit("FT_CLOUD_DIR not set")

        StorageService().sync_to_cloud(
            Path.home() / ".fueltracker" / "backups",
            env.ft_cloud_dir,
        )
        return

    # Always apply any pending migrations before launching the app
    _upgrade_to_head(env.db_path)

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )
    if args.check:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QCoreApplication, Qt, QLocale
        from PySide6.QtGui import QFont, QFontDatabase
    except ImportError:
        print("PySide6 is required")
        raise SystemExit(1) from None

    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication(sys.argv[:1])

    # Use Arabic numerals in calendar widgets
    QLocale.setDefault(
        QLocale(
            QLocale.Language.Thai,
            QLocale.Script.LatinScript,
            QLocale.Country.Thailand,
        )
    )

    # FIX: set Thai-compatible font
    font_dir = os.environ.get("QT_QPA_FONTDIR")
    if font_dir:
        for ttf in Path(font_dir).glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(ttf))
    families = QFontDatabase.families()
    font_family = "Noto Sans Thai" if "Noto Sans Thai" in families else "Tahoma"
    QApplication.setFont(QFont(font_family, 10))

    # --- NEW: use MainController instead of bare MainWindow ---
    from src.controllers.main_controller import MainController

    global _controller
    _controller = MainController()
    # When running in check mode we only want to verify that the UI can
    # be constructed. The oil price fetcher normally starts when the
    # window is first shown which requires migrated tables.  Disable the
    # automatic update timer to avoid touching the database before the
    # tests upgrade it.
    if args.check:
        _controller._price_timer_started = True
    else:
        from . import updater

        if _controller.config.update_hours > 0:
            updater.start_async(_controller.config.update_hours)
    window = _controller.window
    # ----------------------------------------------------------
    if args.check:
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi, True)
        window.show()
        sys.stdout.buffer.write("หน้าต่างหลักทำงานได้".encode("utf-8"))
        sys.stdout.buffer.flush()
        return

    window.show()
    if args.start_minimized or _controller.config.start_minimized:
        window.hide()
    sys.exit(app.exec())
