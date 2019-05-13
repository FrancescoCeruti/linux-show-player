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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QSlider, QStylePainter, QStyleOptionSlider, QStyle


class QStyledSlider(QSlider):
    """QSlider able to paint ticks when using stylesheets."""

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QStylePainter(self)
        painter.setPen(QColor("#a5a294"))

        option = QStyleOptionSlider()
        self.initStyleOption(option)

        tick = 5
        handle = self.style().subControlRect(
            QStyle.CC_Slider, option, QStyle.SC_SliderHandle
        )

        # Draw tick marks
        # Do this manually because they are very badly behaved with stylesheets
        interval = self.tickInterval()
        if interval == 0:
            interval = self.pageStep()

        slide_range = self.maximum() - self.minimum()

        if self.orientation() == Qt.Horizontal:
            no_handle_size = self.width() - handle.width()
            handle_half_size = handle.width() / 2
        else:
            no_handle_size = self.height() - handle.height()
            handle_half_size = handle.height() / 2

        if self.tickPosition() != QSlider.NoTicks:
            for i in range(self.minimum(), self.maximum() + 1, interval):
                y = 0
                x = (
                    round(
                        (i - self.minimum()) / slide_range * no_handle_size
                        + handle_half_size
                    )
                    - 1
                )

                if self.orientation() == Qt.Vertical:
                    x, y = y, x

                # QSlider.TicksAbove == QSlider.TicksLeft
                if (
                    self.tickPosition() == QSlider.TicksBothSides
                    or self.tickPosition() == QSlider.TicksAbove
                ):
                    if self.orientation() == Qt.Horizontal:
                        y = self.rect().top()
                        painter.drawLine(x, y, x, y + tick)
                    else:
                        x = self.rect().left()
                        painter.drawLine(x, y, x + tick, y)

                # QSlider.TicksBelow == QSlider.TicksRight
                if (
                    self.tickPosition() == QSlider.TicksBothSides
                    or self.tickPosition() == QSlider.TicksBelow
                ):
                    if self.orientation() == Qt.Horizontal:
                        y = self.rect().bottom()
                        painter.drawLine(x, y, x, y - tick)
                    else:
                        x = self.rect().right()
                        painter.drawLine(x, y, x - tick, y)
