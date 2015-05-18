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

from lisp.core.signal import Signal
from lisp.backends.base.media_element import ElementType, MediaType
from lisp.backends.gst.gst_element import GstMediaElement
from lisp.backends.gst.gi_repository import Gst


class Dbmeter(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = "DbMeter"

    _properties_ = ('interval', 'peak_ttl', 'peak_falloff')

    def __init__(self, pipe):
        super().__init__()

        self.level_ready = Signal()

        self._level = Gst.ElementFactory.make("level", None)
        self._level.set_property('post-messages', True)
        self._level.set_property('interval', 50 * Gst.MSECOND)
        self._level.set_property('peak-ttl', Gst.SECOND)
        self._level.set_property('peak-falloff', 20)
        self._convert = Gst.ElementFactory.make("audioconvert", None)

        pipe.add(self._level)
        pipe.add(self._convert)

        self._level.link(self._convert)

        self.interval = 50 * Gst.MSECOND
        self.peak_ttl = Gst.SECOND
        self.peak_falloff = 20

        self.property_changed.connect(self.__property_changed)

        self.__bus = pipe.get_bus()
        self.__bus.add_signal_watch()
        self.__handler = self.__bus.connect("message::element",
                                            self.__on_message)

    def dispose(self):
        self.__bus.remove_signal_watch()
        self.__bus.disconnect(self.__handler)

    def sink(self):
        return self._level

    def src(self):
        return self._convert

    def __property_changed(self, name, value):
        name = name.replace('_', '-')
        self._level.set_property(name, value)

    def __on_message(self, bus, message):
        if message.src == self._level:
            structure = message.get_structure()
            if structure is not None and structure.has_name('level'):
                self.level_ready.emit(structure.get_value('peak'),
                                      structure.get_value('rms'),
                                      structure.get_value('decay'))
