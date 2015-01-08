##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.gst.elements.user_element import UserElement
from lisp.ui.settings.section import SettingsSection


class UserElementSettings(SettingsSection):

    NAME = "Personalized"
    ELEMENT = UserElement

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.groupBox = QGroupBox("User defined elements", self)
        self.groupBox.setGeometry(self.geometry())

        self.layout = QVBoxLayout(self.groupBox)

        self.textEdit = QPlainTextEdit(self.groupBox)
        self.layout.addWidget(self.textEdit)

        self.warning = QLabel(self.groupBox)
        self.warning.setText("Only for advanced user.")
        self.warning.setAlignment(QtCore.Qt.AlignCenter)
        self.warning.setStyleSheet("color: red; font-weight: bold")
        self.layout.addWidget(self.warning)

    def enable_check(self, enable):
        self.groupBox.setCheckable(enable)
        self.groupBox.setChecked(False)

    def set_configuration(self, conf):
        if conf is not None and self.id in conf:
            self.textEdit.setPlainText(conf[self.id]["bin"])

    def get_configuration(self):
        conf = {}

        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            conf[self.id] = {"bin": self.textEdit.toPlainText().strip()}

        return conf
