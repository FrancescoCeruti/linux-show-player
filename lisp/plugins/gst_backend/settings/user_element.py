# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPlainTextEdit, QLabel

from lisp.plugins.gst_backend.elements.user_element import UserElement
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class UserElementSettings(SettingsPage):
    ELEMENT = UserElement
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(self.geometry())
        self.groupBox.setLayout(QVBoxLayout())
        self.layout().addWidget(self.groupBox)

        self.textEdit = QPlainTextEdit(self.groupBox)
        self.groupBox.layout().addWidget(self.textEdit)

        self.warning = QLabel(self.groupBox)
        self.warning.setAlignment(QtCore.Qt.AlignCenter)
        self.warning.setStyleSheet("color: #FF2222; font-weight: bold")
        self.groupBox.layout().addWidget(self.warning)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle(
            translate("UserElementSettings", "User defined elements")
        )
        self.warning.setText(
            translate("UserElementSettings", "Only for advanced user!")
        )

    def enableCheck(self, enabled):
        self.groupBox.setCheckable(enabled)
        self.groupBox.setChecked(False)

    def loadSettings(self, settings):
        self.textEdit.setPlainText(settings.get("bin", ""))

    def getSettings(self):
        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            return {"bin": self.textEdit.toPlainText().strip()}

        return {}
