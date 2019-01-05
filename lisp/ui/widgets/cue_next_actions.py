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

from PyQt5.QtCore import QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QComboBox

from lisp.cues.cue import CueNextAction
from lisp.ui.ui_utils import translate


CueNextActionsStrings = {
    CueNextAction.DoNothing: QT_TRANSLATE_NOOP("CueNextAction", "Do Nothing"),
    CueNextAction.TriggerAfterEnd: QT_TRANSLATE_NOOP(
        "CueNextAction", "Trigger after the end"
    ),
    CueNextAction.TriggerAfterWait: QT_TRANSLATE_NOOP(
        "CueNextAction", "Trigger after post wait"
    ),
    CueNextAction.SelectAfterEnd: QT_TRANSLATE_NOOP(
        "CueNextAction", "Select after the end"
    ),
    CueNextAction.SelectAfterWait: QT_TRANSLATE_NOOP(
        "CueNextAction", "Select after post wait"
    ),
}


def tr_next_action(action):
    """
    :param action: CueNextAction to "translate"
    :type action: CueNextAction

    :return: translated UI friendly string to indicate the action
    :rtype: str
    """
    return translate(
        "CueNextAction", CueNextActionsStrings.get(action, action.name)
    )


class CueNextActionComboBox(QComboBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for action in CueNextAction:
            self.addItem(tr_next_action(action), action.value)

    def currentAction(self):
        return self.currentData()

    def setCurrentAction(self, value):
        try:
            value = CueNextAction(value)
            self.setCurrentText(tr_next_action(value))
        except ValueError:
            pass
