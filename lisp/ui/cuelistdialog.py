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
from lisp.utils import logging


class CueListDialog(QDialog):
    def __init__(self, cues=None, properties=('index', 'name'), **kwargs):
        super().__init__(**kwargs)

        self.setMinimumSize(600, 400)

        self._properties = properties
        self._cues = []

        self.list = QTreeWidget(self)
        self.list.setSelectionMode(QTreeWidget.SingleSelection)
        self.list.setSelectionBehavior(QTreeWidget.SelectRows)
        self.list.setAlternatingRowColors(True)
        self.list.setIndentation(0)
        self.list.setHeaderLabels([prop.title() for prop in properties])
        self.list.header().setSectionResizeMode(QHeaderView.Fixed)
        self.list.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.list.header().setStretchLastSection(False)
        self.list.sortByColumn(0, Qt.AscendingOrder)
        if cues is not None:
            self.add_cues(cues)
        self.list.setSortingEnabled(True)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.list)

        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.layout().addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def add_cue(self, cue):
        item = QTreeWidgetItem()
        item.setTextAlignment(0, Qt.AlignCenter)

        for n, prop in enumerate(self._properties):
            try:
                item.setData(n, Qt.DisplayRole, getattr(cue, prop, 'Undefined'))
            except Exception as e:
                logging.exception('Cannot display {0} property'.format(prop), e,
                                  dialog=False)

        self._cues.append(cue)
        self.list.addTopLevelItem(item)

    def add_cues(self, cues):
        for cue in cues:
            self.add_cue(cue)

    def remove_cue(self, cue):
        index = self._cues.index(cue)
        self.remove_cue_by_index(index)

    def remove_cue_by_index(self, index):
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
