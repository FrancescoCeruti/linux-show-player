# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016-1017 Aurélien Cibrario <aurelien.cibrario@gmail.com>
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

"""
A reimplementation of QSplitterHandle and QSplitter for the central splitter
of the list layout.

Permit integration of "collapse event" with "showPlayingAction" in menu
"""

from PyQt5.QtWidgets import QSplitter, QSplitterHandle
from PyQt5.QtCore import Qt

from lisp.core.signal import Signal

class CentralSplitterHandle(QSplitterHandle):

    def __init__(self, splitter):
        super().__init__(Qt.Horizontal, splitter)

        self.splitter = splitter

    def moveEvent(self, event):
        if(self.splitter.sizes()[1] < self.splitter.widget(1).minimumSize().width()):
            self.splitter.right_widget_folded.emit(True)
        else:
            self.splitter.right_widget_folded.emit(False)

class CentralSplitter(QSplitter):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.right_widget_folded = Signal()
        """ emitted when handle moves and fold/unfold right widget (self, bool(is_fold))"""

        self.setOrientation(Qt.Horizontal)
        self.setHandleWidth(6)

    def createHandle(self):
        customhandle = CentralSplitterHandle(self)
        return customhandle
