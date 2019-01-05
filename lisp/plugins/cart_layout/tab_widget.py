# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QTabWidget

from lisp.ui.widgets.qeditabletabbar import QEditableTabBar


class CartTabWidget(QTabWidget):
    DRAG_MAGIC = "LiSP_Drag&Drop"

    keyPressed = pyqtSignal(QKeyEvent)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setTabBar(QEditableTabBar(self))
        self.tabBar().setDrawBase(False)
        self.tabBar().setObjectName("CartTabBar")

        self.setFocusPolicy(Qt.StrongFocus)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().text() == CartTabWidget.DRAG_MAGIC:
            event.accept()

    def dragMoveEvent(self, event):
        if self.tabBar().contentsRect().contains(event.pos()):
            self.setCurrentIndex(self.tabBar().tabAt(event.pos()))
            event.accept()

    def dropEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            self.keyPressed.emit(event)

        super().keyPressEvent(event)

    def tabTexts(self):
        texts = []
        for i in range(self.tabBar().count()):
            texts.append(self.tabBar().tabText(i))

        return texts

    def setTabTexts(self, texts):
        for i, text in enumerate(texts):
            self.tabBar().setTabText(i, text)

    def pages(self):
        for index in range(self.count()):
            yield self.widget(index)
