# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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

from functools import partial

from PyQt6.QtCore import Qt, QEvent, QKeyCombination
from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QSizePolicy,
    QHBoxLayout,
    QMenu,
)

from lisp.ui.icons import IconTheme
from lisp.ui.ui_utils import translate, key_sequence_from_event


class HotKeyEdit(QWidget):
    SPECIAL_KEYS = [
        QKeySequence(Qt.Key.Key_Escape),
        QKeySequence(Qt.Key.Key_Return),
        QKeySequence(Qt.Key.Key_Tab),
        QKeySequence(
            QKeyCombination(Qt.KeyboardModifier.ShiftModifier, Qt.Key.Key_Tab)
        ),
        QKeySequence(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_Tab)
        ),
        QKeySequence(
            QKeyCombination(
                Qt.KeyboardModifier.ShiftModifier
                | Qt.KeyboardModifier.ControlModifier,
                Qt.Key.Key_Tab,
            )
        ),
    ]

    def __init__(
        self,
        sequence=QKeySequence(),
        keysButton=True,
        clearButton=True,
        parent=None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, True)
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, False)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._keySequence = sequence

        self.previewEdit = QLineEdit(self)
        self.previewEdit.setReadOnly(True)
        self.previewEdit.setFocusProxy(self)
        self.previewEdit.installEventFilter(self)
        self.previewEdit.setContextMenuPolicy(
            Qt.ContextMenuPolicy.NoContextMenu
        )
        self.previewEdit.selectionChanged.connect(self.previewEdit.deselect)
        self.layout().addWidget(self.previewEdit)

        self.specialMenu = QMenu()
        for special in HotKeyEdit.SPECIAL_KEYS:
            action = QAction(
                IconTheme.get("list-add-symbolic"),
                special.toString(QKeySequence.SequenceFormat.NativeText),
                self.specialMenu,
            )
            action.triggered.connect(partial(self.setKeySequence, special))
            self.specialMenu.addAction(action)

        if keysButton:
            action = self.previewEdit.addAction(
                IconTheme.get("input-keyboard-symbolic"),
                QLineEdit.ActionPosition.TrailingPosition,
            )
            action.triggered.connect(self.onToolsAction)

        if clearButton:
            action = self.previewEdit.addAction(
                IconTheme.get("edit-clear-symbolic"),
                QLineEdit.ActionPosition.TrailingPosition,
            )
            action.triggered.connect(self.clear)

        self.retranslateUi()

    def retranslateUi(self):
        self.previewEdit.setPlaceholderText(
            translate("HotKeyEdit", "Press shortcut")
        )

    def keySequence(self) -> QKeySequence:
        return self._keySequence

    def setKeySequence(self, keySequence: QKeySequence):
        self._keySequence = keySequence
        self.previewEdit.setText(
            keySequence.toString(QKeySequence.SequenceFormat.NativeText)
        )

    def clear(self):
        self.setKeySequence(QKeySequence())

    def event(self, event: QEvent):
        event_type = event.type()

        if event_type == QEvent.Type.Shortcut:
            return True
        elif event_type == QEvent.Type.ShortcutOverride:
            event.accept()
            return True

        return super().event(event)

    def contextMenuEvent(self, event):
        event.accept()
        self.specialMenu.popup(event.globalPos())

    def keyPressEvent(self, event):
        sequence = key_sequence_from_event(event)
        if sequence:
            self.setKeySequence(sequence)

    def onToolsAction(self):
        self.specialMenu.popup(
            self.previewEdit.mapToGlobal(self.previewEdit.geometry().topRight())
        )
