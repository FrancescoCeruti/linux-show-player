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

from threading import Lock
from time import sleep

from lisp.backends.base.media_element import ElementType, MediaType
from lisp.core.signal import Signal
from lisp.backends.gst.gst_element import GstMediaElement
from lisp.backends.gst.gi_repository import Gst
from lisp.core.decorators import async
from lisp.utils.fade_functor import fade_linear, fadein_quad, fade_inout_quad, \
    fadeout_quad, ntime


class Fade(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = 'Fade'

    FadeIn = {'Linear': fade_linear, 'Quadratic': fadein_quad,
              'Quadratic2': fade_inout_quad}
    FadeOut = {'Linear': fade_linear, 'Quadratic': fadeout_quad,
               'Quadratic2': fade_inout_quad}

    _properties_ = ('fadein', 'fadein_type', 'fadeout', 'fadeout_type')

    def __init__(self, pipe):
        super().__init__()

        # Fade in/out signals
        self.enter_fadein = Signal()
        self.exit_fadein = Signal()
        self.enter_fadeout = Signal()
        self.exit_fadeout = Signal()

        # Mutual exclusion
        self._lock = Lock()
        self._flag = False
        # _flag is needed because when a fadeout occurs during a fadein,
        # or vice versa, the current fade must end before the new starts.
        self._playing = False

        self._volume = Gst.ElementFactory.make('volume', None)
        self._convert = Gst.ElementFactory.make('audioconvert', None)

        pipe.add(self._volume)
        pipe.add(self._convert)

        self._volume.link(self._convert)

        self.fadein = 0
        self.fadein_type = 'Linear'
        self.fadeout = 0
        self.fadeout_type = 'Linear'

        self.property_changed.connect(self.__property_changed)

        self._bus = pipe.get_bus()
        self._bus.add_signal_watch()
        self._handler = self._bus.connect('message', self.__on_message)

    def sink(self):
        return self._volume

    def src(self):
        return self._convert

    def stop(self):
        if self.fadeout > 0:
            self._fadeout()

    pause = stop

    def dispose(self):
        self._bus.remove_signal_watch()
        self._bus.disconnect(self._handler)

    @async
    def _fadein(self):
        self._flag = True
        self._lock.acquire()
        self._flag = False

        try:
            self.enter_fadein.emit()

            functor = Fade.FadeIn[self.fadein_type]
            duration = self.fadein * 100
            volume = self._volume.get_property('volume')
            time = 0

            while time <= duration and self._playing and not self._flag:
                self._volume.set_property('volume',
                                          functor(ntime(time, 0, duration),
                                                  1 - volume, volume))
                time += 1
                sleep(0.01)

            self.exit_fadein.emit()
        finally:
            self._lock.release()

    def _fadeout(self):
        self._flag = True
        self._lock.acquire()
        self._flag = False

        try:
            self.enter_fadeout.emit()

            functor = Fade.FadeOut[self.fadeout_type]
            duration = self.fadeout * 100
            volume = self._volume.get_property('volume')
            time = 0

            while time <= duration and self._playing and not self._flag:
                self._volume.set_property('volume',
                                          functor(ntime(time, 0, duration),
                                                  -volume, volume))
                time += 1
                sleep(0.01)

            self.exit_fadeout.emit()
        finally:
            self._lock.release()

    def __on_message(self, bus, message):
        if message.src == self._volume:
            if message.type == Gst.MessageType.STATE_CHANGED:
                state = message.parse_state_changed()[1]

                self._playing = state == Gst.State.PLAYING

                if self.fadein > 0:
                    # If gone in PLAYING state then start the fadein
                    if self._playing:
                        self._fadein()
                    else:
                        # The next time the volume must start from 0
                        self._volume.set_property('volume', 0)
                elif not self._playing:
                    self._volume.set_property('volume', 1)

    def __property_changed(self, name, value):
        if name == 'fadein' and not self._playing:
            self._volume.set_property('volume', 0 if value > 0 else 0)
