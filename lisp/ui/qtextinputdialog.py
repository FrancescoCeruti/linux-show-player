# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import QDialog, QScrollArea, QPlainTextEdit, QPushButton


class QTextInputDialog(QDialog):

    def __init__(self, initial='', parent=None):
        super().__init__(parent)

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMaximumSize(400, 230)
        self.setMinimumSize(400, 230)
        self.resize(400, 230)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setGeometry(QtCore.QRect(5, 5, 390, 190))
        self.scrollArea.setWidgetResizable(True)

        self.plainTextEdit = QPlainTextEdit()
        self.plainTextEdit.setGeometry(QtCore.QRect(0, 0, 390, 190))
        self.plainTextEdit.setPlainText(initial)

        self.scrollArea.setWidget(self.plainTextEdit)

        self.acceptButton = QPushButton(self)
        self.acceptButton.setGeometry(QtCore.QRect(280, 200, 100, 25))
        self.acceptButton.setText("Ok")

        self.rejectButton = QPushButton(self)
        self.rejectButton.setGeometry(QtCore.QRect(160, 200, 100, 25))
        self.rejectButton.setText("Cancel")

        self.rejectButton.clicked.connect(self.reject)
        self.acceptButton.clicked.connect(self.accept)
