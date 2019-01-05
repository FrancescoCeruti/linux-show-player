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

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider


class QClickSlider(QSlider):
    sliderJumped = pyqtSignal(int)

    def mousePressEvent(self, e):
        cr = self._control_rect()

        if e.button() == Qt.LeftButton and not cr.contains(e.pos()):
            # Set the value to the minimum
            value = self.minimum()
            # zmax is the maximum value starting from zero
            zmax = self.maximum() - self.minimum()

            if self.orientation() == Qt.Vertical:
                # Add the current position multiplied for value/size ratio
                value += (self.height() - e.y()) * (zmax / self.height())
            else:
                value += e.x() * (zmax / self.width())

            if self.value() != value:
                self.setValue(value)
                self.sliderJumped.emit(self.value())
                e.accept()
            else:
                e.ignore()
        else:
            super().mousePressEvent(e)

    def _control_rect(self):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        return self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderHandle
        )
