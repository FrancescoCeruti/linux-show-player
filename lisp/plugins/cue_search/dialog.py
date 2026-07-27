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
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTreeWidgetItem,
    QVBoxLayout,
)

from lisp.cues.media_cue import MediaCue
from lisp.plugins.cue_search.widgets import ResultList
from lisp.plugins.cue_search.search import running_cues, search_cues
from lisp.ui.icons import IconTheme
from lisp.core.signal import Connection
from lisp.cues.cue import Cue, CueState
from lisp.ui.ui_utils import translate


class CueSearchDialog(QDialog):
    ACTION_FOCUS = "focus"
    ACTION_PLAY = "play"
    ACTION_PLAY_STAY = "play_stay"
    ACTION_PLAY_FOCUS = "play_focus"

    TRIGGER_KEYS = (Qt.Key_Enter, Qt.Key_Return)

    def __init__(self, app, config, parent=None):
        super().__init__(parent=parent)
        self._app = app
        self._config = config
        self._observedCues = []

        self.setModal(True)
        self.setMinimumWidth(720)

        self.setLayout(QVBoxLayout())

        self.searchEdit = QLineEdit(self)
        self.searchEdit.setClearButtonEnabled(True)
        self.searchEdit.installEventFilter(self)
        self.searchEdit.textChanged.connect(self.updateResults)
        self.layout().addWidget(self.searchEdit)

        self.resultsInfo = QLabel(self)
        self.layout().addWidget(self.resultsInfo)

        self.resultsView = ResultList(self)
        self.resultsView.installEventFilter(self)
        self.resultsView.itemClicked.connect(self.triggerItem)
        self.resultsView.itemActivated.connect(self.triggerItem)
        self.layout().addWidget(self.resultsView)

        self.actionLayout = QHBoxLayout()
        self.actionLabel = QLabel(self)
        self.actionLayout.addWidget(self.actionLabel)

        self.actionCombo = QComboBox(self)
        self.actionCombo.addItem("", self.ACTION_FOCUS)
        self.actionCombo.addItem("", self.ACTION_PLAY)
        self.actionCombo.addItem("", self.ACTION_PLAY_FOCUS)
        self.actionCombo.addItem("", self.ACTION_PLAY_STAY)
        self.actionCombo.setCurrentIndex(
            max(0, self.actionCombo.findData(self.readActionMode()))
        )
        self.actionCombo.currentIndexChanged.connect(self.saveActionMode)
        self.actionLayout.addWidget(self.actionCombo, 1)
        self.layout().addLayout(self.actionLayout)

        self.helpLabel = QLabel(self)
        self.helpLabel.setWordWrap(True)
        self.layout().addWidget(self.helpLabel)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close, parent=self)
        self.buttonBox.rejected.connect(self.reject)
        self.layout().addWidget(self.buttonBox)

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(translate("CueSearch", "Find cues"))

        self.searchEdit.setPlaceholderText(
            translate("CueSearch", "Type to search in cue title or description")
        )
        self.actionLabel.setText(translate("CueSearch", "Action:"))

        self.actionCombo.setItemText(0, translate("CueSearch", "Focus cue"))
        self.actionCombo.setItemText(1, translate("CueSearch", "Trigger cue"))
        self.actionCombo.setItemText(
            2, translate("CueSearch", "Trigger and focus cue")
        )
        self.actionCombo.setItemText(
            3, translate("CueSearch", "Trigger cue and keep panel open")
        )

        self.helpLabel.setText(
            translate(
                "CueSearch",
                "Press Enter or click to run the action. Hold Ctrl to play louder or Shift to play quieter.",
            )
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.searchEdit.setFocus()
        self.updateResults(self.searchEdit.text())

    def eventFilter(self, watched, event):
        if event.type() == event.KeyPress:
            if watched is self.searchEdit:
                if event.key() in (Qt.Key_Down, Qt.Key_Up):
                    self.resultsView.keyPressEvent(event)
                    return True
                if event.key() in self.TRIGGER_KEYS:
                    self.triggerCurrentItem()
                    return True

            if watched is self.resultsView and event.key() in self.TRIGGER_KEYS:
                self.triggerCurrentItem()
                return True

        return super().eventFilter(watched, event)

    def updateResults(self, text: str):
        query = text.strip()

        self.clearObservedCues()
        self.resultsView.clear()

        if not query:
            matches = running_cues(self._app)
        else:
            matches = search_cues(self._app, query)

        for match in matches:
            self.observeCue(match.cue)

            item = QTreeWidgetItem()
            # Index
            item.setIcon(0, self.cueIcon(match.cue))
            item.setText(0, str(match.cue.index + 1))
            item.setData(0, Qt.UserRole, match.cue)
            item.setTextAlignment(0, Qt.AlignRight | Qt.AlignVCenter)
            # Icon+Name
            item.setText(1, match.name)
            item.setData(1, Qt.UserRole, match.formatted_name)
            # Description
            item.setText(2, match.description)
            item.setData(2, Qt.UserRole, match.formatted_description)

            self.resultsView.addTopLevelItem(item)

        if matches:
            self.resultsView.setCurrentItem(self.resultsView.topLevelItem(0))

            if query:
                self.resultsInfo.setText(
                    translate("CueSearch", "{count} cue(s) found.").format(
                        count=len(matches)
                    )
                )
            else:
                self.resultsInfo.setText(
                    translate("CueSearch", "{count} running cue(s).").format(
                        count=len(matches)
                    )
                )
        else:
            if query:
                self.resultsInfo.setText(
                    translate("CueSearch", "No cue matches the current search.")
                )
            else:
                self.resultsInfo.setText(
                    translate(
                        "CueSearch",
                        "Type in the field above to search cues.",
                    )
                )

        self.resultsView.resizeColumnToContents(0)
        self.resultsView.resizeColumnToContents(1)

    def triggerCurrentItem(self):
        item = self.resultsView.currentItem()
        if item is not None:
            self.triggerItem(item)

    def triggerItem(self, item: QTreeWidgetItem):
        cue = item.data(0, Qt.UserRole)
        if cue is None:
            return

        match self.actionCombo.currentData():
            case self.ACTION_FOCUS:
                self._app.layout.reveal_cue(cue)
                self.accept()
            case self.ACTION_PLAY:
                self.executeCue(cue)
                self.accept()
            case self.ACTION_PLAY_FOCUS:
                self.executeCue(cue)
                self._app.layout.reveal_cue(cue)
                self.accept()
            case self.ACTION_PLAY_STAY:
                self.executeCue(cue)
                self.searchEdit.setFocus()

    def executeCue(self, cue: Cue):
        if not cue.state & CueState.IsRunning:
            self.applyVolumeMultiplier(cue, self.volumeMultiplier())

        cue.execute()

    def applyVolumeMultiplier(self, cue: Cue, mutiplier: float):
        if mutiplier == 1 or not isinstance(cue, MediaCue):
            return

        volume = cue.media.element("Volume")
        if volume is not None:
            volume.live_volume = mutiplier

    def volumeMultiplier(self):
        mod = QApplication.keyboardModifiers()

        if mod & Qt.ControlModifier and not mod & Qt.ShiftModifier:
            return float(self._config.get("volume.up", 1))

        if mod & Qt.ShiftModifier and not mod & Qt.ControlModifier:
            return float(self._config.get("volume.down", 1))

        return 1

    def updateCueState(self, cue: Cue):
        query = self.searchEdit.text().strip()

        for row in range(self.resultsView.topLevelItemCount()):
            item = self.resultsView.topLevelItem(row)

            if cue is item.data(0, Qt.UserRole):
                if query:
                    item.setIcon(0, self.cueIcon(cue))
                elif not cue.state & CueState.IsRunning:
                    self.resultsView.takeTopLevelItem(row)
                    self.stopObservingCue(cue)

                return

    def cueIcon(self, cue: Cue):
        if cue.state & CueState.Running:
            return IconTheme.get(f"{cue.icon}-running")
        elif cue.state & CueState.Pause:
            return IconTheme.get(f"{cue.icon}-pause")
        elif cue.state & CueState.Error:
            return IconTheme.get(f"{cue.icon}-error")

        return IconTheme.get(cue.icon)

    def observeCue(self, cue: Cue):
        self._observedCues.append(cue)

        cue.interrupted.connect(self.updateCueState, Connection.QtQueued)
        cue.started.connect(self.updateCueState, Connection.QtQueued)
        cue.stopped.connect(self.updateCueState, Connection.QtQueued)
        cue.paused.connect(self.updateCueState, Connection.QtQueued)
        cue.error.connect(self.updateCueState, Connection.QtQueued)
        cue.end.connect(self.updateCueState, Connection.QtQueued)

    def stopObservingCue(self, cue: Cue):
        cue.interrupted.disconnect(self.updateCueState)
        cue.started.disconnect(self.updateCueState)
        cue.stopped.disconnect(self.updateCueState)
        cue.paused.disconnect(self.updateCueState)
        cue.error.disconnect(self.updateCueState)
        cue.end.disconnect(self.updateCueState)

        self._observedCues.remove(cue)

    def clearObservedCues(self):
        for cue in self._observedCues:
            cue.interrupted.disconnect(self.updateCueState)
            cue.started.disconnect(self.updateCueState)
            cue.stopped.disconnect(self.updateCueState)
            cue.paused.disconnect(self.updateCueState)
            cue.error.disconnect(self.updateCueState)
            cue.end.disconnect(self.updateCueState)

        self._observedCues.clear()

    def readActionMode(self):
        return self._config.get("action", self.ACTION_FOCUS)

    def saveActionMode(self):
        action = self.actionCombo.currentData()

        if action is not None:
            self._config.set("action", action)
            self._config.write()
