# -*- coding: utf-8 -*-
# mypy: ignore-errors

################################################################################
## Form generated from reading UI file 'add_maintenance_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class Ui_AddMaintenanceDialog(object):
    def setupUi(self, AddMaintenanceDialog):
        if not AddMaintenanceDialog.objectName():
            AddMaintenanceDialog.setObjectName("AddMaintenanceDialog")
        self.verticalLayout = QVBoxLayout(AddMaintenanceDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.vehicleLabel = QLabel(AddMaintenanceDialog)
        self.vehicleLabel.setObjectName("vehicleLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.vehicleLabel)

        self.vehicleComboBox = QComboBox(AddMaintenanceDialog)
        self.vehicleComboBox.setObjectName("vehicleComboBox")

        self.formLayout.setWidget(
            0, QFormLayout.ItemRole.FieldRole, self.vehicleComboBox
        )

        self.nameLabel = QLabel(AddMaintenanceDialog)
        self.nameLabel.setObjectName("nameLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.nameLabel)

        self.nameLineEdit = QLineEdit(AddMaintenanceDialog)
        self.nameLineEdit.setObjectName("nameLineEdit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.nameLineEdit)

        self.odoLabel = QLabel(AddMaintenanceDialog)
        self.odoLabel.setObjectName("odoLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.odoLabel)

        self.odoLineEdit = QLineEdit(AddMaintenanceDialog)
        self.odoLineEdit.setObjectName("odoLineEdit")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.odoLineEdit)

        self.dateLabel = QLabel(AddMaintenanceDialog)
        self.dateLabel.setObjectName("dateLabel")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.dateLabel)

        self.dateEdit = QDateEdit(AddMaintenanceDialog)
        self.dateEdit.setObjectName("dateEdit")
        self.dateEdit.setCalendarPopup(True)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.dateEdit)

        self.noteLabel = QLabel(AddMaintenanceDialog)
        self.noteLabel.setObjectName("noteLabel")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.noteLabel)

        self.noteLineEdit = QLineEdit(AddMaintenanceDialog)
        self.noteLineEdit.setObjectName("noteLineEdit")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.noteLineEdit)

        self.verticalLayout.addLayout(self.formLayout)

        self.buttonBox = QDialogButtonBox(AddMaintenanceDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AddMaintenanceDialog)

        QMetaObject.connectSlotsByName(AddMaintenanceDialog)

    # setupUi

    def retranslateUi(self, AddMaintenanceDialog):
        AddMaintenanceDialog.setWindowTitle(
            QCoreApplication.translate(
                "AddMaintenanceDialog",
                "\u0e01\u0e33\u0e2b\u0e19\u0e14\u0e07\u0e32\u0e19\u0e1a\u0e33\u0e23\u0e38\u0e07\u0e23\u0e31\u0e01\u0e29\u0e32",
                None,
            )
        )
        self.vehicleLabel.setText(
            QCoreApplication.translate("AddMaintenanceDialog", "\u0e23\u0e16", None)
        )
        self.nameLabel.setText(
            QCoreApplication.translate(
                "AddMaintenanceDialog", "\u0e23\u0e32\u0e22\u0e01\u0e32\u0e23", None
            )
        )
        self.odoLabel.setText(
            QCoreApplication.translate(
                "AddMaintenanceDialog",
                "\u0e40\u0e25\u0e02\u0e44\u0e21\u0e25\u0e4c\u0e04\u0e23\u0e1a\u0e01\u0e33\u0e2b\u0e19\u0e14",
                None,
            )
        )
        self.dateLabel.setText(
            QCoreApplication.translate(
                "AddMaintenanceDialog",
                "\u0e27\u0e31\u0e19\u0e04\u0e23\u0e1a\u0e01\u0e33\u0e2b\u0e19\u0e14",
                None,
            )
        )
        self.noteLabel.setText(
            QCoreApplication.translate(
                "AddMaintenanceDialog",
                "\u0e2b\u0e21\u0e32\u0e22\u0e40\u0e2b\u0e15\u0e38",
                None,
            )
        )

    # retranslateUi
