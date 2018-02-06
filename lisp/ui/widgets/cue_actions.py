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

from lisp.cues.cue import CueAction
from lisp.ui.ui_utils import translate


CueActionsStrings = {
    CueAction.Default: QT_TRANSLATE_NOOP('CueAction', 'Default'),
    CueAction.FadeInStart: QT_TRANSLATE_NOOP('CueAction', 'Faded Start'),
    CueAction.FadeOutStop: QT_TRANSLATE_NOOP('CueAction', 'Faded Stop'),
    CueAction.FadeOutPause: QT_TRANSLATE_NOOP('CueAction', 'Faded Pause'),
    CueAction.FadeOutInterrupt: QT_TRANSLATE_NOOP(
        'CueAction', 'Faded Interrupt'),
    CueAction.Start: QT_TRANSLATE_NOOP('CueAction', 'Start'),
    CueAction.Stop: QT_TRANSLATE_NOOP('CueAction', 'Stop'),
    CueAction.Pause: QT_TRANSLATE_NOOP('CueAction', 'Pause'),
    CueAction.DoNothing: QT_TRANSLATE_NOOP('CueAction', 'Do Nothing'),
}


def tr_action(action):
    """
    :param action: CueAction to "translate"
    :type action: CueAction

    :return: translated UI friendly string to indicate the action
    :rtype: str
    """
    return translate(
        'CueAction', CueActionsStrings.get(action, action.name))


class CueActionComboBox(QComboBox):
    class Mode(Enum):
        Action = 0
        Value = 1
        Name = 2

    def __init__(self, actions, mode=Mode.Action, **kwargs):
        super().__init__(**kwargs)
        self.mode = mode
        self.rebuild(actions)

    def rebuild(self, actions):
        self.clear()

        for action in actions:
            if self.mode is CueActionComboBox.Mode.Value:
                value = action.value
            elif self.mode is CueActionComboBox.Mode.Name:
                value = action.name
            else:
                value = action

            self.addItem(tr_action(action), value)

    def currentAction(self):
        return self.currentData()

    def setCurrentAction(self, action):
        try:
            if self.mode is CueActionComboBox.Mode.Value:
                action = CueAction(action)
            elif self.mode is CueActionComboBox.Mode.Name:
                action = CueAction[action]

            self.setCurrentText(tr_action(action))
        except(ValueError, KeyError):
            pass
