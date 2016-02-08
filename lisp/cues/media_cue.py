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

from lisp.core.has_properties import NestedProperties
from lisp.cues.cue import Cue, CueState, CueAction


class MediaCue(Cue):
    _media_ = NestedProperties('media', default={})

    CueActions = (CueAction.Default, CueAction.Start, CueAction.Stop,
                  CueAction.Pause)

    def __init__(self, media, cue_id=None):
        super().__init__(cue_id)

        self.__state = CueState.Stop

        self.media = media
        self.media.changed('duration').connect(self._duration_change)
        self.media.on_play.connect(self._running)
        self.media.stopped.connect(self._stop)
        self.media.paused.connect(self._pause)
        self.media.error.connect(self._error)
        self.media.eos.connect(self._end)
        self.media.interrupted.connect(self._stop)

    def __start__(self):
        self.media.play()

    def __stop__(self):
        self.media.stop()

    def __pause__(self):
        self.media.pause()

    def current_time(self):
        return self.media.current_time()

    @Cue.state.getter
    def state(self):
        return self.__state

    def _duration_change(self, value):
        self.duration = value

    def _running(self, *args):
        self.__state = CueState.Running
        self.started.emit(self)

    def _stop(self, *args):
        self.__state = CueState.Stop
        self.stopped.emit(self)

    def _pause(self, *args):
        self.__state = CueState.Pause
        self.paused.emit(self)

    def _end(self, *args):
        self.__state = CueState.Stop
        self.end.emit(self)

    def _error(self, media, msg, details):
        self.__state = CueState.Error
        self.error.emit(self, msg, details)
