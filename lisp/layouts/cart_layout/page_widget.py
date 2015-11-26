# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QSpacerItem, \
    QSizePolicy
from sortedcontainers import SortedDict


class PageWidget(QWidget):
    context_menu = pyqtSignal(QWidget, QPoint)
    move_drop_event = pyqtSignal(object, tuple)
    copy_drop_event = pyqtSignal(object, tuple)

    DRAG_MAGIC = 'LiSP_Drag&Drop'

    def __init__(self, rows, columns, *args):
        super().__init__(*args)
        self.__rows = rows
        self.__columns = columns
        self.__widgets = SortedDict()

        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.init_layout()

        self.drag_indicator = QLabel(self)
        self.drag_indicator.hide()

    def init_layout(self):
        for row in range(1, self.__rows + 1):
            item = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.layout().addItem(item, row, 0)

        for column in range(1, self.__columns + 1):
            item = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.layout().addItem(item, 0, column)

    def add_widget(self, widget, row, column):
        self._check_index(row, column)
        if (row, column) not in self.__widgets:
            widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.__widgets[(row, column)] = widget
            self.layout().addWidget(widget, row + 1, column + 1)
        else:
            raise IndexError('cell {} already used'.format((row, column)))

    def take_widget(self, row, column):
        self._check_index(row, column)
        if (row, column) in self.__widgets:
            widget = self.__widgets.pop((row, column))
            widget.hide()
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

    def _check_index(self, row, column):
        if not isinstance(row, int):
            raise TypeError('rows index must be integers, not {}'
                            .format(row.__class__.__name__))
        if not isinstance(column, int):
            raise TypeError('columns index must be integers, not {}'
                            .format(column.__class__.__name__))

        if not 0 <= row < self.__rows or not 0 <= column < self.__columns:
            raise IndexError('index out of bound {}'.format((row, column)))

    '''def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            if event.mimeData().text() == GridWidget.DRAG_MAGIC:
                event.accept()

    def dragLeaveEvent(self, e):
        self.posIndicator.hide()
        e.ignore()

    def dropEvent(self, e):
        row = math.ceil(e.pos().y() / (self.ydim + self.margin)) - 1
        column = math.ceil(e.pos().x() / (self.xdim + self.margin)) - 1

        if self.itemAt(row, column) is None:
            if qApp.keyboardModifiers() == Qt.ControlModifier:
                e.setDropAction(Qt.MoveAction)
                self.move_drop_event.emit(e.source(), (-1, row, column))
            elif qApp.keyboardModifiers() == Qt.ShiftModifier:
                e.setDropAction(Qt.CopyAction)
                self.copy_drop_event.emit(e.source(), (-1, row, column))

        self.posIndicator.hide()

        e.accept()'''

    '''def dragMoveEvent(self, e):
        row = math.ceil(e.pos().y() / (self.ydim + self.margin)) - 1
        column = math.ceil(e.pos().x() / (self.xdim + self.margin)) - 1
        if row < self.rows and column < self.columns and row >= 0 and column >= 0:
            self.posIndicator.setGeometry(self.calcItemGeometry(row, column))
            if self.itemAt(row, column) is not None:
                self.posIndicator.setPixmap(QPixmap())
                self.posIndicator.setStyleSheet('background-color: rgba(255,0,0,100)')
            else:
                self.posIndicator.setStyleSheet('background-color: rgba(0,0,255,100)')

            self.posIndicator.raise_()
            self.posIndicator.show()

            e.setDropAction(Qt.MoveAction)
            e.accept()'''
