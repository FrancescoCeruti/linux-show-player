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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QGroupBox

from lisp.application import Application
from lisp.core.properties import Property
from lisp.cues.cue import Cue, CueAction
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class StopAll(Cue):
    Name = QT_TRANSLATE_NOOP("CueName", "Stop-All")
    Category = QT_TRANSLATE_NOOP("CueCategory", "Action cues")

    action = Property(default=CueAction.Stop.value)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate("CueName", self.Name)

    def __start__(self, fade=False):
        Application().layout.execute_all(
            action=CueAction(self.action), quiet=True
        )


class StopAllSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Stop Settings")

    SupportedActions = [
        CueAction.Stop,
        CueAction.FadeOutStop,
        CueAction.Pause,
        CueAction.FadeOutPause,
        CueAction.Interrupt,
        CueAction.FadeOutInterrupt,
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.group = QGroupBox(self)
        self.group.setLayout(QVBoxLayout(self.group))
        self.layout().addWidget(self.group)

        self.actionCombo = QComboBox(self.group)
        for action in StopAllSettings.SupportedActions:
            self.actionCombo.addItem(
                translate("CueAction", action.name), action.value
            )
        self.group.layout().addWidget(self.actionCombo)

        self.retranslateUi()

    def retranslateUi(self):
        self.group.setTitle(translate("StopAll", "Stop Action"))

    def enableCheck(self, enabled):
        self.group.setCheckable(enabled)
        self.group.setChecked(False)

    def getSettings(self):
        conf = {}

        if not (self.group.isCheckable() and not self.group.isChecked()):
            conf["action"] = self.actionCombo.currentData()

        return conf

    def loadSettings(self, settings):
        self.actionCombo.setCurrentText(
            translate("CueAction", settings.get("action", ""))
        )


CueSettingsRegistry().add(StopAllSettings, StopAll)
