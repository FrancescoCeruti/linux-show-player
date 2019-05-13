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

from PyQt5.QtCore import pyqtSignal, QEvent
from PyQt5.QtWidgets import QLabel


class QClickLabel(QLabel):

    clicked = pyqtSignal(QEvent)

    def __init(self, parent):
        super().__init__(parent)

    def mouseReleaseEvent(self, e):
        if self.contentsRect().contains(e.pos()):
            self.clicked.emit(e)
