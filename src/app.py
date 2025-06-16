from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

def main() -> None:
    app = QApplication([])
    win = QMainWindow()
    win.setWindowTitle("FuelTracker (stub)")
    win.setCentralWidget(QLabel("Hello FuelTracker!"))
    win.resize(640, 480)
    win.show()
    app.exec()

if __name__ == "__main__":
    main()
