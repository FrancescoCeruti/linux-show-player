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

from lisp.application import Application
from lisp.core.signal import Connection
from lisp.cues.cue import CueAction


class CueTriggers(Enum):
    Paused = 'Paused'
    Played = 'Played'
    Stopped = 'Stopped'
    Ended = 'Ended'


class CueHandler:

    def __init__(self, cue, triggers):
        # {trigger_action: [(target_id, target_action), ...]}
        self.triggers = triggers
        self.cue = cue

        self.cue.started.connect(self._play, Connection.Async)
        self.cue.paused.connect(self._pause, Connection.Async)
        self.cue.stopped.connect(self._stop, Connection.Async)
        self.cue.end.connect(self._end, Connection.Async)

    def finalize(self):
        self.triggers.clear()

    def _pause(self, *args):
        self._execute(CueTriggers.Paused.value)

    def _play(self, *args):
        self._execute(CueTriggers.Played.value)

    def _stop(self, *args):
        self._execute(CueTriggers.Stopped.value)

    def _end(self, *args):
        self._execute(CueTriggers.Ended.value)

    def _execute(self, trigger):
        for target, target_action in self.triggers.get(trigger, []):
            target = Application().cue_model.get(target)

            if target is not None:
                target.execute(CueAction(target_action))
