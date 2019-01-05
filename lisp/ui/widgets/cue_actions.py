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

from lisp.cues.cue import CueAction
from lisp.ui.ui_utils import translate
from lisp.ui.widgets.qenumcombobox import QEnumComboBox

CueActionsStrings = {
    CueAction.Default: QT_TRANSLATE_NOOP("CueAction", "Default"),
    CueAction.FadeInStart: QT_TRANSLATE_NOOP("CueAction", "Faded Start"),
    CueAction.FadeInResume: QT_TRANSLATE_NOOP("CueAction", "Faded Resume"),
    CueAction.FadeOutPause: QT_TRANSLATE_NOOP("CueAction", "Faded Pause"),
    CueAction.FadeOutStop: QT_TRANSLATE_NOOP("CueAction", "Faded Stop"),
    CueAction.FadeOutInterrupt: QT_TRANSLATE_NOOP(
        "CueAction", "Faded Interrupt"
    ),
    CueAction.Start: QT_TRANSLATE_NOOP("CueAction", "Start"),
    CueAction.Resume: QT_TRANSLATE_NOOP("CueAction", "Resume"),
    CueAction.Pause: QT_TRANSLATE_NOOP("CueAction", "Pause"),
    CueAction.Stop: QT_TRANSLATE_NOOP("CueAction", "Stop"),
    CueAction.DoNothing: QT_TRANSLATE_NOOP("CueAction", "Do Nothing"),
}


def tr_action(action):
    """
    :param action: CueAction to "translate"
    :type action: CueAction

    :return: translated UI friendly string to indicate the action
    :rtype: str
    """
    return translate("CueAction", CueActionsStrings.get(action, action.name))


class CueActionComboBox(QEnumComboBox):
    def __init__(self, actions=(), **kwargs):
        super().__init__(CueAction, items=actions, trItem=tr_action, **kwargs)
