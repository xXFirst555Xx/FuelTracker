# -*- coding: utf-8 -*-
# mypy: ignore-errors

################################################################################
## Form generated from reading UI file 'add_entry_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDateEdit, QDialog, QDialogButtonBox, QFormLayout,
    QLabel, QLineEdit, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_AddEntryDialog(object):
    def setupUi(self, AddEntryDialog):
        if not AddEntryDialog.objectName():
            AddEntryDialog.setObjectName(u"AddEntryDialog")
        self.verticalLayout = QVBoxLayout(AddEntryDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.dateLabel = QLabel(AddEntryDialog)
        self.dateLabel.setObjectName(u"dateLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.dateLabel)

        self.dateEdit = QDateEdit(AddEntryDialog)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setCalendarPopup(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.dateEdit)

        self.vehicleLabel = QLabel(AddEntryDialog)
        self.vehicleLabel.setObjectName(u"vehicleLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.vehicleLabel)

        self.vehicleComboBox = QComboBox(AddEntryDialog)
        self.vehicleComboBox.setObjectName(u"vehicleComboBox")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.vehicleComboBox)

        self.amountLabel = QLabel(AddEntryDialog)
        self.amountLabel.setObjectName(u"amountLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.amountLabel)

        self.amountEdit = QLineEdit(AddEntryDialog)
        self.amountEdit.setObjectName(u"amountEdit")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.amountEdit)

        self.odoBeforeLabel = QLabel(AddEntryDialog)
        self.odoBeforeLabel.setObjectName(u"odoBeforeLabel")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.odoBeforeLabel)

        self.odoBeforeEdit = QLineEdit(AddEntryDialog)
        self.odoBeforeEdit.setObjectName(u"odoBeforeEdit")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.odoBeforeEdit)

        self.odoAfterLabel = QLabel(AddEntryDialog)
        self.odoAfterLabel.setObjectName(u"odoAfterLabel")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.odoAfterLabel)

        self.odoAfterEdit = QLineEdit(AddEntryDialog)
        self.odoAfterEdit.setObjectName(u"odoAfterEdit")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.odoAfterEdit)

        self.litersLabel = QLabel(AddEntryDialog)
        self.litersLabel.setObjectName(u"litersLabel")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.litersLabel)

        self.litersEdit = QLineEdit(AddEntryDialog)
        self.litersEdit.setObjectName(u"litersEdit")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.litersEdit)

        self.autoFillCheckBox = QCheckBox(AddEntryDialog)
        self.autoFillCheckBox.setObjectName(u"autoFillCheckBox")
        self.autoFillCheckBox.setChecked(True)

        self.formLayout.setWidget(6, QFormLayout.ItemRole.SpanningRole, self.autoFillCheckBox)


        self.verticalLayout.addLayout(self.formLayout)

        self.buttonBox = QDialogButtonBox(AddEntryDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AddEntryDialog)

        QMetaObject.connectSlotsByName(AddEntryDialog)
    # setupUi

    def retranslateUi(self, AddEntryDialog):
        AddEntryDialog.setWindowTitle(QCoreApplication.translate("AddEntryDialog", u"\u0e1a\u0e31\u0e19\u0e17\u0e36\u0e01\u0e01\u0e32\u0e23\u0e40\u0e15\u0e34\u0e21\u0e19\u0e49\u0e33\u0e21\u0e31\u0e19", None))
        self.dateLabel.setText(QCoreApplication.translate("AddEntryDialog", u"\u0e27\u0e31\u0e19\u0e17\u0e35\u0e48", None))
        self.vehicleLabel.setText(QCoreApplication.translate("AddEntryDialog", u"\u0e23\u0e16", None))
        self.amountLabel.setText(QCoreApplication.translate("AddEntryDialog", u"\u0e40\u0e07\u0e34\u0e19 (\u0e1a\u0e32\u0e17)", None))
#if QT_CONFIG(tooltip)
        self.amountEdit.setToolTip(QCoreApplication.translate("AddEntryDialog", u"\u0e01\u0e23\u0e2d\u0e01\u0e08\u0e33\u0e19\u0e27\u0e19\u0e40\u0e07\u0e34\u0e19\u0e17\u0e35\u0e48\u0e08\u0e48\u0e32\u0e22", None))
#endif // QT_CONFIG(tooltip)
        self.odoBeforeLabel.setText(QCoreApplication.translate("AddEntryDialog", u"\u0e40\u0e25\u0e02\u0e44\u0e21\u0e25\u0e4c\u0e01\u0e48\u0e2d\u0e19", None))
#if QT_CONFIG(tooltip)
        self.odoBeforeEdit.setToolTip(QCoreApplication.translate("AddEntryDialog", u"\u0e40\u0e25\u0e02\u0e44\u0e21\u0e25\u0e4c\u0e01\u0e48\u0e2d\u0e19\u0e40\u0e15\u0e34\u0e21", None))
#endif // QT_CONFIG(tooltip)
        self.odoAfterLabel.setText(QCoreApplication.translate("AddEntryDialog", u"\u0e40\u0e25\u0e02\u0e44\u0e21\u0e25\u0e4c\u0e2b\u0e25\u0e31\u0e07", None))
#if QT_CONFIG(tooltip)
        self.odoAfterEdit.setToolTip(QCoreApplication.translate("AddEntryDialog", u"\u0e40\u0e25\u0e02\u0e44\u0e21\u0e25\u0e4c\u0e2b\u0e25\u0e31\u0e07\u0e40\u0e15\u0e34\u0e21", None))
#endif // QT_CONFIG(tooltip)
        self.litersLabel.setText(QCoreApplication.translate("AddEntryDialog", u"\u0e25\u0e34\u0e15\u0e23 (\u0e44\u0e21\u0e48\u0e1a\u0e31\u0e07\u0e04\u0e31\u0e1a)", None))
#if QT_CONFIG(tooltip)
        self.litersEdit.setToolTip(QCoreApplication.translate("AddEntryDialog", u"\u0e23\u0e30\u0e1a\u0e38\u0e1b\u0e23\u0e34\u0e21\u0e32\u0e13\u0e40\u0e0a\u0e37\u0e49\u0e2d\u0e40\u0e1e\u0e25\u0e34\u0e07\u0e16\u0e49\u0e32\u0e21\u0e35", None))
#endif // QT_CONFIG(tooltip)
        self.autoFillCheckBox.setText(QCoreApplication.translate("AddEntryDialog", u"Auto-fill fuel usage", None))
    # retranslateUi

