"""จุดเริ่มต้นการทำงานของแอป FuelTracker"""

from pathlib import Path
import os
import argparse

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication

from .controllers import MainController


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    default_db = Path(os.getenv("DB_PATH", "fuel.db"))

    parser = argparse.ArgumentParser(description="FuelTracker – โปรแกรมติดตามการใช้น้ำมัน")
    parser.add_argument(
        "--db-path", default=default_db, type=Path, help="ไฟล์ฐานข้อมูล SQLite"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dark", action="store_true", help="ใช้ธีมมืด")
    group.add_argument(
        "--theme",
        choices=["light", "dark", "modern"],
        help="เลือกธีม (มีผลเหนือค่า FT_THEME)",
    )
    args = parser.parse_args(argv)

    app = QApplication([])
    theme = args.theme
    controller = MainController(
        db_path=args.db_path,
        dark_mode=args.dark if theme is None else None,
        theme=theme,
    )
    controller.window.show()
    app.exec()


if __name__ == "__main__":
    main()
