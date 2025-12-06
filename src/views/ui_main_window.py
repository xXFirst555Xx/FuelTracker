# src/views/ui_main_window.py

from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QColor, QFont, QCursor
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
        # ทำให้ Background โปร่งใส เพื่อให้เห็นเงาและขอบมน
        self.centralwidget.setStyleSheet("background-color: transparent;") 

        # Layout หลักสำหรับจัดการ Margin (เงา)
        self.shadowLayout = QVBoxLayout(self.centralwidget)
        self.shadowLayout.setContentsMargins(10, 10, 10, 10) # เว้นที่ 10px สำหรับเงา
        self.shadowLayout.setSpacing(0)

        # Frame ที่เป็นตัวหน้าต่างจริงๆ (Background สีน้ำเงินเข้ม)
        self.windowFrame = QFrame(self.centralwidget)
        self.windowFrame.setObjectName("windowFrame")
        self.windowFrame.setStyleSheet("""
            QFrame#windowFrame {
                background-color: #0f172a; 
                border-radius: 12px;
                border: 1px solid #334155; /* ขอบบางๆ ให้ดูคม */
            }
        """)
        self.shadowLayout.addWidget(self.windowFrame)

        # Layout ภายในแบ่ง ซ้าย (Sidebar) - ขวา (Content)
        self.mainLayout = QHBoxLayout(self.windowFrame)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # ================= Sidebar (ซ้าย) =================
        self.sidebarFrame = QFrame(self.windowFrame)
        self.sidebarFrame.setObjectName("sidebarFrame")
        self.sidebarFrame.setFixedWidth(240)
        self.sidebarFrame.setStyleSheet("""
            QFrame#sidebarFrame {
                background-color: #0f172a;
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
                border-right: 1px solid #1e293b;
            }
            QPushButton {
                text-align: left;
                padding-left: 25px;
                background-color: transparent;
                color: #94a3b8;
                border: none;
                height: 48px;
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
                font-weight: 600;
            }
        """)
        
        self.sidebarLayout = QVBoxLayout(self.sidebarFrame)
        self.sidebarLayout.setContentsMargins(0, 35, 0, 20)
        self.sidebarLayout.setSpacing(8)

        # Logo Area
        self.appLabel = QLabel("FUEL TRACKER", self.sidebarFrame)
        self.appLabel.setAlignment(Qt.AlignCenter)
        self.appLabel.setStyleSheet("color: white; font-size: 20px; font-weight: 800; letter-spacing: 1px; border: none;")
        self.sidebarLayout.addWidget(self.appLabel)
        
        self.sidebarLayout.addSpacing(25)

        # Menu Items
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
        self.sidebarLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.sidebarLayout.addWidget(self.btnSettings)
        
        # Version Label
        self.versionLabel = QLabel("v1.0.0 Stable", self.sidebarFrame)
        self.versionLabel.setAlignment(Qt.AlignCenter)
        self.versionLabel.setStyleSheet("color: #475569; font-size: 10px; margin-bottom: 5px; border: none;")
        self.sidebarLayout.addWidget(self.versionLabel)

        self.mainLayout.addWidget(self.sidebarFrame)

        # ================= Content Area (ขวา) =================
        self.contentFrame = QFrame(self.windowFrame)
        self.contentFrame.setStyleSheet("""
            QFrame { 
                background-color: #1e293b; 
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            }
            QLabel { color: white; }
        """)
        
        self.contentLayout = QVBoxLayout(self.contentFrame)
        self.contentLayout.setContentsMargins(30, 20, 30, 30)
        self.contentLayout.setSpacing(20)

        # --- Header Bar ---
        self.headerLayout = QHBoxLayout()
        self.pageTitle = QLabel("Dashboard", self.contentFrame)
        self.pageTitle.setStyleSheet("font-size: 24px; font-weight: bold; color: white; border: none;")
        
        # Window Controls (Min, Max, Close)
        self.windowBtnsLayout = QHBoxLayout()
        self.windowBtnsLayout.setSpacing(8)
        
        btn_style = """
            QPushButton { background-color: #334155; border-radius: 6px; color: white; border: none; font-weight: bold; }
            QPushButton:hover { background-color: #475569; }
        """
        close_style = """
            QPushButton { background-color: #334155; border-radius: 6px; color: white; border: none; font-weight: bold; }
            QPushButton:hover { background-color: #ef4444; }
        """
        
        self.btnMinimize = QPushButton("─", self.contentFrame)
        self.btnMinimize.setFixedSize(32, 32)
        self.btnMinimize.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnMinimize.setStyleSheet(btn_style)

        self.btnMaximize = QPushButton("☐", self.contentFrame)
        self.btnMaximize.setFixedSize(32, 32)
        self.btnMaximize.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnMaximize.setStyleSheet(btn_style)

        self.btnClose = QPushButton("✕", self.contentFrame)
        self.btnClose.setFixedSize(32, 32)
        self.btnClose.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnClose.setStyleSheet(close_style)

        self.windowBtnsLayout.addWidget(self.btnMinimize)
        self.windowBtnsLayout.addWidget(self.btnMaximize)
        self.windowBtnsLayout.addWidget(self.btnClose)

        self.headerLayout.addWidget(self.pageTitle)
        self.headerLayout.addStretch()
        self.headerLayout.addLayout(self.windowBtnsLayout)
        self.contentLayout.addLayout(self.headerLayout)

        # --- Action Buttons ---
        self.actionLayout = QHBoxLayout()
        self.btnAddFuel = QPushButton("+ เติมน้ำมัน", self.contentFrame)
        self.btnAddFuel.setFixedSize(140, 42)
        self.btnAddFuel.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnAddFuel.setStyleSheet("""
            QPushButton { 
                background-color: #3b82f6; color: white; font-weight: bold; border-radius: 8px; border: none; 
            }
            QPushButton:hover { background-color: #2563eb; margin-top: -2px; }
            QPushButton:pressed { margin-top: 0px; }
        """)
        
        self.btnImport = QPushButton("นำเข้า CSV", self.contentFrame)
        self.btnImport.setFixedSize(120, 42)
        self.btnImport.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnImport.setStyleSheet("""
            QPushButton { 
                background-color: #334155; color: white; border-radius: 8px; border: none; 
            }
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
        self.fuelTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
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
            QScrollBar:vertical { background: #0f172a; width: 8px; margin: 0px; }
            QScrollBar::handle:vertical { background: #475569; border-radius: 4px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #64748b; }
        """)
        self.homeLayout.addWidget(self.fuelTable)
        self.stackedWidget.addWidget(self.pageHome)
        
        self.pageReports = QWidget(); self.stackedWidget.addWidget(self.pageReports)
        self.pageMaintenance = QWidget(); self.stackedWidget.addWidget(self.pageMaintenance)
        self.pageSettings = QWidget(); self.stackedWidget.addWidget(self.pageSettings)

        self.contentLayout.addWidget(self.stackedWidget)
        self.mainLayout.addWidget(self.contentFrame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Fuel Tracker Modern")
