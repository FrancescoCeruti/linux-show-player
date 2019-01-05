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

from enum import Enum

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.core.signal import Connection
from lisp.cues.cue import CueAction


class CueTriggers(Enum):
    Started = QT_TRANSLATE_NOOP("CueTriggers", "Started")
    Paused = QT_TRANSLATE_NOOP("CueTriggers", "Paused")
    Stopped = QT_TRANSLATE_NOOP("CueTriggers", "Stopped")
    Ended = QT_TRANSLATE_NOOP("CueTriggers", "Ended")


class CueHandler:
    def __init__(self, app, cue, triggers):
        self.app = app
        self.triggers = triggers
        self.cue = cue

        self.cue.started.connect(self.__started, Connection.Async)
        self.cue.paused.connect(self.__paused, Connection.Async)
        self.cue.stopped.connect(self.__stopped, Connection.Async)
        self.cue.end.connect(self.__ended, Connection.Async)

    def __paused(self):
        self.__execute(CueTriggers.Paused.value)

    def __started(self):
        self.__execute(CueTriggers.Started.value)

    def __stopped(self):
        self.__execute(CueTriggers.Stopped.value)

    def __ended(self):
        self.__execute(CueTriggers.Ended.value)

    def __execute(self, trigger):
        for target_id, action in self.triggers.get(trigger, []):
            target = self.app.cue_model.get(target_id)

            if target is not None:
                target.execute(CueAction(action))
