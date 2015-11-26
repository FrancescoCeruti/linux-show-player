# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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


class CueTriggers(Enum):
    Pause = 'Pause'
    Play = 'Play'
    Stop = 'Stop'
    End = 'End'


class CueHandler:

    def __init__(self, cue, triggers):
        # {trigger_action: [(target_id, target_action), ...]}
        self.triggers = triggers
        self.cue = cue

        self.cue.start.connect(self._play, mode=Connection.Async)
        self.cue.pause.connect(self._pause, mode=Connection.Async)
        self.cue.stop.connect(self._stop, mode=Connection.Async)
        self.cue.end.connect(self._end, mode=Connection.Async)

        #self.cue_time = CueTime(cue)
        #self.cue_time.notify.connect(self._time, mode=Connection.Async)

    def finalize(self):
        self.triggers.clear()

    def _pause(self, *args):
        self._execute(CueTriggers.Pause.value)

    def _play(self, *args):
        self._execute(CueTriggers.Play.value)

    def _stop(self, *args):
        self._execute(CueTriggers.Stop.value)

    def _end(self, *args):
        self._execute(CueTriggers.End.value)

    '''def _time(self, time):
        # The maximum precision is tenths of seconds (sec/10)
        self._execute(time // 100)'''

    def _execute(self, trigger):
        for target, target_action in self.triggers.get(trigger, []):
            target = Application().cue_model.get(target)

            if target is not None:
                target.execute(target.CueAction(target_action))
