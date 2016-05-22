# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy, qApp
from sortedcontainers import SortedDict


class PageWidget(QWidget):
    move_drop_event = pyqtSignal(object, int, int)
    copy_drop_event = pyqtSignal(object, int, int)

    DRAG_MAGIC = 'LiSP_Drag&Drop'

    def __init__(self, rows, columns, *args):
        super().__init__(*args)
        self.setAcceptDrops(True)

        self.__rows = rows
        self.__columns = columns
        self.__widgets = SortedDict()

        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(4, 4, 4, 4)
        self.init_layout()

    def init_layout(self):
        for row in range(0, self.__rows):
            self.layout().setRowStretch(row, 1)
            # item = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
            # self.layout().addItem(item, row, 0)

        for column in range(0, self.__columns):
            self.layout().setColumnStretch(column, 1)
            # item = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
            # self.layout().addItem(item, 0, column)

    def add_widget(self, widget, row, column):
        self._check_index(row, column)
        if (row, column) not in self.__widgets:
            widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.__widgets[(row, column)] = widget
            self.layout().addWidget(widget, row, column)
            widget.show()
        else:
            raise IndexError('cell {} already used'.format((row, column)))

    def take_widget(self, row, column):
        self._check_index(row, column)
        if (row, column) in self.__widgets:
            widget = self.__widgets.pop((row, column))
            widget.hide()
            self.layout().removeWidget(widget)
            return widget
        else:
            raise IndexError('cell {} is empty'.format((row, column)))

    def move_widget(self, o_row, o_column, n_row, n_column):
        widget = self.take_widget(o_row, o_column)
        self.add_widget(widget, n_row, n_column)

    def widget(self, row, column):
        self._check_index(row, column)
        return self.__widgets.get((row, column))

    def index(self, widget):
        for index, f_widget in self.__widgets.items():
            if widget is f_widget:
                return index

        return -1, -1

    def widgets(self):
        return iter(self.__widgets.values())

    def reset(self):
        self.__widgets.clear()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            if event.mimeData().text() == PageWidget.DRAG_MAGIC:
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        event.ignore()

    def dropEvent(self, event):
        row, column = self._event_index(event)
        if self.layout().itemAtPosition(row, column) is None:
            if qApp.keyboardModifiers() == Qt.ControlModifier:
                event.setDropAction(Qt.MoveAction)
                event.accept()
                self.move_drop_event.emit(event.source(), row, column)
            elif qApp.keyboardModifiers() == Qt.ShiftModifier:
                event.setDropAction(Qt.CopyAction)
                self.copy_drop_event.emit(event.source(), row, column)
                event.accept()

        event.ignore()

    def dragMoveEvent(self, event):
        row, column = self._event_index(event)
        if self.layout().itemAtPosition(row, column) is None:
            event.accept()
        else:
            event.ignore()

    def _check_index(self, row, column):
        if not isinstance(row, int):
            raise TypeError('rows index must be integers, not {}'
                            .format(row.__class__.__name__))
        if not isinstance(column, int):
            raise TypeError('columns index must be integers, not {}'
                            .format(column.__class__.__name__))

        if not 0 <= row < self.__rows or not 0 <= column < self.__columns:
            raise IndexError('index out of bound {}'.format((row, column)))

    def _event_index(self, event):
        # Margins and spacings are equals
        space = self.layout().horizontalSpacing()
        margin = self.layout().contentsMargins().right()

        r_size = (self.height() + margin * 2) // self.__rows + space
        c_size = (self.width() + margin * 2) // self.__columns + space

        row = math.ceil(event.pos().y() / r_size) - 1
        column = math.ceil(event.pos().x() / c_size) - 1

        return row, column
