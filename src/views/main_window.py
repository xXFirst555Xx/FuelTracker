# src/views/main_window.py

import sys
from PySide6.QtWidgets import (QMainWindow, QGraphicsDropShadowEffect, QSizeGrip, 
                               QButtonGroup)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QMouseEvent

from src.views.ui_main_window import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_frameless_window()
        self.setup_connections()
        self.setup_sidebar_navigation()
        
        # ตัวแปรสำหรับลากหน้าต่าง
        self._old_pos = None

    def setup_frameless_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Shadow Effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(25)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 100))
        self.ui.windowFrame.setGraphicsEffect(self.shadow)
        
        # SizeGrip (ปุ่มขยายมุมขวาล่าง)
        self.sizegrip = QSizeGrip(self.ui.windowFrame)
        self.sizegrip.setGeometry(100, 100, 25, 25)
        self.sizegrip.setStyleSheet("background: transparent;")
        # [สำคัญ] สั่งให้ SizeGrip ลอยอยู่บนสุด ป้องกันตารางบัง
        self.sizegrip.raise_()

    def setup_connections(self):
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnMinimize.clicked.connect(self.showMinimized)
        
        # [NEW] เชื่อมปุ่ม Maximize/Restore
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
        print("Add Fuel clicked")

    def on_click_import(self):
        print("Import clicked")

    # --- [Logic ใหม่] การจัดการ Maximize / Restore ---
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.ui.btnMaximize.setText("☐") # ไอคอนสี่เหลี่ยม (ขยาย)
            # คืนค่า Margin และ Rounded Corners
            self.ui.shadowLayout.setContentsMargins(10, 10, 10, 10)
            self.ui.windowFrame.setStyleSheet("""
                QFrame#windowFrame {
                    background-color: #0f172a; 
                    border-radius: 15px;
                    border: 1px solid #334155;
                }
            """)
        else:
            self.showMaximized()
            self.ui.btnMaximize.setText("❐") # ไอคอนซ้อนกัน (ย่อกลับ)
            # ลบ Margin ออกเพื่อให้เต็มจอจริงๆ และลบขอบมน
            self.ui.shadowLayout.setContentsMargins(0, 0, 0, 0)
            self.ui.windowFrame.setStyleSheet("""
                QFrame#windowFrame {
                    background-color: #0f172a; 
                    border-radius: 0px;
                    border: none;
                }
            """)

    # --- Mouse Events ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # [Fix UX] อนุญาตให้ลากเฉพาะเมื่อกดที่ส่วนบน (Header) เท่านั้น (ความสูง < 60px)
            # และต้องไม่ใช่สถานะ Maximize
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
        # [New UX] ดับเบิลคลิกที่ Header เพื่อ Maximize
        if event.button() == Qt.LeftButton and event.position().y() < 60:
            self.toggle_maximize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'sizegrip'):
            rect = self.ui.windowFrame.rect()
            # ขยับ SizeGrip และสั่งให้ลอยบนสุดเสมอ
            self.sizegrip.move(rect.width() - 25, rect.height() - 25)
            self.sizegrip.raise_()
