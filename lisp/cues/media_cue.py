# This file is part of Linux Show Player
#
# Copyright 2023 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.core.decorators import async_function
from lisp.core.fade_functions import FadeInType, FadeOutType
from lisp.core.properties import Property
from lisp.cues.cue import Cue, CueAction, CueState


class MediaCue(Cue):
    Name = QT_TRANSLATE_NOOP("CueName", "Media Cue")

    media = Property()
    icon = Property("speaker")
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
        CueAction.LoopRelease,
    )

    def __init__(self, app, media, id=None):
        super().__init__(app, id=id)
        self.media = media
        self.media.changed("duration").connect(self._duration_change)
        self.media.elements_changed.connect(self.__elements_changed)
        self.media.error.connect(self._on_error)
        self.media.eos.connect(self._on_eos)

        self.__in_fadein = False
        self.__in_fadeout = False

        self.__fade_lock = Lock()
        self.__fader = None
        self.__volume = None

        self.__elements_changed()

    def __elements_changed(self):
        # Ensure the current fade, if any, is not running.
        if self.__fader is not None:
            self.__fader.stop()

        # Create a new fader, if possible
        self.__volume = self.media.element("Volume")
        if self.__volume is not None:
            self.__fader = self.__volume.get_fader("live_volume")
        else:
            self.__fader = None

    def __start__(self, fade=False):
        # If we are fading-in on the start of the media, we need to ensure
        # that the volume starts at 0
        if fade and self.fadein_duration > 0 and self._can_fade():
            self.__volume.live_volume = 0

        self.media.play()

        # Once the media is playing we can start the fade-in, if needed
        if fade and self.fadein_duration > 0 and self._can_fade():
            self._on_start_fade()

        return True

    def __stop__(self, fade=False):
        if self.__in_fadeout:
            self.__fader.stop()
        else:
            if self.__in_fadein:
                self.__fader.stop()

            if fade and self._state & CueState.Running and self._can_fade():
                self._st_lock.release()
                ended = self.__fadeout(
                    self.fadeout_duration,
                    0,
                    FadeOutType[self.fadeout_type],
                )
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

            if fade and self._state & CueState.Running and self._can_fade():
                self._st_lock.release()
                ended = self.__fadeout(
                    self.fadeout_duration,
                    0,
                    FadeOutType[self.fadeout_type],
                )
                self._st_lock.acquire()
                if not ended:
                    return False

        self.media.pause()
        return True

    def __interrupt__(self, fade=False):
        if self._can_fade():
            self.__fader.stop()

            fade_duration = self._interrupt_fade_duration()
            if fade and fade_duration > 0 and self._state & CueState.Running:
                self.__fadeout(fade_duration, 0, self._interrupt_fade_type())

        self.media.stop()

    @async_function
    def fadein(self, duration, fade_type):
        if not self._st_lock.acquire(timeout=0.1):
            return

        if self._state & CueState.Running and self._can_fade():
            self.__fader.stop()

            if duration <= 0:
                self.__volume.live_volume = self.__volume.volume
            else:
                self._st_lock.release()
                self.__fadein(duration, self.__volume.volume, fade_type)
                return

        self._st_lock.release()

    def loop_release(self):
        self.media.loop_release()

    @async_function
    def fadeout(self, duration, fade_type):
        if not self._st_lock.acquire(timeout=0.1):
            return

        if self._state & CueState.Running and self._can_fade():
            self.__fader.stop()

            if duration <= 0:
                self.__volume.live_volume = 0
            else:
                self._st_lock.release()
                self.__fadeout(duration, 0, fade_type)
                return

        self._st_lock.release()

    def __fadein(self, duration, to_value, fade_type):
        ended = True
        if duration > 0 and self._can_fade():
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
        if duration > 0 and self._can_fade():
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

    def is_fading_in(self):
        return self.__in_fadein

    def is_fading_out(self):
        return self.__in_fadeout

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

    def _can_fade(self):
        return self.__volume is not None and self.__fader is not None

    @async_function
    def _on_start_fade(self):
        if self._can_fade():
            self.__fadein(
                self.fadein_duration,
                self.__volume.volume,
                FadeInType[self.fadein_type],
            )
