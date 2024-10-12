# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QLabel, QSizePolicy


class ElidedLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )

        self.__elideMode = Qt.TextElideMode.ElideRight
        self.__prevWidth = 0
        self.__prevText = ""
        self.__elided = ""

    def elideMode(self):
        return self.__elideMode

    def setElideMode(self, mode):
        self.__elideMode = mode

    def paintEvent(self, event):
        text = self.text()
        width = self.width()

        if text != self.__prevText or width != self.__prevWidth:
            self.__prevText = text
            self.__prevWidth = width
            self.__elided = self.fontMetrics().elidedText(
                text, self.__elideMode, width
            )

        painter = QPainter(self)
        painter.drawText(self.rect(), self.alignment(), self.__elided)
