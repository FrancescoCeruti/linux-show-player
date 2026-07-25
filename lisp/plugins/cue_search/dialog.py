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

from html import escape
import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QAbstractTextDocumentLayout, QTextDocument
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QStyle,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from lisp.ui.icons import IconTheme
from lisp.backend.audio_utils import MAX_VOLUME, db_to_linear
from lisp.core.signal import Connection
from lisp.cues.cue import CueState
from lisp.ui.ui_utils import translate

SEARCH_HIGHLIGHT_ROLE = Qt.UserRole + 1
SEARCH_GAIN_BOOST = db_to_linear(8, min_db_zero=False)
SEARCH_GAIN_CUT = db_to_linear(-12, min_db_zero=False)


class CueSearchHighlightDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        html = index.data(SEARCH_HIGHLIGHT_ROLE)
        if not html:
            super().paint(painter, option, index)
            return

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        style = (
            options.widget.style()
            if options.widget is not None
            else QApplication.style()
        )

        document = QTextDocument()
        document.setHtml(html)

        options.text = ""

        painter.save()
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        text_rect = style.subElementRect(
            QStyle.SE_ItemViewItemText, options, options.widget
        )

        if options.state & QStyle.State_Selected:
            palette = options.palette
            color = palette.color(palette.Active, palette.HighlightedText)
            document.setDefaultStyleSheet(
                f"b {{ color: {color.name()}; font-weight: 700; }} "
                f"span {{ color: {color.name()}; }}"
            )

        context = QAbstractTextDocumentLayout.PaintContext()
        painter.translate(text_rect.topLeft())
        painter.setClipRect(text_rect.translated(-text_rect.topLeft()))
        document.documentLayout().draw(painter, context)
        painter.restore()


