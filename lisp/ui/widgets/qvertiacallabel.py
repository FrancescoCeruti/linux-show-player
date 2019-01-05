# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QLabel


class QVerticalLabel(QLabel):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.rotate(-90)

        region = QtCore.QRect(-self.height(), 0, self.height(), self.width())
        hint = painter.drawText(region, self.alignment(), self.text())

        painter.end()

        self.setMaximumWidth(hint.height())
        self.setMinimumWidth(0)
        self.setMaximumHeight(16_777_215)
        self.setMinimumHeight(hint.width())

    def sizeHint(self):
        return self.size()
