# ADDED: import sys for proper exit handling
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

def main() -> None:
    app = QApplication(sys.argv[:1])
    win = QMainWindow()
    win.setWindowTitle("FuelTracker (stub)")
    win.setCentralWidget(QLabel("Hello FuelTracker!"))
    win.resize(640, 480)
    win.show()
    # CHANGED: exit cleanly with sys.exit
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
