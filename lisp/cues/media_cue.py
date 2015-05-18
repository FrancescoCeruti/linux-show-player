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

from enum import Enum, unique

from lisp.backends.base.media import MediaState
from lisp.cues.cue import Cue
from lisp.core.decorators import synchronized, async


class MediaCue(Cue):
    @unique
    class CueAction(Enum):
        Default = 0
        Play = 1
        Pause = 2
        Stop = 3

    _properties_ = ['pause']
    _properties_.extend(Cue._properties_)

    def __init__(self, media, cue_id=None):
        super().__init__(cue_id)

        self.media = media
        self.pause = False

        self.__finalized = False

    @async
    @synchronized(blocking=False)
    def execute(self, action=CueAction.Default):
        self.on_execute.emit(self, action)

        if action == MediaCue.CueAction.Default:
            if self.media.state != MediaState.Playing:
                self.media.play()
            elif self.pause:
                self.media.pause()
            else:
                self.media.stop()
        elif action == MediaCue.CueAction.Play:
            self.media.play()
        elif action == MediaCue.CueAction.Pause:
            self.media.pause()
        elif action == MediaCue.CueAction.Stop:
            self.media.stop()

        self.executed.emit(self, action)

    def properties(self):
        properties = super().properties().copy()
        properties['media'] = self.media.properties()
        return properties

    def update_properties(self, properties):
        if 'media' in properties:
            media_props = properties.pop('media')
            self.media.update_properties(media_props)

        super().update_properties(properties)

    def finalize(self):
        if not self.__finalized:
            self.__finalized = True
            self.media.finalize()

    def finalized(self):
        return self.__finalized
