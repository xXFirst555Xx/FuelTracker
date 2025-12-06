# src/views/main_window.py

import sys
from PySide6.QtWidgets import (QMainWindow, QGraphicsDropShadowEffect, QSizeGrip, 
                               QButtonGroup, QApplication)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QMouseEvent

from src.views.ui_main_window import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ตั้งค่า Frameless และอื่นๆ
        self.setup_frameless_window()
        self.setup_connections()
        self.setup_sidebar_navigation()
        
        # ตัวแปรสำหรับลากหน้าต่าง
        self._old_pos = None

    def setup_frameless_window(self):
        """ตั้งค่าหน้าต่างไร้ขอบและเงา"""
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # สร้างเงา (Shadow)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 100))
        
        # ใส่เงาที่ windowFrame แทนตัว Main เพื่อไม่ให้เงาขาดเวลาขยาย
        self.ui.windowFrame.setGraphicsEffect(self.shadow)
        
        # SizeGrip (ปุ่มดึงขยายมุมขวาล่าง)
        self.sizegrip = QSizeGrip(self.ui.windowFrame)
        self.sizegrip.setFixedSize(20, 20)
        self.sizegrip.setStyleSheet("background: transparent;")
        self.sizegrip.raise_() # ยกให้ลอยเหนือ widget อื่นเสมอ

    def setup_connections(self):
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnMinimize.clicked.connect(self.showMinimized)
        self.ui.btnMaximize.clicked.connect(self.toggle_maximize)

        # เชื่อมปุ่ม Action
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
        # เปลี่ยน Title ตามชื่อปุ่ม
        title_text = button.text().split('(')[0].strip()
        self.ui.pageTitle.setText(title_text)

        # เปลี่ยนหน้า StackedWidget
        if button == self.ui.btnHome:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageHome)
        elif button == self.ui.btnReports:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageReports)
        elif button == self.ui.btnMaintenance:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageMaintenance)
        elif button == self.ui.btnSettings:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageSettings)
        
    def on_click_add_fuel(self):
        print("Add Fuel Clicked")
        # TODO: เปิด Dialog เพิ่มข้อมูล

    def on_click_import(self):
        print("Import Clicked")
        # TODO: เปิด Dialog นำเข้าข้อมูล

    # --- Logic จัดการ Maximize/Restore ---
    def toggle_maximize(self):
        if self.isMaximized():
            # คืนค่าหน้าต่างปกติ
            self.showNormal()
            self.ui.btnMaximize.setText("☐")
            
            # คืนค่า Margin ให้มีที่ว่างสำหรับเงา
            self.ui.shadowLayout.setContentsMargins(10, 10, 10, 10)
            self.ui.windowFrame.setStyleSheet("""
                QFrame#windowFrame {
                    background-color: #0f172a; 
                    border-radius: 12px;
                    border: 1px solid #334155;
                }
            """)
            # เปิดเงา และ ปุ่มขยาย
            self.ui.windowFrame.setGraphicsEffect(self.shadow)
            self.sizegrip.show()
        else:
            # ขยายเต็มจอ
            self.showMaximized()
            self.ui.btnMaximize.setText("❐")
            
            # ลบ Margin ออกเพื่อให้เต็มจอจริงๆ
            self.ui.shadowLayout.setContentsMargins(0, 0, 0, 0)
            # ลบขอบมนออกให้เป็นสี่เหลี่ยม
            self.ui.windowFrame.setStyleSheet("""
                QFrame#windowFrame {
                    background-color: #0f172a; 
                    border-radius: 0px;
                    border: none;
                }
            """)
            # ปิดเงา (ประหยัด Performance) และซ่อนปุ่มขยาย
            self.ui.windowFrame.setGraphicsEffect(None)
            self.sizegrip.hide()

    # --- Mouse Events (ลากหน้าต่าง) ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # ยอมให้ลากเฉพาะเมื่อกดที่ Header ด้านบน (y < 60px) และไม่ได้ Maximize อยู่
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
        # ดับเบิลคลิกที่ Header เพื่อขยาย/ย่อ
        if event.button() == Qt.LeftButton and event.position().y() < 60:
            self.toggle_maximize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # ย้ายปุ่ม SizeGrip ไปมุมขวาล่างเสมอ
        if hasattr(self, 'sizegrip') and self.sizegrip.isVisible():
            rect = self.ui.windowFrame.rect()
            self.sizegrip.move(rect.width() - 25, rect.height() - 25)
