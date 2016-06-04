# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import QDialog, QLabel, QTimeEdit, QPushButton


class QTimeInputDialog(QDialog):

    def __init__(self, title='', description='', initial=QtCore.QTime(),
                 minValue=QtCore.QTime(), maxValue=QtCore.QTime(),
                 dformat='mm.ss', parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMaximumSize(300, 110)
        self.setMinimumSize(300, 110)
        self.resize(300, 130)

        self.label = QLabel(description, self)
        self.label.setGeometry(10, 0, 280, 20)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.time = QTimeEdit(self)
        self.time.setDisplayFormat(dformat)
        self.time.setMaximumTime(maxValue)
        self.time.setMinimumTime(minValue)
        self.time.setTime(initial)
        self.time.setGeometry(10, 30, 280, 25)

        self.acceptButton = QPushButton(self)
        self.acceptButton.setGeometry(QtCore.QRect(180, 80, 100, 25))
        self.acceptButton.setText("Ok")

        self.rejectButton = QPushButton(self)
        self.rejectButton.setGeometry(QtCore.QRect(60, 80, 100, 25))
        self.rejectButton.setText("Cancel")

        self.rejectButton.clicked.connect(self.reject)
        self.acceptButton.clicked.connect(self.accept)
