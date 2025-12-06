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
        
        # --- 1. Main Container (พื้นหลังหลัก) ---
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: transparent;") # โปร่งใสเพื่อให้เห็นเงา (ถ้าใช้ Frameless)

        # Frame หลักสำหรับใส่เนื้อหา (แยกเลเยอร์เพื่อให้ทำขอบมนได้)
        self.windowFrame = QFrame(self.centralwidget)
        self.windowFrame.setObjectName("windowFrame")
        self.windowFrame.setGeometry(QRect(10, 10, 1080, 680)) # เผื่อพื้นที่ให้เงา 10px
        self.windowFrame.setStyleSheet("""
            QFrame#windowFrame {
                background-color: #0f172a; /* พื้นหลังสีน้ำเงินเข้ม */
                border-radius: 15px;
            }
        """)
        
        # Layout หลักแบ่งซ้าย-ขวา
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
                color: #3b82f6; /* สีฟ้า */
                border-right: 3px solid #3b82f6;
                font-weight: bold;
            }
        """)
        
        self.sidebarLayout = QVBoxLayout(self.sidebarFrame)
        self.sidebarLayout.setContentsMargins(0, 40, 0, 20)
        self.sidebarLayout.setSpacing(10)

        # Logo Text
        self.appLabel = QLabel("FUEL TRACKER", self.sidebarFrame)
        self.appLabel.setAlignment(Qt.AlignCenter)
        self.appLabel.setStyleSheet("color: white; font-size: 22px; font-weight: 800; letter-spacing: 2px;")
        self.sidebarLayout.addWidget(self.appLabel)
        
        self.sidebarLayout.addSpacing(30) # เว้นระยะห่าง

        # --- Menu Buttons ---
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
        
        # Spacer ดันปุ่มตั้งค่าลงล่าง
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sidebarLayout.addItem(spacerItem)
        
        self.sidebarLayout.addWidget(self.btnSettings)
        
        self.versionLabel = QLabel("v1.0.0", self.sidebarFrame)
        self.versionLabel.setAlignment(Qt.AlignCenter)
        self.versionLabel.setStyleSheet("color: #475569; font-size: 10px; margin-bottom: 10px;")
        self.sidebarLayout.addWidget(self.versionLabel)

        self.mainLayout.addWidget(self.sidebarFrame)

        # ============================================================
        # ส่วนที่ 3: Content Area (เนื้อหาตรงกลาง)
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
        self.contentLayout.setContentsMargins(30, 30, 30, 30)
        self.contentLayout.setSpacing(20)

        # --- Header ---
        self.headerLayout = QHBoxLayout()
        self.pageTitle = QLabel("Dashboard", self.contentFrame)
        self.pageTitle.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        
        # ปุ่ม Close/Minimize (มุมขวาบน)
        self.windowBtnsLayout = QHBoxLayout()
        self.windowBtnsLayout.setSpacing(10)
        
        self.btnMinimize = QPushButton("─", self.contentFrame)
        self.btnMinimize.setFixedSize(30, 30)
        self.btnMinimize.setStyleSheet("background-color: #334155; border-radius: 15px; color: white;")

        self.btnClose = QPushButton("✕", self.contentFrame)
        self.btnClose.setFixedSize(30, 30)
        self.btnClose.setStyleSheet("""
            QPushButton { background-color: #334155; border-radius: 15px; color: white; }
            QPushButton:hover { background-color: #ef4444; }
        """)

        self.windowBtnsLayout.addWidget(self.btnMinimize)
        self.windowBtnsLayout.addWidget(self.btnClose)

        self.headerLayout.addWidget(self.pageTitle)
        self.headerLayout.addStretch()
        self.headerLayout.addLayout(self.windowBtnsLayout)
        self.contentLayout.addLayout(self.headerLayout)

        # --- Action Buttons Bar ---
        self.actionLayout = QHBoxLayout()
        self.btnAddFuel = QPushButton("+ เติมน้ำมัน", self.contentFrame)
        self.btnAddFuel.setFixedSize(140, 45)
        self.btnAddFuel.setCursor(Qt.PointingHandCursor)
        self.btnAddFuel.setStyleSheet("""
            background-color: #3b82f6; color: white; font-weight: bold; font-size: 14px; border-radius: 8px;
        """)
        
        self.btnImport = QPushButton("นำเข้า CSV", self.contentFrame)
        self.btnImport.setFixedSize(120, 45)
        self.btnImport.setCursor(Qt.PointingHandCursor)
        self.btnImport.setStyleSheet("""
            QPushButton { background-color: #334155; color: white; font-size: 14px; border-radius: 8px; }
            QPushButton:hover { background-color: #475569; }
        """)

        self.actionLayout.addWidget(self.btnAddFuel)
        self.actionLayout.addWidget(self.btnImport)
        self.actionLayout.addStretch()
        self.contentLayout.addLayout(self.actionLayout)

        # --- Stacked Widget (พื้นที่เปลี่ยนหน้า) ---
        self.stackedWidget = QStackedWidget(self.contentFrame)
        
        # ---------------- Page 1: Home (ตาราง) ----------------
        self.pageHome = QWidget()
        self.homeLayout = QVBoxLayout(self.pageHome)
        self.homeLayout.setContentsMargins(0, 0, 0, 0)
        
        # ตารางข้อมูล
        self.fuelTable = QTableWidget(self.pageHome)
        self.fuelTable.setColumnCount(5)
        self.fuelTable.setHorizontalHeaderLabels(["วันที่", "ยานพาหนะ", "จำนวนลิตร", "ราคา/ลิตร", "ราคารวม"])
        self.fuelTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fuelTable.verticalHeader().setVisible(False)
        self.fuelTable.setAlternatingRowColors(True)
        self.fuelTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fuelTable.setStyleSheet("""
            QTableWidget {
                background-color: #0f172a;
                gridline-color: transparent;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #334155;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #94a3b8;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item { padding: 8px; }
        """)
        self.homeLayout.addWidget(self.fuelTable)
        self.stackedWidget.addWidget(self.pageHome)
        
        # ---------------- Page 2: Reports ----------------
        self.pageReports = QWidget()
        self.reportsLayout = QVBoxLayout(self.pageReports)
        
        self.lblReports = QLabel("หน้ารายงานสรุป (Reports)", self.pageReports)
        self.lblReports.setAlignment(Qt.AlignCenter)
        self.lblReports.setStyleSheet("font-size: 20px; color: #64748b;")
        self.reportsLayout.addWidget(self.lblReports)
        # TODO: ใส่กราฟตรงนี้
        
        self.stackedWidget.addWidget(self.pageReports)

        # ---------------- Page 3: Maintenance ----------------
        self.pageMaintenance = QWidget()
        self.maintLayout = QVBoxLayout(self.pageMaintenance)
        
        self.lblMaint = QLabel("รายการซ่อมบำรุง (Maintenance)", self.pageMaintenance)
        self.lblMaint.setAlignment(Qt.AlignCenter)
        self.lblMaint.setStyleSheet("font-size: 20px; color: #64748b;")
        self.maintLayout.addWidget(self.lblMaint)
        # TODO: ใส่ตารางซ่อมบำรุง
        
        self.stackedWidget.addWidget(self.pageMaintenance)
        
        # ---------------- Page 4: Settings ----------------
        self.pageSettings = QWidget()
        self.settingsLayout = QVBoxLayout(self.pageSettings)
        
        self.lblSettings = QLabel("ตั้งค่าระบบ (System Settings)", self.pageSettings)
        self.lblSettings.setAlignment(Qt.AlignCenter)
        self.lblSettings.setStyleSheet("font-size: 20px; color: #64748b;")
        self.settingsLayout.addWidget(self.lblSettings)
        # TODO: ใส่ฟอร์มตั้งค่า
        
        self.stackedWidget.addWidget(self.pageSettings)

        self.contentLayout.addWidget(self.stackedWidget)
        self.mainLayout.addWidget(self.contentFrame)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Fuel Tracker Modern")
