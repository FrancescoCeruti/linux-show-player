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

from lisp.backends.base.media import MediaState, Media
from lisp.core.has_properties import Property, NestedProperty
from lisp.cues.cue import Cue
from lisp.core.decorators import synchronized_method, async


class MediaCue(Cue):

    class CueAction(Enum):
        Default = 0
        Play = 1
        Pause = 2
        Stop = 3

    pause = Property(default=False)
    _media_ = NestedProperty('media', default={})

    def __init__(self, media, cue_id=None):
        super().__init__(cue_id)
        self.media = media

    def execute(self, action=CueAction.Default):
        # If "default", decide the action to execute
        if action == MediaCue.CueAction.Default:
            if self.media.state != MediaState.Playing:
                action = MediaCue.CueAction.Play
            elif self.pause:
                action = MediaCue.CueAction.Pause
            else:
                action = MediaCue.CueAction.Stop

        if action == MediaCue.CueAction.Play:
            self.media.play()
        elif action == MediaCue.CueAction.Pause:
            self.media.pause()
        elif action == MediaCue.CueAction.Stop:
            self.media.stop()
