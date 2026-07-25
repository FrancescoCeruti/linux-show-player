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
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from lisp.ui.ui_utils import translate


SEARCH_ACTION_KEY = "search.cueSearch.action"
SEARCH_ACTION_FOCUS = "focus"
SEARCH_ACTION_PLAY = "play"
SEARCH_ACTION_PLAY_STAY = "play_stay"
SEARCH_ACTION_PLAY_FOCUS = "play_focus"


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
        self.searchEdit.installEventFilter(self)
        self.searchEdit.textChanged.connect(self._update_results)
        self.layout().addWidget(self.searchEdit)

        self.actionLayout = QHBoxLayout()
        self.actionLabel = QLabel(self)
        self.actionLayout.addWidget(self.actionLabel)

        self.actionCombo = QComboBox(self)
        self.actionCombo.currentIndexChanged.connect(self._save_action_mode)
        self.actionLayout.addWidget(self.actionCombo, 1)
        self.layout().addLayout(self.actionLayout)

        self.resultsInfo = QLabel(self)
        self.layout().addWidget(self.resultsInfo)

        self.resultsView = QTreeWidget(self)
        self.resultsView.setRootIsDecorated(False)
        self.resultsView.setUniformRowHeights(True)
        self.resultsView.setAlternatingRowColors(True)
        self.resultsView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.resultsView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultsView.installEventFilter(self)
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
        self.actionLabel.setText(translate("CueSearch", "When activating:"))

        current_action = self._current_action_mode()
        self.actionCombo.blockSignals(True)
        self.actionCombo.clear()
        self.actionCombo.addItem(
            translate("CueSearch", "Focus cue"), SEARCH_ACTION_FOCUS
        )
        self.actionCombo.addItem(
            translate("CueSearch", "Play cue and close"),
            SEARCH_ACTION_PLAY,
        )
        self.actionCombo.addItem(
            translate("CueSearch", "Play cue and keep panel open"),
            SEARCH_ACTION_PLAY_STAY,
        )
        self.actionCombo.addItem(
            translate("CueSearch", "Play and focus cue"),
            SEARCH_ACTION_PLAY_FOCUS,
        )

        index = self.actionCombo.findData(current_action)
        if index < 0:
            index = 0
        self.actionCombo.setCurrentIndex(index)
        self.actionCombo.blockSignals(False)

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

    def eventFilter(self, watched, event):
        if event.type() == event.KeyPress:
            if watched is self.searchEdit:
                if event.key() == Qt.Key_Down:
                    self._move_current_result(1)
                    return True
                if event.key() == Qt.Key_Up:
                    self._move_current_result(-1)
                    return True
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    self._activate_current_result()
                    return True

            if watched is self.resultsView and event.key() in (
                Qt.Key_Return,
                Qt.Key_Enter,
            ):
                self._activate_current_result()
                return True

        return super().eventFilter(watched, event)

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

        action_mode = self._current_action_mode()

        if action_mode == SEARCH_ACTION_FOCUS:
            self._app.session.layout.reveal_cue(cue)
            self.accept()
            return

        cue.execute()

        if action_mode == SEARCH_ACTION_PLAY:
            self.accept()
            return

        if action_mode == SEARCH_ACTION_PLAY_FOCUS:
            self._app.session.layout.reveal_cue(cue)

        self._refocus_dialog()

    def _activate_current_result(self):
        item = self.resultsView.currentItem()
        if item is None and self.resultsView.topLevelItemCount() > 0:
            item = self.resultsView.topLevelItem(0)

        if item is not None:
            self._activate_item(item)

    def _move_current_result(self, step):
        count = self.resultsView.topLevelItemCount()
        if count <= 0:
            return

        item = self.resultsView.currentItem()
        if item is None:
            index = 0 if step > 0 else count - 1
        else:
            index = self.resultsView.indexOfTopLevelItem(item) + step
            index = max(0, min(index, count - 1))

        item = self.resultsView.topLevelItem(index)
        self.resultsView.setCurrentItem(item)
        self.resultsView.scrollToItem(item)

    def _current_action_mode(self):
        if SEARCH_ACTION_KEY in self._app.conf:
            action_mode = self._app.conf[SEARCH_ACTION_KEY]
        else:
            action_mode = SEARCH_ACTION_FOCUS

        if action_mode not in (
            SEARCH_ACTION_FOCUS,
            SEARCH_ACTION_PLAY,
            SEARCH_ACTION_PLAY_STAY,
            SEARCH_ACTION_PLAY_FOCUS,
        ):
            return SEARCH_ACTION_FOCUS

        return action_mode

    def _save_action_mode(self):
        action_mode = self.actionCombo.currentData()
        if action_mode is None:
            return

        if SEARCH_ACTION_KEY in self._app.conf:
            self._app.conf.set(SEARCH_ACTION_KEY, action_mode)
        else:
            self._app.conf.update(
                {"search": {"cueSearch": {"action": action_mode}}}
            )
        self._app.conf.write()

    def _refocus_dialog(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.searchEdit.setFocus()
