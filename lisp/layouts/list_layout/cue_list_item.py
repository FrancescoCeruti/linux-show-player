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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem

from lisp.core.signal import Connection
from lisp.ui.ui_utils import load_icon


class CueListItem(QTreeWidgetItem):

    def __init__(self, cue):
        super().__init__()

        self.cue = cue
        self.num_column = 1
        self.name_column = 2

        self._selected = False

        self.cue.changed('name').connect(
            self._update_name, Connection.QtQueued)
        self.cue.changed('index').connect(
            self._update_index, Connection.QtQueued)

        self._update_name(self.cue.name)
        self._update_index(self.cue.index)

        self.setTextAlignment(self.num_column, Qt.AlignCenter)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        self.setIcon(0, load_icon('mark-location' if value else ''))

    def _update_index(self, index):
        self.setText(self.num_column, str(index))

    def _update_name(self, name):
        self.setText(self.name_column, name)
