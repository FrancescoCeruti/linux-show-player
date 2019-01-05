# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton


class QIconPushButton(QPushButton):
    """QPushButton that resize dynamically it's icon."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__icon_margin = 5

    def setIconMargin(self, margin):
        self.__icon_margin = int(margin)

    def iconMargin(self):
        return self.__icon_margin

    def resizeEvent(self, event):
        size = min(self.width(), self.height()) - 8
        self.setIconSize(QSize(size, size))
