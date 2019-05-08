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


from PyQt5.QtCore import QTime, QTimer
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QLabel


class DigitalLabelClock(QLabel):
    def __init__(self, resolution=1000, time_format="hh:mm", parent=None):
        super().__init__(parent)
        self.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))

        self.time_format = time_format
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(resolution)

        self.updateTime()

    def updateTime(self):
        time = QTime.currentTime()
        text = time.toString(self.time_format)

        self.setText(text)
