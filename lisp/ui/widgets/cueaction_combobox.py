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

from enum import Enum

from PyQt5.QtCore import QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QComboBox

from lisp.cues.cue import Cue, CueAction
from lisp.ui.ui_utils import translate

QT_TRANSLATE_NOOP('CueAction', 'Default')
QT_TRANSLATE_NOOP('CueAction', 'FadeInStart')
QT_TRANSLATE_NOOP('CueAction', 'FadeOutStop')
QT_TRANSLATE_NOOP('CueAction', 'FadeOutPause')
QT_TRANSLATE_NOOP('CueAction', 'Start')
QT_TRANSLATE_NOOP('CueAction', 'Stop')
QT_TRANSLATE_NOOP('CueAction', 'Pause')


class CueActionComboBox(QComboBox):
    class Mode(Enum):
        Action = 0
        Value = 1
        Name = 2

    def __init__(self, cue_class, mode=Mode.Action, **kwargs):
        super().__init__(**kwargs)
        self.mode = mode

        if issubclass(cue_class, Cue):
            for action in cue_class.CueActions:
                if mode is CueActionComboBox.Mode.Value:
                    value = action.value
                elif mode is CueActionComboBox.Mode.Name:
                    value = action.name
                else:
                    value = action

                self.addItem(translate('CueAction', action.name), value)

    def currentAction(self):
        return self.currentData()

    def setCurrentAction(self, action):
        if self.mode is CueActionComboBox.Mode.Value:
            name = CueAction(action).name
        elif self.mode is CueActionComboBox.Mode.Action:
            name = action.name
        else:
            name = action

        self.setCurrentText(translate('CueAction', name))
