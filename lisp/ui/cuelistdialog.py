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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QTreeWidget,
    QHeaderView,
    QVBoxLayout,
    QDialogButtonBox,
    QTreeWidgetItem,
)


class CueSelectDialog(QDialog):
    def __init__(
        self,
        cues=None,
        properties=("index", "name"),
        selection_mode=QTreeWidget.SingleSelection,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.setMinimumSize(600, 400)

        self._properties = list(properties)
        self._cues = {}

        self.list = QTreeWidget(self)
        self.list.setSelectionMode(selection_mode)
        self.list.setSelectionBehavior(QTreeWidget.SelectRows)
        self.list.setAlternatingRowColors(True)
        self.list.setIndentation(0)
        self.list.setHeaderLabels([prop.title() for prop in properties])
        self.list.header().setSectionResizeMode(QHeaderView.Fixed)
        self.list.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.list.header().setStretchLastSection(False)
        self.list.sortByColumn(0, Qt.AscendingOrder)
        self.list.setSortingEnabled(True)

        if cues is not None:
            self.add_cues(cues)

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
            item.setData(n, Qt.DisplayRole, getattr(cue, prop, "Undefined"))

        self._cues[cue] = item
        item.setData(0, Qt.UserRole, cue)
        self.list.addTopLevelItem(item)

    def add_cues(self, cues):
        self.list.setSortingEnabled(False)
        for cue in cues:
            self.add_cue(cue)
        self.list.setSortingEnabled(True)

    def remove_cue(self, cue):
        index = self.list.indexOfTopLevelItem(self._cues.pop(cue))
        self.list.takeTopLevelItem(index)

    def reset(self):
        self.list.clear()
        self._cues.clear()

    def selected_cues(self):
        cues = []
        for item in self.list.selectedItems():
            cues.append(item.data(0, Qt.UserRole))
        return cues

    def selected_cue(self):
        items = self.list.selectedItems()
        if items:
            return items[0].data(0, Qt.UserRole)
