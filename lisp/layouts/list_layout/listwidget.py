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

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeyEvent, QContextMenuEvent
from PyQt5.QtWidgets import QTreeWidget, qApp


class ListWidget(QTreeWidget):

    key_event = pyqtSignal(QKeyEvent)
    context_event = pyqtSignal(QContextMenuEvent)
    drop_move_event = QtCore.pyqtSignal(int, int)
    drop_copy_event = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setDragDropMode(self.InternalMove)
        self.setAlternatingRowColors(True)
        self.setAllColumnsShowFocus(True)
        self.setVerticalScrollMode(self.ScrollPerItem)

        self.header().setDragEnabled(False)
        self.header().setStretchLastSection(False)

        self.setIndentation(0)

    def contextMenuEvent(self, event):
        self.context_event.emit(event)

    def keyPressEvent(self, event):
        self.key_event.emit(event)
        super().keyPressEvent(event)

    def dropEvent(self, event):
        if(qApp.keyboardModifiers() == QtCore.Qt.ShiftModifier):
            event.setDropAction(QtCore.Qt.CopyAction)
            self.drop_copy_event.emit(self.drag_start,
                                      self.indexFromItem(self.drag_item).row())
        else:
            event.setDropAction(QtCore.Qt.MoveAction)
            super().dropEvent(event)
            self.drop_move_event.emit(self.drag_start,
                                      self.indexFromItem(self.drag_item).row())

        event.accept()

    def mousePressEvent(self, event):
        self.drag_item = self.itemAt(event.pos())
        self.drag_start = self.indexFromItem(self.drag_item).row()
        super().mousePressEvent(event)
