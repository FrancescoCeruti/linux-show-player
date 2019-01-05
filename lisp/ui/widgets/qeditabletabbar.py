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

from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtWidgets import QTabBar, QLineEdit


class QEditableTabBar(QTabBar):
    textChanged = pyqtSignal(int, str)

    def __init__(self, *args):
        super().__init__(*args)

        self._editor = QLineEdit(self)
        self._editor.setWindowFlags(Qt.Popup)
        self._editor.setFocusProxy(self)

        self._editor.editingFinished.connect(self.handleEditingFinished)
        self._editor.installEventFilter(self)

    def eventFilter(self, widget, event):
        clickOutside = event.type() == QEvent.MouseButtonPress and not self._editor.geometry().contains(
            event.globalPos()
        )
        escKey = (
            event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape
        )

        if clickOutside or escKey:
            self._editor.hide()
            return True

        return super().eventFilter(widget, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F2:
            self.editTab(self.currentIndex())
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        self.editTab(index)

    def editTab(self, index):
        if 0 <= index < self.count():
            rect = self.tabRect(index)

            self._editor.setFixedSize(rect.size())
            self._editor.move(self.parent().mapToGlobal(rect.topLeft()))
            self._editor.setText(self.tabText(index))
            self._editor.show()

    def handleEditingFinished(self):
        self._editor.hide()

        index = self.currentIndex()
        text = self._editor.text()
        if index >= 0:
            self.setTabText(index, text)
            self.textChanged.emit(index, text)
