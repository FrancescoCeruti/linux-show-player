##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

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

        self.setSelectionMode(self.SingleSelection)

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

        # CTRL+Space change the item selection, this is a bad way to prevent
        # the behavior ( TODO: change in next version )
        if(not (event.key() == QtCore.Qt.Key_Space and
           qApp.keyboardModifiers() == QtCore.Qt.ControlModifier)):
            super().keyPressEvent(event)

    def dropEvent(self, event):
        if qApp.keyboardModifiers() == QtCore.Qt.ControlModifier:
            event.setDropAction(QtCore.Qt.CopyAction)
            self.drop_copy_event.emit(self.drag_start,
                                      self.indexAt(event.pos()).row())
        else:
            event.setDropAction(QtCore.Qt.MoveAction)
            super().dropEvent(event)
            self.drop_move_event.emit(self.drag_start,
                                      self.indexAt(event.pos()).row())

        event.accept()

    def mousePressEvent(self, event):
        self.drag_item = self.itemAt(event.pos())
        self.drag_start = self.indexFromItem(self.drag_item).row()

        if qApp.keyboardModifiers() != QtCore.Qt.ControlModifier:
            super().mousePressEvent(event)
