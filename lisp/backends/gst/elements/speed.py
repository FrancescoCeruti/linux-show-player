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

from lisp.backends.base.media_element import ElementType, MediaType
from lisp.backends.gst.gst_element import GstMediaElement
from lisp.backends.gst.gi_repository import Gst


class Speed(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = "Speed"

    _properties_ = ('speed', )

    def __init__(self, pipe):
        super().__init__()

        self._scaletempo = Gst.ElementFactory.make("scaletempo", None)
        self._convert = Gst.ElementFactory.make("audioconvert", None)

        pipe.add(self._scaletempo)
        pipe.add(self._convert)

        self._scaletempo.link(self._convert)

        self.__speed = 1.0

        self.__bus = pipe.get_bus()
        self.__bus.add_signal_watch()
        self.__handler = self.__bus.connect("message", self.__on_message)

        self._state = None

    @property
    def speed(self):
        return self.__speed

    @speed.setter
    def speed(self, value):
        if value != self.__speed:
            self.__speed = value

            if self._state == Gst.State.PLAYING:
                self.__changeSpeed()

    def sink(self):
        return self._scaletempo

    def src(self):
        return self._convert

    def dispose(self):
        self.__bus.remove_signal_watch()
        self.__bus.disconnect(self.__handler)

    def __on_message(self, bus, message):
        if message.type == Gst.MessageType.STATE_CHANGED:
            if message.src == self._scaletempo:
                self._state = message.parse_state_changed()[1]

                if self._state == Gst.State.PLAYING:
                    self.__changeSpeed()

    def __changeSpeed(self):
        current_position = self._scaletempo.query_position(Gst.Format.TIME)[1]

        self._scaletempo.seek(self.speed,
                              Gst.Format.TIME,
                              Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
                              Gst.SeekType.SET,
                              current_position,
                              Gst.SeekType.NONE,
                              0)
