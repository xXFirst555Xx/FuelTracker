# src/views/main_window.py

import sys
from PySide6.QtWidgets import (QMainWindow, QGraphicsDropShadowEffect, QSizeGrip, 
                               QButtonGroup, QMessageBox)
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
        self._old_pos = None

    def setup_frameless_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # เงา (Shadow)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))
        # ใส่เงาที่ windowFrame แทน centralwidget เพื่อความเนียน
        self.ui.windowFrame.setGraphicsEffect(shadow)
        
        # ปุ่มขยายหน้าต่าง (SizeGrip)
        self.sizegrip = QSizeGrip(self.ui.windowFrame) # ใส่ใน windowFrame
        self.sizegrip.setGeometry(100, 100, 25, 25)
        self.sizegrip.setStyleSheet("background: transparent;") # ซ่อนพื้นหลัง size grip

    def setup_connections(self):
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnMinimize.clicked.connect(self.showMinimized) # [NEW] เพิ่มปุ่มย่อ

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
        print("Opening Add Fuel Dialog...")

    def on_click_import(self):
        print("Opening Import Dialog...")

    # --- Mouse Events for Dragging ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # ยอมให้ลากเฉพาะเมื่อกดที่ Title Bar หรือ Sidebar เท่านั้น (กันไม่ให้ลากเวลากดตาราง)
            # แต่เพื่อความง่าย ให้ลากได้ทั้งหน้าต่างยกเว้นปุ่ม
            self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._old_pos:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.pos() + delta)
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._old_pos = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'sizegrip'):
            rect = self.ui.windowFrame.rect()
            # ย้ายปุ่มขยายไปมุมขวาล่างของ Frame
            self.sizegrip.move(rect.width() - 25, rect.height() - 25)
