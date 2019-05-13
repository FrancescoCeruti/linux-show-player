# This file is part of Linux Show Player
#
# This file contains a PyQt5 version of QProgressIndicator.cpp from
# https://github.com/mojocorp/QProgressIndicator
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


from PyQt5.QtCore import Qt, QSize, QRectF
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QSizePolicy


class QProgressWheel(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self._angle = 0
        self._delay = 100
        self._displayedWhenStopped = False
        self._timerId = -1

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.NoFocus)

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, delay):
        if self._timerId != -1:
            self.killTimer(self._timerId)

        self._delay = delay

        if self._timerId != -1:
            self._timerId = self.startTimer(self._delay)

    @property
    def displayedWhenStopped(self):
        return self._displayedWhenStopped

    @displayedWhenStopped.setter
    def displayedWhenStopped(self, display):
        self._displayedWhenStopped = display
        self.update()

    def isAnimated(self):
        return self._timerId != -1

    def startAnimation(self):
        self._angle = 0

        if self._timerId == -1:
            self._timerId = self.startTimer(self._delay)

    def stopAnimation(self):
        if self._timerId != -1:
            self.killTimer(self._timerId)

        self._timerId = -1
        self.update()

    def sizeHint(self):
        return QSize(20, 20)

    def timerEvent(self, event):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self._displayedWhenStopped and not self.isAnimated():
            return

        width = min(self.width(), self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        outerRadius = (width - 1) * 0.5
        innerRadius = (width - 1) * 0.5 * 0.38

        capsuleHeight = outerRadius - innerRadius
        capsuleWidth = capsuleHeight * (0.23 if width > 32 else 0.35)
        capsuleRadius = capsuleWidth / 2

        # Use the pen (text) color to draw the "capsules"
        color = painter.pen().color()
        painter.setPen(Qt.NoPen)
        painter.translate(self.rect().center())
        painter.rotate(self._angle)

        for i in range(0, 12):
            color.setAlphaF(1.0 - (i / 12.0) if self.isAnimated() else 0.2)
            painter.setBrush(color)
            painter.rotate(-30)

            painter.drawRoundedRect(
                QRectF(
                    capsuleWidth * -0.5,
                    (innerRadius + capsuleHeight) * -1,
                    capsuleWidth,
                    capsuleHeight,
                ),
                capsuleRadius,
                capsuleRadius,
            )
