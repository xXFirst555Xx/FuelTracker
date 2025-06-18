# -*- coding: utf-8 -*-
# mypy: ignore-errors

################################################################################
## Form generated from reading UI file 'about_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QSizePolicy, QVBoxLayout, QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        self.verticalLayout = QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.aboutLabel = QLabel(AboutDialog)
        self.aboutLabel.setObjectName(u"aboutLabel")
        self.aboutLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.aboutLabel)

        self.buttonBox = QDialogButtonBox(AboutDialog)
        self.buttonBox.setObjectName(u"buttonBox")

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AboutDialog)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"\u0e40\u0e01\u0e35\u0e48\u0e22\u0e27\u0e01\u0e31\u0e1a", None))
        self.aboutLabel.setText(QCoreApplication.translate("AboutDialog", u"FuelTracker \u0e40\u0e1b\u0e47\u0e19\u0e41\u0e2d\u0e1b\u0e15\u0e31\u0e27\u0e2d\u0e22\u0e48\u0e32\u0e07\u0e2a\u0e33\u0e2b\u0e23\u0e31\u0e1a\u0e15\u0e34\u0e14\u0e15\u0e32\u0e21\u0e01\u0e32\u0e23\u0e43\u0e0a\u0e49\u0e19\u0e49\u0e33\u0e21\u0e31\u0e19\n"
"\u0e40\u0e27\u0e2d\u0e23\u0e4c\u0e0a\u0e31\u0e19\u0e19\u0e35\u0e49\u0e43\u0e0a\u0e49\u0e0a\u0e38\u0e14\u0e44\u0e2d\u0e04\u0e2d\u0e19 Feather \u0e43\u0e19\u0e41\u0e16\u0e1a\u0e14\u0e49\u0e32\u0e19\u0e02\u0e49\u0e32\u0e07\u0e1e\u0e23\u0e49\u0e2d\u0e21\u0e1b\u0e49\u0e32\u0e22\u0e20\u0e32\u0e29\u0e32\u0e44\u0e17\u0e22", None))
    # retranslateUi

