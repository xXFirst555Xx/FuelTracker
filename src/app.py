from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

def main() -> None:
    app = QApplication([])
    win = QMainWindow()
    win.setWindowTitle("FuelTracker (stub)")
    win.setCentralWidget(QLabel("Hello FuelTracker!"))
    win.resize(640, 480)
    win.show()
    # CHANGED: exit cleanly with sys.exit
    import sys
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
