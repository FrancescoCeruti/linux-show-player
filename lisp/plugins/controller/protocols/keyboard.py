# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QTableView,
    QHeaderView,
    QPushButton,
    QVBoxLayout,
)

from lisp.application import Application
from lisp.plugins.controller.common import LayoutAction, tr_layout_action
from lisp.plugins.controller.protocol import Protocol
from lisp.ui.qdelegates import (
    LineEditDelegate,
    CueActionDelegate,
    EnumComboBoxDelegate,
)
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.pages import SettingsPage, CuePageMixin
from lisp.ui.ui_utils import translate


class KeyboardSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Keyboard Shortcuts")

    def __init__(self, actionDelegate, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.keyGroup = QGroupBox(self)
        self.keyGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.keyGroup)

        self.keyboardModel = SimpleTableModel(
            [
                translate("ControllerKeySettings", "Key"),
                translate("ControllerKeySettings", "Action"),
            ]
        )

        self.keyboardView = KeyboardView(actionDelegate, parent=self.keyGroup)
        self.keyboardView.setModel(self.keyboardModel)
        self.keyGroup.layout().addWidget(self.keyboardView, 0, 0, 1, 2)

        self.addButton = QPushButton(self.keyGroup)
        self.addButton.clicked.connect(self._addEmpty)
        self.keyGroup.layout().addWidget(self.addButton, 1, 0)

        self.removeButton = QPushButton(self.keyGroup)
        self.removeButton.clicked.connect(self._removeCurrent)
        self.keyGroup.layout().addWidget(self.removeButton, 1, 1)

        self.retranslateUi()
        self._defaultAction = None

    def retranslateUi(self):
        self.keyGroup.setTitle(translate("ControllerKeySettings", "Shortcuts"))
        self.addButton.setText(translate("ControllerSettings", "Add"))
        self.removeButton.setText(translate("ControllerSettings", "Remove"))

    def enableCheck(self, enabled):
        self.keyGroup.setCheckable(enabled)
        self.keyGroup.setChecked(False)

    def getSettings(self):
        return {"keyboard": self.keyboardModel.rows}

    def loadSettings(self, settings):
        for key, action in settings.get("keyboard", []):
            self.keyboardModel.appendRow(key, action)

    def _addEmpty(self):
        self.keyboardModel.appendRow("", self._defaultAction)

    def _removeCurrent(self):
        self.keyboardModel.removeRow(self.keyboardView.currentIndex().row())


class KeyboardCueSettings(KeyboardSettings, CuePageMixin):
    def __init__(self, cueType, **kwargs):
        super().__init__(
            actionDelegate=CueActionDelegate(
                cue_class=cueType, mode=CueActionDelegate.Mode.Name
            ),
            cueType=cueType,
            **kwargs,
        )
        self._defaultAction = self.cueType.CueActions[0].name


class KeyboardLayoutSettings(KeyboardSettings):
    def __init__(self, **kwargs):
        super().__init__(
            actionDelegate=EnumComboBoxDelegate(
                LayoutAction,
                mode=EnumComboBoxDelegate.Mode.Name,
                trItem=tr_layout_action,
            ),
            **kwargs,
        )
        self._defaultAction = LayoutAction.Go.name


class KeyboardView(QTableView):
    def __init__(self, actionDelegate, **kwargs):
        super().__init__(**kwargs)

        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setHighlightSections(False)

        self.verticalHeader().sectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(24)
        self.verticalHeader().setHighlightSections(False)

        self.delegates = [LineEditDelegate(max_length=1), actionDelegate]

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)


class Keyboard(Protocol):
    CueSettings = KeyboardCueSettings
    LayoutSettings = KeyboardLayoutSettings

    def init(self):
        Application().layout.key_pressed.connect(self.__key_pressed)

    def reset(self):
        Application().layout.key_pressed.disconnect(self.__key_pressed)

    def __key_pressed(self, key_event):
        if not key_event.isAutoRepeat() and key_event.text() != "":
            self.protocol_event.emit(key_event.text())
