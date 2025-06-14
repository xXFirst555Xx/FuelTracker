"""FuelTracker application entry point."""

from pathlib import Path
import os
import argparse

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication

from .controllers import MainController


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    default_db = Path(os.getenv("DB_PATH", "fuel.db"))

    parser = argparse.ArgumentParser(description="FuelTracker")
    parser.add_argument("--db-path", default=default_db, type=Path, help="SQLite database file")
    parser.add_argument("--dark", action="store_true", help="Use dark theme")
    args = parser.parse_args(argv)

    app = QApplication([])
    controller = MainController(db_path=args.db_path, dark_mode=args.dark)
    controller.window.show()
    app.exec()


if __name__ == "__main__":
    main()
