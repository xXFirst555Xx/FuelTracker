"""FuelTracker application entry point."""

from pathlib import Path
import os

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication

from .controllers import MainController


def main() -> None:
    load_dotenv()
    db_path = Path(os.getenv("DB_PATH", "fuel.db"))
    app = QApplication([])
    controller = MainController(db_path=db_path)
    controller.window.show()
    app.exec()


if __name__ == "__main__":
    main()
