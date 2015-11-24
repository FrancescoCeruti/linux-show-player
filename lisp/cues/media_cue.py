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

from lisp.backends.base.media import MediaState
from lisp.core.has_properties import Property, NestedProperties
from lisp.cues.cue import Cue, CueState


class MediaCue(Cue):

    MEDIA_TO_CUE_STATE = {
        MediaState.Null: CueState.Stop,
        MediaState.Error: CueState.Error,
        MediaState.Paused: CueState.Pause,
        MediaState.Playing: CueState.Running,
        MediaState.Stopped: CueState.Stop
    }

    class CueAction(Enum):
        Default = 0
        Play = 1
        Pause = 2
        Stop = 3

    media_pause = Property(default=False)
    _media_ = NestedProperties('media', default={})

    def __init__(self, media, cue_id=None):
        super().__init__(cue_id)

        self.media = media
        self.media.changed('duration').connect(self._duration_change)
        self.media.on_play.connect(self._running)
        self.media.stopped.connect(self._stop)
        self.media.paused.connect(self._pause)
        self.media.error.connect(self._error)
        self.media.eos.connect(self._end)
        self.media.interrupted.connect(self._stop)

    def __execute__(self, action=CueAction.Default):
        # If "default", decide the action to execute
        if action == MediaCue.CueAction.Default:
            if self.media.state != MediaState.Playing:
                action = MediaCue.CueAction.Play
            elif self.media_pause:
                action = MediaCue.CueAction.Pause
            else:
                action = MediaCue.CueAction.Stop

        if action == MediaCue.CueAction.Play:
            self.media.play()
        elif action == MediaCue.CueAction.Pause:
            self.media.pause()
        elif action == MediaCue.CueAction.Stop:
            self.media.stop()

    def current_time(self):
        return self.media.current_time()

    @Cue.state.getter
    def state(self):
        return self.MEDIA_TO_CUE_STATE.get(self.media.state, CueState.Error)

    def _duration_change(self, value):
        self.duration = value

    def _running(self, *args):
        self.start.emit(self)

    def _stop(self, *args):
        self.stop.emit(self)

    def _pause(self, *args):
        self.pause.emit(self)

    def _end(self, *args):
        self.end.emit(self)

    def _error(self, media, msg, details):
        self.error.emit(self, msg, details)
