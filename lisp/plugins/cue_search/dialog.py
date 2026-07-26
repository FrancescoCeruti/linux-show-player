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

from dataclasses import dataclass
from difflib import Match, SequenceMatcher
import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextDocumentFragment
from PyQt5.QtWidgets import (
    QApplication,
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

from lisp.cues.media_cue import MediaCue
from lisp.plugins.cue_search.delegates import CueSearchHighlightDelegate
from lisp.ui.icons import IconTheme
from lisp.core.signal import Connection
from lisp.cues.cue import Cue, CueState
from lisp.ui.ui_utils import translate


@dataclass
class TextMatchResult:
    matches: list[Match]
    score: float


@dataclass
class CueMatchResult:
    cue: Cue
    score: int
    name: str
    description: str
    formatted_name: str
    formatted_description: str


class CueSearchDialog(QDialog):
    ACTION_FOCUS = "focus"
    ACTION_PLAY = "play"
    ACTION_PLAY_STAY = "play_stay"
    ACTION_PLAY_FOCUS = "play_focus"

    def __init__(self, app, config, parent=None):
        super().__init__(parent=parent)
        self._app = app
        self._config = config
        self._observedCues = []

        self.setModal(True)
        self.setMinimumWidth(720)
        self.setWindowTitle(translate("CueSearch", "Find cues"))

        self.setLayout(QVBoxLayout())

        self.searchEdit = QLineEdit(self)
        self.searchEdit.setClearButtonEnabled(True)
        self.searchEdit.installEventFilter(self)
        self.searchEdit.textChanged.connect(self.updateResults)
        self.layout().addWidget(self.searchEdit)

        self.resultsInfo = QLabel(self)
        self.layout().addWidget(self.resultsInfo)

        self.resultsView = QTreeWidget(self)
        self.resultsView.setRootIsDecorated(False)
        self.resultsView.setUniformRowHeights(True)
        self.resultsView.setAlternatingRowColors(True)
        self.resultsView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.resultsView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultsView.installEventFilter(self)
        self.resultsView.setItemDelegateForColumn(
            1, CueSearchHighlightDelegate(self.resultsView)
        )
        self.resultsView.setItemDelegateForColumn(
            2, CueSearchHighlightDelegate(self.resultsView)
        )
        self.resultsView.itemClicked.connect(self.triggerItem)
        self.resultsView.itemActivated.connect(self.triggerItem)
        self.resultsView.setStyleSheet("""
            QWidget::item:selected,
            QWidget::item:selected:hover {
                color: palette(text);
                background-color: rgba(250, 220, 0, 100);
            }
        """)
        self.layout().addWidget(self.resultsView)

        self.actionLayout = QHBoxLayout()
        self.actionLabel = QLabel(self)
        self.actionLayout.addWidget(self.actionLabel)

        self.actionCombo = QComboBox(self)
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
        self.searchEdit.setPlaceholderText(
            translate("CueSearch", "Type to search in cue title or description")
        )
        self.actionLabel.setText(translate("CueSearch", "Action:"))

        self.actionCombo.blockSignals(True)
        self.actionCombo.clear()
        self.actionCombo.addItem(
            translate("CueSearch", "Focus cue"), self.ACTION_FOCUS
        )
        self.actionCombo.addItem(
            translate("CueSearch", "Trigger cue"), self.ACTION_PLAY
        )
        self.actionCombo.addItem(
            translate("CueSearch", "Trigger and focus cue"),
            self.ACTION_PLAY_FOCUS,
        )
        self.actionCombo.addItem(
            translate("CueSearch", "Trigger cue and keep panel open"),
            self.ACTION_PLAY_STAY,
        )
        self.actionCombo.setCurrentIndex(
            max(0, self.actionCombo.findData(self.readActionMode()))
        )
        self.actionCombo.blockSignals(False)

        self.resultsView.setHeaderLabels(
            (
                translate("CueSearch", "#"),
                translate("CueSearch", "Cue"),
                translate("CueSearch", "Description"),
            )
        )
        self.resultsView.header().setStretchLastSection(True)

        self.helpLabel.setText(
            translate(
                "CueSearch",
                "Hold Ctrl to play louder or Shift to play quieter. ",
            )
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.searchEdit.setFocus()
        self.searchEdit.selectAll()
        self.updateResults(self.searchEdit.text())

    def eventFilter(self, watched, event):
        if event.type() == event.KeyPress:
            if watched is self.searchEdit:
                if event.key() in (Qt.Key_Down, Qt.Key_Up):
                    self.resultsView.keyPressEvent(event)
                    return True
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    self.triggerCurrentItem()
                    return True

            if watched is self.resultsView and event.key() in (
                Qt.Key_Return,
                Qt.Key_Enter,
            ):
                self.triggerCurrentItem()
                return True

        return super().eventFilter(watched, event)

    def matchText(self, text: str, query: str) -> TextMatchResult:
        matcher = SequenceMatcher(
            a=query.casefold(), b=text.casefold(), autojunk=False
        )

        matches = matcher.get_matching_blocks()
        # Keep only blocks that matched from the start of the query
        matches = list(filter(lambda match: match.a == 0, matches))
        # Check if we found an exact match
        exactMatch = len(matches) > 0 and matches[0].size == len(query)

        return TextMatchResult(matches, matcher.ratio() + int(exactMatch))

    def searchCues(self, query: str) -> list[CueMatchResult]:
        matches = []

        for cue in self._app.session.layout.cues():
            name = self.toPlainText(cue.name)
            description = self.toPlainText(cue.description)

            name_match = self.matchText(name, query)
            description_match = self.matchText(description, query)

            if not name_match.matches and not description_match.matches:
                continue

            match = CueMatchResult(cue, 0, name, description, "", "")

            if name_match.matches:
                match.score += name_match.score
                match.formatted_name = self.highlightedMatchedText(
                    name, name_match
                )

            if description_match.matches:
                match.score += description_match.score / 2
                match.formatted_description = self.highlightedMatchedText(
                    description, description_match
                )

            matches.append(match)

        matches.sort(key=lambda item: (-item.score, item.cue.index))

        return matches

    def runningCues(self):
        matches = []

        for cue in self._app.session.layout.cues():
            if cue.state & CueState.IsRunning:
                name = self.toPlainText(cue.name)
                description = self.toPlainText(cue.description)

                matches.append(
                    CueMatchResult(cue, 0, name, description, "", "")
                )

        return matches

    def updateResults(self, text: str):
        query = text.strip()

        self.clearObservedCues()
        self.resultsView.clear()

        if not query:
            matches = self.runningCues()
        else:
            matches = self.searchCues(query)

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
                info_text = translate(
                    "CueSearch", "{count} cue(s) found."
                ).format(count=len(matches))
            else:
                info_text = translate(
                    "CueSearch", "{count} running cue(s)."
                ).format(count=len(matches))

            self.resultsInfo.setText(info_text)
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
                self._app.session.layout.reveal_cue(cue)
                self.accept()
            case self.ACTION_PLAY:
                self.executeCue(cue)
                self.accept()
            case self.ACTION_PLAY_FOCUS:
                self.executeCue(cue)
                self._app.session.layout.reveal_cue(cue)
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
                    pass
                elif not (cue.state & CueState.IsRunning):
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

        cue.started.connect(self.updateCueState, Connection.QtQueued)
        cue.stopped.connect(self.updateCueState, Connection.QtQueued)
        cue.interrupted.connect(self.updateCueState, Connection.QtQueued)
        cue.paused.connect(self.updateCueState, Connection.QtQueued)
        cue.error.connect(self.updateCueState, Connection.QtQueued)
        cue.end.connect(self.updateCueState, Connection.QtQueued)

    def stopObservingCue(self, cue: Cue):
        cue.started.disconnect(self.updateCueState)
        cue.stopped.disconnect(self.updateCueState)
        cue.interrupted.disconnect(self.updateCueState)
        cue.paused.disconnect(self.updateCueState)
        cue.error.disconnect(self.updateCueState)
        cue.end.disconnect(self.updateCueState)

        self._observedCues.remove(cue)

    def clearObservedCues(self):
        for cue in self._observedCues:
            cue.started.disconnect(self.updateCueState)
            cue.stopped.disconnect(self.updateCueState)
            cue.interrupted.disconnect(self.updateCueState)
            cue.paused.disconnect(self.updateCueState)
            cue.error.disconnect(self.updateCueState)
            cue.end.disconnect(self.updateCueState)

        self._observedCues.clear()

    def toPlainText(self, text: str):
        text = QTextDocumentFragment.fromHtml(text).toPlainText()

        return re.sub(r"\s+", " ", text).strip()

    def highlightedMatchedText(self, text: str, match_result: TextMatchResult):
        if not text:
            return ""

        if not match_result.matches:
            return text

        result = ""

        for n, current in enumerate(match_result.matches):
            if n == 0:
                # Append text before first match
                result += text[: current.b]
            else:
                # Append between previous and current match
                previous = match_result.matches[n - 1]
                result += text[previous.b + previous.size : current.b]

            # Append matched text in "bold"
            result += (
                "<b>" + text[current.b : current.b + current.size] + "</b>"
            )

        # Append text after last match
        return result + text[current.b + current.size :]

    def readActionMode(self):
        return self._config.get("action", self.ACTION_FOCUS)

    def saveActionMode(self):
        action_mode = self.actionCombo.currentData()

        if action_mode is not None:
            self._config.set("action", action_mode)
            self._config.write()
