# src/views/main_window.py

import sys
from PySide6.QtWidgets import (QMainWindow, QGraphicsDropShadowEffect, QSizeGrip, 
                               QButtonGroup, QApplication, QMessageBox, QTableWidgetItem)
from PySide6.QtCore import Qt, QPoint, QEvent
from PySide6.QtGui import QColor, QMouseEvent

from src.views.ui_main_window import Ui_MainWindow

# Import Dialogs (ใช้ try-except กัน error กรณีไฟล์ยังไม่พร้อม)
try:
    from src.views.dialogs.add_entry_dialog import AddEntryDialog
except ImportError:
    AddEntryDialog = None

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_frameless_window()
        self.setup_connections()
        self.setup_sidebar_navigation()
        self._old_pos = None

        # [NEW] โหลดข้อมูลตัวอย่างทันทีที่เปิด
        self.populate_dummy_data()

    def setup_frameless_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 140))
        self.ui.windowFrame.setGraphicsEffect(self.shadow)
        
        self.sizegrip = QSizeGrip(self.ui.windowFrame)
        self.sizegrip.setFixedSize(20, 20)
        self.sizegrip.setStyleSheet("background: transparent;")
        self.sizegrip.raise_()

    def setup_connections(self):
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnMinimize.clicked.connect(self.showMinimized)
        self.ui.btnMaximize.clicked.connect(self.toggle_maximize)

        self.ui.btnAddFuel.clicked.connect(self.on_click_add_fuel)
        self.ui.btnImport.clicked.connect(self.on_click_import)

    def setup_sidebar_navigation(self):
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_group.addButton(self.ui.btnHome)
        self.nav_group.addButton(self.ui.btnReports)
        self.nav_group.addButton(self.ui.btnMaintenance)
        self.nav_group.addButton(self.ui.btnSettings)
        self.nav_group.buttonClicked.connect(self.on_navigation_changed)

    def on_navigation_changed(self, button):
        title_text = button.text().split('(')[0].strip()
        self.ui.pageTitle.setText(title_text)

        if button == self.ui.btnHome:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageHome)
        elif button == self.ui.btnReports:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageReports)
        elif button == self.ui.btnMaintenance:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageMaintenance)
        elif button == self.ui.btnSettings:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageSettings)
        
    def on_click_add_fuel(self):
        """เปิดหน้าต่างบันทึกข้อมูล"""
        if AddEntryDialog:
            dialog = AddEntryDialog(self)
            if dialog.exec():
                print("Saved!")
                # self.refresh_data() # โหลดข้อมูลใหม่ตรงนี้
        else:
            QMessageBox.warning(self, "Warning", "AddEntryDialog not found/imported.")

    def on_click_import(self):
        print("Import Clicked")

    # --- [NEW] Dummy Data Mockup ---
    def populate_dummy_data(self):
        """ใส่ข้อมูลตัวอย่างเพื่อให้ UI ดูสวยงามทันที"""
        # อัปเดต Card
        self.ui.lblTotalVal.setText("฿ 4,500.00")
        self.ui.lblLitersVal.setText("125.50 L")
        self.ui.lblAvgVal.setText("฿ 35.85")

        # อัปเดตตาราง
        data = [
            ("2023-10-01", "Toyota Camry", "40.5 L", "35.50", "1,437.75"),
            ("2023-10-08", "Honda Civic", "35.0 L", "36.00", "1,260.00"),
            ("2023-10-15", "Toyota Camry", "50.0 L", "35.20", "1,760.00"),
        ]
        self.ui.fuelTable.setRowCount(len(data))
        for row, (d, v, l, p, t) in enumerate(data):
            self.ui.fuelTable.setItem(row, 0, QTableWidgetItem(d))
            self.ui.fuelTable.setItem(row, 1, QTableWidgetItem(v))
            self.ui.fuelTable.setItem(row, 2, QTableWidgetItem(l))
            self.ui.fuelTable.setItem(row, 3, QTableWidgetItem(p))
            self.ui.fuelTable.setItem(row, 4, QTableWidgetItem(t))

    # --- Window State Management ---
    def changeEvent(self, event):
        """[PRO TIP] จัดการกรณี Windows Snap (ลากชนขอบบน)"""
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMaximized:
                # ถ้า User ลากชนขอบบน -> ปรับ UI เป็น Maximize
                self.ui.btnMaximize.setText("❐")
                self.ui.shadowLayout.setContentsMargins(0, 0, 0, 0)
                self.ui.windowFrame.setStyleSheet(
                    "QFrame#windowFrame {"
                    " background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b1220, stop:1 #0d1727);"
                    " border-radius: 0px; border: none; }"
                )
                self.ui.windowFrame.setGraphicsEffect(None)
                self.sizegrip.hide()
            else:
                # ถ้า User ดึงกลับมา -> ปรับ UI เป็น Normal
                self.ui.btnMaximize.setText("☐")
                self.ui.shadowLayout.setContentsMargins(10, 10, 10, 10)
                self.ui.windowFrame.setStyleSheet(
                    "QFrame#windowFrame {"
                    " background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b1220, stop:1 #0d1727);"
                    " border-radius: 14px; border: 1px solid #1f2937; }"
                )
                self.ui.windowFrame.setGraphicsEffect(self.shadow)
                self.sizegrip.show()
        super().changeEvent(event)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # --- Mouse Events ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if event.position().y() < 60 and not self.isMaximized():
                self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._old_pos:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.pos() + delta)
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._old_pos = None

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and event.position().y() < 60:
            self.toggle_maximize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'sizegrip') and self.sizegrip.isVisible():
            rect = self.ui.windowFrame.rect()
            self.sizegrip.move(rect.width() - 25, rect.height() - 25)
