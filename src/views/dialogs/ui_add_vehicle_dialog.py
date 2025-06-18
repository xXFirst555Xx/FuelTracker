# -*- coding: utf-8 -*-
# mypy: ignore-errors

################################################################################
## Form generated from reading UI file 'add_vehicle_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtWidgets import (QDialogButtonBox,
    QFormLayout, QLabel, QLineEdit, QVBoxLayout)

class Ui_AddVehicleDialog(object):
    def setupUi(self, AddVehicleDialog):
        if not AddVehicleDialog.objectName():
            AddVehicleDialog.setObjectName(u"AddVehicleDialog")
        self.verticalLayout = QVBoxLayout(AddVehicleDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.nameLabel = QLabel(AddVehicleDialog)
        self.nameLabel.setObjectName(u"nameLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.nameLabel)

        self.nameLineEdit = QLineEdit(AddVehicleDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.nameLineEdit)

        self.typeLabel = QLabel(AddVehicleDialog)
        self.typeLabel.setObjectName(u"typeLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.typeLabel)

        self.typeLineEdit = QLineEdit(AddVehicleDialog)
        self.typeLineEdit.setObjectName(u"typeLineEdit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.typeLineEdit)

        self.plateLabel = QLabel(AddVehicleDialog)
        self.plateLabel.setObjectName(u"plateLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.plateLabel)

        self.plateLineEdit = QLineEdit(AddVehicleDialog)
        self.plateLineEdit.setObjectName(u"plateLineEdit")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.plateLineEdit)

        self.capacityLabel = QLabel(AddVehicleDialog)
        self.capacityLabel.setObjectName(u"capacityLabel")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.capacityLabel)

        self.capacityLineEdit = QLineEdit(AddVehicleDialog)
        self.capacityLineEdit.setObjectName(u"capacityLineEdit")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.capacityLineEdit)


        self.verticalLayout.addLayout(self.formLayout)

        self.buttonBox = QDialogButtonBox(AddVehicleDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AddVehicleDialog)

        QMetaObject.connectSlotsByName(AddVehicleDialog)
    # setupUi

    def retranslateUi(self, AddVehicleDialog):
        AddVehicleDialog.setWindowTitle(QCoreApplication.translate("AddVehicleDialog", u"\u0e40\u0e1e\u0e34\u0e48\u0e21\u0e22\u0e32\u0e19\u0e1e\u0e32\u0e2b\u0e19\u0e30", None))
        self.nameLabel.setText(QCoreApplication.translate("AddVehicleDialog", u"\u0e0a\u0e37\u0e48\u0e2d", None))
        self.typeLabel.setText(QCoreApplication.translate("AddVehicleDialog", u"\u0e1b\u0e23\u0e30\u0e40\u0e20\u0e17", None))
        self.plateLabel.setText(QCoreApplication.translate("AddVehicleDialog", u"\u0e1b\u0e49\u0e32\u0e22\u0e17\u0e30\u0e40\u0e1a\u0e35\u0e22\u0e19", None))
        self.capacityLabel.setText(QCoreApplication.translate("AddVehicleDialog", u"\u0e04\u0e27\u0e32\u0e21\u0e08\u0e38\u0e16\u0e31\u0e07 (\u0e25\u0e34\u0e15\u0e23)", None))
    # retranslateUi

