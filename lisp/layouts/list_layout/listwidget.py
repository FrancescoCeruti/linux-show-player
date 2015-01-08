##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeyEvent, QContextMenuEvent
from PyQt5.QtWidgets import QTreeWidget


class ListWidget(QTreeWidget):

    key_event = pyqtSignal(QKeyEvent)
    context_event = pyqtSignal(QContextMenuEvent)
    drop_event = QtCore.pyqtSignal(int, int)

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
        super().dropEvent(event)
        self.drop_event.emit(self.startPosition,
                             self.indexFromItem(self.draggingItem).row())

    def mousePressEvent(self, event):
        self.draggingItem = self.itemAt(event.pos())
        self.startPosition = self.indexFromItem(self.draggingItem).row()
        super().mousePressEvent(event)
