# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox

from lisp.application import Application
from lisp.core.has_properties import Property
from lisp.cues.cue import Cue, CueAction
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate


class StopAll(Cue):
    Name = QT_TRANSLATE_NOOP('CueName', 'Stop-All')

    action = Property(default=CueAction.Stop.value)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate('CueName', self.Name)

    def __start__(self, fade=False):
        for cue in Application().cue_model:
            action = self.__adjust_action(cue, CueAction(self.action))
            if action:
                cue.execute(action=action)

        return False

    def __adjust_action(self, cue, action, fade=False):
        if action in cue.CueActions:
            return action
        elif action is CueAction.FadeOutPause:
            return self.__adjust_action(cue, CueAction.Pause, True)
        elif action is CueAction.Pause and fade:
            return self.__adjust_action(cue, CueAction.FadeOutStop)
        elif action is CueAction.FadeOutInterrupt:
            return self.__adjust_action(cue, CueAction.Interrupt)
        elif action is CueAction.FadeOutStop:
            return self.__adjust_action(cue, CueAction.Stop)

        return None


class StopAllSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Stop Settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.group = QGroupBox(self)
        self.group.setLayout(QVBoxLayout(self.group))
        self.layout().addWidget(self.group)

        self.actionCombo = QComboBox(self.group)
        for action in [CueAction.Stop, CueAction.FadeOutStop, CueAction.Pause,
                       CueAction.FadeOutPause, CueAction.Interrupt,
                       CueAction.FadeOutInterrupt]:
            self.actionCombo.addItem(
                translate('CueAction', action.name), action.value)
        self.group.layout().addWidget(self.actionCombo)

        self.retranslateUi()

    def retranslateUi(self):
        self.group.setTitle(translate('StopAll', 'Stop Action'))

    def enable_check(self, enabled):
        self.group.setCheckable(enabled)
        self.group.setChecked(False)

    def get_settings(self):
        conf = {}

        if not (self.group.isCheckable() and not self.group.isChecked()):
            conf['action'] = self.actionCombo.currentData()

        return conf

    def load_settings(self, settings):
        self.actionCombo.setCurrentText(
            translate('CueAction', settings.get('action', '')))


CueSettingsRegistry().add_item(StopAllSettings, StopAll)
