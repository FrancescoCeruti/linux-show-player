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

import math

from PyQt6.QtCore import pyqtSignal, Qt, QPoint
from PyQt6.QtWidgets import QWidget, QGridLayout, QSizePolicy
from sortedcontainers import SortedDict

from lisp.backend import get_backend
from lisp.core.util import typename


class CartPageWidget(QWidget):
    contextMenuRequested = pyqtSignal(QPoint)
    moveWidgetRequested = pyqtSignal(object, int, int)
    copyWidgetRequested = pyqtSignal(object, int, int)

    DRAG_MAGIC = "LiSP_Drag&Drop"

    def __init__(self, rows, columns, *args):
        super().__init__(*args)
        self.setAcceptDrops(True)

        self.__rows = rows
        self.__columns = columns
        self.__widgets = SortedDict()

        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(4, 4, 4, 4)
        self.initLayout()

    def initLayout(self):
        for row in range(0, self.__rows):
            self.layout().setRowStretch(row, 1)

        for column in range(0, self.__columns):
            self.layout().setColumnStretch(column, 1)

    def addWidget(self, widget, row, column):
        self._checkIndex(row, column)
        if (row, column) not in self.__widgets:
            widget.setSizePolicy(
                QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
            )
            self.__widgets[(row, column)] = widget
            self.layout().addWidget(widget, row, column)
            widget.show()
        else:
            raise IndexError(f"cell {row, column} already used")

    def takeWidget(self, row, column):
        self._checkIndex(row, column)
        if (row, column) in self.__widgets:
            widget = self.__widgets.pop((row, column))
            widget.hide()
            self.layout().removeWidget(widget)
            return widget
        else:
            raise IndexError(f"cell {row, column} is empty")

    def moveWidget(self, o_row, o_column, n_row, n_column):
        widget = self.takeWidget(o_row, o_column)
        self.addWidget(widget, n_row, n_column)

    def widget(self, row, column):
        self._checkIndex(row, column)
        return self.__widgets.get((row, column))

    def indexOf(self, widget):
        for index, f_widget in self.__widgets.items():
            if widget is f_widget:
                return index

        return -1, -1

    def widgets(self):
        return iter(self.__widgets.values())

    def reset(self):
        self.__widgets.clear()

    def contextMenuEvent(self, event):
        self.contextMenuRequested.emit(event.globalPos())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and all(
            [x.isLocalFile() for x in event.mimeData().urls()]
        ):
            event.accept()
        elif event.mimeData().text() == CartPageWidget.DRAG_MAGIC:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            # If files are being dropped, add them as cues
            get_backend().add_cue_from_urls(event.mimeData().urls())
        else:
            # Otherwise copy/move existing cue.
            row, column = self.indexAt(event.pos())

            if self.layout().itemAtPosition(row, column) is None:
                if event.proposedAction() == Qt.DropAction.MoveAction:
                    self.moveWidgetRequested.emit(event.source(), row, column)
                elif event.proposedAction() == Qt.DropAction.CopyAction:
                    self.copyWidgetRequested.emit(event.source(), row, column)

    def indexAt(self, pos):
        # All four margins (left, right, top, bottom) of a cue widget are equal
        margin = self.layout().contentsMargins().right()

        r_size = (self.height() + margin * 2) // self.__rows
        c_size = (self.width() + margin * 2) // self.__columns

        row = math.floor(pos.y() / r_size)
        column = math.floor(pos.x() / c_size)

        return row, column

    def widgetAt(self, pos):
        return self.widget(*self.indexAt(pos))

    def _checkIndex(self, row, column):
        if not isinstance(row, int):
            raise TypeError(f"rows index must be integers, not {typename(row)}")
        if not isinstance(column, int):
            raise TypeError(
                f"columns index must be integers, not {typename(column)}"
            )

        if not 0 <= row < self.__rows or not 0 <= column < self.__columns:
            raise IndexError(f"index out of bound {row, column}")