class CueSearchDialog(QDialog):
    ACTION_FOCUS = "focus"
    ACTION_PLAY = "play"
    ACTION_PLAY_STAY = "play_stay"
    ACTION_PLAY_FOCUS = "play_focus"

    def __init__(self, app, config, parent=None):
        super().__init__(parent=parent)
        self._app = app
        self._config = config
        self._cue_volume_restorers = {}
        self._observed_cues = []
        self._last_query = None

        self.setModal(True)
        self.setMinimumWidth(720)
        self.setWindowTitle(translate("CueSearch", "Find cues"))

        self.setLayout(QVBoxLayout())

        self.searchEdit = QLineEdit(self)
        self.searchEdit.setClearButtonEnabled(True)
        self.searchEdit.installEventFilter(self)
        self.searchEdit.textChanged.connect(self._update_results)
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
        self.resultsView.itemClicked.connect(self._activate_item)
        self.resultsView.itemActivated.connect(self._activate_item)
        self.layout().addWidget(self.resultsView)

        self.actionLayout = QHBoxLayout()
        self.actionLabel = QLabel(self)
        self.actionLayout.addWidget(self.actionLabel)

        self.actionCombo = QComboBox(self)
        self.actionCombo.currentIndexChanged.connect(self._save_action_mode)
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
        self.actionLabel.setText(translate("CueSearch", "When activating:"))

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
            max(0, self.actionCombo.findData(self._read_action_mode()))
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
        self._update_results(self.searchEdit.text())

    def eventFilter(self, watched, event):
        if event.type() == event.KeyPress:
            if watched is self.searchEdit:
                if event.key() in (Qt.Key_Down, Qt.Key_Up):
                    self.resultsView.keyPressEvent(event)
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
        query = text.casefold().strip()

        current_item = self.resultsView.currentItem()
        current_cue_id = None
        if current_item is not None and query == self._last_query:
            current_cue = current_item.data(0, Qt.UserRole)
            if current_cue is not None:
                current_cue_id = current_cue.id

        self._last_query = query

        self._disconnect_observed_cues()
        self.resultsView.clear()

        matches = []
        for cue in self._app.session.layout.cues():
            name = self._normalize_display_text(cue.name or "")
            description = self._normalize_display_text(cue.description or "")

            if not query:
                if self._cue_state_color(cue) is None:
                    continue

                matches.append((0, cue, name, description, None, None))
                continue

            name_match = self._match_text(name, query)
            description_match = self._match_text(description, query)

            if name_match is None and description_match is None:
                continue

            score = 0
            if name_match is not None:
                score += name_match["score"] + 1000
            if description_match is not None:
                score += description_match["score"]

            matches.append(
                (score, cue, name, description, name_match, description_match)
            )

        matches.sort(key=lambda item: (-item[0], item[1].index))

        selected_item = None
        for (
            _,
            cue,
            name,
            description,
            name_match,
            description_match,
        ) in matches:
            self._observe_cue(cue)
            item = QTreeWidgetItem(
                (
                    str(cue.index + 1),
                    name,
                    description,
                )
            )
            item.setIcon(1, IconTheme.get(cue.icon))
            item.setData(0, Qt.UserRole, cue)
            state_color = self._cue_state_color(cue)
            if state_color:
                item.setForeground(
                    0, QApplication.palette().brush(QApplication.palette().Text)
                )
            item.setData(
                1,
                SEARCH_HIGHLIGHT_ROLE,
                self._format_highlighted_text(name, name_match, state_color),
            )
            item.setData(
                2,
                SEARCH_HIGHLIGHT_ROLE,
                self._format_highlighted_text(
                    description, description_match, state_color
                ),
            )
            self.resultsView.addTopLevelItem(item)

            if cue.id == current_cue_id:
                selected_item = item

        if matches:
            if selected_item is None:
                selected_item = self.resultsView.topLevelItem(0)

            self.resultsView.setCurrentItem(selected_item)
            if query:
                info_text = translate(
                    "CueSearch", "{count} cue(s) found."
                ).format(count=len(matches))
            else:
                info_text = translate(
                    "CueSearch",
                    "{count} playing or terminating cue(s).",
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

        for column in range(self.resultsView.columnCount() - 1):
            self.resultsView.resizeColumnToContents(column)

    def _activate_item(self, item, *_):
        cue = item.data(0, Qt.UserRole)
        if cue is None:
            return

        match self.actionCombo.currentData():
            case self.ACTION_FOCUS:
                self._app.session.layout.reveal_cue(cue)
                self.accept()
            case self.ACTION_PLAY:
                cue.execute()
                self.accept()
            case self.ACTION_PLAY_FOCUS:
                cue.execute()
                self._app.session.layout.reveal_cue(cue)
                self.accept()
            case self.ACTION_PLAY_STAY:
                cue.execute()
                self.searchEdit.setFocus()

    def _activate_current_result(self):
        item = self.resultsView.currentItem()
        if item is not None:
            self._activate_item(item)

    def _read_action_mode(self):
        return self._config.get("cueSearch.action", self.ACTION_FOCUS)

    def _save_action_mode(self):
        action_mode = self.actionCombo.currentData()

        if action_mode is not None:
            self._config.set("cueSearch.action", action_mode)
            self._config.write()

    def _refresh_results(self, *_):
        self._update_results(self.searchEdit.text())

    def _execute_cue(self, cue):
        multiplier = 1
        if not cue.state & CueState.IsRunning:
            multiplier = self._activation_volume_multiplier()

        if multiplier != 1:
            self._prepare_temporary_volume_override(cue, multiplier)

        cue.execute()

    def _activation_volume_multiplier(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ControlModifier and not (
            modifiers & Qt.ShiftModifier
        ):
            return SEARCH_GAIN_BOOST

        if modifiers & Qt.ShiftModifier and not (
            modifiers & Qt.ControlModifier
        ):
            return SEARCH_GAIN_CUT

        return 1

    def _prepare_temporary_volume_override(self, cue, multiplier):
        volume = self._cue_volume_element(cue)
        if volume is None:
            return

        current_volume = getattr(volume, "volume", None)
        if current_volume is None:
            return

        target_volume = max(0, min(MAX_VOLUME, current_volume * multiplier))
        if target_volume == current_volume:
            return

        self._restore_cue_volume(cue)

        volume.volume = target_volume
        volume.live_volume = target_volume

        def restore(*_):
            self._restore_cue_volume(cue)

        self._cue_volume_restorers[cue.id] = (restore, current_volume)
        cue.stopped.connect(restore)
        cue.interrupted.connect(restore)
        cue.end.connect(restore)
        cue.error.connect(restore)

    def _restore_cue_volume(self, cue):
        restore_data = self._cue_volume_restorers.pop(cue.id, None)
        if restore_data is None:
            return

        restore, original_volume = restore_data
        cue.stopped.disconnect(restore)
        cue.interrupted.disconnect(restore)
        cue.end.disconnect(restore)
        cue.error.disconnect(restore)

        volume = self._cue_volume_element(cue)
        if volume is not None:
            volume.volume = original_volume

    @staticmethod
    def _cue_volume_element(cue):
        media = getattr(cue, "media", None)
        if media is None:
            return None

        return media.element("Volume")

    def _observe_cue(self, cue):
        self._observed_cues.append(cue)
        cue.started.connect(self._refresh_results, Connection.QtQueued)
        cue.stopped.connect(self._refresh_results, Connection.QtQueued)
        cue.interrupted.connect(self._refresh_results, Connection.QtQueued)
        cue.paused.connect(self._refresh_results, Connection.QtQueued)
        cue.error.connect(self._refresh_results, Connection.QtQueued)
        cue.end.connect(self._refresh_results, Connection.QtQueued)
        cue.fadeout_start.connect(self._refresh_results, Connection.QtQueued)
        cue.fadeout_end.connect(self._refresh_results, Connection.QtQueued)

    def _disconnect_observed_cues(self):
        for cue in self._observed_cues:
            cue.started.disconnect(self._refresh_results)
            cue.stopped.disconnect(self._refresh_results)
            cue.interrupted.disconnect(self._refresh_results)
            cue.paused.disconnect(self._refresh_results)
            cue.error.disconnect(self._refresh_results)
            cue.end.disconnect(self._refresh_results)
            cue.fadeout_start.disconnect(self._refresh_results)
            cue.fadeout_end.disconnect(self._refresh_results)

        self._observed_cues.clear()

    @staticmethod
    def _cue_state_color(cue):
        if cue.is_fading_out():
            return CueSearchDialog._theme_state_color(
                "error", QApplication.palette().brightText().color().name()
            )

        if cue.state & CueState.Running:
            return CueSearchDialog._theme_state_color(
                "running", QApplication.palette().link().color().name()
            )

        return None

    @staticmethod
    def _theme_state_color(state, fallback):
        stylesheet = QApplication.instance().styleSheet()
        pattern = (
            r'#ListTimeWidget\[state="{}"\]::chunk:horizontal\s*{{'
            r"[^}}]*background-color:\s*([^;]+);"
        ).format(re.escape(state))
        match = re.search(pattern, stylesheet, re.MULTILINE | re.DOTALL)
        if match is not None:
            return match.group(1).strip()

        return fallback

    @staticmethod
    def _normalize_display_text(text):
        text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", text).strip()

    def _match_text(self, text, query):
        if not text:
            return None

        folded_text = text.casefold()
        folded_query = query.casefold()

        exact_index = folded_text.find(folded_query)
        if exact_index >= 0:
            indices = tuple(range(exact_index, exact_index + len(folded_query)))
            return {
                "indices": indices,
                "score": 10000 + len(folded_query) * 100 - exact_index,
            }

        indices = []
        start = 0
        for character in folded_query:
            index = folded_text.find(character, start)
            if index < 0:
                return None

            indices.append(index)
            start = index + 1

        score = len(indices) * 20
        span = indices[-1] - indices[0]
        score += max(0, 60 - span)

        previous = None
        for index in indices:
            if index == 0 or not folded_text[index - 1].isalnum():
                score += 15

            if previous is not None:
                if index == previous + 1:
                    score += 25
                else:
                    score -= min(index - previous - 1, 10)

            previous = index

        return {"indices": tuple(indices), "score": score}

    def _format_highlighted_text(self, text, match, color=None):
        if not text:
            return ""

        style = ""
        if color:
            style = f' style="color: {color};"'

        if match is None:
            return f"<span{style}>{escape(text)}</span>"

        highlighted = []
        indices = set(match["indices"])
        current = []
        bold = False

        for index, character in enumerate(text):
            is_match = index in indices
            if is_match != bold:
                if current:
                    chunk = escape("".join(current))
                    if bold:
                        highlighted.append(f"<b>{chunk}</b>")
                    else:
                        highlighted.append(chunk)
                current = [character]
                bold = is_match
            else:
                current.append(character)

        if current:
            chunk = escape("".join(current))
            if bold:
                highlighted.append(f"<b>{chunk}</b>")
            else:
                highlighted.append(chunk)

        return f"<span{style}>{''.join(highlighted)}</span>"
