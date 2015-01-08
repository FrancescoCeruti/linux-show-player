##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import math
from mimetypes import guess_type

from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *  # @UnusedWildImport


class GridFullException(Exception):
    pass


class AutoResizer(QtCore.QObject):

    def __init__(self, item):
        super().__init__()
        self.item = item

    def eventFilter(self, qobj, event):
        if(event.type() == QtCore.QEvent.Resize):
            self.item.resize(event.size())
            self.item.update()

        return True


# TODO: Can this use a QGridLayout ??
class GridWidget(QWidget):

    move_drop_event = QtCore.pyqtSignal(object, tuple)
    copy_drop_event = QtCore.pyqtSignal(object, tuple)
    file_dropp_event = QtCore.pyqtSignal(list)

    def __init__(self, parent, rows=1, columns=1):
        super().__init__(parent)

        if(rows < 1 or columns < 1):
            raise ValueError('Columns and Rows number must be > 0')

        self.setAcceptDrops(True)
        self.resizeFilter = AutoResizer(self)
        parent.installEventFilter(self.resizeFilter)

        self.rows = rows
        self.columns = columns
        self.dragAudioFiles = []

        self.xdim = 0
        self.ydim = 0
        self.margin = 3
        self.calcItemsSize()

        self.setGeometry(self.parent().geometry())

        self.posIndicator = QLabel(self)
        self.posIndicator.setGeometry(self.calcItemGeometry(0, 0))
        self.posIndicator.hide()

        self.resetGrid()

    def dragEnterEvent(self, e):
        if(e.mimeData().hasUrls()):
            for url in e.mimeData().urls():
                url = url.toString().replace('file://', '')
                if(guess_type(url)[0].startswith('audio')):
                    self.dragAudioFiles.append(url)
            if(len(self.dragAudioFiles) > 0):
                e.accept()
                return
        elif(e.mimeData().hasText()):
            if(e.mimeData().text() == 'GridLayout_Drag&Drop'):
                e.accept()
                return
        e.ignore()

    def dragLeaveEvent(self, e):
        self.posIndicator.hide()
        e.ignore()

    def dropEvent(self, e):
        row = math.ceil(e.pos().y() / (self.ydim + self.margin)) - 1
        column = math.ceil(e.pos().x() / (self.xdim + self.margin)) - 1
        if(self.itemAt(row, column) is None):
            if(len(self.dragAudioFiles) > 0):
                self.file_dropp_event.emit(self.dragAudioFiles)
                self.dragAudioFiles = []
            elif(qApp.keyboardModifiers() == QtCore.Qt.ControlModifier):
                e.setDropAction(QtCore.Qt.MoveAction)
                self.move_drop_event.emit(e.source(), (-1, row, column))
            elif(qApp.keyboardModifiers() == QtCore.Qt.ShiftModifier):
                e.setDropAction(QtCore.Qt.CopyAction)
                self.copy_drop_event.emit(e.source(), (-1, row, column))

        self.posIndicator.hide()

        e.accept()

    def moveWidget(self, widget, pos):
        if(self.itemAt(pos[0], pos[1]) is not None):
            self.removeItem(widget)
            self.addItem(widget, pos[0], pos[1])

    def dragMoveEvent(self, e):
        row = math.ceil(e.pos().y() / (self.ydim + self.margin)) - 1
        column = math.ceil(e.pos().x() / (self.xdim + self.margin)) - 1
        if(row < self.rows and column < self.columns and row >= 0 and column >= 0):
            self.posIndicator.setGeometry(self.calcItemGeometry(row, column))
            if(self.itemAt(row, column) is not None):
                self.posIndicator.setPixmap(QPixmap())
                self.posIndicator.setStyleSheet('background-color: rgba(255,0,0,100)')
            else:
                self.posIndicator.setStyleSheet('background-color: rgba(0,0,255,100)')

            self.posIndicator.raise_()
            self.posIndicator.show()

            e.setDropAction(QtCore.Qt.MoveAction)
            e.accept()

    def resetGrid(self):
        self.items = []
        self.index = [0, 0]
        for r in range(self.rows):
            self.items.append([])
            for c in range(self.columns):  # @UnusedVariable
                self.items[r].append(None)

    def addItem(self, item, row=-1, column=-1):
        if(row >= self.rows or column >= self.columns):
            raise ValueError('Column and row value must be in the assigned range')

        if(row < 0 or column < 0):
            if(self.isFull()):
                raise GridFullException('The grid is full. No more elements can be added')
            row = self.index[0]
            column = self.index[1]

        self.items[row][column] = item
        item.setParent(self)
        item.setGeometry(self.calcItemGeometry(row, column))
        item.setVisible(True)
        if(not self.isFull()):
            self.nextIndex()
        return (row, column)

    def removeItem(self, item):
        index = self.indexOf(item)
        if(index is not None):
            self.removeItemAt(index[0], index[1])

    def removeItemAt(self, row, column):
        if(row >= self.rows or column >= self.columns or row < 0 or column < 0):
            raise ValueError('Column and row value must be in the assigned range')

        self.items[row][column].setVisible(False)
        self.items[row][column] = None
        self.nextIndex()
        self.update()

    def indexOf(self, item):
        for r in range(self.rows):
            for c in range(self.columns):
                if(self.items[r][c] == item):
                    return r, c
        return None

    def itemAt(self, row, column):
        if(row >= self.rows or column >= self.columns or row < 0 or column < 0):
            raise ValueError('Column and row value must be in the assigned range')
        return self.items[row][column]

    def isFull(self):
        for r in range(self.rows):
            for c in range(self.columns):
                if(self.items[r][c] is None):
                    return False
        return True

    def nextIndex(self):
        for r in range(self.rows):
            for c in range(self.columns):
                if(self.items[r][c] is None):
                    self.index[0] = r
                    self.index[1] = c
                    return

        raise GridFullException('The grid is full. No more elements can be added')

    def calcItemGeometry(self, row, column):
        rect = QtCore.QRect()
        rect.setWidth(self.xdim)
        rect.setHeight(self.ydim)

        left = column * self.xdim + (column + 1) * self.margin
        top = row * self.ydim + (row + 1) * self.margin
        rect.translate(left, top)

        return rect

    def calcItemsSize(self):
        self.xdim = int((self.parentWidget().geometry().width() - self.margin * (self.columns + 1)) / self.columns)
        self.ydim = int((self.parentWidget().geometry().height() - self.margin * (self.rows + 1)) / self.rows)

    def update(self):
        super(GridWidget, self).update()
        self.posIndicator.hide()
        self.calcItemsSize()
        for row in self.items:
            for el in row:
                if(el is not None):
                    el.setGeometry(self.calcItemGeometry(self.items.index(row),
                                                         row.index(el)))

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        self.items[key] = value
