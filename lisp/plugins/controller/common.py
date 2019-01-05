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

from PyQt5.QtCore import QT_TRANSLATE_NOOP
from enum import Enum

from lisp.ui.ui_utils import translate


class LayoutAction(Enum):
    Go = "Go"
    Reset = "Reset"

    StopAll = "StopAll"
    PauseAll = "PauseAll"
    ResumeAll = "ResumeAll"
    InterruptAll = "InterrupAll"
    FadeOutAll = "FadeOutAll"
    FadeInAll = "FadeInAll"

    StandbyForward = "StandbyForward"
    StandbyBack = "StandbyBack"


LayoutActionsStrings = {
    LayoutAction.Go: QT_TRANSLATE_NOOP("GlobalAction", "Go"),
    LayoutAction.Reset: QT_TRANSLATE_NOOP("GlobalAction", "Reset"),
    LayoutAction.StopAll: QT_TRANSLATE_NOOP("GlobalAction", "Stop all cues"),
    LayoutAction.PauseAll: QT_TRANSLATE_NOOP("GlobalAction", "Pause all cues"),
    LayoutAction.ResumeAll: QT_TRANSLATE_NOOP(
        "GlobalAction", "Resume all cues"
    ),
    LayoutAction.InterruptAll: QT_TRANSLATE_NOOP(
        "GlobalAction", "Interrupt all cues"
    ),
    LayoutAction.FadeOutAll: QT_TRANSLATE_NOOP(
        "GlobalAction", "Fade-out all cues"
    ),
    LayoutAction.FadeInAll: QT_TRANSLATE_NOOP(
        "GlobalAction", "Fade-in all cues"
    ),
    LayoutAction.StandbyForward: QT_TRANSLATE_NOOP(
        "GlobalAction", "Move standby forward"
    ),
    LayoutAction.StandbyBack: QT_TRANSLATE_NOOP(
        "GlobalAction", "Move standby back"
    ),
}


def tr_layout_action(action):
    return translate("CueAction", LayoutActionsStrings.get(action, action.name))
