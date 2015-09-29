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
#from lisp.backends.base.media_time import MediaTime
from lisp.core.signal import Connection


class MediaTriggers(Enum):
    Pause = 'Pause'
    Paused = 'Paused'
    Play = 'Play'
    Stop = 'Stop'
    Stopped = 'Stopped'
    EoS = 'EoS'


class MediaHandler:

    def __init__(self, media, triggers):
        # {trigger_action: [(target_id, target_action), ...]}
        self.triggers = triggers
        self.media = media

        self.media.on_pause.connect(self._pause, mode=Connection.Async)
        self.media.paused.connect(self._paused, mode=Connection.Async)
        self.media.on_play.connect(self._play, mode=Connection.Async)
        self.media.on_stop.connect(self._stop, mode=Connection.Async)
        self.media.stopped.connect(self._stopped, mode=Connection.Async)
        self.media.eos.connect(self._eos, mode=Connection.Async)

        #self.media_time = MediaTime(media)
        #self.media_time.notify.connect(self._time, mode=Connection.Async)

    def finalize(self):
        self.triggers.clear()

    def _pause(self, *args):
        self._execute(MediaTriggers.Pause.value)

    def _paused(self, *args):
        self._execute(MediaTriggers.Paused.value)

    def _play(self, *args):
        self._execute(MediaTriggers.Play.value)

    def _stop(self, *args):
        self._execute(MediaTriggers.Stop.value)

    def _stopped(self, *args):
        self._execute(MediaTriggers.Stopped.value)

    def _eos(self, *args):
        self._execute(MediaTriggers.EoS.value)

    '''def _time(self, time):
        # The maximum precision is tenths of seconds (sec/10)
        self._execute(time // 100)'''

    def _execute(self, trigger):
        for target, target_action in self.triggers.get(trigger, []):
            target = Application().layout.get_cue_by_id(target)

            if target is not None:
                target.execute(target.CueAction(target_action))
