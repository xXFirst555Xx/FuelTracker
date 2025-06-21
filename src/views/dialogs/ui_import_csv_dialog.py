# -*- coding: utf-8 -*-
# mypy: ignore-errors

################################################################################
## Form generated from reading UI file 'import_csv_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
)


class Ui_ImportCsvDialog(object):
    def setupUi(self, ImportCsvDialog):
        if not ImportCsvDialog.objectName():
            ImportCsvDialog.setObjectName("ImportCsvDialog")
        self.verticalLayout = QVBoxLayout(ImportCsvDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.fileLabel = QLabel(ImportCsvDialog)
        self.fileLabel.setObjectName("fileLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fileLabel)

        self.fileLayout = QHBoxLayout()
        self.fileLayout.setObjectName("fileLayout")
        self.fileLineEdit = QLineEdit(ImportCsvDialog)
        self.fileLineEdit.setObjectName("fileLineEdit")

        self.fileLayout.addWidget(self.fileLineEdit)

        self.browseButton = QPushButton(ImportCsvDialog)
        self.browseButton.setObjectName("browseButton")

        self.fileLayout.addWidget(self.browseButton)

        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.fileLayout)

        self.vehicleLabel = QLabel(ImportCsvDialog)
        self.vehicleLabel.setObjectName("vehicleLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.vehicleLabel)

        self.vehicleComboBox = QComboBox(ImportCsvDialog)
        self.vehicleComboBox.setObjectName("vehicleComboBox")

        self.formLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.vehicleComboBox
        )

        self.verticalLayout.addLayout(self.formLayout)

        self.previewTable = QTableWidget(ImportCsvDialog)
        self.previewTable.setObjectName("previewTable")

        self.verticalLayout.addWidget(self.previewTable)

        self.buttonBox = QDialogButtonBox(ImportCsvDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ImportCsvDialog)

        QMetaObject.connectSlotsByName(ImportCsvDialog)

    # setupUi

    def retranslateUi(self, ImportCsvDialog):
        ImportCsvDialog.setWindowTitle(
            QCoreApplication.translate(
                "ImportCsvDialog",
                "\u0e19\u0e33\u0e40\u0e02\u0e49\u0e32\u0e08\u0e32\u0e01 CSV",
                None,
            )
        )
        self.fileLabel.setText(
            QCoreApplication.translate(
                "ImportCsvDialog", "\u0e44\u0e1f\u0e25\u0e4c CSV", None
            )
        )
        self.browseButton.setText(
            QCoreApplication.translate(
                "ImportCsvDialog", "\u0e40\u0e25\u0e37\u0e2d\u0e01...", None
            )
        )
        self.vehicleLabel.setText(
            QCoreApplication.translate("ImportCsvDialog", "\u0e23\u0e16", None)
        )

    # retranslateUi
