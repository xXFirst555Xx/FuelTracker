"""FuelTracker application entry point."""

from PySide6.QtWidgets import QApplication

from .controllers import MainController


def main() -> None:
    app = QApplication([])
    controller = MainController()
    controller.window.show()
    app.exec()


if __name__ == "__main__":
    main()
