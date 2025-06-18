# -*- coding: utf-8 -*-
# mypy: ignore-errors

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtGui import (QFont, QIcon)
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDateEdit,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSpinBox, QSplitter, QStackedWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.mainSplitter = QSplitter(self.centralwidget)
        self.mainSplitter.setObjectName(u"mainSplitter")
        self.mainSplitter.setOrientation(Qt.Horizontal)
        self.sidebarList = QListWidget(self.mainSplitter)
        icon = QIcon()
        icon.addFile(u"icons:home.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qlistwidgetitem = QListWidgetItem(self.sidebarList)
        __qlistwidgetitem.setIcon(icon)
        icon1 = QIcon()
        icon1.addFile(u"icons:plus-square.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qlistwidgetitem1 = QListWidgetItem(self.sidebarList)
        __qlistwidgetitem1.setIcon(icon1)
        icon2 = QIcon()
        icon2.addFile(u"icons:bar-chart-2.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qlistwidgetitem2 = QListWidgetItem(self.sidebarList)
        __qlistwidgetitem2.setIcon(icon2)
        icon3 = QIcon()
        icon3.addFile(u"icons:settings.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qlistwidgetitem3 = QListWidgetItem(self.sidebarList)
        __qlistwidgetitem3.setIcon(icon3)
        self.sidebarList.setObjectName(u"sidebarList")
        self.sidebarList.setMinimumWidth(200)
        self.sidebarList.setMaximumWidth(240)
        self.sidebarList.setTextElideMode(Qt.ElideRight)
        font = QFont()
        font.setFamilies([u"Tahoma, Arial, sans-serif"])
        font.setPointSize(11)
        self.sidebarList.setFont(font)
        self.sidebarList.setIconSize(QSize(32, 32))
        self.sidebarList.setSpacing(8)
        self.mainSplitter.addWidget(self.sidebarList)
        self.stackedWidget = QStackedWidget(self.mainSplitter)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.dashboardPage = QWidget()
        self.dashboardPage.setObjectName(u"dashboardPage")
        self.dashboardLayout = QVBoxLayout(self.dashboardPage)
        self.dashboardLayout.setObjectName(u"dashboardLayout")
        self.addVehicleButton = QPushButton(self.dashboardPage)
        self.addVehicleButton.setObjectName(u"addVehicleButton")
        icon4 = QIcon()
        icon4.addFile(u"icons:plus-circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.addVehicleButton.setIcon(icon4)

        self.dashboardLayout.addWidget(self.addVehicleButton)

        self.editVehicleButton = QPushButton(self.dashboardPage)
        self.editVehicleButton.setObjectName(u"editVehicleButton")
        icon5 = QIcon()
        icon5.addFile(u"icons:edit-2.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.editVehicleButton.setIcon(icon5)

        self.dashboardLayout.addWidget(self.editVehicleButton)

        self.deleteVehicleButton = QPushButton(self.dashboardPage)
        self.deleteVehicleButton.setObjectName(u"deleteVehicleButton")
        icon6 = QIcon()
        icon6.addFile(u"icons:trash-2.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.deleteVehicleButton.setIcon(icon6)

        self.dashboardLayout.addWidget(self.deleteVehicleButton)

        self.searchLineEdit = QLineEdit(self.dashboardPage)
        self.searchLineEdit.setObjectName(u"searchLineEdit")

        self.dashboardLayout.addWidget(self.searchLineEdit)

        self.startDateEdit = QDateEdit(self.dashboardPage)
        self.startDateEdit.setObjectName(u"startDateEdit")
        self.startDateEdit.setCalendarPopup(True)

        self.dashboardLayout.addWidget(self.startDateEdit)

        self.vehicleListWidget = QListWidget(self.dashboardPage)
        self.vehicleListWidget.setObjectName(u"vehicleListWidget")

        self.dashboardLayout.addWidget(self.vehicleListWidget)

        self.stackedWidget.addWidget(self.dashboardPage)
        self.addEntryPage = QWidget()
        self.addEntryPage.setObjectName(u"addEntryPage")
        self.entryLayout = QVBoxLayout(self.addEntryPage)
        self.entryLayout.setObjectName(u"entryLayout")
        self.addEntryButton = QPushButton(self.addEntryPage)
        self.addEntryButton.setObjectName(u"addEntryButton")
        self.addEntryButton.setIcon(icon4)

        self.entryLayout.addWidget(self.addEntryButton)

        self.importCSVButton = QPushButton(self.addEntryPage)
        self.importCSVButton.setObjectName(u"importCSVButton")
        self.importCSVButton.setIcon(icon1)

        self.entryLayout.addWidget(self.importCSVButton)

        self.stackedWidget.addWidget(self.addEntryPage)
        self.reportsPage = QWidget()
        self.reportsPage.setObjectName(u"reportsPage")
        self.reportsLayout = QVBoxLayout(self.reportsPage)
        self.reportsLayout.setObjectName(u"reportsLayout")
        self.reportsContainer = QWidget(self.reportsPage)
        self.reportsContainer.setObjectName(u"reportsContainer")

        self.reportsLayout.addWidget(self.reportsContainer)

        self.backButton = QPushButton(self.reportsPage)
        self.backButton.setObjectName(u"backButton")
        icon7 = QIcon()
        icon7.addFile(u"icons:arrow-left.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.backButton.setIcon(icon7)

        self.reportsLayout.addWidget(self.backButton)

        self.stackedWidget.addWidget(self.reportsPage)
        self.settingsPage = QWidget()
        self.settingsPage.setObjectName(u"settingsPage")
        self.settingsLayout = QVBoxLayout(self.settingsPage)
        self.settingsLayout.setObjectName(u"settingsLayout")
        self.settingsLabel = QLabel(self.settingsPage)
        self.settingsLabel.setObjectName(u"settingsLabel")

        self.settingsLayout.addWidget(self.settingsLabel)

        self.aboutButton = QPushButton(self.settingsPage)
        self.aboutButton.setObjectName(u"aboutButton")
        icon8 = QIcon()
        icon8.addFile(u"icons:info.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.aboutButton.setIcon(icon8)

        self.settingsLayout.addWidget(self.aboutButton)

        self.stationLayout = QHBoxLayout()
        self.stationLayout.setObjectName(u"stationLayout")
        self.stationLabel = QLabel(self.settingsPage)
        self.stationLabel.setObjectName(u"stationLabel")

        self.stationLayout.addWidget(self.stationLabel)

        self.stationComboBox = QComboBox(self.settingsPage)
        self.stationComboBox.setObjectName(u"stationComboBox")

        self.stationLayout.addWidget(self.stationComboBox)


        self.settingsLayout.addLayout(self.stationLayout)

        self.priceUpdateLayout = QHBoxLayout()
        self.priceUpdateLayout.setObjectName(u"priceUpdateLayout")
        self.updateLabel = QLabel(self.settingsPage)
        self.updateLabel.setObjectName(u"updateLabel")

        self.priceUpdateLayout.addWidget(self.updateLabel)

        self.updateIntervalSpinBox = QSpinBox(self.settingsPage)
        self.updateIntervalSpinBox.setObjectName(u"updateIntervalSpinBox")
        self.updateIntervalSpinBox.setMinimum(1)
        self.updateIntervalSpinBox.setMaximum(168)
        self.updateIntervalSpinBox.setValue(24)

        self.priceUpdateLayout.addWidget(self.updateIntervalSpinBox)


        self.settingsLayout.addLayout(self.priceUpdateLayout)

        self.themeLayout = QHBoxLayout()
        self.themeLayout.setObjectName(u"themeLayout")
        self.themeLabel = QLabel(self.settingsPage)
        self.themeLabel.setObjectName(u"themeLabel")

        self.themeLayout.addWidget(self.themeLabel)

        self.themeComboBox = QComboBox(self.settingsPage)
        self.themeComboBox.addItem("")
        self.themeComboBox.addItem("")
        self.themeComboBox.addItem("")
        self.themeComboBox.addItem("")
        self.themeComboBox.addItem("")
        self.themeComboBox.setObjectName(u"themeComboBox")

        self.themeLayout.addWidget(self.themeComboBox)


        self.settingsLayout.addLayout(self.themeLayout)

        self.syncCheckBox = QCheckBox(self.settingsPage)
        self.syncCheckBox.setObjectName(u"syncCheckBox")

        self.settingsLayout.addWidget(self.syncCheckBox)

        self.hotkeyCheckBox = QCheckBox(self.settingsPage)
        self.hotkeyCheckBox.setObjectName(u"hotkeyCheckBox")

        self.settingsLayout.addWidget(self.hotkeyCheckBox)

        self.startupShortcutButton = QPushButton(self.settingsPage)
        self.startupShortcutButton.setObjectName(u"startupShortcutButton")

        self.settingsLayout.addWidget(self.startupShortcutButton)

        self.cloudPathLayout = QHBoxLayout()
        self.cloudPathLayout.setObjectName(u"cloudPathLayout")
        self.cloudPathEdit = QLineEdit(self.settingsPage)
        self.cloudPathEdit.setObjectName(u"cloudPathEdit")

        self.cloudPathLayout.addWidget(self.cloudPathEdit)

        self.browseCloudButton = QPushButton(self.settingsPage)
        self.browseCloudButton.setObjectName(u"browseCloudButton")

        self.cloudPathLayout.addWidget(self.browseCloudButton)


        self.settingsLayout.addLayout(self.cloudPathLayout)

        self.budgetLayout = QHBoxLayout()
        self.budgetLayout.setObjectName(u"budgetLayout")
        self.budgetVehicleComboBox = QComboBox(self.settingsPage)
        self.budgetVehicleComboBox.setObjectName(u"budgetVehicleComboBox")

        self.budgetLayout.addWidget(self.budgetVehicleComboBox)

        self.budgetEdit = QLineEdit(self.settingsPage)
        self.budgetEdit.setObjectName(u"budgetEdit")

        self.budgetLayout.addWidget(self.budgetEdit)

        self.saveBudgetButton = QPushButton(self.settingsPage)
        self.saveBudgetButton.setObjectName(u"saveBudgetButton")

        self.budgetLayout.addWidget(self.saveBudgetButton)


        self.settingsLayout.addLayout(self.budgetLayout)

        self.stackedWidget.addWidget(self.settingsPage)
        self.mainSplitter.addWidget(self.stackedWidget)

        self.horizontalLayout.addWidget(self.mainSplitter)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"FuelTracker \u2013 \u0e15\u0e31\u0e27\u0e15\u0e34\u0e14\u0e15\u0e32\u0e21\u0e01\u0e32\u0e23\u0e43\u0e0a\u0e49\u0e19\u0e49\u0e33\u0e21\u0e31\u0e19", None))

        __sortingEnabled = self.sidebarList.isSortingEnabled()
        self.sidebarList.setSortingEnabled(False)
        ___qlistwidgetitem = self.sidebarList.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u0e2b\u0e19\u0e49\u0e32\u0e2b\u0e25\u0e31\u0e01", None))
        ___qlistwidgetitem1 = self.sidebarList.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\u0e1a\u0e31\u0e19\u0e17\u0e36\u0e01\u0e43\u0e2b\u0e21\u0e48", None))
        ___qlistwidgetitem2 = self.sidebarList.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("MainWindow", u"\u0e23\u0e32\u0e22\u0e07\u0e32\u0e19", None))
        ___qlistwidgetitem3 = self.sidebarList.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("MainWindow", u"\u0e15\u0e31\u0e49\u0e07\u0e04\u0e48\u0e32", None))
        self.sidebarList.setSortingEnabled(__sortingEnabled)

        self.addVehicleButton.setText(QCoreApplication.translate("MainWindow", u"\u0e40\u0e1e\u0e34\u0e48\u0e21\u0e22\u0e32\u0e19\u0e1e\u0e32\u0e2b\u0e19\u0e30", None))
        self.editVehicleButton.setText(QCoreApplication.translate("MainWindow", u"\u0e41\u0e01\u0e49\u0e44\u0e02\u0e22\u0e32\u0e19\u0e1e\u0e32\u0e2b\u0e19\u0e30", None))
        self.deleteVehicleButton.setText(QCoreApplication.translate("MainWindow", u"\u0e25\u0e1a\u0e22\u0e32\u0e19\u0e1e\u0e32\u0e2b\u0e19\u0e30", None))
        self.searchLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0e04\u0e49\u0e19\u0e2b\u0e32...", None))
        self.addEntryButton.setText(QCoreApplication.translate("MainWindow", u"\u0e40\u0e1e\u0e34\u0e48\u0e21\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25\u0e01\u0e32\u0e23\u0e40\u0e15\u0e34\u0e21\u0e19\u0e49\u0e33\u0e21\u0e31\u0e19", None))
        self.importCSVButton.setText(QCoreApplication.translate("MainWindow", u"\u0e19\u0e33\u0e40\u0e02\u0e49\u0e32\u0e08\u0e32\u0e01 CSV", None))
        self.backButton.setText(QCoreApplication.translate("MainWindow", u"\u0e22\u0e49\u0e2d\u0e19\u0e01\u0e25\u0e31\u0e1a", None))
        self.settingsLabel.setText(QCoreApplication.translate("MainWindow", u"\u0e01\u0e32\u0e23\u0e15\u0e31\u0e49\u0e07\u0e04\u0e48\u0e32", None))
        self.aboutButton.setText(QCoreApplication.translate("MainWindow", u"\u0e40\u0e01\u0e35\u0e48\u0e22\u0e27\u0e01\u0e31\u0e1a", None))
        self.stationLabel.setText(QCoreApplication.translate("MainWindow", u"\u0e2a\u0e16\u0e32\u0e19\u0e35", None))
        self.updateLabel.setText(QCoreApplication.translate("MainWindow", u"\u0e2d\u0e31\u0e1b\u0e40\u0e14\u0e15\u0e23\u0e32\u0e04\u0e32 (\u0e0a\u0e31\u0e48\u0e27\u0e42\u0e21\u0e07)", None))
        self.themeLabel.setText(QCoreApplication.translate("MainWindow", u"\u0e18\u0e35\u0e21", None))
        self.themeComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"system", None))
        self.themeComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"light", None))
        self.themeComboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"dark", None))
        self.themeComboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"modern", None))
        self.themeComboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"vivid", None))

        self.syncCheckBox.setText(QCoreApplication.translate("MainWindow", u"\u0e2a\u0e33\u0e23\u0e2d\u0e07\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25\u0e02\u0e36\u0e49\u0e19\u0e04\u0e25\u0e32\u0e27\u0e14\u0e4c\u0e2d\u0e31\u0e15\u0e42\u0e19\u0e21\u0e31\u0e15\u0e34", None))
        self.hotkeyCheckBox.setText(QCoreApplication.translate("MainWindow", u"\u0e40\u0e1b\u0e34\u0e14\u0e43\u0e0a\u0e49\u0e1b\u0e38\u0e48\u0e21\u0e25\u0e31\u0e14\u0e40\u0e1e\u0e34\u0e48\u0e21\u0e23\u0e32\u0e22\u0e01\u0e32\u0e23", None))
        self.startupShortcutButton.setText(QCoreApplication.translate("MainWindow", u"\u0e40\u0e23\u0e34\u0e48\u0e21\u0e1e\u0e23\u0e49\u0e2d\u0e21\u0e27\u0e34\u0e19\u0e42\u0e14\u0e27\u0e2a\u0e4c", None))
        self.cloudPathEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0e42\u0e1f\u0e25\u0e40\u0e14\u0e2d\u0e23\u0e4c\u0e04\u0e25\u0e32\u0e27\u0e14\u0e4c", None))
        self.browseCloudButton.setText(QCoreApplication.translate("MainWindow", u"\u0e40\u0e25\u0e37\u0e2d\u0e01...", None))
        self.budgetEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0e07\u0e1a\u0e15\u0e48\u0e2d\u0e40\u0e14\u0e37\u0e2d\u0e19 (\u0e1a\u0e32\u0e17)", None))
        self.saveBudgetButton.setText(QCoreApplication.translate("MainWindow", u"\u0e1a\u0e31\u0e19\u0e17\u0e36\u0e01\u0e07\u0e1a", None))
    # retranslateUi

