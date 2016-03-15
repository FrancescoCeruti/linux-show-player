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

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeyEvent, QContextMenuEvent
from PyQt5.QtWidgets import QTreeWidget, QHeaderView

from lisp.core.signal import Connection
from lisp.layouts.list_layout.cue_list_item import CueListItem
from lisp.layouts.list_layout.listwidgets import CueStatusIcon, PreWaitWidget, \
    CueTimeWidget, NextActionIcon, PostWaitWidget


class CueListView(QTreeWidget):

    key_event = pyqtSignal(QKeyEvent)
    context_event = pyqtSignal(QContextMenuEvent)
    drop_move_event = QtCore.pyqtSignal(int, int)
    drop_copy_event = QtCore.pyqtSignal(int, int)

    H_NAMES = ['', '#', 'Cue', 'Pre wait', 'Action', 'Post wait', '']
    H_WIDGETS = [CueStatusIcon, None, None, PreWaitWidget, CueTimeWidget,
                 PostWaitWidget, NextActionIcon]

    def __init__(self, cue_model, parent=None):
        """
        :type cue_model: lisp.layouts.list_layout.cue_list_model.CueListModel
        """
        super().__init__(parent)
        self._model = cue_model
        self._model.item_added.connect(self.__cue_added, Connection.QtDirect)
        self._model.item_moved.connect(self.__cue_moved, Connection.QtDirect)
        self._model.item_removed.connect(self.__cue_removed, Connection.QtDirect)
        self._drag_item = None
        self._drag_start = None
        self.__item_moving = False

        self.setHeaderLabels(CueListView.H_NAMES)
        self.header().setDragEnabled(False)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.Fixed)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(2, QHeaderView.Stretch)

        self.setColumnWidth(0, 40)
        self.setColumnWidth(len(CueListView.H_NAMES) - 1, 18)
        self.setDragDropMode(self.InternalMove)
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(self.ScrollPerItem)

        self.setIndentation(0)

    def contextMenuEvent(self, event):
        if self.itemAt(event.pos()) is not None:
            self.context_event.emit(event)
        else:
            super().contextMenuEvent(event)

    def keyPressEvent(self, event):
        self.key_event.emit(event)
        super().keyPressEvent(event)

    def dropEvent(self, event):
        event.setDropAction(QtCore.Qt.MoveAction)
        super().dropEvent(event)
        self.__item_moving = True
        self._model.move(self._drag_start,
                         self.indexFromItem(self._drag_item).row())

        event.accept()

    def mousePressEvent(self, event):
        self._drag_item = self.itemAt(event.pos())
        self._drag_start = self.indexFromItem(self._drag_item).row()
        super().mousePressEvent(event)

    def __cue_added(self, cue):
        item = CueListItem(cue)
        item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled)

        self.insertTopLevelItem(cue.index, item)
        self.__init_item(item, cue)

        if len(self._model) == 1:
            self.setCurrentItem(item)
            self.setFocus()

    def __cue_moved(self, start, end):
        if not self.__item_moving:
            item = self.takeTopLevelItem(start)
            self.insertTopLevelItem(end, item)
        else:
            item = self.topLevelItem(end)

        self.setCurrentItem(item)
        self.__item_moving = False
        self.__init_item(item, self._model.item(end))

    def __cue_removed(self, cue):
        self.takeTopLevelItem(cue.index)

        index = cue.index
        if index > 0:
            index -= 1
        self.setCurrentIndex(self.model().index(index, 0))

    def __init_item(self, item, cue):
        item.name_column = CueListView.H_NAMES.index('Cue')
        for index, widget in enumerate(CueListView.H_WIDGETS):
            if widget is not None:
                self.setItemWidget(item, index, widget(cue))

        self.updateGeometries()