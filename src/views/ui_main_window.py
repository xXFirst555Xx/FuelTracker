# src/views/ui_main_window.py

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QStackedWidget, QSpacerItem, 
                               QSizePolicy, QTableWidget, QHeaderView)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 650) # ปรับขนาดเริ่มต้นให้กว้างขึ้น

        # 1. Main Container (พื้นหลังหลัก)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # ใช้ HBox เพื่อแบ่งซ้าย-ขวา
        self.mainLayout = QHBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # ============================================================
        # ส่วนที่ 1: Sidebar (เมนูทางซ้าย)
        # ============================================================
        self.sidebarFrame = QFrame(self.centralwidget)
        self.sidebarFrame.setObjectName("sidebarFrame")
        self.sidebarFrame.setFixedWidth(220) # ล็อกความกว้างเมนูซ้าย
        self.sidebarFrame.setStyleSheet("""
            QFrame#sidebarFrame {
                background-color: #0f172a; /* สีน้ำเงินเข้ม */
                border-right: 1px solid #334155;
            }
            QPushButton {
                text-align: left;
                padding-left: 20px;
                background-color: transparent;
                color: #94a3b8;
                border: none;
                height: 45px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: white;
            }
            QPushButton:checked {
                background-color: #3b82f6; /* สีฟ้าเมื่อถูกเลือก */
                color: white;
                border-right: 3px solid white;
            }
        """)
        
        self.sidebarLayout = QVBoxLayout(self.sidebarFrame)
        self.sidebarLayout.setContentsMargins(0, 30, 0, 20)
        self.sidebarLayout.setSpacing(5)

        # Logo / App Name
        self.appLabel = QLabel("Fuel Tracker", self.sidebarFrame)
        self.appLabel.setAlignment(Qt.AlignCenter)
        self.appLabel.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        self.sidebarLayout.addWidget(self.appLabel)

        # Menu Buttons
        self.btnHome = QPushButton(" หน้าแรก (Home)", self.sidebarFrame)
        self.btnHome.setCheckable(True)
        self.btnHome.setChecked(True) # เลือกอันนี้เป็นค่าเริ่มต้น
        
        self.btnReports = QPushButton(" รายงาน (Reports)", self.sidebarFrame)
        self.btnReports.setCheckable(True)

        self.btnMaintenance = QPushButton(" ซ่อมบำรุง (Maintenance)", self.sidebarFrame)
        self.btnMaintenance.setCheckable(True)
        
        self.btnSettings = QPushButton(" ตั้งค่า (Settings)", self.sidebarFrame)
        self.btnSettings.setCheckable(True)

        self.sidebarLayout.addWidget(self.btnHome)
        self.sidebarLayout.addWidget(self.btnReports)
        self.sidebarLayout.addWidget(self.btnMaintenance)
        
        # Spacer ดันปุ่มตั้งค่าลงไปล่างสุด
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sidebarLayout.addItem(spacerItem)
        
        self.sidebarLayout.addWidget(self.btnSettings)

        self.mainLayout.addWidget(self.sidebarFrame)

        # ============================================================
        # ส่วนที่ 2: Content Area (เนื้อหาตรงกลาง)
        # ============================================================
        self.contentFrame = QFrame(self.centralwidget)
        self.contentFrame.setObjectName("contentFrame")
        self.contentFrame.setStyleSheet("#contentFrame { background-color: #1e293b; border-radius: 0px 10px 10px 0px; }")
        
        self.contentLayout = QVBoxLayout(self.contentFrame)
        self.contentLayout.setContentsMargins(20, 20, 20, 20)
        self.contentLayout.setSpacing(15)

        # Header Bar (ชื่อหน้า + ปุ่ม Close)
        self.headerLayout = QHBoxLayout()
        self.pageTitle = QLabel("Dashboard", self.contentFrame)
        self.pageTitle.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        # ปุ่ม Close (สำหรับ Frameless Window)
        self.btnClose = QPushButton("✕", self.contentFrame)
        self.btnClose.setFixedSize(30, 30)
        self.btnClose.setStyleSheet("""
            QPushButton { background-color: transparent; color: #94a3b8; font-size: 16px; border-radius: 15px; }
            QPushButton:hover { background-color: #ef4444; color: white; }
        """)

        self.headerLayout.addWidget(self.pageTitle)
        self.headerLayout.addStretch()
        self.headerLayout.addWidget(self.btnClose)
        self.contentLayout.addLayout(self.headerLayout)

        # Action Buttons (ปุ่มลัดต่างๆ)
        self.actionLayout = QHBoxLayout()
        
        self.btnAddFuel = QPushButton("+ เติมน้ำมัน", self.contentFrame)
        self.btnAddFuel.setFixedSize(120, 40)
        self.btnAddFuel.setStyleSheet("""
            background-color: #3b82f6; color: white; font-weight: bold; border-radius: 8px;
        """)
        
        self.btnImport = QPushButton("นำเข้า CSV", self.contentFrame)
        self.btnImport.setFixedSize(100, 40)
        self.btnImport.setStyleSheet("""
            background-color: #334155; color: white; border-radius: 8px;
        """)

        self.actionLayout.addWidget(self.btnAddFuel)
        self.actionLayout.addWidget(self.btnImport)
        self.actionLayout.addStretch() # ดันปุ่มไปทางซ้าย
        self.contentLayout.addLayout(self.actionLayout)

        # Stacked Widget (พื้นที่เปลี่ยนหน้า)
        self.stackedWidget = QStackedWidget(self.contentFrame)
        
        # หน้า 1: ตารางข้อมูล (Home)
        self.pageHome = QWidget()
        self.homeLayout = QVBoxLayout(self.pageHome)
        self.homeLayout.setContentsMargins(0, 0, 0, 0)
        
        self.fuelTable = QTableWidget(self.pageHome)
        self.fuelTable.setStyleSheet("border: none; background-color: #0f172a; color: white;")
        self.homeLayout.addWidget(self.fuelTable)
        
        self.stackedWidget.addWidget(self.pageHome)
        
        # หน้า 2: รายงาน (Reports)
        self.pageReports = QWidget() # เดี๋ยวค่อยใส่กราฟ
        self.stackedWidget.addWidget(self.pageReports)

        self.contentLayout.addWidget(self.stackedWidget)

        self.mainLayout.addWidget(self.contentFrame)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Fuel Tracker Modern")
