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

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.core.configuration import config
from lisp.core.decorators import async

from lisp.core.fade_functions import FadeInType, FadeOutType
from lisp.core.fader import Fader
from lisp.core.has_properties import NestedProperties
from lisp.cues.cue import Cue, CueAction, CueState


class MediaCue(Cue):
    Name = QT_TRANSLATE_NOOP('CueName', 'Media Cue')

    _media_ = NestedProperties('media', default={})

    CueActions = (CueAction.Default, CueAction.Start, CueAction.FadeInStart,
                  CueAction.Stop, CueAction.FadeOutStop, CueAction.Pause,
                  CueAction.FadeOutPause, CueAction.Interrupt,
                  CueAction.FadeOutInterrupt)

    def __init__(self, media, id=None):
        super().__init__(id=id)
        self.default_start_action = CueAction.FadeInStart.value
        self.default_stop_action = CueAction.FadeOutStop.value

        self.media = media
        self.media.changed('duration').connect(self._duration_change)
        self.media.elements_changed.connect(self.__elements_changed)
        self.media.error.connect(self._on_error)
        self.media.eos.connect(self._on_eos)

        self.__in_fadein = False
        self.__in_fadeout = False

        self.__volume = self.media.element('Volume')
        self.__fader = Fader(self.__volume, 'current_volume')

    def __elements_changed(self):
        self.__volume = self.media.element('Volume')
        self.__fader.target = self.__volume

    def __start__(self, fade=False):
        if fade and self._can_fadein():
            self.__volume.current_volume = 0

        self.media.play()

        if fade:
            self._fadein()

        return True

    def __stop__(self, fade=False):
        if self.__in_fadeout:
            self.__fader.stop()
        else:
            if self.__in_fadein:
                self.__fader.stop()

            if self._state & CueState.Running and fade and not self._fadeout():
                return False

        self.media.stop()
        return True

    def __pause__(self, fade=False):
        if self.__in_fadeout:
            self.__fader.stop()
        else:
            if self.__in_fadein:
                self.__fader.stop()

            if fade and not self._fadeout():
                return False

        self.media.pause()
        return True

    def __interrupt__(self, fade=False):
        self.__fader.stop()

        if fade:
            self._fadeout(interrupt=True)

        self.media.interrupt()

    def current_time(self):
        return self.media.current_time()

    def _duration_change(self, value):
        self.duration = value

    def _on_eos(self, *args):
        with self._st_lock:
            self.__fader.stop()
            self._ended()

    def _on_error(self, media, message, details):
        with self._st_lock:
            self.__fader.stop()
            self._error(message, details)

    def _can_fadein(self):
        return self.__volume is not None and self.fadein_duration > 0

    def _can_fadeout(self, interrupt=False):
        if self.__volume is not None:
            if interrupt:
                try:
                    return config['MediaCue'].getfloat('InterruptFade') > 0
                except (KeyError, ValueError):
                    return False
            else:
                return self.fadeout_duration > 0

        return False

    @async
    def _fadein(self):
        if self._can_fadein():
            self.__in_fadein = True
            self.fadein_start.emit()
            try:
                self.__fader.prepare()
                self.__fader.fade(self.fadein_duration,
                                  self.__volume.volume,
                                  FadeInType[self.fadein_type])
            finally:
                self.__in_fadein = False
                self.fadein_end.emit()

    def _fadeout(self, interrupt=False):
        ended = True
        if self._can_fadeout(interrupt):
            self.__in_fadeout = True
            self.fadeout_start.emit()
            try:
                self.__fader.prepare()
                if not interrupt:
                    self._st_lock.release()
                    duration = self.fadeout_duration
                    type = FadeOutType[self.fadeout_type]
                else:
                    duration = config['MediaCue'].getfloat('InterruptFade')
                    type = FadeOutType[config['MediaCue']['InterruptFadeType']]

                ended = self.__fader.fade(duration, 0, type)

                if not interrupt:
                    self._st_lock.acquire()
            finally:
                self.__in_fadeout = False
                self.fadeout_end.emit()

        return ended
