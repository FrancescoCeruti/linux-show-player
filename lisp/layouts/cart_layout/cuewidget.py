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

from PyQt5.QtCore import pyqtSignal, QPoint, Qt, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QWidget

from lisp.ui.qclicklabel import QClickLabel


class CueWidget(QWidget):

    context_menu_request = pyqtSignal(object, QPoint)
    focus_changed = pyqtSignal(object)
    edit_request = pyqtSignal(object)
    cue_execute = pyqtSignal(object)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.cue = None
        self.selected = False

        self.nameButton = QClickLabel(self)
        self.nameButton.setObjectName('ButtonCueWidget')
        self.nameButton.setWordWrap(True)
        self.nameButton.setAlignment(Qt.AlignCenter)
        self.nameButton.setFocusPolicy(Qt.NoFocus)
        self.nameButton.clicked.connect(self.on_click)

    def contextMenuEvent(self, event):
        self.context_menu_request.emit(self, event.globalPos())

    def mouseMoveEvent(self, e):
        if(e.buttons() == Qt.LeftButton and
                (e.modifiers() == Qt.ControlModifier or
                 e.modifiers() == Qt.ShiftModifier)):
            mimeData = QMimeData()
            mimeData.setText('GridLayout_Drag&Drop')

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(self.grab(self.rect()))

            if e.modifiers() == Qt.ControlModifier:
                drag.exec_(Qt.MoveAction)
            else:
                drag.exec_(Qt.CopyAction)
        else:
            e.ignore()

    def set_cue(self, cue):
        if self.cue is not None:
            raise Exception('Media already assigned')

        self.cue = cue
        self.cue.changed('stylesheet').connect(self.update_style)
        self.cue.changed('name').connect(self.update_name)

        self.update_name(cue.name)
        self.update_style(cue.stylesheet)

    def update_name(self, name):
        self.nameButton.setText(name)

    def on_click(self, e):
        if e.button() != Qt.RightButton:
            if e.modifiers() == Qt.ShiftModifier:
                self.edit_request.emit(self.cue)
            elif e.modifiers() == Qt.ControlModifier:
                self.select()
            else:
                self.cue_execute.emit(self.cue)
                self.cue.execute()

    def update_style(self, stylesheet):
        stylesheet += 'text-decoration: underline;' if self.selected else ''
        self.nameButton.setStyleSheet(stylesheet)

    def resizeEvent(self, *args, **kwargs):
        self.update()

    def update(self):
        super().update()
        self.nameButton.setGeometry(self.rect())
