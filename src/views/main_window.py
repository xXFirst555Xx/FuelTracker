# src/views/main_window.py

import sys
from PySide6.QtWidgets import QMainWindow, QGraphicsDropShadowEffect, QSizeGrip
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QMouseEvent

from src.views.ui_main_window import Ui_MainWindow
# ... (imports อื่นๆ ของคุณที่มีอยู่เดิม) ...

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- [ส่วนที่ 1: ตั้งค่า Frameless Window] ---
        # 1. ลบขอบหน้าต่างเดิมออก
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 2. ทำให้พื้นหลังโปร่งใส (เพื่อให้เห็นเงา)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 3. สร้างเงา (Drop Shadow) ให้ดูมีมิติ
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 100)) # สีดำจางๆ
        
        # ใส่เงาเข้าไปที่ centralwidget
        self.ui.centralwidget.setGraphicsEffect(shadow)
        
        # 4. เพิ่มปุ่มสำหรับดึงขยายหน้าต่าง (มุมล่างขวา)
        self.sizegrip = QSizeGrip(self.ui.centralwidget)
        self.sizegrip.setGeometry(100, 100, 20, 20) # เดี๋ยวจะถูกย้ายไปมุมขวาล่างเอง
        # ----------------------------------------

        # ตัวแปรสำหรับใช้ลากหน้าต่าง
        self._old_pos = None

        # ... (โค้ด Logic อื่นๆ ของคุณต่อจากตรงนี้) ...

    # --- [ส่วนที่ 2: ฟังก์ชันให้ลากหน้าต่างได้] ---
    def mousePressEvent(self, event: QMouseEvent):
        """เริ่มจดจำตำแหน่งเมาส์เมื่อกดคลิกซ้ายค้าง"""
        if event.button() == Qt.LeftButton:
            self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        """คำนวณระยะทางและย้ายหน้าต่างตามเมาส์"""
        if self._old_pos:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.pos() + delta)
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ล้างค่าเมื่อปล่อยเมาส์"""
        self._old_pos = None

    def resizeEvent(self, event):
        """ย้ายปุ่มขยายหน้าต่างไปไว้มุมขวาล่างเสมอ"""
        super().resizeEvent(event)
        if hasattr(self, 'sizegrip'):
            rect = self.rect()
            # ขยับ SizeGrip ไปที่มุมขวาล่าง (ลบขอบออกนิดหน่อยเพื่อให้สวย)
            self.sizegrip.move(rect.width() - 25, rect.height() - 25)

    # --- [ส่วนที่ 3: ปุ่มปิดโปรแกรม (สำคัญ!)] ---
    # คุณต้องไปแก้ในไฟล์ UI หรือสร้างปุ่ม Close ในหน้านี้เพิ่ม
    # ไม่อย่างนั้นคุณจะปิดโปรแกรมไม่ได้ (ต้องกด Alt+F4)
