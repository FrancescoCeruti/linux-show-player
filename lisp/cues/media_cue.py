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

from threading import Lock

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.audio_utils import MIN_VOLUME
from lisp.core.configuration import AppConfig
from lisp.core.decorators import async_function
from lisp.core.fade_functions import FadeInType, FadeOutType
from lisp.core.fader import Fader
from lisp.core.properties import Property
from lisp.cues.cue import Cue, CueAction, CueState


class MediaCue(Cue):
    Name = QT_TRANSLATE_NOOP("CueName", "Media Cue")

    media = Property()
    default_start_action = Property(default=CueAction.FadeInStart.value)
    default_stop_action = Property(default=CueAction.FadeOutStop.value)

    CueActions = (
        CueAction.Default,
        CueAction.Start,
        CueAction.FadeInStart,
        CueAction.Resume,
        CueAction.FadeInResume,
        CueAction.Stop,
        CueAction.FadeOutStop,
        CueAction.Pause,
        CueAction.FadeOutPause,
        CueAction.FadeOut,
        CueAction.FadeIn,
        CueAction.Interrupt,
        CueAction.FadeOutInterrupt,
    )

    def __init__(self, media, id=None):
        super().__init__(id=id)
        self.media = media
        self.media.changed("duration").connect(self._duration_change)
        self.media.elements_changed.connect(self.__elements_changed)
        self.media.error.connect(self._on_error)
        self.media.eos.connect(self._on_eos)

        self.__in_fadein = False
        self.__in_fadeout = False

        self.__volume = self.media.element("Volume")
        self.__fader = Fader(self.__volume, "live_volume")
        self.__fade_lock = Lock()

    def __elements_changed(self):
        self.__volume = self.media.element("Volume")
        self.__fader.target = self.__volume

    def __start__(self, fade=False):
        if fade and self._can_fade(self.fadein_duration):
            self.__volume.live_volume = 0

        self.media.play()
        if fade:
            self._on_start_fade()

        return True

    def __stop__(self, fade=False):
        if self.__in_fadeout:
            self.__fader.stop()
        else:
            if self.__in_fadein:
                self.__fader.stop()

            if self._state & CueState.Running and fade:
                self._st_lock.release()
                ended = self._on_stop_fade()
                self._st_lock.acquire()
                if not ended:
                    return False

        self.media.stop()
        return True

    def __pause__(self, fade=False):
        if self.__in_fadeout:
            self.__fader.stop()
        else:
            if self.__in_fadein:
                self.__fader.stop()

            if fade:
                self._st_lock.release()
                ended = self._on_stop_fade()
                self._st_lock.acquire()
                if not ended:
                    return False

        self.media.pause()
        return True

    def __interrupt__(self, fade=False):
        self.__fader.stop()

        if self._state & CueState.Running and fade:
            self._on_stop_fade(interrupt=True)

        self.media.stop()

    @async_function
    def fadein(self, duration, fade_type):
        if not self._st_lock.acquire(timeout=0.1):
            return

        if self._state & CueState.Running:
            self.__fader.stop()

            if self.__volume is not None:
                if duration <= 0:
                    self.__volume.live_volume = self.__volume.volume
                else:
                    self._st_lock.release()
                    self.__fadein(duration, self.__volume.volume, fade_type)
                    return

        self._st_lock.release()

    @async_function
    def fadeout(self, duration, fade_type):
        if not self._st_lock.acquire(timeout=0.1):
            return

        if self._state & CueState.Running:
            self.__fader.stop()

            if self.__volume is not None:
                if duration <= 0:
                    self.__volume.live_volume = 0
                else:
                    self._st_lock.release()
                    self.__fadeout(duration, MIN_VOLUME, fade_type)
                    return

        self._st_lock.release()

    def __fadein(self, duration, to_value, fade_type):
        ended = True
        if self._can_fade(duration):
            with self.__fade_lock:
                self.__in_fadein = True
                self.fadein_start.emit()
                try:
                    self.__fader.prepare()
                    ended = self.__fader.fade(duration, to_value, fade_type)
                finally:
                    self.__in_fadein = False
                    self.fadein_end.emit()

        return ended

    def __fadeout(self, duration, to_value, fade_type):
        ended = True
        if self._can_fade(duration):
            with self.__fade_lock:
                self.__in_fadeout = True
                self.fadeout_start.emit()
                try:
                    self.__fader.prepare()
                    ended = self.__fader.fade(duration, to_value, fade_type)
                finally:
                    self.__in_fadeout = False
                    self.fadeout_end.emit()

        return ended

    def current_time(self):
        return self.media.current_time()

    def _duration_change(self, value):
        self.duration = value

    def _on_eos(self):
        with self._st_lock:
            self.__fader.stop()
            self._ended()

    def _on_error(self):
        with self._st_lock:
            self.__fader.stop()
            self._error()

    def _can_fade(self, duration):
        return self.__volume is not None and duration > 0

    @async_function
    def _on_start_fade(self):
        if self.__volume is not None:
            self.__fadein(
                self.fadein_duration,
                self.__volume.volume,
                FadeInType[self.fadein_type],
            )

    def _on_stop_fade(self, interrupt=False):
        if interrupt:
            duration = AppConfig().get("cue.interruptFade", 0)
            fade_type = AppConfig().get(
                "cue.interruptFadeType", FadeOutType.Linear.name
            )
        else:
            duration = self.fadeout_duration
            fade_type = self.fadeout_type

        return self.__fadeout(duration, 0, FadeOutType[fade_type])
