# src/views/ui_main_window.py

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor, QFont, QIcon
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QStackedWidget, QSpacerItem, 
                               QSizePolicy, QTableWidget, QHeaderView, QAbstractItemView)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1150, 750)
        
        # --- 1. Main Container ---
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setStyleSheet("background-color: transparent;") 

        # Layout หลักสำหรับเงา (Margins)
        self.shadowLayout = QVBoxLayout(self.centralwidget)
        self.shadowLayout.setContentsMargins(10, 10, 10, 10)
        self.shadowLayout.setSpacing(0)

        # Frame หน้าต่างหลัก
        self.windowFrame = QFrame(self.centralwidget)
        self.windowFrame.setObjectName("windowFrame")
        self.windowFrame.setStyleSheet("""
            QFrame#windowFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b1220, stop:1 #0d1727);
                border-radius: 14px;
                border: 1px solid #1f2937;
            }
        """)
        self.shadowLayout.addWidget(self.windowFrame)

        # Layout แบ่งซ้าย-ขวา
        self.mainLayout = QHBoxLayout(self.windowFrame)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # ================= Sidebar (ซ้าย) =================
        self.sidebarFrame = QFrame(self.windowFrame)
        self.sidebarFrame.setFixedWidth(240)
        self.sidebarFrame.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0c1424, stop:1 #0d1727);
                border-top-left-radius: 14px;
                border-bottom-left-radius: 14px;
                border-right: 1px solid #1f2a3c;
            }
            QPushButton {
                text-align: left; padding-left: 22px;
                background-color: transparent; color: #9fb1c9;
                border: none; height: 46px; font-size: 14px; font-weight: 600;
                border-radius: 10px; margin: 0 10px;
            }
            QPushButton:hover { background-color: #182339; color: white; }
            QPushButton:checked {
                background-color: #12233a; color: #60a5fa;
                border: 1px solid #2b3c55; font-weight: 700;
            }
        """)
        
        self.sidebarLayout = QVBoxLayout(self.sidebarFrame)
        self.sidebarLayout.setContentsMargins(0, 35, 0, 20)
        self.sidebarLayout.setSpacing(8)

        # Logo
        self.appLabel = QLabel("FUEL TRACKER", self.sidebarFrame)
        self.appLabel.setAlignment(Qt.AlignCenter)
        self.appLabel.setStyleSheet("color: white; font-size: 20px; font-weight: 800; letter-spacing: 1px; border: none;")
        self.sidebarLayout.addWidget(self.appLabel)
        self.sidebarLayout.addSpacing(25)

        # Menu Buttons
        self.btnHome = QPushButton(" หน้าแรก (Dashboard)", self.sidebarFrame)
        self.btnHome.setCheckable(True); self.btnHome.setChecked(True)
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
        
        self.versionLabel = QLabel("v1.0.0 Pro", self.sidebarFrame)
        self.versionLabel.setAlignment(Qt.AlignCenter)
        self.versionLabel.setStyleSheet("color: #475569; font-size: 10px; margin-bottom: 5px; border: none;")
        self.sidebarLayout.addWidget(self.versionLabel)

        self.mainLayout.addWidget(self.sidebarFrame)

        # ================= Content Area (ขวา) =================
        self.contentFrame = QFrame(self.windowFrame)
        self.contentFrame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-top-right-radius: 14px;
                border-bottom-right-radius: 14px;
            }
            QLabel { color: #e2e8f0; border: none; }
        """)
        
        self.contentLayout = QVBoxLayout(self.contentFrame)
        self.contentLayout.setContentsMargins(30, 25, 30, 30)
        self.contentLayout.setSpacing(18)

        # --- Header ---
        self.headerLayout = QHBoxLayout()
        self.pageTitle = QLabel("Dashboard", self.contentFrame)
        self.pageTitle.setStyleSheet("font-size: 26px; font-weight: 900; letter-spacing: 0.5px;")
        
        # Window Controls
        self.windowBtnsLayout = QHBoxLayout()
        self.windowBtnsLayout.setSpacing(8)
        btn_style = "QPushButton { background-color: #334155; border-radius: 6px; color: white; border: none; font-weight: bold; } QPushButton:hover { background-color: #475569; }"
        
        self.btnMinimize = QPushButton("─", self.contentFrame)
        self.btnMinimize.setFixedSize(32, 32); self.btnMinimize.setCursor(QCursor(Qt.PointingHandCursor)); self.btnMinimize.setStyleSheet(btn_style)
        self.btnMaximize = QPushButton("☐", self.contentFrame)
        self.btnMaximize.setFixedSize(32, 32); self.btnMaximize.setCursor(QCursor(Qt.PointingHandCursor)); self.btnMaximize.setStyleSheet(btn_style)
        self.btnClose = QPushButton("✕", self.contentFrame)
        self.btnClose.setFixedSize(32, 32); self.btnClose.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnClose.setStyleSheet("QPushButton { background-color: #334155; border-radius: 6px; color: white; border: none; font-weight: bold; } QPushButton:hover { background-color: #ef4444; }")

        self.windowBtnsLayout.addWidget(self.btnMinimize)
        self.windowBtnsLayout.addWidget(self.btnMaximize)
        self.windowBtnsLayout.addWidget(self.btnClose)

        self.headerLayout.addWidget(self.pageTitle)
        self.headerLayout.addStretch()
        self.headerLayout.addLayout(self.windowBtnsLayout)
        self.contentLayout.addLayout(self.headerLayout)

        # --- Header Meta Bar ---
        self.metaFrame = QFrame(self.contentFrame)
        self.metaFrame.setObjectName("metaFrame")
        self.metaFrame.setStyleSheet("""
            QFrame#metaFrame {
                background-color: #0b1220;
                border: 1px solid #1f2937;
                border-radius: 12px;
            }
            QLabel { color: #cbd5e1; }
        """)
        self.metaLayout = QHBoxLayout(self.metaFrame)
        self.metaLayout.setContentsMargins(16, 12, 16, 12)
        self.metaLayout.setSpacing(10)

        def build_pill(text, accent):
            pill = QLabel(text, self.metaFrame)
            pill.setStyleSheet(
                f"padding: 8px 12px; border-radius: 10px;"
                f" background-color: {accent}20; color: #e2e8f0;"
                f" border: 1px solid {accent}40; font-weight: 700;"
            )
            return pill

        self.metaLayout.addWidget(build_pill("● Live dashboard", "#22c55e"))
        self.metaLayout.addWidget(build_pill("⏳ Upcoming maintenance", "#f97316"))
        self.metaLayout.addWidget(build_pill("⇅ Synced", "#38bdf8"))
        self.metaLayout.addStretch()

        self.contentLayout.addWidget(self.metaFrame)

        # --- Action Buttons ---
        self.actionLayout = QHBoxLayout()
        self.btnAddFuel = QPushButton("+ เติมน้ำมัน", self.contentFrame)
        self.btnAddFuel.setFixedSize(150, 44)
        self.btnAddFuel.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnAddFuel.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #22d3ee);
                color: white; font-weight: 800; border-radius: 12px; border: none; font-size: 14px;
                padding: 0 16px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton:pressed { background-color: #1e40af; }
        """)

        self.btnImport = QPushButton("นำเข้า CSV", self.contentFrame)
        self.btnImport.setFixedSize(126, 44); self.btnImport.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnImport.setStyleSheet("""
            QPushButton {
                background-color: #111827; color: #e2e8f0; border-radius: 12px; border: 1px solid #1f2937; font-size: 14px;
                font-weight: 700; padding: 0 14px;
            }
            QPushButton:hover { background-color: #1f2937; }
        """)

        self.actionLayout.addWidget(self.btnAddFuel)
        self.actionLayout.addWidget(self.btnImport)
        self.actionLayout.addStretch()
        self.contentLayout.addLayout(self.actionLayout)

        # --- Stacked Pages ---
        self.stackedWidget = QStackedWidget(self.contentFrame)
        self.stackedWidget.setStyleSheet("background-color: transparent;")
        
        # [PAGE 1] Home Dashboard
        self.pageHome = QWidget()
        self.homeLayout = QVBoxLayout(self.pageHome)
        self.homeLayout.setContentsMargins(0, 0, 0, 0)
        self.homeLayout.setSpacing(20)

        # --- Summary Cards ---
        self.cardsLayout = QHBoxLayout()
        self.cardsLayout.setSpacing(20)

        # Helper function to create cards and return the Value Label
        def create_card(title, value, icon_color):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #0b1220;
                    border-radius: 14px;
                    border: 1px solid #1f2937;
                }}
                QFrame:hover {{ border: 1px solid {icon_color}; box-shadow: 0px 10px 25px rgba(0,0,0,0.35); }}
            """)
            card.setFixedHeight(120)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(20, 16, 20, 16)
            cl.setSpacing(6)

            lbl_t = QLabel(title)
            lbl_t.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 800; border: none; background: transparent;")

            lbl_v = QLabel(value)
            lbl_v.setStyleSheet("color: white; font-size: 28px; font-weight: 900; border: none; background: transparent;")

            trend = QLabel("▲ 4.2% เทียบสัปดาห์ก่อน", card)
            trend.setStyleSheet(f"color: {icon_color}; font-size: 11px; font-weight: 700;")

            cl.addWidget(lbl_t)
            cl.addWidget(lbl_v)
            cl.addWidget(trend)
            return card, lbl_v

        # สร้างการ์ดและเก็บตัวแปร Label ไว้ใช้งาน
        self.cardTotal, self.lblTotalVal = create_card("TOTAL SPENT (บาท)", "฿ 0.00", "#ef4444")
        self.cardLiters, self.lblLitersVal = create_card("TOTAL FUEL (ลิตร)", "0.00 L", "#3b82f6")
        self.cardAvg, self.lblAvgVal = create_card("AVG PRICE (บาท/ลิตร)", "฿ 0.00", "#10b981")

        self.cardsLayout.addWidget(self.cardTotal)
        self.cardsLayout.addWidget(self.cardLiters)
        self.cardsLayout.addWidget(self.cardAvg)
        self.homeLayout.addLayout(self.cardsLayout)

        self.tableHeaderFrame = QFrame(self.pageHome)
        self.tableHeaderFrame.setStyleSheet("""
            QFrame { background-color: #0b1220; border-radius: 12px; border: 1px solid #1f2937; }
            QLabel { color: #cbd5e1; }
        """)
        self.tableHeaderLayout = QHBoxLayout(self.tableHeaderFrame)
        self.tableHeaderLayout.setContentsMargins(16, 12, 16, 12)
        self.tableHeaderLayout.setSpacing(8)

        self.tableTitle = QLabel("รายการเติมน้ำมันล่าสุด", self.tableHeaderFrame)
        self.tableTitle.setStyleSheet("font-size: 16px; font-weight: 800;")
        self.tableSubtitle = QLabel("สรุปข้อมูลช่วยมองเห็นเทรนด์การใช้เชื้อเพลิง", self.tableHeaderFrame)
        self.tableSubtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")

        self.tableHeaderLayout.addWidget(self.tableTitle)
        self.tableHeaderLayout.addWidget(self.tableSubtitle)
        self.tableHeaderLayout.addStretch()
        self.tableHeaderLayout.addWidget(QLabel("↻ อัปเดตอัตโนมัติ", self.tableHeaderFrame))

        self.homeLayout.addWidget(self.tableHeaderFrame)

        # Fuel Table
        self.fuelTable = QTableWidget(self.pageHome)
        self.fuelTable.setColumnCount(5)
        self.fuelTable.setHorizontalHeaderLabels(["วันที่", "ยานพาหนะ", "จำนวนลิตร", "ราคา/ลิตร", "ราคารวม"])
        self.fuelTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fuelTable.verticalHeader().setVisible(False)
        self.fuelTable.setAlternatingRowColors(True)
        self.fuelTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fuelTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fuelTable.setShowGrid(False) 
        self.fuelTable.setStyleSheet("""
            QTableWidget {
                background-color: #0b1220;
                border-radius: 12px;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                gridline-color: transparent;
                alternate-background-color: #0f1828;
            }
            QHeaderView::section {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f172a, stop:1 #111827);
                color: #94a3b8;
                padding: 14px;
                border: none;
                font-weight: 800;
                text-transform: uppercase;
                font-size: 12px;
                letter-spacing: 0.5px;
            }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #1f2937; }
            QTableWidget::item:selected { background-color: #2563eb; color: white; }
            QScrollBar:vertical { background: #0f172a; width: 10px; margin: 0px; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #334155; border-radius: 5px; min-height: 20px; }
        """)
        self.homeLayout.addWidget(self.fuelTable)
        self.stackedWidget.addWidget(self.pageHome)
        
        # Other Pages
        self.pageReports = QWidget(); self.stackedWidget.addWidget(self.pageReports)
        self.pageMaintenance = QWidget(); self.stackedWidget.addWidget(self.pageMaintenance)
        self.pageSettings = QWidget(); self.stackedWidget.addWidget(self.pageSettings)

        self.contentLayout.addWidget(self.stackedWidget)
        self.mainLayout.addWidget(self.contentFrame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Fuel Tracker Pro")
