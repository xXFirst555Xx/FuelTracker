import sys
from PySide6.QtWidgets import (QMainWindow, QGraphicsDropShadowEffect, QSizeGrip, 
                               QButtonGroup, QMessageBox)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QMouseEvent

# Import UI ที่เราสร้างไว้
from src.views.ui_main_window import Ui_MainWindow

# Import Dialog อื่นๆ (ถ้าคุณมีไฟล์พวกนี้อยู่แล้ว ถ้าไม่มีให้คอมเมนต์ไว้ก่อน)
# from src.views.dialogs.add_entry_dialog import AddEntryDialog
# from src.views.dialogs.import_csv_dialog import ImportCSVDialog

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        # 1. โหลดหน้า UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 2. ตั้งค่า Frameless Window (ไร้ขอบ + มีเงา)
        self.setup_frameless_window()
        
        # 3. เชื่อมต่อปุ่มต่างๆ (Signal & Slots)
        self.setup_connections()
        
        # 4. ตั้งค่า Sidebar ให้กดแล้วสลับปุ่มได้
        self.setup_sidebar_navigation()

        # ตัวแปรสำหรับใช้ลากหน้าต่าง
        self._old_pos = None

    def setup_frameless_window(self):
        """ตั้งค่าหน้าต่างไร้ขอบ ใส่เงา และปุ่มขยาย"""
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # สร้างเงา (Drop Shadow)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.ui.centralwidget.setGraphicsEffect(shadow)
        
        # ปุ่มสำหรับดึงขยายหน้าต่าง (มุมล่างขวา)
        self.sizegrip = QSizeGrip(self.ui.centralwidget)
        self.sizegrip.setGeometry(100, 100, 20, 20)

    def setup_connections(self):
        """เชื่อมปุ่มต่างๆ เข้ากับฟังก์ชัน"""
        
        # ปุ่ม Close มุมขวาบน
        self.ui.btnClose.clicked.connect(self.close)

        # ปุ่ม Action หลัก
        self.ui.btnAddFuel.clicked.connect(self.on_click_add_fuel)
        self.ui.btnImport.clicked.connect(self.on_click_import)

    def setup_sidebar_navigation(self):
        """จัดการกลุ่มปุ่ม Sidebar ให้ทำงานเหมือน Tab"""
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True) # ให้เลือกได้ทีละปุ่ม
        
        # เพิ่มปุ่มเข้ากลุ่ม
        self.nav_group.addButton(self.ui.btnHome)
        self.nav_group.addButton(self.ui.btnReports)
        self.nav_group.addButton(self.ui.btnMaintenance)
        self.nav_group.addButton(self.ui.btnSettings)
        
        # เชื่อมสัญญาณเมื่อกดปุ่มในกลุ่ม
        self.nav_group.buttonClicked.connect(self.on_navigation_changed)

    def on_navigation_changed(self, button):
        """ฟังก์ชันเปลี่ยนหน้าเมื่อกด Sidebar"""
        
        # 1. เปลี่ยนชื่อหัวข้อหน้า (Page Title)
        # ตัดคำเอาเฉพาะชื่อไทย เช่น " หน้าแรก (Home)" -> "หน้าแรก"
        title_text = button.text().split('(')[0].strip()
        self.ui.pageTitle.setText(title_text)

        # 2. สลับหน้าใน StackedWidget
        if button == self.ui.btnHome:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageHome)
        elif button == self.ui.btnReports:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageReports)
        # เพิ่มหน้าอื่นๆ ตามที่คุณสร้างใน ui_main_window.py
        # elif button == self.ui.btnMaintenance:
        #     self.ui.stackedWidget.setCurrentWidget(self.ui.pageMaintenance)
        
    def on_click_add_fuel(self):
        """กดปุ่ม + เติมน้ำมัน"""
        print("Clicked Add Fuel")
        # ใส่โค้ดเปิด Dialog ตรงนี้
        # dialog = AddEntryDialog(self)
        # if dialog.exec():
        #     self.refresh_data()

    def on_click_import(self):
        """กดปุ่มนำเข้า"""
        print("Clicked Import")
        # ใส่โค้ดเปิด Import Dialog ตรงนี้

    # --- ฟังก์ชันสำหรับลากหน้าต่าง (Mouse Events) ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
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
        # ย้ายปุ่ม SizeGrip ไปมุมขวาล่างเสมอ
        if hasattr(self, 'sizegrip'):
            rect = self.rect()
            self.sizegrip.move(rect.width() - 25, rect.height() - 25)
