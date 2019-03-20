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

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QPushButton, QColorDialog

from lisp.ui.ui_utils import translate


class QColorButton(QPushButton):
    """Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser.
    Right-clicking resets the color to None (no-color).
    """

    colorChanged = pyqtSignal()

    def __init__(self, *args):
        super().__init__(*args)
        self._color = None

        self.setToolTip(translate("QColorButton", "Right click to reset"))
        self.pressed.connect(self.onColorPicker)

    def setColor(self, color):
        if self._color != color:
            self._color = color
            self.colorChanged.emit()

        if self._color is not None:
            self.setStyleSheet(
                "QColorButton {{ background-color: {0}; }}".format(self._color)
            )
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        dlg = QColorDialog()

        if self._color is not None:
            dlg.setCurrentColor(QColor(self._color))
        if dlg.exec() == dlg.Accepted:
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(None)

        return super(QColorButton, self).mousePressEvent(e)
