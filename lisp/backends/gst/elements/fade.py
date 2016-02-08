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

from threading import Lock
from time import sleep

from lisp.backends.base.media_element import ElementType, MediaType
from lisp.backends.gst.gi_repository import Gst
from lisp.backends.gst.gst_element import GstMediaElement
from lisp.core.decorators import async
from lisp.core.has_properties import Property
from lisp.core.signal import Signal
from lisp.utils.fade_functor import ntime, FadeOut, FadeIn


class Fade(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = 'Fade'

    fadein = Property(default=0)
    fadein_type = Property(default='Linear')
    fadeout = Property(default=0)
    fadeout_type = Property(default='Linear')

    def __init__(self, pipeline):
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

        self.pipeline = pipeline
        self.volume = Gst.ElementFactory.make('volume', None)
        self.audio_convert = Gst.ElementFactory.make('audioconvert', None)

        self.pipeline.add(self.volume)
        self.pipeline.add(self.audio_convert)

        self.volume.link(self.audio_convert)

        # If we have a non null fadein we need to start form volume 0
        self.changed('fadein').connect(self.__prepare)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        self._handler = bus.connect('message', self.__on_message)

    def sink(self):
        return self.volume

    def src(self):
        return self.audio_convert

    def stop(self):
        if self.fadeout > 0:
            self._fadeout()

    pause = stop

    def dispose(self):
        bus = self.pipeline.get_bus()
        bus.remove_signal_watch()
        bus.disconnect(self._handler)

    @async
    def _fadein(self):
        self._flag = True
        self._lock.acquire()
        self._flag = False

        try:
            self.enter_fadein.emit()

            functor = FadeIn[self.fadein_type]
            duration = self.fadein * 100
            volume = self.volume.get_property('volume')
            time = 0

            while time <= duration and self._playing and not self._flag:
                self.volume.set_property('volume',
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

            functor = FadeOut[self.fadeout_type]
            duration = self.fadeout * 100
            volume = self.volume.get_property('volume')
            time = 0

            while time <= duration and self._playing and not self._flag:
                self.volume.set_property('volume',
                                          functor(ntime(time, 0, duration),
                                                  -volume, volume))
                time += 1
                sleep(0.01)

            self.exit_fadeout.emit()
        finally:
            self._lock.release()

    def __on_message(self, bus, message):
        if message.src == self.volume:
            if message.type == Gst.MessageType.STATE_CHANGED:
                state = message.parse_state_changed()[1]
                self._playing = state == Gst.State.PLAYING

                if self.fadein > 0:
                    # If gone in PLAYING state then start the fadein
                    if self._playing:
                        self._fadein()
                    else:
                        # The next time the volume must start from 0
                        self.volume.set_property('volume', 0)
                elif not self._playing:
                    self.volume.set_property('volume', 1)

    def __prepare(self, value):
        if not self._playing:
            self.volume.set_property('volume', 0 if value > 0 else 0)
