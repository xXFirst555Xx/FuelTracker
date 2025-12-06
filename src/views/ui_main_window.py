# src/views/ui_main_window.py

from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QIcon, QFont, QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QStackedWidget, QSpacerItem, 
                               QSizePolicy, QTableWidget, QHeaderView, QAbstractItemView)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 700)
        
        # --- 1. Main Container ---
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: transparent;") 

        # [FIXED] ใช้ Layout จัดการแทน setGeometry เพื่อให้ยืดหดได้
        self.shadowLayout = QVBoxLayout(self.centralwidget)
        self.shadowLayout.setContentsMargins(10, 10, 10, 10) # เว้นที่ให้เงา 10px
        self.shadowLayout.setSpacing(0)

        # Frame หลัก
        self.windowFrame = QFrame(self.centralwidget)
        self.windowFrame.setObjectName("windowFrame")
        self.windowFrame.setStyleSheet("""
            QFrame#windowFrame {
                background-color: #0f172a; 
                border-radius: 15px;
                border: 1px solid #334155; /* เพิ่มขอบบางๆ ให้ดูคมชัดขึ้น */
            }
        """)
        
        # ใส่ windowFrame ลงใน Layout
        self.shadowLayout.addWidget(self.windowFrame)

        # Layout แบ่งซ้าย-ขวา ภายใน windowFrame
        self.mainLayout = QHBoxLayout(self.windowFrame)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # ============================================================
        # ส่วนที่ 2: Sidebar (เมนูทางซ้าย)
        # ============================================================
        self.sidebarFrame = QFrame(self.windowFrame)
        self.sidebarFrame.setObjectName("sidebarFrame")
        self.sidebarFrame.setFixedWidth(240)
        self.sidebarFrame.setStyleSheet("""
            QFrame#sidebarFrame {
                background-color: #0f172a;
                border-top-left-radius: 15px;
                border-bottom-left-radius: 15px;
                border-right: 1px solid #1e293b;
            }
            QPushButton {
                text-align: left;
                padding-left: 30px;
                background-color: transparent;
                color: #94a3b8;
                border: none;
                height: 50px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: white;
            }
            QPushButton:checked {
                background-color: #1e293b;
                color: #3b82f6; 
                border-right: 3px solid #3b82f6;
                font-weight: bold;
            }
        """)
        
        self.sidebarLayout = QVBoxLayout(self.sidebarFrame)
        self.sidebarLayout.setContentsMargins(0, 30, 0, 20)
        self.sidebarLayout.setSpacing(5)

        # Logo
        self.appLabel = QLabel("FUEL TRACKER", self.sidebarFrame)
        self.appLabel.setAlignment(Qt.AlignCenter)
        self.appLabel.setStyleSheet("color: white; font-size: 20px; font-weight: 800; letter-spacing: 1px;")
        self.sidebarLayout.addWidget(self.appLabel)
        
        self.sidebarLayout.addSpacing(20)

        # Menu Buttons
        self.btnHome = QPushButton(" หน้าแรก (Dashboard)", self.sidebarFrame)
        self.btnHome.setCheckable(True)
        self.btnHome.setChecked(True)
        
        self.btnReports = QPushButton(" รายงาน (Reports)", self.sidebarFrame)
        self.btnReports.setCheckable(True)

        self.btnMaintenance = QPushButton(" ซ่อมบำรุง (Services)", self.sidebarFrame)
        self.btnMaintenance.setCheckable(True)
        
        self.btnSettings = QPushButton(" ตั้งค่า (Settings)", self.sidebarFrame)
        self.btnSettings.setCheckable(True)

        self.sidebarLayout.addWidget(self.btnHome)
        self.sidebarLayout.addWidget(self.btnReports)
        self.sidebarLayout.addWidget(self.btnMaintenance)
        
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sidebarLayout.addItem(spacerItem)
        
        self.sidebarLayout.addWidget(self.btnSettings)
        
        # Version
        self.versionLabel = QLabel("v1.0.0", self.sidebarFrame)
        self.versionLabel.setAlignment(Qt.AlignCenter)
        self.versionLabel.setStyleSheet("color: #475569; font-size: 10px; margin-bottom: 5px;")
        self.sidebarLayout.addWidget(self.versionLabel)

        self.mainLayout.addWidget(self.sidebarFrame)

        # ============================================================
        # ส่วนที่ 3: Content Area (เนื้อหาขวา)
        # ============================================================
        self.contentFrame = QFrame(self.windowFrame)
        self.contentFrame.setStyleSheet("""
            QFrame { 
                background-color: #1e293b; 
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
            }
            QLabel { color: white; }
        """)
        
        self.contentLayout = QVBoxLayout(self.contentFrame)
        self.contentLayout.setContentsMargins(30, 25, 30, 30)
        self.contentLayout.setSpacing(20)

        # --- Header ---
        self.headerLayout = QHBoxLayout()
        self.pageTitle = QLabel("Dashboard", self.contentFrame)
        self.pageTitle.setStyleSheet("font-size: 24px; font-weight: bold; color: white; border: none;")
        
        # Window Controls
        self.windowBtnsLayout = QHBoxLayout()
        self.windowBtnsLayout.setSpacing(8)
        
        self.btnMinimize = QPushButton("─", self.contentFrame)
        self.btnMinimize.setFixedSize(30, 30)
        self.btnMinimize.setCursor(Qt.PointingHandCursor)
        self.btnMinimize.setStyleSheet("""
            QPushButton { background-color: #334155; border-radius: 15px; color: white; border: none; }
            QPushButton:hover { background-color: #475569; }
        """)

        self.btnClose = QPushButton("✕", self.contentFrame)
        self.btnClose.setFixedSize(30, 30)
        self.btnClose.setCursor(Qt.PointingHandCursor)
        self.btnClose.setStyleSheet("""
            QPushButton { background-color: #334155; border-radius: 15px; color: white; border: none; }
            QPushButton:hover { background-color: #ef4444; }
        """)

        self.windowBtnsLayout.addWidget(self.btnMinimize)
        self.windowBtnsLayout.addWidget(self.btnClose)

        self.headerLayout.addWidget(self.pageTitle)
        self.headerLayout.addStretch()
        self.headerLayout.addLayout(self.windowBtnsLayout)
        self.contentLayout.addLayout(self.headerLayout)

        # --- Action Buttons ---
        self.actionLayout = QHBoxLayout()
        self.btnAddFuel = QPushButton("+ เติมน้ำมัน", self.contentFrame)
        self.btnAddFuel.setFixedSize(130, 40)
        self.btnAddFuel.setCursor(Qt.PointingHandCursor)
        self.btnAddFuel.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; font-weight: bold; border-radius: 8px; border: none; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        
        self.btnImport = QPushButton("นำเข้า CSV", self.contentFrame)
        self.btnImport.setFixedSize(110, 40)
        self.btnImport.setCursor(Qt.PointingHandCursor)
        self.btnImport.setStyleSheet("""
            QPushButton { background-color: #334155; color: white; border-radius: 8px; border: none; }
            QPushButton:hover { background-color: #475569; }
        """)

        self.actionLayout.addWidget(self.btnAddFuel)
        self.actionLayout.addWidget(self.btnImport)
        self.actionLayout.addStretch()
        self.contentLayout.addLayout(self.actionLayout)

        # --- Stacked Pages ---
        self.stackedWidget = QStackedWidget(self.contentFrame)
        self.stackedWidget.setStyleSheet("background-color: transparent;")
        
        # Page 1: Home
        self.pageHome = QWidget()
        self.homeLayout = QVBoxLayout(self.pageHome)
        self.homeLayout.setContentsMargins(0, 0, 0, 0)
        
        self.fuelTable = QTableWidget(self.pageHome)
        self.fuelTable.setColumnCount(5)
        self.fuelTable.setHorizontalHeaderLabels(["วันที่", "ยานพาหนะ", "จำนวนลิตร", "ราคา/ลิตร", "ราคารวม"])
        self.fuelTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fuelTable.verticalHeader().setVisible(False)
        self.fuelTable.setAlternatingRowColors(True)
        self.fuelTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fuelTable.setEditTriggers(QAbstractItemView.NoEditTriggers) # ห้ามแก้ข้อมูลในตารางโดยตรง
        self.fuelTable.setStyleSheet("""
            QTableWidget {
                background-color: #0f172a;
                gridline-color: transparent;
                border-radius: 8px;
                color: #e2e8f0;
                border: 1px solid #334155;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #94a3b8;
                padding: 12px;
                border: none;
                font-weight: bold;
                border-bottom: 1px solid #334155;
            }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #1e293b; }
            QTableWidget::item:selected { background-color: #334155; color: white; }
        """)
        self.homeLayout.addWidget(self.fuelTable)
        self.stackedWidget.addWidget(self.pageHome)
        
        # Page 2, 3, 4 (Placeholder)
        self.pageReports = QWidget(); self.stackedWidget.addWidget(self.pageReports)
        self.pageMaintenance = QWidget(); self.stackedWidget.addWidget(self.pageMaintenance)
        self.pageSettings = QWidget(); self.stackedWidget.addWidget(self.pageSettings)

        self.contentLayout.addWidget(self.stackedWidget)
        self.mainLayout.addWidget(self.contentFrame)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Fuel Tracker Modern")
