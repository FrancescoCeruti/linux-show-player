# This file is part of Linux Show Player
#
# Copyright 2026 Francesco Ceruti <ceppofrancy@gmail.com>
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
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from lisp.ui.ui_utils import translate


class CueSearchDialog(QDialog):
    def __init__(self, app, parent=None):
        super().__init__(parent=parent)
        self._app = app

        self.setModal(True)
        self.setMinimumWidth(720)
        self.setWindowTitle(translate("CueSearch", "Find cues"))

        self.setLayout(QVBoxLayout())

        self.searchEdit = QLineEdit(self)
        self.searchEdit.setClearButtonEnabled(True)
        self.searchEdit.textChanged.connect(self._update_results)
        self.searchEdit.returnPressed.connect(self._activate_current_result)
        self.layout().addWidget(self.searchEdit)

        self.resultsInfo = QLabel(self)
        self.layout().addWidget(self.resultsInfo)

        self.resultsView = QTreeWidget(self)
        self.resultsView.setRootIsDecorated(False)
        self.resultsView.setUniformRowHeights(True)
        self.resultsView.setAlternatingRowColors(True)
        self.resultsView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.resultsView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultsView.itemActivated.connect(self._activate_item)
        self.resultsView.itemDoubleClicked.connect(self._activate_item)
        self.layout().addWidget(self.resultsView)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close, parent=self)
        self.buttonBox.rejected.connect(self.reject)
        self.layout().addWidget(self.buttonBox)

        self.retranslateUi()
        self._update_results("")

    def retranslateUi(self):
        self.searchEdit.setPlaceholderText(
            translate(
                "CueSearch", "Type to search in cue title or description"
            )
        )
        self.resultsView.setHeaderLabels(
            (
                translate("CueSearch", "#"),
                translate("CueSearch", "Cue"),
                translate("CueSearch", "Description"),
            )
        )
        self.resultsView.header().setStretchLastSection(True)

    def showEvent(self, event):
        super().showEvent(event)
        self.searchEdit.setFocus()
        self.searchEdit.selectAll()
        self._update_results(self.searchEdit.text())

    def _update_results(self, text):
        self.resultsView.clear()

        query = text.casefold().strip()
        if not query:
            self.resultsInfo.setText(
                translate(
                    "CueSearch", "Type in the field above to search cues."
                )
            )
            return

        matches = []
        for cue in self._app.session.layout.cues():
            name = (cue.name or "")
            description = (cue.description or "")
            if query in name.casefold() or query in description.casefold():
                matches.append(cue)

        for cue in matches:
            item = QTreeWidgetItem(
                (
                    str(cue.index + 1),
                    cue.name or "",
                    cue.description or "",
                )
            )
            item.setData(0, Qt.UserRole, cue)
            self.resultsView.addTopLevelItem(item)

        if matches:
            self.resultsView.setCurrentItem(self.resultsView.topLevelItem(0))
            self.resultsInfo.setText(
                translate("CueSearch", "{count} cue(s) found.").format(
                    count=len(matches)
                )
            )
        else:
            self.resultsInfo.setText(
                translate("CueSearch", "No cue matches the current search.")
            )

        for column in range(self.resultsView.columnCount() - 1):
            self.resultsView.resizeColumnToContents(column)

    def _activate_item(self, item, *_):
        cue = item.data(0, Qt.UserRole)
        if cue is None:
            return

        self._app.session.layout.reveal_cue(cue)
        self.accept()

    def _activate_current_result(self):
        item = self.resultsView.currentItem()
        if item is None and self.resultsView.topLevelItemCount() > 0:
            item = self.resultsView.topLevelItem(0)

        if item is not None:
            self._activate_item(item)
