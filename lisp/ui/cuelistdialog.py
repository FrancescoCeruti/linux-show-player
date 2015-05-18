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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTreeWidget, QHeaderView, QVBoxLayout, \
    QDialogButtonBox, QTreeWidgetItem


class CueListDialog(QDialog):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setMinimumSize(400, 300)

        self._cues = []

        self.list = QTreeWidget(self)
        self.list.setSelectionMode(self.list.SingleSelection)
        self.list.setSelectionBehavior(self.list.SelectRows)
        self.list.setAlternatingRowColors(True)
        self.list.setIndentation(0)
        self.list.setHeaderLabels(['Index', 'Name'])
        self.list.header().setSectionResizeMode(QHeaderView.Fixed)
        self.list.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.list.header().setStretchLastSection(False)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.list)

        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.layout().addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def add_cue(self, cue):
        try:
            item = QTreeWidgetItem()
            item.setTextAlignment(0, Qt.AlignCenter)

            for n, prop in enumerate(['index', 'name']):
                item.setText(n, str(cue.properties().get(prop, 'Undefined')))

            self._cues.append(cue)
            self.list.addTopLevelItem(item)
        except Exception:
            pass

    def add_cues(self, cues):
        for cue in cues:
            self.add_cue(cue)

    def remove_cue(self, index):
        self.list.takeTopLevelItem(index)
        return self._cues.pop(index)

    def reset(self):
        self.list.clear()
        self._cues.clear()

    def selected_cues(self):
        cues = []
        for item in self.list.selectedItems():
            index = self.list.indexOfTopLevelItem(item)
            cues.append(self._cues[index])
        return cues
